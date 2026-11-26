# Project Context & Architecture: Kraków Transit Analytics (ZTP GTFS-RT)

## 1. Opis Projektu (Project Overview)
System analityczny badający punktualność komunikacji miejskiej w Krakowie na podstawie otwartych danych ZTP Kraków (`gtfs.ztp.krakow.pl`). 
Główny cel: Zbieranie w czasie rzeczywistym predykcji i czasów przyjazdów autobusów na przystanki, wyliczanie opóźnień względem rozkładu jazdy oraz prezentacja statystyk (średnia, mediana P50, percentyl P90, rozkład godzinowy) w aplikacji webowej.

---

## 2. Stack Technologiczny (Tech Stack)

### Warstwa Danych (Database & Storage)
* **Baza danych:** PostgreSQL 16 + rozszerzenie **TimescaleDB** (obraz Docker: `timescale/timescaledb-ha:pg16`).
* **Przechowywanie:**
  * **Tabele słownikowe (Relacyjne SQL):** Dane z `GTFS Static` (`stops`, `routes`, `trips`).
  * **Tabela szeregów czasowych (TimescaleDB Hypertable):** Dane o opóźnieniach z `GTFS-Realtime` (`stop_delay_logs`).
  * **Przetwarzanie w locie (In-Memory):** Pliki `.pb` oraz `.zip` są pobierane i parsowane bezpośrednio w pamięci RAM (`io.BytesIO`), bez zapisywania tysięcy małych plików na dysku.

### Backend & Data Ingestion (Python)
* **Język:** Python 3.11+ (pełne wykorzystanie `asyncio` i Type Hints).
* **Klient HTTP:** `httpx` (asynchroniczny, obsługa Conditional Requests: `ETag` / `If-None-Match` oraz `Last-Modified` / `If-Modified-Since`).
* **Parser GTFS-RT:** `gtfs-realtime-bindings` (`google.transit.gtfs_realtime_pb2` – Protocol Buffers).
* **Baza danych / ORM:** **SQLAlchemy 2.0 (async)** (`DeclarativeBase`, `Mapped`, `mapped_column`) + sterownik **`asyncpg`**. Wykorzystanie dialektu PostgreSQL do masowych operacji `UPSERT` (`from sqlalchemy.dialects.postgresql import insert as pg_insert`).
* **Framework API:** **FastAPI** (wystawienie zagregowanych statystyk przez REST API do frontendu).

### Frontend
* **Framework:** **Next.js (App Router)** + TypeScript.
* **UI & Wykresy:** Tailwind CSS + `shadcn/ui` + Recharts / Tremor / Apache ECharts.
* **Mapy (Docelowo):** MapLibre GL + Deck.gl.

---

## 3. Źródła Danych i Logika Ingestii (Data Pipeline)

Dane pochodzą z serwerów ZTP Kraków (w MVP skupiamy się na autobusach – sufiks `_A`):
1. **GTFS Static (`https://gtfs.ztp.krakow.pl/GTFS_KRK_A.zip`):**
   * Zawiera pliki CSV (`.txt`): `stops.txt`, `routes.txt`, `trips.txt`, `stop_times.txt`.
   * **Zasada aktualizacji:** Nigdy nie wykonujemy `TRUNCATE` / `DELETE` na tabelach słownikowych, aby nie osierocić historycznych logów opóźnień. Stosujemy `UPSERT` (`ON CONFLICT DO UPDATE`) po kluczu głównym, dopisując nowe identyfikatory i aktualizując istniejące.
   * *(Rozwinięcie docelowe)*: Wersjonowanie rozkładów poprzez hashowanie wierszy (SHA-256 z kanonicznej reprezentacji kursu i jego przystanków) lub kolumnę `feed_version_id`.
2. **GTFS-Realtime (`https://gtfs.ztp.krakow.pl/TripUpdates_A.pb`):**
   * Binarny strumień Protocol Buffers odpytywany w pętli co 15–20 sekund.
   * **Smart Polling (Dwustopniowe sito):**
     1. Sprawdzenie nagłówków HTTP (`ETag` / `Last-Modified`) -> jeśli serwer zwraca `304 Not Modified`, pomijamy cykl.
     2. Sprawdzenie `feed.header.timestamp` wewnątrz rozpakowanego Protobufa -> jeśli `timestamp <= last_pb_timestamp`, pomijamy zapis do bazy.

---

## 4. Architektura Bazy Danych (Schemat MVP)

### Tabele Słownikowe (GTFS Static)
* **`stops`:** `stop_id` (PK, String), `stop_code`, `stop_name` (Indexed), `stop_lat`, `stop_lon`.
* **`routes`:** `route_id` (PK, String), `route_short_name` (Indexed, np. `"139"`), `route_long_name`, `route_type`.
* **`trips`:** `trip_id` (PK, String), `route_id` (FK -> `routes.route_id`), `service_id`, `trip_headsign`, `direction_id`, `block_id`, `shape_id`.

### Tabela Czasowa – Hypertable (`stop_delay_logs`)
* **Koncepcja (Samowystarczalność / Denormalizacja pod MVP):** Zamiast trzymać każdy odczyt co 20 sekund jako osobny duplikat, utrzymujemy jeden, zawsze aktualny rekord dla danego kursu na danym przystanku w konkretnym dniu.
* **Klucz główny / Unikalny pod UPSERT:** Złożony z identyfikatora dnia kursu (np. `service_date` / czas partycjonowania), `trip_id` oraz `stop_id`.
* **Wyliczanie czasu rozkładowego w locie:** Z pliku `TripUpdates_A.pb` pobieramy `arrival.time` (rzeczywisty przewidywany czas Unix Timestamp) oraz `arrival.delay` (opóźnienie w sekundach). Czas rozkładowy wyliczamy matematycznie: `scheduled_arrival = actual_arrival - delay`.
* **Zapis:** Masowy `Batch UPSERT` (`ON CONFLICT DO UPDATE`) aktualizujący opóźnienie w miarę zbliżania się autobusu do przystanku, aż do ostatecznego zameldowania się na przystanku.

---

## 5. Zakres MVP (Co robimy teraz, a co odkładamy na później)

| Element | Wersja MVP (Aktualny cel) | Wersja Docelowa (Post-MVP) |
| :--- | :--- | :--- |
| **Wyliczanie opóźnień** | Gotowe pole `delay` z `TripUpdates_A.pb` | Geofencing GPS w PostGIS z `VehiclePositions_A.pb` (`ST_DWithin`) |
| **Zakres taboru** | Tylko autobusy (`_A`) | Autobusy (`_A`) + Tramwaje (`_T`) |
| **Komunikacja z bazą** | PostgreSQL + TimescaleDB (Batch UPSERT) | Dodanie warstwy Redis (stan live) + Continuous Aggregates |
| **Komunikacja API -> Front** | Klasyczny REST API w FastAPI | REST API + WebSockets / Server-Sent Events (SSE) dla mapy live |

---

## 6. ZASADY WSPÓŁPRACY DLA AI (AI Collaboration Rules - CRITICAL!)

Jeśli czytasz ten dokument jako asystent AI wspierający mnie w tym projekcie, **bezwzględnie przestrzegaj poniższych zasad**:

1. **TRYB MENTORINGU (Zero gotowców):** Chcę nauczyć się myśleć jak inżynier oprogramowania. **NIE PISZ ZA MNIE GOTOWEGO KODU APLIKACJI.** 
   * Tłumacz koncepcje, architekturę, strukturę danych i algorytmy słownie lub za pomocą pseudokodu.
   * Wskazuj odpowiednie metody z bibliotek, pułapki (edge-case'y, limity parametrów SQL, kodowanie znaków `utf-8-sig`, użycie `HasField` w Protobufie) i zadawaj pytania naprowadzające.
   * Rób dokładne *Code Review* kodu, który sam napiszę i Ci wkleję.
2. **OZNACZANIE KODU (Tagowanie):** Jeśli wyraźnie poproszę Cię o napisanie fragmentu kodu (np. nudnego boilerplate'u) lub pokazujesz krótki, abstrakcyjny przykład składni na innej domenie, **KAŻDA pojedyncza linijka kodu napisana lub poprawiona przez Ciebie MUSI kończyć się komentarzem**:
   * `# created with Gemini Argon` (dla nowego kodu)
   * `# fixed with Gemini Argon` (dla poprawionej linijki podczas Code Review)
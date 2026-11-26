from datetime import date  # fixed with Gemini Argon
from typing import Optional

from sqlalchemy import Date, Float, Index, Integer, String  # fixed with Gemini Argon
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class VersionedMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    row_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)


class Route(VersionedMixin, Base):
    __tablename__ = "routes"
    __table_args__ = (
        Index("ix_routes_id_valid_to", "route_id", "valid_to"),
        Index("ix_routes_id_valid_range", "route_id", "valid_from", "valid_to"),
    )

    route_id: Mapped[str] = mapped_column(String, nullable=False)  # fixed with Gemini Argon
    agency_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # fixed with Gemini Argon
    route_short_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    route_long_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # fixed with Gemini Argon
    route_desc: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # fixed with Gemini Argon
    route_type: Mapped[int] = mapped_column(Integer, nullable=False)
    route_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    route_color: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    route_text_color: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # fixed with Gemini Argon
    route_sort_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    continuous_pickup: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    continuous_drop_off: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class StopTime(VersionedMixin, Base):
    __tablename__ = "stop_times"
    __table_args__ = (
        Index("ix_stop_times_trip_valid_to", "trip_id", "valid_to"),
        Index("ix_stop_times_trip_valid_range", "trip_id", "valid_from", "valid_to"),
        Index("ix_stop_times_stop_valid_to", "stop_id", "valid_to"),
    )

    trip_id: Mapped[str] = mapped_column(String, nullable=False)
    arrival_time: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # fixed with Gemini Argon
    departure_time: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # fixed with Gemini Argon
    stop_id: Mapped[str] = mapped_column(String, nullable=False)  # fixed with Gemini Argon
    stop_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    stop_headsign: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pickup_type: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    drop_off_type: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shape_dist_traveled: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timepoint: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class CalendarDate(VersionedMixin, Base):
    __tablename__ = "calendar_dates"
    __table_args__ = (
        Index("ix_calendar_dates_service_valid_to", "service_id", "valid_to"),
        Index("ix_calendar_dates_service_valid_range", "service_id", "valid_from", "valid_to"),
    )

    service_id: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    exception_type: Mapped[int] = mapped_column(Integer, nullable=False)


class Calendar(VersionedMixin, Base):
    __tablename__ = "calendar"
    __table_args__ = (
        Index("ix_calendar_service_valid_to", "service_id", "valid_to"),
        Index("ix_calendar_service_valid_range", "service_id", "valid_from", "valid_to"),
    )

    service_id: Mapped[str] = mapped_column(String, nullable=False)
    monday: Mapped[int] = mapped_column(Integer, nullable=False)
    tuesday: Mapped[int] = mapped_column(Integer, nullable=False)
    wednesday: Mapped[int] = mapped_column(Integer, nullable=False)
    thursday: Mapped[int] = mapped_column(Integer, nullable=False)
    friday: Mapped[int] = mapped_column(Integer, nullable=False)
    saturday: Mapped[int] = mapped_column(Integer, nullable=False)
    sunday: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[str] = mapped_column(String, nullable=False)
    end_date: Mapped[str] = mapped_column(String, nullable=False)


class Stop(VersionedMixin, Base):
    __tablename__ = "stops"
    __table_args__ = (
        Index("ix_stops_id_valid_to", "stop_id", "valid_to"),
        Index("ix_stops_id_valid_range", "stop_id", "valid_from", "valid_to"),
    )

    stop_id: Mapped[str] = mapped_column(String, nullable=False)  # fixed with Gemini Argon
    stop_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    stop_name: Mapped[str] = mapped_column(String, nullable=False)
    stop_desc: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # fixed with Gemini Argon
    stop_lat: Mapped[float] = mapped_column(Float, nullable=False)
    stop_lon: Mapped[float] = mapped_column(Float, nullable=False)
    zone_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # fixed with Gemini Argon
    stop_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location_type: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    parent_station: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    stop_timezone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    wheelchair_boarding: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    platform_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class Shapez(VersionedMixin, Base):
    __tablename__ = "shapez"
    __table_args__ = (
        Index("ix_shapez_id_valid_to", "shape_id", "valid_to"),
        Index("ix_shapez_id_valid_range", "shape_id", "valid_from", "valid_to"),
    )

    shape_id: Mapped[str] = mapped_column(String, nullable=False)  # fixed with Gemini Argon
    shape_pt_lat: Mapped[float] = mapped_column(Float, nullable=False)
    shape_pt_lon: Mapped[float] = mapped_column(Float, nullable=False)
    shape_pt_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    shape_dist_traveled: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class Trip(VersionedMixin, Base):
    __tablename__ = "trips"
    __table_args__ = (
        Index("ix_trips_id_valid_to", "trip_id", "valid_to"),
        Index("ix_trips_id_valid_range", "trip_id", "valid_from", "valid_to"),
        Index("ix_trips_route_valid_to", "route_id", "valid_to"),
    )

    route_id: Mapped[str] = mapped_column(String, nullable=False)  # fixed with Gemini Argon
    service_id: Mapped[str] = mapped_column(String, nullable=False)
    trip_id: Mapped[str] = mapped_column(String, nullable=False)
    trip_headsign: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    trip_short_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    direction_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    block_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # fixed with Gemini Argon
    shape_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # fixed with Gemini Argon
    wheelchair_accessible: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bikes_allowed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
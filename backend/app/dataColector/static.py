import time

import httpx
import io
import zipfile
import csv

from sqlalchemy import engine
from sqlalchemy import create_engine, String, Float, select, insert
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from dotenv import load_dotenv
import os

from datetime import date

from database.staticTemplate import Base, Trip, Stop, Route, StopTime, CalendarDate, Calendar, Shapez  # fixed with Gemini Argon


import hashlib
import json
from typing import Any

load_dotenv()
engine = create_engine(f"postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_IP")}/{os.getenv("POSTGRES_DB")}")

Base.metadata.create_all(engine)


def createHash(record : dict, agruments : list[str]) -> str:
    m = hashlib.md5()
    for k, v in record.items():
        if v == "":
            record[k] = None

    for arg in agruments:
        m.update(record[arg].encode("utf-8"))
    return m.hexdigest()



def update_database(content : list[dict], filename : str,timestamp : int) -> None:
    global engine
    match filename.replace(".txt",""):
        case "trips":
            hashing_arguments = ["route_id","service_id","trip_id","direction_id","shape_id"]
            print("updatuje trip")
            for i, record in enumerate(content):
                content[i]["row_hash"] = createHash(record,hashing_arguments)
                content[i]["valid_from"] = date.today()
                content[i]["valid_to"] = None
            print("updatuje trip, dodane hashowanie")
            with Session(engine) as session:
                session.execute(insert(Trip), content)
                session.commit()
        case "stops":
            print("updatuje stops")
            hashing_arguments = ["stop_id","stop_name","stop_lat","stop_lon"]
            for i, record in enumerate(content):
                content[i]["row_hash"] = createHash(record,hashing_arguments)
                content[i]["valid_from"] = date.today()
                content[i]["valid_to"] = None
            print("updatuje stop, dodane hashowanie")
            with Session(engine) as session:
                session.execute(insert(Stop), content)
                session.commit()
        case "routes":  # created with Gemini Argon
            print("updatuje routes")  # created with Gemini Argon
            hashing_arguments = ["route_id", "agency_id", "route_short_name", "route_long_name", "route_type"]  # created with Gemini Argon
            for i, record in enumerate(content):  # created with Gemini Argon
                content[i]["row_hash"] = createHash(record, hashing_arguments)  # created with Gemini Argon
                content[i]["valid_from"] = date.today()  # created with Gemini Argon
                content[i]["valid_to"] = None  # created with Gemini Argon
            print("updatuje routes, dodane hashowanie")  # created with Gemini Argon
            with Session(engine) as session:  # created with Gemini Argon
                session.execute(insert(Route), content)  # created with Gemini Argon
                session.commit()  # created with Gemini Argon
        case "stop_times":  # created with Gemini Argon
            print("updatuje stop_times")  # created with Gemini Argon
            hashing_arguments = ["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence", "stop_headsign", "pickup_type", "drop_off_type"]  # created with Gemini Argon
            for i, record in enumerate(content):  # created with Gemini Argon
                content[i]["row_hash"] = createHash(record, hashing_arguments)  # created with Gemini Argon
                content[i]["valid_from"] = date.today()  # created with Gemini Argon
                content[i]["valid_to"] = None  # created with Gemini Argon
            print("updatuje stop_times, dodane hashowanie")  # created with Gemini Argon
            with Session(engine) as session:  # created with Gemini Argon
                session.execute(insert(StopTime), content)  # created with Gemini Argon
                session.commit()  # created with Gemini Argon
        case "calendar_dates":  # created with Gemini Argon
            print("updatuje calendar_dates")  # created with Gemini Argon
            hashing_arguments = ["service_id", "date", "exception_type"]  # created with Gemini Argon
            for i, record in enumerate(content):  # created with Gemini Argon
                content[i]["row_hash"] = createHash(record, hashing_arguments)  # created with Gemini Argon
                content[i]["valid_from"] = date.today()  # created with Gemini Argon
                content[i]["valid_to"] = None  # created with Gemini Argon
            print("updatuje calendar_dates, dodane hashowanie")  # created with Gemini Argon
            with Session(engine) as session:  # created with Gemini Argon
                session.execute(insert(CalendarDate), content)  # created with Gemini Argon
                session.commit()  # created with Gemini Argon
        case "calendar":  # created with Gemini Argon
            print("updatuje calendar")  # created with Gemini Argon
            hashing_arguments = ["service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "start_date", "end_date"]  # created with Gemini Argon
            for i, record in enumerate(content):  # created with Gemini Argon
                content[i]["row_hash"] = createHash(record, hashing_arguments)  # created with Gemini Argon
                content[i]["valid_from"] = date.today()  # created with Gemini Argon
                content[i]["valid_to"] = None  # created with Gemini Argon
            print("updatuje calendar, dodane hashowanie")  # created with Gemini Argon
            with Session(engine) as session:  # created with Gemini Argon
                session.execute(insert(Calendar), content)  # created with Gemini Argon
                session.commit()  # created with Gemini Argon
        case "shapes":  # created with Gemini Argon
            print("updatuje shapes")  # created with Gemini Argon
            hashing_arguments = ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence", "shape_dist_traveled"]  # created with Gemini Argon
            for i, record in enumerate(content):  # created with Gemini Argon
                content[i]["row_hash"] = createHash(record, hashing_arguments)  # created with Gemini Argon
                content[i]["valid_from"] = date.today()  # created with Gemini Argon
                content[i]["valid_to"] = None  # created with Gemini Argon
            print("updatuje shapes, dodane hashowanie")  # created with Gemini Argon
            with Session(engine) as session:  # created with Gemini Argon
                session.execute(insert(Shapez), content)  # created with Gemini Argon
                session.commit()  # created with Gemini Argon



def transformation(content,timestamp):
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for filename in zf.namelist():
            content = io.TextIOWrapper(zf.open(filename), encoding='utf-8')
            csvContent = csv.DictReader(content, delimiter=',')
            list_content = list(csvContent)
            print(filename, list_content[0])
            update_database(list_content,filename,time.time())
        print("koniec plików")


# TODO make request with etag to not download the redundant data
Etag = ''
while True:
    r = httpx.get("https://gtfs.ztp.krakow.pl/GTFS_KRK_A.zip")

    if Etag != r.headers["ETag"]:
        timestamp = time.time()
        transformation(r.content,timestamp)
        print("zrobione, ide spac")
    time.sleep(60*60*24)



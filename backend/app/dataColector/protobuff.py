import time
from datetime import datetime  # created with Gemini Argon
from zoneinfo import ZoneInfo  # created with Gemini Argon

from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import httpx




dataTemplate = {
    "timestamp":0,
    "trip_id":0,
    "route_id":0,
    "stop_id":0,
    "predicted_time":0,
    "delay":None, # fixepd with Gemini Argon
    "recorded_at":0,
    "service_day":None,
    "vehicle_id":0,
}


def update_database(record : dict):
    pass

# TODO:
# poprawic aby nie uzywac messageToDict tylko operowac na bitach, szybsze
def prepare_data(feed):
    message = MessageToDict(feed)
    header_ts = int(message["header"]["timestamp"])  # created with Gemini Argon
    krakow_tz = ZoneInfo("Europe/Warsaw")  # created with Gemini Argon
    for trip in message.get("entity", []):  # fixed with Gemini Argon
        trip_update = trip.get("tripUpdate", {})  # created with Gemini Argon
        trip_info = trip_update.get("trip", {})  # created with Gemini Argon
        vehicle_info = trip_update.get("vehicle", {})  # created with Gemini Argon
        recorded_at = int(trip_update.get("timestamp", header_ts))  # fixed with Gemini Argon
        for stopSequence in trip_update.get("stopTimeUpdate", []):  # fixed with Gemini Argon
            arrival = stopSequence.get("arrival", {})  # created with Gemini Argon
            departure = stopSequence.get("departure", {})  # created with Gemini Argon
            if int(arrival.get("time", 0)) > 0:  # created with Gemini Argon
                event = arrival  # created with Gemini Argon
            elif int(departure.get("time", 0)) > 0:  # created with Gemini Argon
                event = departure  # created with Gemini Argon
            else:  # created with Gemini Argon
                continue  # created with Gemini Argon
            predicted_time = int(event["time"])  # created with Gemini Argon
            raw_delay = event.get("delay")  # created with Gemini Argon
            record = dataTemplate.copy()  # created with Gemini Argon
            record["timestamp"] = header_ts  # created with Gemini Argon
            record["recorded_at"] = recorded_at  # fixed with Gemini Argon
            record["service_day"] = datetime.fromtimestamp(predicted_time, tz=krakow_tz).date()  # created with Gemini Argon
            record["trip_id"] = trip_info.get("tripId")  # fixed with Gemini Argon
            record["route_id"] = trip_info.get("routeId")  # fixed with Gemini Argon
            record["stop_id"] = stopSequence.get("stopId")  # fixed with Gemini Argon
            record["predicted_time"] = predicted_time  # fixed with Gemini Argon
            record["delay"] = int(raw_delay) if raw_delay is not None else None  # fixed with Gemini Argon
            record["vehicle_id"] = vehicle_info.get("id")  # created with Gemini Argon

            print(record)
            update_database(record)# fixed with Gemini Argon
            record = {}




r = httpx.get('https://gtfs.ztp.krakow.pl/TripUpdates_A.pb')

Etag = r.headers['ETag']
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(r.content)

timestamp = feed.header.timestamp
update_database(feed)

while (True):
    r = httpx.get('https://gtfs.ztp.krakow.pl/TripUpdates_A.pb')
    if Etag != r.headers['ETag']:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(r.content)
        if feed.header.timestamp != timestamp:
            prepare_data(feed)
    else:
        print("No updates available")
    time.sleep(15)





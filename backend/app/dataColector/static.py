import time

import httpx
import io
import zipfile
import csv

def update_database(content):
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for filename in zf.namelist():
            content = io.TextIOWrapper(zf.open(filename), encoding='utf-8')
            csvContent = csv.DictReader(content, delimiter=',')
            print(list(csvContent))




Etag = ''
while True:
    r = httpx.get("https://gtfs.ztp.krakow.pl/GTFS_KRK_A.zip")

    if Etag != r.headers["ETag"]:
        update_database(r.content)
    time.sleep(60*60*24)



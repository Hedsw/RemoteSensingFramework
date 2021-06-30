import os
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from glob import glob

class sentinelAPI:
    def API_info():
        link = 'https://scihub.copernicus.eu/dhus'
        loginId = 'kannsky'
        password = 'dbsgur1004!'

        return SentinelAPI(loginId, password, link)

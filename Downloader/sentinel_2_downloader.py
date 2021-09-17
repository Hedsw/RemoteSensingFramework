# Sentinel File 받을 때, 이거 그.. falskdeploy Pem키 가지고 있는 flaskwebcrawlertest 이름으로 있는 파일 안에 구현 되어 있음 
# connect to the API
import os
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from glob import glob
from xml.etree.ElementTree import parse
#from downloadmethod.sentinelAPI import API
from filechecker.zipreleaser import unzipper
import pandas as pd


class sentinel2:
    def sentinel_2(jsondirectory, from_period, to_period):
        filenames = []
        tree = parse('../XMLfiles/sentinel.xml')
        root = tree.getroot()
        getINFO = root.findall("Download")
        #USERID = getINFO.find("Userid")
        USERID = [x.findtext("Userid") for x in getINFO]
        PASSWORD = [x.findtext("Password") for x in getINFO]
        #LINK = [x.findtext("Hostname") for x in getINFO]
        USERID = str(USERID[0])
        PASSWORD = str(PASSWORD[0])
        #print(type(USERID), type(PASSWORD) , " What is typed?")
        #print(USERID, PASSWORD)

        api = SentinelAPI(USERID, PASSWORD, "https://apihub.copernicus.eu/apihub")
        # download single scene by known product id
        #product_id = '22e7af63-07ad-4076-8541-f6655388dc5e'
        # This is to download directly through product_id
        #api.download(product_id)

        # search by polygon, time, and SciHub query keywords
        footprint = geojson_to_wkt(read_geojson(jsondirectory))
        periodFrom_TEST = "20190622"
        periodTo_TEST = "20190624"
        print("Footprint is done and searching files now.. ")
        tiles = ['35VMD', '35VLD', '35VLE']

        products = api.query(footprint,
                            date = (periodFrom_TEST, periodTo_TEST), # We can choose specific date also.
                            #date = ("NOW-5DAYS", "NOW"), # "NOW-XXDAYS", "NOW" -> download files from before 10 days to Now
                            platformname = 'Sentinel-2',
                            cloudcoverpercentage=(0, 30))
        if len(products) == 0:
            print("There is no files on the period and conditions")
        
        if len(products) > 4:
            print("CAN NOT DOWNLOAD OVER 4 FILE CONCURRENTLY. SENTINEL API IS NOT SUPPORTED. CHECK SENTINEL API REFERENCE")
            return False
        
        """
        HTTP status 403 Forbidden: User quota exceeded: MediaRegulationException : 
        An exception occured while creating a stream: Maximum number of 4 concurrent flows achieved by the user "kannsky"
        일반 유저들은 총 4개만 연속으로 다운 받을 수 있기 때문에 맨 앞에 4개만 받도록 제한 걸어둠. 안그러면 에러가 난다.
        
        """
#        products_df = api.to_dataframe(products)
#        products_df_sorted = products_df.sort_values(['cloudcoverpercentage', 'ingestiondate'], ascending=[True, True])
#        products_df_sorted = products_df_sorted.head(5)
        
        # download_all(products, directory_path=’.’, max_attempts=10, checksum=True, n_concurrent_dl=None, lta_retry_delay=None, fail_fast=False, nodefilter=None)
        api.download_all(products, "../storage/sentinelfiles/", 10, True, 4)
        
        """
                
        # Download query files
        print("File Number: ", + len(products))
        if len(products) == 0:
            print("There is no files on the period and conditions")
            return False
            
        print("File Query is done")

        # download all results from the search
        #api.download_all(products)
        api.download_all(products)
        
        
        # convert to Pandas DataFrame
        products_df = api.to_dataframe(products)

        # GeoJSON FeatureCollection containing footprints and metadata of the scenes
        api.to_geojson(products)

        # GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
        api.to_geodataframe(products)

        # Get basic information about the product: its title, file size, MD5 sum, date, footprint and
        # its download url
        api.get_product_odata(product_id)

        # Get the product's full metadata available on the server
        api.get_product_odata(product_id, full=True)
        
        """

        return True

    # To extract files, use unzip()
    #unzipper.unzip()
'''
https://sentinelsat.readthedocs.io/en/v1.10/

'''
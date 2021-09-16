# Sentinel File 받을 때, 이거 그.. falskdeploy Pem키 가지고 있는 flaskwebcrawlertest 이름으로 있는 파일 안에 구현 되어 있음 
# connect to the API
import os
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from glob import glob
from downloadmethod.sentinelAPI import sentinelAPI
from filechecker.zipreleaser import unzipper

class sentinel2:
    def sentinel_2(self, jsondirectory):
        filenames = []
        api = sentinel_API()

        # download single scene by known product id
        # product_id = '22e7af63-07ad-4076-8541-f6655388dc5e'
        # This is to download directly through product_id
        #api.download(product_id)

        # search by polygon, time, and SciHub query keywords
        footprint = geojson_to_wkt(read_geojson(self.jsondirectory))

        print("Footprint is done and searching files now.. ")
        tiles = ['35VMD', '35VLD', '35VLE']

        products = api.query(footprint,
                            #date = ('20190622', '20190624'), # We can choose specific date also.
                            date = ("NOW-5DAYS", "NOW"), # "NOW-XXDAYS", "NOW" -> download files from before 10 days to Now
                            platformname = 'Sentinel-2', # Sentinel-1, Sentinel-2, Sentinel-3
                            cloudcoverpercentage = (0, 10)) # Cloud cover percentage 0 - 100%

        # Download query files
        print("File Number: ", + len(products))
        print("File Query is done")

        # download all results from the search
        #api.download_all(products)
        print(api.download_all(products))

    # To extract files, use unzip()
    #unzipper.unzip()

'''
lists = glob('storage/*.zip')

for i in range(len(lists)):
    os.system('unzip %s /storage' %lists[i])

'''

"""
TEST APIs below
"""

'''
# convert to Pandas DataFrame
products_df = api.to_dataframe(products)
print("Convert Product_df is started")

products_df_sorted = products_df.sort_values(['cloudcoverpercentage', 'ingestiondate'], ascending=[True, True])
products_df_sorted = products_df_sorted.head(5)

# download sorted and reduced products
print("Convert Product_df is done")
api.download_all(products_df_sorted.index)

'''

'''
# GeoJSON FeatureCollection containing footprints and metadata of the scenes
api.to_geojson(products)
print("Convert Product_df is done")

# GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
api.to_geodataframe(products)

# Get basic information about the product: its title, file size, MD5 sum, date, footprint and
# its download url
api.get_product_odata(product_id)

# Get the product's full metadata available on the server
api.get_product_odata(product_id, full=True)

# https://scihub.copernicus.eu/dhus/odata/v1/Products('22e7af63-07ad-4076-8541-f6655388dc5e')
'''

'''
api = SentinelAPI("XXXXXX", "XXXXXXX")

tiles = ["35VMD", "35VLD", "35VLE"]

query_kwargs = {
    "platformname": "Sentinel-2",
    "producttype": "S2MSI1C",
    "cloudcoverpercentage": (0, 100),
    'date': ("NOW-1DAY", "NOW")

}

products = OrderedDict()
for tile in tiles:
    kw = query_kwargs.copy()
    kw["tileid"] = tile
    pp = api.query(**kw)
    products.update(pp)

api.download_all(products)

https://sentinelsat.readthedocs.io/en/v0.15/

'''
import os
from glob import glob

class unzipper:
    def unzip(self):
        #os.system('wget -P files/nc4file/ --user gogod951 --password dbsGUR123@# https://disc2.gesdisc.eosdis.nasa.gov/data/TRMM_RT/TRMM_3B42RT_Daily.7/2002/01/%s' %filename)
        os.system('mv *.zip ../../storage/sentinelfiles')

        lists = glob('../../storage/sentinelfiles/*.zip')
        print(lists)

        for i in range(len(lists)):
            os.system('unzip %s' %lists[i])
        os.system('mv *.SAFE ../../storage/sentinelfiles')

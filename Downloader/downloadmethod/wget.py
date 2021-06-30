import wget
import os

def wgetcall(url, filename):
    os.system('wget -P ../../storage/nc4file/ --user gogod951 --password dbsGUR123@# %s/%s' %(url,filename))

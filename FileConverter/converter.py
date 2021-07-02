from osgeo import gdal
from glob import glob
import numpy as numpy
import matplotlib.pyplot as plt
import os
import threading
import time

name = []
filenames = []
#print("Test")
class fileconverter:
    def nc4converter(i,lists):
        try:
            os.system('mkdir ../storage/outputtif/%s' %i)
            os.system('gdal_translate -sds %s ../storage/outputtif/%s/output.tif' %(lists[i], i))
            time.sleep(0.15)
            os.system('gdal_merge.py -separate -o ../storage/outputtif/%s/final_output.tif ../storage/outputtif/%s/output*tif' %(i,i))
            os.system('mv ../storage/outputtif/%s/final_output.tif ../storage/geotiffiles/geotif_%s.tif' %(i,i))
            #os.system('rm storage/geoTIFfile/%s/geoFiles/output*tif' %i)
            #os.system('rm -rf ../storage/outputtif/*')
        except Exception as e:
            print(" File not found, please refer to the website manually for download link", e)
        return True
    
class threadrunner:
    def threadstarter():
        os.system('rm -rf ../storage/nc4file/*1')
        lists = glob('../storage/nc4file/*.nc4')
        for i in range(len(lists)):    
            processThread = threading.Thread(target=fileconverter.nc4converter, args=(i,lists)) # parameters and functions have to be passed separately
            processThread.start() # START THE THREAD
        return True
    #starter()
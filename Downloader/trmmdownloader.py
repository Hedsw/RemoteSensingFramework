'''
File Size Linux.. In terminal..
sudo du -sh
'''
import urllib.request as urllib2
import re,requests,wget,os,threading
from bs4 import BeautifulSoup
from xml.etree.ElementTree import parse

# FILE LINK GET FROM XML
class xmlcontroller:
    def xml_trmm_rt_file():
        tree = parse('../XMLfiles/trmm_rt.xml')
        root = tree.getroot()
        trmm = root.findall("DATA")
        link = [x.findtext("LINK") for x in trmm]
        #types = [x.findtext("TYPES") for x in trmm]
        #year = [x.findtext("START_YEAR") for x in trmm]
        print(link[0] + " Show Me the link")
        return link[0]

    def xml_merged_ir_file():
        tree = parse('../XMLfiles/merged_ir.xml')
        root = tree.getroot()
        trmm = root.findall("DATA")
        link = [x.findtext("LINK") for x in trmm]
        #types = [x.findtext("TYPES") for x in trmm]
        #year = [x.findtext("START_YEAR") for x in trmm]
        return link[0]

# BRING FILE NAME FROM LINK 
class filecontroller:
    def filenamesget(url):
        #baseUrl = url_sample
        filenames = []
        req = urllib2.Request(url)
        sourcecode = urllib2.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, 'html.parser')

        xml = "xml"
        for href in soup.find("table").find_all('a', href=re.compile("nc4")):
            fname = href["href"]
            filenames.append(fname)
            
        setfile = set(filenames)
        filenames.clear()
        list_set = list(setfile)
        list_set.sort()
        for i in list_set:
            if xml not in i:
                filenames.append(i)
        return filenames
    
# download files into converter-system folder - 1 
class downloadcontroller: 
    def wgetdownload(url,filename):
        try:
            os.system('wget -P ../storage/nc4file/ --user gogod951 --password dbsGUR123@# %s/%s' %(url,filename))
        except Exception as e:
            print(" File not found, please refer to the website manually for download link", e)

class threadcontroller:
    def threadrun(url, filenames):
        for name in filenames:
            processThread = threading.Thread(target=downloadcontroller.wgetdownload, args=(url, name)) # parameters and functions have to be passed separately
            processThread.start() # START THE THREAD
        # Join Thread HERE. Because For loop is over, then other Thread will be started. before then next Thread should be waited.
        processThread.join()
        
        return True
    
class trmmdownload:
    def download(url):
        filenames = filecontroller.filenamesget(url)
        threadcontroller.threadrun(url, filenames)
        
        

#threadrun(url_sample)



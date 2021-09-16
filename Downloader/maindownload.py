'''
File Size Linux.. In terminal..
sudo du -sh
'''
import urllib.request as urllib2
import re,requests,wget,os,threading
from bs4 import BeautifulSoup
from xml.etree.ElementTree import parse
from db_downloadinfo import dbdownloadtable_insert
from db_convertinfo import dbconverttable_insert

# FILE LINK GET FROM XML
class xmlcontroller:
    def xml_trmm_rt_file(fromP, toP):
        tree = parse('../XMLfiles/trmm_rt.xml')
        root = tree.getroot()
        trmm = root.findall("DATA")
        link = [x.findtext("LINK") for x in trmm]
        #types = [x.findtext("TYPES") for x in trmm]
        #year = [x.findtext("START_YEAR") for x in trmm]
        #print(link[0] + " Show Me the link")
        return link[0]

    def xml_merged_ir_file(yearfrom, yearto): # yearfrom만 가지고 일하고 있고.. yaerto는 아직 안하고 있다
        tree = parse('../XMLfiles/merged_ir.xml')
        root = tree.getroot()
        merged_ir = root.findall("DATA")
        
        year = [x.findtext("YEAR") for x in merged_ir]
        
        # types = [x.findtext("TYPES") for x in trmm]
        # year = [x.findtext("START_YEAR") for x in trmm]
        #print(year)
        find_year_link = [x.findtext("LINK") for x in merged_ir]
        
        return find_year_link[0]
        
        """ # 
        find_link = ""
        for find_year in find_year_link:
            if yearfrom in find_year:
                find_link = find_year
        
        if len(find_link) >= 2:
            return find_link
        else:
            return "No Link"
        """

# BRING FILE NAME FROM LINK 
class filecontroller_trmm:
    def filenamesget_trmm(url):
        #baseUrl = url_sample
        filenames = []
        req = urllib2.Request(url)
        sourcecode = urllib2.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, 'html.parser')

        xml = "xml"
        for href in soup.find("table").find_all('a', href=re.compile('nc4')):
            fname = href["href"]
            filenames.append(fname)
            
        setfile = set(filenames)
        filenames.clear()
        list_set = list(setfile)
        list_set.sort()

        #print("setFile", setfile)
        #print("list_set", list_set)        
        
        for i in list_set:
            if xml not in i:
                dbdownloadtable_insert.dbinsertInfo(i, 'nc4')
                tmp = str(i)
                #print(tmp)
                replaced = tmp.replace('nc4', 'tiff')
                #print(replaced, ' <- Coverted ')
                dbconverttable_insert.dbinsertInfo(replaced, 'tiff')
                filenames.append(i)
        return filenames
    
    
class filecontroller_mergedIR:
    def filenameget_mergedir(url, fromP, toP, monthfrom, monthto):
        filenames = []
        req = urllib2.Request(url)
        sourcecode = urllib2.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, 'html.parser')

        xml = "xml"
        
        for href in soup.find("table").find_all('a', href = re.compile('nc4')):
            fname = href["href"]
            filenames.append(fname)
        
        setfile = set(filenames)
        filenames.clear()
        list_set = list(setfile)
        list_set.sort()
        
        for i in list_set:
            if xml not in i:
                tmp = str(i)
                #replaced = tmp.replace('nc4', 'tiff')
                # Should have to add database
                filenames.append(i)
        #print(filenames , " Hello", fromP, toP, monthfrom, monthto)        
        return filenames
        
        #print("setFile", setfile)
        #print("list_set", list_set)
        #print("fileNames", filenames)
            
# download files into converter-system folder - 1 
class downloadcontroller_trmmRT: 
    def wgetdownload_trmm(url,filename):
        try:
            # If you want to change downlaod file directory, change here!
            os.system('wget -P ../storage/nc4file/ --user gogod951 --password dbsGUR123@# %s/%s' %(url,filename))
        except Exception as e:
            print(" File not found, please refer to the website manually for download link", e)
class downloadcontroller_mergedIR: 
    def wgetdownload_mergedir(url,filename):
        try:
            # If you want to change downlaod file directory, change here!
            os.system('wget -P ../storage/nc4file/ --user gogod951 --password dbsGUR123@# %s/%s' %(url,filename))
        except Exception as e:
            print(" File not found, please refer to the website manually for download link", e)


class threadcontroller_trmmRT:
    def threadrun_trmm(url, filenames):
        for name in filenames:
            processThread = threading.Thread(target=downloadcontroller_trmmRT.wgetdownload_trmm, args=(url, name)) # parameters and functions have to be passed separately
            processThread.start() # START THE THREAD
        # Join Thread HERE. Because For loop is over, then other Thread will be started. before then next Thread should be waited.
        processThread.join()
        return True
    
class threadcontroller_mergedIR:
    def threadrun_mergedir(url, filenames):
        for name in filenames:
            processThread = threading.Thread(target=downloadcontroller_mergedIR.wgetdownload_mergedir, args=(url, name)) # parameters and functions have to be passed separately
            processThread.start() # START THE THREAD
        # Join Thread HERE. Because For loop is over, then other Thread will be started. before then next Thread should be waited.
        processThread.join()
        return True
    
    
class downloadclass_nasa_trmm:
    def download_trmm(url):
        filenames = filecontroller_trmm.filenamesget_trmm(url)
        # print(filenames, "File Name")
        
        # 쓰레드 돌리려면 아래거 하면 됨 
        # DO NOT USE THIS THREAD WHEN YOU TEST CODE!!! IT WILL DOWNLOAD OVER HUNDREADS OF FILES SIMULTANEOUSLY!!!
        threadcontroller_trmmRT.threadrun_trmm(url, filenames)
        
class downloadclass_nasa_mergedir:
    def download_mergedir(url, fromY, toY, fromM, toM):
        try:
            filenames = filecontroller_mergedIR.filenameget_mergedir(url, fromY, toY, fromM, toM)
            #print(filenames, "FileName_mergedIR")
            period_ym = fromY + fromM
            
            yearcount = int(toY) - int(fromY)
            monthcount = int(toM) - int(fromM)
            
            # 여기서 이제.. 연, 달로 받아오는거 해야하는데.. 지금은 연 단위로만 만들었음.
            # TO DO: Year Change. EX) Nov.2011 - JAN.2012
            
            filtered_filename = []
            
            for i in range(0, monthcount + 1):
                month = int(fromM) + i
                period_ym = fromY + str(month)
                for j in filenames:
                    if j.find(period_ym):
                        filtered_filename.append(j)
            print(filtered_filename)
            print(url)
            # DO NOT USE THIS THREAD WHEN YOU TEST CODE!!! IT WILL DOWNLOAD OVER HUNDREAD OF FILES SIMULTANEOUSLY!!!
            threadcontroller_mergedIR.threadrun_mergedir(url, filtered_filename)
            return True 
        
        except OSError:
            print("OS Error")
            return False
        
"""
class mergedirdownload:
    def download(url, fromY, toY, fromM, toM):
        filenames = filecontroller.filenameget_mergedir(url, fromY, toY, fromM, toM)
        print(filenames, "FileName_mergedIR")
        period_ym = fromY + fromM
        
        yearcount = int(toY) - int(fromY)
        monthcount = int(toM) - int(fromM)
        
        # 여기서 이제.. 연, 달로 받아오는거 해야하는데.. 지금은 연 단위로만 만들었음.
        for i in range(0, monthcount + 1):
            month = int(fromM) + i
            period_ym = fromY + str(month)
            for j in filenames:
                if j.find(period_ym):
                    print(j)
                    print(url)
        
        #여기서 Thread Run 시작해야함.
        
"""
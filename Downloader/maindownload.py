# Abstract Method
from abc import ABC, abstractmethod
import sys,os,time,requests
from xml.etree.ElementTree import parse
from flask import Flask, render_template, request
from downloader import threadcontroller_trmmRT
from downloader import threadcontroller_mergedIR 
from downloader import xmlcontroller
from downloader import downloadclass_nasa_trmm #여기에 import할 때는 클래스를 임포트 하는 것
from downloader import downloadclass_nasa_mergedir
from sentinel_1_downloader import sentinel1 
from sentinel_2_downloader import sentinel2 

app = Flask(__name__, template_folder='../templates') 
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')
# https://dev.to/takaakit/uml-diagram-for-gof-design-pattern-examples-in-python-4j40#strategy

class Context():
    #strategy: AbstractDownloader 
    def __init__(self, strategy):
        self._strategy = strategy
    #strategy: Strategy  ## the strategy interface
    def _setdownload(self, from_period, to_period, url):
        self._strategy.download(from_period, to_period, url)
    def _setprintInfo(self, fromP, toP):
        self._strategy.printInfo(fromP, toP)
    def _setdownloadstatuschecker(self, signal):
        self._strategy.downloadstatuschecker(signal)
    def _setdbInsert(self):
        self._strategy.dbinsert()
        
class AbstractDownloader(ABC):
    # 타입 체커 하나 더 넣으면 좋을듯.. 그리고... 마이크로서비스 하나 더 만들어서 총 3개 운영해야 함.. 하나는 어답터 나머지 두개는 다운로더, 컨버터 이렇게
    @abstractmethod
    def download(from_period, to_period, url):
        pass
    
    @abstractmethod
    def printInfo(fromP, toP):
        pass
    
    @abstractmethod
    def downloadstatuschecker(signal):
        pass
    
    @abstractmethod
    def dbinsert():
        pass

class nasa_mergedIR_API():
    @app.route('/download/mergedir', methods = ['GET', 'POST'], endpoint = 'downloadAPI_mergedIR')
    def downloadAPI_mergedIR():
        try:
            if request.method == 'POST':
                # Sub Class
                print("POST")
                from_period = request.form['periodfrom']
                to_period = request.form['periodto']
                url = ""
                lists = request.form['lists']
                print(from_period, to_period, lists, " Work?")
                context = Context(nasa_mergedIR_downloader())
                context._setprintInfo(from_period, to_period)
                signal = context._setdownload(from_period, to_period, url)
                context._setdownloadstatuschecker(signal)
            else:
                print("GET")
                pass     
        except OSError:
            print("OS Error")
            
        return render_template('index.html')

class nasa_trmmRT_API():
    @app.route('/download/trmmRT', methods = ['GET', 'POST'], endpoint = 'downloadAPI_trmmRT')
    def downloadAPI_trmmRT():
        try:
            if request.method == 'POST':
                # Sub Class
                from_period = request.form['periodfrom']
                to_period = request.form['periodto']
                url = ""
                print(from_period, to_period, " Work?")
                context = Context(nasa_trmmRT_downloader())
                context._setprintInfo(from_period, to_period)
                signal = context._setdownload(from_period, to_period, url)
                context._setdownloadstatuschecker(signal)
            else:
                print("GET")
                pass
        except OSError:
            print("OS ERORR. Check your AWS EC2 machine ")
        return render_template('index.html')

       
class copernicus_sentinel_1_API():
    @app.route('/download/sentinel1', methods =['GET', 'POST'], endpoint = 'downloadAPI_sentinel_1')
    def downloadAPI_sentinel_1():
        from_period = request.form['periodfrom']
        to_period = request.form['periodto']
        lists = ""
        if request.method == 'POST':
            print("POST Method")            
            #sentinel1 = copernicus_sentinel_1()
            # TO DO: X,Y 좌표 값 받지말고, 파일을 받는게 더 나을 듯
            #sentinel1.Sendtinel1_downloader(from_period, to_period)
            parse_from = from_period.replace('-', '')
            parse_to = to_period.replace('-', '')
                        
            context = Context(copernicus_sentinel_1())
            context._setprintInfo(parse_from, parse_to)
            signal = context._setdownload(parse_from, parse_to, lists)
            context._setdownloadstatuschecker(signal)

            if len(parse_from) != len(parse_to):
                print("Period Information is wrong.. ", parse_from, parse_to)
                    
        elif request.method == 'GET': # GET
            print("GET Method")            
            #sentinel1 = copernicus_sentinel_1()
            # TO DO: X,Y 좌표 값 받지말고, 파일을 받는게 더 나을 듯
            #sentinel1.Sendtinel1_downloader(from_period, to_period)
            parse_from = from_period.replace('-', '')
            parse_to = to_period.replace('-', '')
                        
            context = Context(copernicus_sentinel_1())
            context._setprintInfo(parse_from, parse_to)
            signal = context._setdownload(parse_from, parse_to, lists)
            context._setdownloadstatuschecker(signal)

            if len(parse_from) != len(parse_to):
                print("Period Information is wrong.. ", parse_from, parse_to)
        else:
            print("Wrong Communication Method")
            
        return render_template('index.html')

class copernicus_sentinel_2_API():
    @app.route('/download/sentinel2', methods =['GET', 'POST'], endpoint = 'downloadAPI_sentinel_2')
    def downloadAPI_sentinel_2():
        #from_period = request.form['periodfrom']
        #to_period = request.form['periodto']
        from_period = "20210901"
        to_period = "20210909"
        #parse_from = from_period.replace('-', '')
        #parse_to = to_period.replace('-', '')
        print(from_period, to_period, " <- Check Period")
        if request.method == 'POST':
            print("POST Method")
            print(from_period, to_period, " Period is correctly Inserted")
            """
            sentinel2 = copernicus_sentinel_2()
            # TO DO: X,Y 좌표 값 받지말고, 파일을 받는게 더 나을 듯
            sentinel2.Sendtinel2_downloader(from_period, to_period)
            """
            # TO DO: X,Y 좌표 값 받지말고, 파일을 받는게 더 나을 듯s
            context = Context(copernicus_sentinel_2())
            lists = ""
            context._setprintInfo(from_period, to_period)
            signal = context._setdownload(from_period, to_period, lists)
            context._setdownloadstatuschecker(signal)
            
        elif request.method == 'GET': # GET
            print("GET Method")
            #print(from_period, to_period, " Period is correctly Inserted")
            """
            sentinel2 = copernicus_sentinel_2()
            # TO DO: X,Y 좌표 값 받기
            sentinel2.Sendtinel2_downloader(from_period, to_period)
            """
            context = Context(copernicus_sentinel_2())
            lists = ""
            context._setprintInfo(from_period, to_period)
            signal = context._setdownload(from_period, to_period, lists)
            context._setdownloadstatuschecker(signal)
            
        else:
            print("Wrong Communication Method")

        return render_template('index.html')

class copernicus_sentinel_2(AbstractDownloader):         
    def download(self, from_period, to_period, url):
        polydir = copernicus_sentinel_2.jsonparser("polygoninformation.geojson")

        # Polygon File should be used to get GPS address. API Query is used to set options liks platformname, date, cloudcoverpercentage
        # To do.. Setting Day and Month // XYZ 
        # 유저보고 파일 업로드하게 시키는 것이 더 빠를 듯.. 그리고 Data-Month는 HTML을 통해서 입력 받고.. 
        signal = sentinel2.sentinel_2(polydir, from_period, to_period)
        print(signal, " Sentinel-2 Name")
        
        return render_template('index.html')
    
    def jsonparser(json):
        if len(json) == 0:
            print(" No Json File")
            return       
        jsondir = "/home/ubuntu/RemoteSensing_v1/Downloader/sentinel_folder/" + json
        return jsondir
            
    #Overriding
    def downloadstatuschecker(self, signal):
        # TO DO: Sentinel 형식에 맞게 변경시켜야함 
        if signal == False:
            print("Downloading is failure. Check Further procedure. 1. Check Thread is not broken. 2. Check URL is not broken.")
        else:
            print("Process is sucessful. ")
    
    #Overriding
    def printInfo(self, fromP, toP):
        # TODO: 이거 날짜 두개 입력받아서, URl 출력하도록 만들어야함 URL은 XML 파일로 하는 것이 좋을듯.. 파싱해서 가져오는거지. mergedIR처럼
        #print(fromP, toP)
        if fromP == None or toP == None:
            return "invalid Period"
        tree = parse('../XMLfiles/sentinel.xml')
        root = tree.getroot()
        trmm = root.findall("DATA")
        link = [x.findtext("LINK") for x in trmm]
        print(link, " <-- Target URL")
        #return link[0]
        print("URL ", link, "FROM Period", fromP, "To Period", toP)
    
    #Overriding    
    def dbinsert(self):
        pass


class copernicus_sentinel_1(AbstractDownloader):         
    def download(self, from_period, to_period, url):    
        polydir = copernicus_sentinel_1.jsonparser("polygoninformation.geojson")
        #copernicus_sentinel_1.printInfo(from_period, to_period)
        #parsed_from_period, parsed_to_period = copernicus_sentinel_1.parser(from_period, to_period)
        #print(parsed_from_period, parsed_to_period, " Parsed OK")
        
        # Polygon File should be used to get GPS address. API Query is used to set options liks platformname, date, cloudcoverpercentage
        # To do.. Setting Day and Month // XYZ 
        # 유저보고 파일 업로드하게 시키는 것이 더 빠를 듯.. 그리고 Data-Month는 HTML을 통해서 입력 받고.. 
        signal = sentinel1.sentinel_1(polydir, from_period, to_period)
        print(signal, " Sentinel-1 Name")
        return render_template('index.html')
    
    def jsonparser(json):
        if len(json) == 0:
            print(" No Json File")
            return       
        jsondir = "/home/ubuntu/RemoteSensing_v1/Downloader/sentinel_folder/" + json
        return jsondir
    
    #Overriding
    def downloadstatuschecker(self, signal):
        # TO DO: Sentinel 형식에 맞게 변경시켜야함 
        if signal == False:
            print("Downloading is failure. Check Further procedure. 1. Check Thread is not broken. 2. Check URL is not broken.")
        else:
            print("Process is sucessful. ")
    
    #Overriding
    def printInfo(self, fromP, toP):
        # TODO: 이거 날짜 두개 입력받아서, URl 출력하도록 만들어야함 URL은 XML 파일로 하는 것이 좋을듯.. 파싱해서 가져오는거지. mergedIR처럼
        #print(fromP, toP)
        if fromP == None or toP == None:
            return "invalid Period"
        tree = parse('../XMLfiles/sentinel.xml')
        root = tree.getroot()
        trmm = root.findall("DATA")
        link = [x.findtext("LINK") for x in trmm]
        print(link, " <-- Target URL")
        #return link[0]
        print("URL ", link, "FROM Period", fromP, "To Period", toP)

    #Overriding    
    def dbinsert(self):
        pass
        

# https://www.gleek.io/blog/class-diagram-arrows.html
class nasa_trmmRT_downloader(AbstractDownloader):
    def download(self, from_period, to_period, url):
        try:
            months = []
            trmmsignal = False
            lists = request.form['lists']
            tmp1 = from_period.split('-')
            tmp2 = to_period.split('-')
            # year and month return
            yearfrom, monthfrom, yearto, monthto = tmp1[0], tmp1[1], tmp2[0], tmp2[1]
            
            if yearfrom == None or yearto == None:
                return "invalid Period"
            tree = parse('../XMLfiles/trmm_rt.xml')
            root = tree.getroot()
            trmm = root.findall("DATA")
            _listUrl = []
            for i in range(int(monthfrom), int(monthto)+1):
                # 0 - 238 case or 0 - 12 case have to separate
                url = [x.findtext("LINK") for x in trmm]
                url = url[0]
                if "3B42RT.7" in lists:
                    if i < 10:
                        j = "00" + str(i)
                        url = url + "/" + lists + "/" + yearfrom + "/" + j
                    else:
                        j = "0" + str(i)
                        url = url + "/" + lists + "/" + yearfrom + "/" + j            
                else:
                    if i < 10:
                        j = "0" + str(i)
                        url = url + "/" + lists + "/" + yearfrom + "/" + j
                    else:
                        url = url + "/" + lists + "/" + yearfrom + "/" + str(i)
                    
                if nasa_trmmRT_downloader.filelistcheckers(url):
                    _listUrl.append(url)
            print(yearfrom, monthfrom, yearto, monthto, url)
            # 테스트 용
            # 진짜 돌릴 때 아래 코드 
            #바로 아랫줄 돌리면 쓰레드 돌아간다
            #print(_listUrl, " Merged URL List")
            for url in _listUrl:
                downloadclass_nasa_trmm.download_trmm(url)
            #nasa_trmmRT_downloader.downloadstatuschecker(trmmsignal)
            
        except OSError:
            print("API someting problem during download method")
            
        return render_template('index.html')

    def filelistcheckers(url):
        if "3B42RT" in url:
            print(url + " 3B43RT exists")
            return True 
        elif "3B42RT.7" in url:
            print (url + "3B42RT.7")
            return True 
        elif "3B42RT_daily.007" in url:
            print (url + "3B42RT.7")
            return True 
        else:
            print("InValid File Type")
            return False

    #Overriding
    def printInfo(self, fromP, toP):
        if fromP == None or toP == None:
            return "invalid Period"
        tree = parse('../XMLfiles/trmm_rt.xml')
        root = tree.getroot()
        trmm = root.findall("DATA")
        link = [x.findtext("LINK") for x in trmm]
        print(link, " <-- Target URL")
        return link[0]
            
    #Overriding
    def downloadstatuschecker(self, signal):
        if signal == False:
            print("Downloading is failure. Check Further procedure. 1. Check Thread is not broken. 2. Check URL is not broken.")
        else:
            print("Download is successful")
    
    
    #Overriding    
    def dbinsert(self):
        pass
     
class nasa_mergedIR_downloader(AbstractDownloader):
    def download(self, from_period, to_period, url):
        try:
            tmp1 = from_period.split('-')
            tmp2 = to_period.split('-')
            # year and month return
            yearfrom, monthfrom, yearto, monthto = tmp1[0], tmp1[1], tmp2[0], tmp2[1]
            
            if yearfrom == None or yearto == None:
                print("invalid Period")
            tree = parse('../XMLfiles/merged_ir.xml')
            root = tree.getroot()
            merged_ir = root.findall("DATA")
            year = [x.findtext("YEAR") for x in merged_ir]
            
            url = [x.findtext("LINK") for x in merged_ir]
            yearcount = int(yearto) - int(yearfrom)

            # 1998 + yearcount + 1 
            for i in range(0, yearcount+1):
                for j in range(1, 2):
                    url = xmlcontroller.xml_merged_ir_file(yearfrom, yearto)
                    url = str(url)
                    tmp_year = int(yearfrom) + i
                    if j < 10: # 0 ~ 9
                        j = "00" + str(j)
                        url += str(tmp_year) + "/" + str(j)
                    elif j > 9 and j < 100: # 10 ~ 99
                        j = "0" + str(j)
                        url += str(tmp_year) + "/" + str(j)
                    print(url)
            downloadclass_nasa_mergedir.download_mergedir(url, yearfrom, yearto, monthfrom, monthto)
            
            #여기까지가 이제 URL을 가져온거고.. 그 다음부터는.. 뒤에 슬러쉬 슬러쉬 붙이면서 가야함.. 마지막에
            # URL 들어왔을 때. https://disc2.gesdisc.eosdis.nasa.gov/data/MERGED_IR/GPM_MERGIR.1/2008/347/merg_2008121200_4km-pixel.nc4
            # 이런식으로 들어온다 하면... 뒤에 부분 파싱 해야함. 2008이 있는지.. 01이 있는지..이런식으로 연, 달 별로 파싱 해서 다운로드 시작해야함     
        except OSError:
            print("OS Error")
        return render_template('index.html')
       
        #Overriding
    def printInfo(self, fromP, toP):
        if fromP == None or toP == None:
            print("invalid Period")
            return False
        tree = parse('../XMLfiles/merged_ir.xml')
        root = tree.getroot()
        merged_ir = root.findall("DATA")
        year = [x.findtext("YEAR") for x in merged_ir]
        
        self.find_year_link = [x.findtext("LINK") for x in merged_ir]
        print(self.find_year_link , " <- URL ")
        return self.find_year_link[0]
    
    def downloadstatuschecker(self, signal):
        if signal == False:
            print("Downloading is failure. Check Further procedure. 1. Check Thread is not broken. 2. Check URL is not broken.")
        else:
            print("Download is successful")
            
    #Overriding    
    def dbinsert(self):
        pass

# Here is Download Port Number
app.run(host='0.0.0.0', port=5005)   






       
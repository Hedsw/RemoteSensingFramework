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

class Context:
    def __init__(self, strategy):
        self._strategy = strategy
    #strategy: Strategy  ## the strategy interface
    
    def download(self, from_period, to_period, url):
        self._strategy.download(from_period, to_period, url)
    
    def parser(self, period1, period2):
        self._strategy.parser(period1, period2)
        
    def printInfo(self, fromP, toP):
        self._strategy.printInfo(fromP, toP)
    
    def downloadstatuschecker(self):
        self._strategy.downloadstatuschecker()


class AbstractDownloader(ABC):
    # 타입 체커 하나 더 넣으면 좋을듯.. 그리고... 마이크로서비스 하나 더 만들어서 총 3개 운영해야 함.. 하나는 어답터 나머지 두개는 다운로더, 컨버터 이렇게
    @abstractmethod
    def download(from_period, to_period, url):
        pass
    
    @abstractmethod
    def parser(period1, period2):
        pass
    
    @abstractmethod
    def printInfo(fromP, toP):
        pass
    
    @abstractmethod
    def downloadstatuschecker(signal):
        pass


class nasa_trmmRT_API():
    @app.route('/download/trmmRT', methods = ['GET', 'POST'], endpoint = 'downloadAPI_trmmRT')
    def downloadAPI_trmmRT():
        try:
            if request.method == 'POST':
                # Sub Class
                from_period = request.form['periodfrom']
                to_period = request.form['periodto']
                url = ""
                #concrete_strategy = nasa_trmmRT_downloader()
                context = Context(nasa_trmmRT_downloader())
                context.download(from_period, to_period, url)
                
            else:
                print("GET")
                pass
                
        except OSError:
            print("OS ERORR. Check your AWS EC2 machine ")

        return render_template('index.html')


class nasa_mergedIR_API():
    @app.route('/download/mergedir', methods = ['GET', 'POST'], endpoint = 'downloadAPI_mergedIR_API')
    def downloadAPI_mergedIR_API():
        try:
            if request.method == 'POST':
                # Sub Class
                print("GET POST")
                
                from_period = request.form['periodfrom']
                to_period = request.form['periodto']
                lists = request.form['lists']
                context = Context(nasa_mergedIR_downloader())
                context.download(from_period, to_period, lists)
                
            else:
                print("GET")
                pass        
        
        except OSError:
            print("OS ERORR. Check your AWS EC2 machine ")
            
        return render_template('index.html')


class nasa_mergedIR_downloader(AbstractDownloader):
    def download(self, from_period, to_period, url):
        try:
                if nasa_mergedIR_downloader.printInfo(from_period, to_period) is None:
                    print("Invalid URL")
                    return False
                yearfrom, monthfrom, yearto, monthto, url = nasa_mergedIR_downloader.parser(from_period, to_period)
                
                print(yearfrom, monthfrom, yearto, monthto, url)
                # To Run download... 다운로드 돌리려면 아래꺼 실행..
                signal = downloadclass_nasa_mergedir.download_mergedir(url, yearfrom, yearto, monthfrom, monthto)
                nasa_mergedIR_downloader.downloadstatuschecker(signal)
                
                #여기까지가 이제 URL을 가져온거고.. 그 다음부터는.. 뒤에 슬러쉬 슬러쉬 붙이면서 가야함.. 마지막에
                # URL 들어왔을 때. https://disc2.gesdisc.eosdis.nasa.gov/data/MERGED_IR/GPM_MERGIR.1/2008/347/merg_2008121200_4km-pixel.nc4
                # 이런식으로 들어온다 하면... 뒤에 부분 파싱 해야함. 2008이 있는지.. 01이 있는지..이런식으로 연, 달 별로 파싱 해서 다운로드 시작해야함
                
        except OSError:
            print("OS Error")
        return render_template('index.html')
    
    #Overriding
    def parser(from_period, to_period):
        tmp1 = from_period.split('-')
        tmp2 = to_period.split('-')
        # year and month return
        yearfrom, monthfrom, yearto, monthto = tmp1[0], tmp1[1], tmp2[0], tmp2[1]
        url = nasa_mergedIR_downloader.printInfo(yearfrom, yearto) # XMLFiels/Merged_IR.xml
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
        return yearfrom, monthfrom, yearto, monthto, url
    
        #Overriding
    def printInfo(fromP, toP):
        if fromP == None or toP == None:
            print("invalid Period")
            return False
        tree = parse('../XMLfiles/merged_ir.xml')
        root = tree.getroot()
        merged_ir = root.findall("DATA")
        year = [x.findtext("YEAR") for x in merged_ir]
        
        # types = [x.findtext("TYPES") for x in trmm]
        # year = [x.findtext("START_YEAR") for x in trmm]
        #print(year)
        find_year_link = [x.findtext("LINK") for x in merged_ir]
        
        return find_year_link[0]
    
    def downloadstatuschecker(signal):
        if signal == False:
            print("Downloading is failure. Check Further procedure. 1. Check Thread is not broken. 2. Check URL is not broken.")
        else:
            print("Download is successful")
       
                
class nasa_trmmRT_downloader(AbstractDownloader):
    def download(self, from_period, to_period, url):
#   def download_trmmRT(self, from_period, to_period, url):

        try:
                if nasa_trmmRT_downloader.printInfo(from_period, to_period) is None:
                    print("Invalid URL")
                    return False
                yearfrom, monthfrom, yearto, monthto, url = nasa_trmmRT_downloader.parser(from_period, to_period)

                print(yearfrom, monthfrom, yearto, monthto, url)

                # 테스트 용
                # trmmsignal = True 
                # 진짜 돌릴 때 아래 코드 
                #바로 아랫줄 돌리면 쓰레드 돌아간다
                trmmsignal = downloadclass_nasa_trmm.download_trmm(url)
                nasa_trmmRT_downloader.downloadstatuschecker(trmmsignal)
        except OSError:
            print("OS Error")
            
        return render_template('index.html')
    
    #Overriding
    def parser(from_period, to_period):
        months = []
        trmmsignal = False
        lists = request.form['lists']
        tmp1 = from_period.split('-')
        tmp2 = to_period.split('-')
        # year and month return
        yearfrom, monthfrom, yearto, monthto = tmp1[0], tmp1[1], tmp2[0], tmp2[1]
        if nasa_trmmRT_downloader.printInfo(yearfrom, yearto) is None:
            print("Invalid URL")
            return False
        
        for i in range(int(monthfrom), int(monthto)+1):
            url = nasa_trmmRT_downloader.printInfo(yearfrom, yearto)

            # 0 - 238 case or 0 - 12 case have to separate
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
                
            nasa_trmmRT_downloader.filelistcheckers(url)
             
        return yearfrom, monthfrom, yearto, monthto, url
    
    def filelistcheckers(url):
        if "3B42RT" in url:
            print(url + " 3B43RT exists")
            pass
        elif "3B42RT.7" in url:
            print (url + "3B42RT.7")
            pass
        elif "3B42RT_daily.007" in url:
            print (url + "3B42RT.7")
            pass
        else:
            print("InValid File Type")
            pass

    #Overriding
    def printInfo(fromP, toP):
        if fromP == None or toP == None:
            return "invalid Period"
        tree = parse('../XMLfiles/trmm_rt.xml')
        root = tree.getroot()
        trmm = root.findall("DATA")
        link = [x.findtext("LINK") for x in trmm]
        return link[0]
            
    #Overriding
    def downloadstatuschecker(signal):
        if signal == False:
            print("Downloading is failure. Check Further procedure. 1. Check Thread is not broken. 2. Check URL is not broken.")
        else:
            print("Download is successful")
     


class copernicus_sentinel_1_API():
    @app.route('/download/sentinel1', methods =['GET', 'POST'], endpoint = 'downloadAPI_sentinel_1')
    def downloadAPI_sentinel_1():
        from_period = request.form['periodfrom']
        to_period = request.form['periodto']
        if request.method == 'POST':
            print("POST Method")
            #print(from_period, to_period, " Period is correctly Inserted")
            
            #sentinel1 = copernicus_sentinel_1()
            # TO DO: X,Y 좌표 값 받지말고, 파일을 받는게 더 나을 듯
            #sentinel1.Sendtinel1_downloader(from_period, to_period)
            
            lists = ""
            # TO DO: X,Y 좌표 값 받지말고, 파일을 받는게 더 나을 듯
            context = Context(copernicus_sentinel_1())
            context.download(from_period, to_period, lists)
            
            
        elif request.method == 'GET': # GET
            print("GET Method")
            #print(from_period, to_period, " Period is correctly Inserted")

            """
            sentinel1 = copernicus_sentinel_1()
            # TO DO: X,Y 좌표 값 받기
            sentinel1.Sendtinel1_downloader(from_period, to_period)
            """
            # TO DO: X,Y 좌표 값 받지말고, 파일을 받는게 더 나을 듯
            context = Context(copernicus_sentinel_1())
            context.download(from_period, to_period, lists)
        else:
            print("Wrong Communication Method")
            
        return render_template('index.html')

class copernicus_sentinel_2_API():
    @app.route('/download/sentinel2', methods =['GET', 'POST'], endpoint = 'downloadAPI_sentinel_2')
    def downloadAPI_sentinel_2():
#            from_period = request.form['periodfrom']
#            to_period = request.form['periodto']
        from_period = "20210901"
        to_period = "20210909"
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
            context.download(from_period, to_period, lists)
            
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
            context.download(from_period, to_period, lists)
            
        else:
            print("Wrong Communication Method")

        return render_template('index.html')


class copernicus_sentinel_1(AbstractDownloader):         
    def download(self, from_period, to_period, url):
    #def Sendtinel1_downloader(self, from_period, to_period):
        """
        parse_status = copernicus_sentinel_1.parser(from_period, to_period)
        if parse_status == False:
            print("Period is too long")
            return 
        """        
        polydir = copernicus_sentinel_1.jsonparser("polygoninformation.geojson")
        copernicus_sentinel_1.printInfo(from_period, to_period)
        parsed_from_period, parsed_to_period = copernicus_sentinel_1.parser(from_period, to_period)
        print(parsed_from_period, parsed_to_period, " Parsed OK")
        
        # Polygon File should be used to get GPS address. API Query is used to set options liks platformname, date, cloudcoverpercentage
        # To do.. Setting Day and Month // XYZ 
        # 유저보고 파일 업로드하게 시키는 것이 더 빠를 듯.. 그리고 Data-Month는 HTML을 통해서 입력 받고.. 
        signal = sentinel1.sentinel_1(polydir, from_period, to_period)
        print(signal, " Sentinel-1 Name")
        copernicus_sentinel_1.downloadstatuschecker(signal)
        
        return render_template('index.html')
    
    def jsonparser(json):
        if len(json) == 0:
            print(" No Json File")
            return       
        jsondir = "/home/ubuntu/RemoteSensing_v1/Downloader/sentinel_folder/" + json
        return jsondir
        
    #Overriding # Parser는 Period 기간 체크 하는 것으로 만들자 
    def parser(from_period, to_period):
        # Todo: Need to check Months and dates
        # 20201208 20201218
        
        if len(from_period) != len(to_period):
            print("Period Information is wrong.. ", from_period, to_period)
        
        parse_from = from_period.replace('-', '')
        parse_to = to_period.replace('-', '')
        
        return parse_from, parse_to
    
    #Overriding
    def downloadstatuschecker(signal):
        # TO DO: Sentinel 형식에 맞게 변경시켜야함 
        if signal == False:
            print("Downloading is failure. Check Further procedure. 1. Check Thread is not broken. 2. Check URL is not broken.")
        else:
            print("Process is sucessful. ")
    
    #Overriding
    def printInfo(fromP, toP):
        # TODO: 이거 날짜 두개 입력받아서, URl 출력하도록 만들어야함 URL은 XML 파일로 하는 것이 좋을듯.. 파싱해서 가져오는거지. mergedIR처럼
        URL = "https://scihub.copernicus.eu/dhus/odata/v1/Products"
        
        print("URL ", URL, "FROM Period", fromP, "To Period", toP)
        #print(fromP, toP)
        return URL, fromP, toP

class copernicus_sentinel_2(AbstractDownloader):         
    def download(self, from_period, to_period, url):
#    def Sendtinel2_downloader(self, from_period, to_period):
    
        """
        parse_status = copernicus_sentinel_2.parser(from_period, to_period)
        if parse_status == False:
            print("Period is too long")
            return 
        """        
        polydir = copernicus_sentinel_2.jsonparser("polygoninformation.geojson")
        copernicus_sentinel_2.printInfo(from_period, to_period)
        parsed_from_period, parsed_to_period = copernicus_sentinel_2.parser(from_period, to_period)
        print(parsed_from_period, parsed_to_period, " Parsed OK")
        
        # Polygon File should be used to get GPS address. API Query is used to set options liks platformname, date, cloudcoverpercentage
        # To do.. Setting Day and Month // XYZ 
        # 유저보고 파일 업로드하게 시키는 것이 더 빠를 듯.. 그리고 Data-Month는 HTML을 통해서 입력 받고.. 
        signal = sentinel2.sentinel_2(polydir, from_period, to_period)
        print(signal, " Sentinel-2 Name")
        copernicus_sentinel_2.downloadstatuschecker(signal)
        
        return render_template('index.html')
    
    def jsonparser(json):
        if len(json) == 0:
            print(" No Json File")
            return       
        jsondir = "/home/ubuntu/RemoteSensing_v1/Downloader/sentinel_folder/" + json
        return jsondir
        
    #Overriding # Parser는 Period 기간 체크 하는 것으로 만들자 
    def parser(from_period, to_period):
        # Todo: Need to check Months and dates
        # 20201208 20201218
        
        if len(from_period) != len(to_period):
            print("Period Information is wrong.. ", from_period, to_period)
        
        parse_from = from_period.replace('-', '')
        parse_to = to_period.replace('-', '')
        
        return parse_from, parse_to
    
    #Overriding
    def downloadstatuschecker(signal):
        # TO DO: Sentinel 형식에 맞게 변경시켜야함 
        if signal == False:
            print("Downloading is failure. Check Further procedure. 1. Check Thread is not broken. 2. Check URL is not broken.")
        else:
            print("Process is sucessful. ")
    
    #Overriding
    def printInfo(fromP, toP):
        # TODO: 이거 날짜 두개 입력받아서, URl 출력하도록 만들어야함 URL은 XML 파일로 하는 것이 좋을듯.. 파싱해서 가져오는거지. mergedIR처럼
        URL = "https://scihub.copernicus.eu/dhus/odata/v1/Products"
        
        print("URL ", URL, "FROM Period", fromP, "To Period", toP)
        #print(fromP, toP)
        return URL, fromP, toP

# Here is Download Port Number
app.run(host='0.0.0.0', port=5001)   






       
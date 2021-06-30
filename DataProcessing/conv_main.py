import sys,os,time,requests
from flask import Flask, render_template, request
from converter import dataprocessor

app = Flask(__name__, template_folder='../templates')
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')

class DataProcessorController:
    @app.route('/converter/tifftonc4', methods=['POST','GET'])
    def convtiff2nc4():
        # url_itmes는 GET이나 POST로 데이터 송수신할 때 사용 함. 
        url_items = "http://localhost:5001/download/trmm_rt"
        if request.method == 'POST':
            #response = requests.get(url_items)
            #print(response.text)
            print("NC4 Converter POST Method starts")    
            dataprocessor.threadstarter()
        elif request.method == 'GET':
            response = requests.get(url_items)
            #print(response.text)
            print("NC4 Starter GET Method")    

        return render_template('index.html')
#Convert Port Number
app.run(host='0.0.0.0', port=5002)

#1 Bash가 File Converter 5002
#2 Bash가 File Downloader 5001

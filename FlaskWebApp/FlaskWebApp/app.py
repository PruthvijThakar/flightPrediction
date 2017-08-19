
# coding: utf-8

# In[ ]:

from flask import Flask, render_template,request
from wtforms import Form
import urllib
from urllib.request import urlopen
import json


 
# App config.
#DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


 


@app.route("/prediction", methods=['GET'])
def hello():
    return render_template('hello.html',val = 0)


@app.route("/prediction", methods=['POST'])
def hello1():
    #form = ReusableForm(request.form)
 
    #print(form.errors)
    if request.method == 'POST':
       
        month=request.form['Month']
        carrier=request.form['Carrier']
        mC=request.form['MC']
        tD=request.form['TD']
        oAGD=request.form['OAGD']
        fLIGHTD=request.form['FLIGHTD']
        
        print(month,' ',carrier,' ',mC,' ',tD,' ',oAGD,' ',fLIGHTD)
        value = call_Azure(month,carrier,mC,tD,oAGD,fLIGHTD)
       
    return render_template('hello.html', val = value)



def call_Azure(Month,UniqueCarrier,totaldelay,MC,T_O_GATE_DELAY_A,T_GATE_DELAY_A):   
    data =  {

            "Inputs": {

                    "input1":
                    {
                        "ColumnNames": ["Month", "UniqueCarrier", "totaldelay", "MC", "T_O_GATE_DELAY_A", "T_GATE_DELAY_A"],
                        "Values": [ [Month,UniqueCarrier,totaldelay,MC,T_O_GATE_DELAY_A,T_GATE_DELAY_A] ]
                    },        },
                "GlobalParameters": {
    }
        }

    body = str.encode(json.dumps(data))

    url = 'https://ussouthcentral.services.azureml.net/workspaces/5c32fb054b7b4b2093fb67cdf0bc825e/services/b5dd1b7d47d245bb8fd19002ac8eab54/execute?api-version=2.0&details=true'
    api_key = 'r/uV0emle2iSYisWpD6vHilbXa745d/Ys+c+XCGKaShUgeJ9b6S6K2aooWrD/V/7ChLvhIp2oqIot03B+KRzSg==' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers) 

    try:
        response = urllib.request.urlopen(req)

        # If you are using Python 3+, replace urllib2 with urllib.request in the above code:
        # req = urllib.request.Request(url, body, headers) 
        # response = urllib.request.urlopen(req)

        data = response.read()
    #    print(data)
        encoding = response.info().get_content_charset('utf-8')
        JSON_object = json.loads(data.decode(encoding))
       # print(JSON_object)
        print(JSON_object['Results']['output1']['value']['Values'][0][6])



    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())

        print(json.loads(error.read()))   
        
    res = JSON_object['Results']['output1']['value']['Values'][0][6]    
    res_int = int(float(res))
    return res_int   

if __name__ == "__main__":
    app.run()


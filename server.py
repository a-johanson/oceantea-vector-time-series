from flask import Flask
from flask import request
import scipy as sp
from io import BytesIO
from threading import Lock
import adcp as adcp

app = Flask(__name__)
app.debug = True

csvString = """a,b,c,d,e
1,2,3,4,5
6,7,8,9,10
11,12,13,14,15"""
adcp.adcpImport("test", 100, 6.16, 4.0, csvString.encode())

print(adcp.adcpGetJSONSeries("test", 99.5))

def getADCPDataFileName(station):
    return "adcp_data/adcp-dirmag-{}.rds".format(station)

@app.route('/<station>', methods=["POST"])
def upload_station(station):
    #TODO: check and sanitize inputs
    #decoded = request.get_data().decode("utf-8")
    startDepth = request.args.get("startDepth")
    firstBinHeight = request.args.get("firstBinHeight")
    binHeight = request.args.get("binHeight")
    adcp.adcpImport(station, startDepth, firstBinHeight, binHeight, request.get_data())
    return
    
#TODO: add enpoints

#if __name__ == '__main__':
#    #app.run(host='0.0.0.0')
#    app.run(threaded=True, port=3334)
 
from flask import Flask
from flask import Response
from flask import request
from flask import jsonify
from flask import abort
#import scipy as sp
from io import BytesIO
#from threading import Lock
import adcp as adcp

app = Flask(__name__)
app.debug = True

#csvString = """a,b,c,d,e
#1,2,3,4,5
#6,7,8,9,10
#11,12,13,14,15"""
#adcp.adcpImport("test", 100, 6.16, 4.0, csvString.encode())
#
#print(adcp.adcpGetJSONSeries("test", 99.5))


@app.route("/adcp/<station>", methods=["POST"])
def uploadADCPData(station):
	#TODO: check and sanitize inputs
	#decoded = request.get_data().decode("utf-8")
	try:
		startDepth = float(request.args.get("startDepth"))
		firstBinHeight = float(request.args.get("firstBinHeight"))
		binHeight = float(request.args.get("binHeight"))
	except:
		abort(400)
		return
	if not adcp.adcpImport(station, startDepth, firstBinHeight, binHeight, request.get_data()):
		abort(500)
		return
	return jsonify(success=True)
	#resp = Response(response='{"success":true}', \
	#	status=200, \
	#	mimetype="application/json")
	#return resp

@app.route("/adcp/<station>", methods=["GET"])
def checkADCPExistance(station):
	#TODO: check and sanitize inputs
	return jsonify(exists=adcp.adcpIsInDB(station))
	#resp = Response(response='{{"exists":{}}}'.format("true" if adcp.adcpIsInDB(station) else "false"), \
	#	status=200, \
	#	mimetype="application/json")
	#return resp

@app.route("/adcp/<station>", methods=["DELETE"])
def deleteADCPData(station):
	#TODO: check and sanitize inputs
	return jsonify(success=adcp.adcpDelete(station))
	#resp = Response(response='{{"exists":{}}}'.format("true" if adcp.adcpIsInDB(station) else "false"), \
	#	status=200, \
	#	mimetype="application/json")
	#return resp


@app.route("/adcp/<station>/<depth>", methods=["GET"])
def getADCPSeries(station, depth):
	#TODO: check and sanitize inputs
	try:
		fDepth = float(depth)
	except:
		return jsonify(data=[])
	resp = Response(response=adcp.adcpGetJSONSeries(station, fDepth), \
		status=200, \
		mimetype="application/json")
	return resp



#TODO: add enpoints

if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    app.run(threaded=True, port=3334)
 
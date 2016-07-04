from flask import Blueprint
from flask import Response
from flask import request
from flask import jsonify
#from flask import abort
from io import BytesIO
import json as json
import re as re

import db as db

timeseriesAPI = Blueprint("timeseriesAPI", __name__)


@timeseriesAPI.route("/", methods=["GET"])
@timeseriesAPI.route("", methods=["GET"])
def getTimeseries():
	timeseries = []
	tsDB = db.getTSDB()
	for ts in tsDB:
		alreadyExists = False
		for ats in timeseries:
			if ats["station"] == tsDB[ts]["station"] and ats["dataType"] == tsDB[ts]["dataType"] and ats["depth"] == tsDB[ts]["depth"]:
				alreadyExists = True
				break
		if not alreadyExists:
			timeseries.append(tsDB[ts])
	
	if "includeAggregatedMetadata" in request.args:
		return Response(response=json.dumps({
			"datatypes": {"dirmag": {
				"printName": "Water Flow",
				"unit": "mm/s"
				}
			},
			"regions": {},
			"stations": db.getStationsDB(),
			"devices": [],
			"timeseries": timeseries
		}), status=200, mimetype="application/json")
	else:
		return Response(response=json.dumps({"timeseries": timeseries}), status=200, mimetype="application/json")

def isInt(str):
	try: 
		int(str)
		return True
	except ValueError:
		return False

def tsParametersAreValid(station, dataType, depth, direction=None):
	stationRE = re.compile(r"^[A-Za-z0-9\-]+$")
	dataTypeRE = re.compile(r"^[A-Za-z0-9\-_]+$")
	validDir = (direction is None) or (direction=="up" or direction=="down")
	return (stationRE.match(station) and dataTypeRE.match(dataType) and isInt(depth) and validDir)


@timeseriesAPI.route("/adcp/<station>/<dataType>/<depth>", defaults={"direction": None}, methods=["DELETE"])
@timeseriesAPI.route("/adcp/<station>/<dataType>/<depth>/<direction>", methods=["DELETE"])
def deleteADCPData(station, dataType, depth, direction):
	result = False
	if tsParametersAreValid(station, dataType, depth, direction):
		if direction is None:
			resultUp = db.adcpDelete(station, dataType, depth, "up")
			resultDown = db.adcpDelete(station, dataType, depth, "down")
			result = bool(resultUp or resultDown)
		else:
			result = db.adcpDelete(station, dataType, depth, direction)
	return Response(response=json.dumps({"success": result}), status=200 if result else 500, mimetype="application/json")


@timeseriesAPI.route("/adcp/<station>/<dataType>/<depth>", methods=["GET"])
def getADCPSeries(station, dataType, depth):
	if not tsParametersAreValid(station, dataType, depth):
		return jsonify(data=[])
	
	try:
		fDepth = float(depth)
	except:
		return jsonify(data=[])
	
	extractDepth = fDepth
	if "extractDepth" in request.args:
		try:
			extractDepth = float(request.args["extractDepth"])
		except:
			pass
	
	resp = Response(response=db.adcpGetJSONSeries(station, dataType, depth, extractDepth), \
		status=200, \
		mimetype="application/json")
	return resp

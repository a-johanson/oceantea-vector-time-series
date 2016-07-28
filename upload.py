# Copyright 2016 Arne Johanson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Blueprint
from flask import request
from flask import jsonify
import re

import db

uploadAPI = Blueprint("uploadAPI", __name__)

def getFailureResponse(msg):
	return jsonify(success=False, message=msg), 400

def isInt(str):
	try: 
		int(str)
		return True
	except ValueError:
		return False

def isFloat(str, min, max):
	try: 
		v = float(str)
		return v >= min and v <= max
	except ValueError:
		return False


@uploadAPI.route("/", methods=["POST"])
@uploadAPI.route("", methods=["POST"])
def uploadADCPData():
	if not ("dataFile" in request.files and \
	"timeSeriesType" in request.form and \
	"station" in request.form and \
	"depth" in request.form and \
	"referenceDate" in request.form and \
	"latitude" in request.form and \
	"longitude" in request.form and \
	"region" in request.form and \
	"device" in request.form and \
	"adcpDirection" in request.form and \
	"adcpFirstBinHeight" in request.form and \
	"adcpBinHeight" in request.form):
		return getFailureResponse("Too few form parameters")
	
	csvFile = request.files["dataFile"]
	
	if request.form["timeSeriesType"] != "adcp":
		return getFailureResponse("Time series type must be adcp")
	
	stationRE = re.compile(r"^[A-Za-z0-9]+[A-Za-z0-9\-]*[A-Za-z0-9]+$")
	if not stationRE.match(request.form["station"]):
		return getFailureResponse("Station ID is mal-formatted")
	
	if not isInt(request.form["depth"]):
		return getFailureResponse("Depth is mal-formatted")
	
	if request.form["adcpDirection"] != "up" and request.form["adcpDirection"] != "down":
		return getFailureResponse("ADCP direction must be up or down")
	
	if not isFloat(request.form["adcpFirstBinHeight"], 0.0, 100000.0):
		return getFailureResponse("First bin height is mal-formatted")
		
	if not isFloat(request.form["adcpBinHeight"], 0.0, 100000.0):
		return getFailureResponse("Bin height is mal-formatted")
	
	dateRE = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})$")
	dateMatch = dateRE.match(request.form["referenceDate"])
	if dateMatch is None:
		return getFailureResponse("Reference date is mal-formatted")
	
	metadata = {
		"station": request.form["station"],
		"dataType": "dirmag",
		"depth": int(request.form["depth"]),
		"t_reference": dateMatch.group(1) + "T" + dateMatch.group(2) + "Z",
		"adcpDirection": request.form["adcpDirection"],
		"adcpFirstBinHeight": float(request.form["adcpFirstBinHeight"]),
		"adcpBinHeight": float(request.form["adcpBinHeight"])
	}
	
	stationsDB = db.getStationsDB()
	if not (request.form["station"] in stationsDB):
		if not isFloat(request.form["latitude"], -90.0, 90.0):
			return getFailureResponse("Latitude is mal-formatted")
		if not isFloat(request.form["longitude"], -180.0, 180.0):
			return getFailureResponse("Longitude is mal-formatted")
		
		regionRE = re.compile(r"^[A-Za-z]+[A-Za-z ]*[A-Za-z]+$")
		if not regionRE.match(request.form["region"]):
			return getFailureResponse("Region name is mal-formatted")
		
		deviceRE = re.compile(r"^[A-Za-z0-9]+[A-Za-z0-9\-]*[A-Za-z0-9]+$")
		if not deviceRE.match(request.form["device"]):
			return getFailureResponse("Device ID is mal-formatted")
		
		metadata["lat"] = float(request.form["latitude"])
		metadata["lon"] = float(request.form["longitude"])
		metadata["region"] = re.sub(" ", "-", request.form["region"].lower())
		metadata["regionPrintName"] = request.form["region"]
		metadata["device"] = request.form["device"]
	else:
		metadata["lat"] = stationsDB[request.form["station"]].lat
		metadata["lon"] = stationsDB[request.form["station"]].lon
		metadata["region"] = stationsDB[request.form["station"]].region
		metadata["regionPrintName"] = stationsDB[request.form["station"]].regionPrintName
		metadata["device"] = stationsDB[request.form["station"]].device

	metadata["tsType"] = request.form["timeSeriesType"]
	
	result = db.adcpImport(csvFile.stream, metadata)
	try:
		csvFile.close()
	except:
		pass
	return jsonify(success=result, message="Time series added successfully" if result else "Could not parse/store time series data"), 200 if result else 500

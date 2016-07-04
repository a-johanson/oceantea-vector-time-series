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

import numpy as np
from io import BytesIO
from threading import Lock
import pickle as pickle
import json as json
import math as math
from os import remove

adcpLock = Lock()
adcpDBPath = "data/adcp_db.pickle"
adcpDB = {}

def adcpGetDBKey(station, dataType, depth, direction):
	return "adcp-{}-{}-{}-{}".format(station, dataType, depth, direction)

def adcpReadDB():
	global adcpDB
	try:
		adcpDB = pickle.load(open(adcpDBPath, "rb"))
	except:
		adcpDB = {}

adcpReadDB()

def getTSDB():
	global adcpDB
	return adcpDB

def adcpAcquireLock():
	global adcpLock
	while not adcpLock.acquire():
		pass

def adcpReleaseLock():
	global adcpLock
	adcpLock.release()

def adcpWriteDB(acquireLock=True):
	global adcpDB
	if acquireLock:
		adcpAcquireLock()
	try:
		pickle.dump(adcpDB, open(adcpDBPath, "wb"))
	except:
		pass
	if acquireLock:
		adcpReleaseLock()
		


def adcpAddToDB(metadata):
	global adcpDB
	key = adcpGetDBKey(metadata["station"], metadata["dataType"], metadata["depth"], metadata["adcpDirection"])
	adcpDB[key] = metadata
	adcpWriteDB()

def adcpDeleteFromDB(station, dataType, depth, direction, acquireLock=True):
	global adcpDB
	key = adcpGetDBKey(station, dataType, depth, direction)
	if not (key in adcpDB):
		return False
	if acquireLock:
		adcpAcquireLock()
	del adcpDB[key]
	adcpWriteDB(False)
	if acquireLock:
		adcpReleaseLock()
	


def adcpGetFileName(station, dataType, depth, direction):
	return "data/adcp-{}-{}-{}-{}.npy".format(station, dataType, depth, direction)
	
def adcpStore(metadata, dataSet):
	try:
		dataSet.tofile(adcpGetFileName(metadata["station"], metadata["dataType"], metadata["depth"], metadata["adcpDirection"]))
		return True
	except:
		return False

def adcpDelete(station, dataType, depth, direction):
	adcpAcquireLock()
	adcpDeleteFromDB(station, dataType, depth, direction, False)
	try:
		remove(adcpGetFileName(station, dataType, depth, direction))
	except:
		adcpReleaseLock()
		return False
	adcpReleaseLock()
	return True

def adcpImport(csvFile, metadata):
	header = ""
	while True:
		try:
			header = csvFile.readline().decode("utf-8")
		except:
			return False
		if len(header) <= 0 or header[0]!='#':
			break
	try:
		dataSet = np.genfromtxt(csvFile, delimiter=",", comments="#", dtype=float, invalid_raise=True)
	except:
		return False
	if len(dataSet.shape) <= 1:
		return False
	nCols = dataSet.shape[1]
	if nCols < 3 or nCols%2 != 1:
		return False
	nBins = (nCols-1)/2
	metadata["nBins"] = int(nBins) 
	if adcpStore(metadata, dataSet):
		adcpAddToDB(metadata)
		return True
	return False


	
def adcpLoad(station, dataType, depth, direction, nCols):
	fileName = adcpGetFileName(station, dataType, depth, direction)
	try:
		return np.fromfile(fileName).reshape((-1, int(nCols)))
	except:
		return np.zeros((1, nCols))
	

def adcpGetJSONSeries(station, dataType, startDepth, depth):
	global adcpDB
	dirSign = 1.0 if depth <= float(startDepth) else -1.0
	direction = "up" if dirSign > 0.0 else "down"
	key = adcpGetDBKey(station, dataType, startDepth, direction)
	if not (key in adcpDB):
		return json.dumps({"data":[]})
	
	distance = dirSign*(adcpDB[key]["depth"] - depth)
	iBin = int(math.ceil(max(distance - adcpDB[key]["adcpFirstBinHeight"], 0.0) / adcpDB[key]["adcpBinHeight"]))
	if iBin >= adcpDB[key]["nBins"] or distance < 0.0:
		return json.dumps({"data":[]})
	
	dataSet = adcpLoad(station, dataType, startDepth, direction, 1 + 2*adcpDB[key]["nBins"])
	result = np.empty((dataSet.shape[0], 4))
	result[:,[0,2,3]] = np.nan_to_num(dataSet[:, [0, int(1+iBin), int(1+adcpDB[key]["nBins"]+iBin)]])
	result[:,1] = depth 
	return json.dumps({"data": result.tolist()})



def getStationsDB():
	return {}


import numpy as np
#import pandas as pandas
from io import BytesIO
from threading import Lock
import pickle as pickle
import json as json
import math as math
from os import remove

adcpLock = Lock()
adcpDBPath = "data/adcp_db.pickle"
adcpDB = {}

def adcpGetDBKey(station, dataType, depth):
	return "adcp-{}-{}-{}".format(station, dataType, depth)

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
	key = adcpGetDBKey(metadata["station"], metadata["dataType"], metadata["depth"])
	adcpDB[key] = metadata
	adcpWriteDB()

def adcpDeleteFromDB(station, dataType, depth, acquireLock=True):
	global adcpDB
	key = adcpGetDBKey(station, dataType, depth)
	if not (key in adcpDB):
		return False
	if acquireLock:
		adcpAcquireLock()
	del adcpDB[key]
	adcpWriteDB(False)
	if acquireLock:
		adcpReleaseLock()
	


def adcpGetFileName(station, dataType, depth):
	return "data/adcp-{}-{}-{}.npy".format(station, dataType, depth)
	
def adcpStore(metadata, dataSet):
	try:
		dataSet.tofile(adcpGetFileName(metadata["station"], metadata["dataType"], metadata["depth"]))
		return True
	except:
		return False

def adcpDelete(station, dataType, depth):
	adcpAcquireLock()
	adcpDeleteFromDB(station, dataType, depth, False)
	try:
		remove(adcpGetFileName(station, dataType, depth))
	except:
		adcpReleaseLock()
		return False
	adcpReleaseLock()
	return True

# import dirmag
def adcpImport(csvFile, metadata):
	header = ""
	while True:
		try:
			header = csvFile.readline().decode("utf-8")
		except:
			return False
		if len(header) <= 0 or header[0]!='#':
			break
	print(header)
	try:
		dataSet = np.genfromtxt(csvFile, delimiter=",", comments="#", dtype=float, invalid_raise=True)
	except:
		return False
	#print(dataSet)
	print(dataSet.shape)
	if len(dataSet.shape) <= 1:
		return False
	nCols = dataSet.shape[1]
	#print(nCols)
	if nCols < 3 or nCols%2 != 1:
		return False
	nBins = (nCols-1)/2
	metadata["nBins"] = nBins 
	if adcpStore(metadata, dataSet):
		adcpAddToDB(metadata)
		return True
	return False


	
def adcpLoad(station, dataType, depth, nCols):
	fileName = adcpGetFileName(station, dataType, depth)
	try:
		return np.fromfile(fileName).reshape((-1, nCols))
	except:
		return np.zeros((1, nCols))
	

def adcpGetJSONSeries(station, dataType, startDepth, depth):
	global adcpDB
	key = adcpGetDBKey(station, dataType, startDepth)
	if not (key in adcpDB):
		return json.dumps({"data":[]})
	
	distance = adcpDB[key]["depth"] - depth
	iBin = math.ceil(max(distance - adcpDB[key]["adcpFirstBinHeight"], 0.0) / adcpDB[key]["adcpBinHeight"])
	if iBin >= adcpDB[key]["nBins"] or distance < 0.0:
		return json.dumps({"data":[]})
	
	dataSet = adcpLoad(station, dataType, startDepth, 1 + 2*adcpDB[key]["nBins"])
	result = np.empty((dataSet.shape[0], 4))
	result[:,[0,2,3]] = dataSet[:, [0, 1+iBin, 1+adcpDB[key]["nBins"]+iBin]]
	result[:,1] = depth 
	return json.dumps({"data": result.tolist()})



def getStationsDB():
	return {}

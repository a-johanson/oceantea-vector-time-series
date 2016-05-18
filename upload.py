from flask import Blueprint
from flask import Response
from flask import request
from flask import jsonify
from flask import abort

import adcp as adcp

uploadAPI = Blueprint("uploadAPI", __name__)


@uploadAPI.route("/", methods=["POST"])
@uploadAPI.route("", methods=["POST"])
def uploadADCPData():
	file = request.files["dataFile"]
	print("test" in request.form)
	print(file.readline())
	return jsonify(success=True)

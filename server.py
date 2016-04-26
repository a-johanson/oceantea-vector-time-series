from flask import Flask
from flask import request
import scipy as sp
from io import BytesIO

app = Flask(__name__)
app.debug = True

def getADCPDataFileName(station):
    return "adcp_data/adcp-dirmag-{}.rds".format(station)

@app.route('/<station>', methods=["POST"])
def upload_station(station):
    #decoded = request.get_data().decode("utf-8")
    inputData = sp.genfromtxt(BytesIO(request.get_data()), delimiter=",")
    return sp.array2string(inputData)

if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    app.run(port=3334)
 
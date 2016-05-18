from flask import Flask
from timeseries import timeseriesAPI


app = Flask(__name__)
app.debug = True

app.register_blueprint(timeseriesAPI, url_prefix="/timeseries")


if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    app.run(threaded=True, port=3336)
 
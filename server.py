from flask import Flask
from timeseries import timeseriesAPI
from upload import uploadAPI


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 120 * 1024 * 1024 # 120 MB
app.debug = False

app.register_blueprint(timeseriesAPI, url_prefix="/timeseries")
app.register_blueprint(uploadAPI, url_prefix="/upload")


if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    app.run(threaded=True, port=3336, use_debugger=False, use_reloader=False)
 
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

from flask import Flask
from timeseries import timeseriesAPI
from upload import uploadAPI
import sys


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 120 * 1024 * 1024 # 120 MB
app.debug = False

app.register_blueprint(timeseriesAPI, url_prefix="/timeseries")
app.register_blueprint(uploadAPI, url_prefix="/upload")


if __name__ == "__main__":
	acceptAllHosts = False
	for arg in sys.argv:
		if arg == "--acceptAllHosts":
			acceptAllHosts = True
			break
	
	app.run(host="0.0.0.0" if acceptAllHosts else "127.0.0.1", port=3336, threaded=True, use_debugger=False, use_reloader=False)

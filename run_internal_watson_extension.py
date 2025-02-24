from flask import Flask
import os
from common.config import app

from watson.internal_watson_extension.routes import api_blueprint

api = Flask(__name__)

base_url = app.internal_watson_extension_base_url
api.register_blueprint(api_blueprint, url_prefix=base_url)

if __name__ == "__main__":
    port = int(app.internal_watson_extension_port)
    print(f"Starting app at port {port} with base URL: {base_url}")
    api.run(port=port)

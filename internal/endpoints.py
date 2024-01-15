from flask import Flask, jsonify

from common import logging


app = Flask(__name__)
logger = logging.initialize_logging()


@app.route("/", methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

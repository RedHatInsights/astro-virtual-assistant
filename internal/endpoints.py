from flask import Flask, jsonify

from common import logging
from common.config import app


flask_app = Flask(__name__)
logger = logging.initialize_logging()


def start_internal_api():
    logger.info("Starting virtual assistant internal api...")
    flask_app.run(host=app.hostname, port=app.internal_api_port)


@flask_app.route("/api/", methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

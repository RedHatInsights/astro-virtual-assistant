from flask import Flask, Response, jsonify, request
import json
import csv
from io import StringIO

from common import logging
from common.config import app

from internal import db

flask_app = Flask(__name__)
logger = logging.initialize_logging()

API_PREFIX = "/api/v1"
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000

KEYS_TO_INCLUDE = {
    'event',
    'message_id',
    'text',
    'timestamp'
}


def start_internal_api():
    logger.info("Starting virtual assistant internal api...")
    flask_app.run(host=app.hostname, port=app.internal_api_port)


@flask_app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


# Returns messages sent by users
# params:
#  - limit (optional): limit the number of messages returned; default is 100
#  - offset (optional): offset the returned messages; default is 0
#  - start_date (optional): only return messages sent after this date
#  - end_date (optional): only return messages sent before this date
#  - unique (optional): if true, only return unique messages (i.e. typed by the user, no commands)
#  - csv (optional): if true, return messages in csv format
@flask_app.route(API_PREFIX + "/messages", methods=["GET"])
def get_messages():
    limit = request.args.get('limit') or DEFAULT_LIMIT
    offset = request.args.get('offset') or 0
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    unique = request.args.get('unique') in ['true', 'True', '1'] or False
    is_csv = request.args.get('csv') in ['true', 'True', '1'] or False

    logger.error(unique)

    query = "SELECT data FROM events WHERE type_name='user'"

    if start_date:
        query += " AND timestamp >= '" + start_date + "'"
    if end_date:
        query += " AND timestamp <= '" + end_date + "'"

    if int(limit) > MAX_LIMIT:
        return jsonify({"error": "limit must be less than " + str(MAX_LIMIT)})
    if int(limit) < 0:
        return jsonify({"error": "limit must be greater than 0"})
    
    query += " LIMIT " + str(limit) + " OFFSET " + str(offset)

    with db.db_cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

        # making a separate json list to exclude certain keys
        message_list = []
        for row in rows:
            row_json = json.loads(row[0])

            if unique and row_json['text'].startswith('/'):
                continue

            message = {k: row_json[k] for k in row_json.keys() & KEYS_TO_INCLUDE}

            parse_data = row_json['parse_data']
            message['entities'] = parse_data['entities']
            message['intent'] = parse_data['intent']
            message['intent_ranking'] = parse_data['intent_ranking']

            message_list.append(message)
        
        if is_csv:
            csv_io = StringIO()
            writer = csv.DictWriter(csv_io, fieldnames=message_list[0].keys())
            writer.writeheader()
            writer.writerows(message_list)
            csv_data = csv_io.getvalue()
            return Response(csv_data, mimetype='text/csv')

        return jsonify(message_list)


# Returns conversation data, i.e. messages sent by users and responses sent back by the bot
@flask_app.route(API_PREFIX + "/conversations", methods=["GET"])
def get_conversations():
    # Your code here
    pass

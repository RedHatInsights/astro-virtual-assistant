from flask import Flask, Response, jsonify, request
from sqlalchemy import and_, or_, true, asc
from sqlalchemy.orm import sessionmaker
import json

from common import logging
from common.config import app
from common.identity import decode_identity

from internal.utils import read_arguments, export_csv
from internal.database.db import DB
from internal.database.models import Events


API_PREFIX = "/api/v1"

DATA_KEYS_TO_INCLUDE = {"message_id", "text", "timestamp"}


flask_app = Flask(__name__)
db = DB()
engine = db.get_engine()
Session = sessionmaker(engine)
logger = logging.initialize_logging()


def start_internal_api():
    logger.info("Starting virtual assistant internal api...")
    flask_app.run(host=app.hostname, port=app.internal_api_port)


@flask_app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


# Returns messages from all conversations
# params:
#  - limit (optional): limit the number of messages returned; default is 100
#  - offset (optional): offset the returned messages; default is 0
#  - start_date (optional): only return messages sent after this date
#  - end_date (optional): only return messages sent before this date
#  - type_name (optional): only return messages of this type
#  - unique (optional): if true, only return unique messages (i.e. typed by the user, no commands)
#  - format (optional): "csv" or "json" format; default is "json"
@flask_app.route(API_PREFIX + "/messages", methods=["GET"])
def get_messages():
    args = read_arguments()
    if isinstance(args, ValueError):
        return Response(args, status=400)

    session = Session()
    conditions = []
    if args.type_name:
        conditions.append(Events.type_name == args.type_name)
    if args.start_date:
        conditions.append(Events.timestamp > args.start_date)
    if args.end_date:
        conditions.append(Events.timestamp < args.end_date)
    conditions = and_(true(), *conditions)

    rows = (
        session.query(
            Events.sender_id,
            Events.type_name,
            Events.intent_name,
            Events.action_name,
            Events.data,
        )
        .where(conditions)
        .order_by(asc(Events.timestamp))
        .limit(args.limit)
        .offset(args.offset)
        .all()
    )

    message_list = []
    for row in rows:
        data_json = json.loads(row[4])  # data column needs to be parsed

        # exclude commands if unique is true
        if args.unique and (
            "text" not in data_json
            or data_json["text"] is None
            or data_json["text"].startswith("/")
        ):
            continue

        message = process_message(row)
        message_list.append(message)

    if args.format == "csv":
        return export_csv(message_list)

    return jsonify(message_list)


# Returns complete conversation given a sender_id
# params:
#  - sender_id (required): sender_id of the conversation
#  - limit (optional): limit the number of messages returned; default is 100
#  - start_date (optional): only return messages sent after this date
#  - end_date (optional): only return messages sent before this date
#  - type_name (optional): only return messages of this type
#  - unique (optional): if true, only return unique messages (i.e. typed by the user, no commands)
#  - offset (optional): offset the returned messages; default is 0
#  - format (optional): "csv" or "json" format; default is "json"
@flask_app.route(API_PREFIX + "/messages/<sender_id>", methods=["GET"])
def get_conversation_by_sender_id(sender_id):
    args = read_arguments()
    if isinstance(args, ValueError):
        return Response(args, status=400)

    session = Session()
    conditions = [Events.sender_id == sender_id]
    if args.type_name:
        conditions.append(Events.type_name == args.type_name)
    if args.start_date:
        conditions.append(Events.timestamp > args.start_date)
    if args.end_date:
        conditions.append(Events.timestamp < args.end_date)
    conditions = and_(true(), *conditions)

    session = Session()
    rows = (
        session.query(
            Events.sender_id,
            Events.type_name,
            Events.intent_name,
            Events.action_name,
            Events.data,
        )
        .where(conditions)
        .order_by(asc(Events.timestamp))
        .limit(args.limit)
        .offset(args.offset)
        .all()
    )

    message_list = []
    for row in rows:
        data_json = json.loads(row[4])  # data column needs to be parsed

        # exclude commands if unique is true
        if args.unique and (
            "text" not in data_json
            or data_json["text"] is None
            or data_json["text"].startswith("/")
        ):
            continue

        message = process_message(row)
        message_list.append(message)

    if args.format == "csv":
        return export_csv(message_list)

    return jsonify(message_list)


# Returns list of sender_id
# params:
#  - unity_id (optional): only return messages from this username
#  - limit (optional): limit the number of messages returned; default is 100
#  - offset (optional): offset the returned messages; default is 0
#  - start_date (optional): only return messages sent after this date
#  - end_date (optional): only return messages sent before this date
#  - format (optional): "csv" or "json" format; default is "json"
@flask_app.route(API_PREFIX + "/senders", methods=["GET"])
def get_senders():
    args = read_arguments()
    if isinstance(args, ValueError):
        return Response(args, status=400)

    session = Session()
    conditions = []
    if args.start_date:
        conditions.append(Events.timestamp > args.start_date)
    if args.end_date:
        conditions.append(Events.timestamp < args.end_date)
    conditions = and_(true(), *conditions)

    rows = (
        session.query(Events.sender_id, Events.data)
        .distinct()
        .where(conditions)
        .order_by(asc(Events.sender_id))
        .limit(args.limit)
        .offset(args.offset)
        .all()
    )

    sender_list = []
    for row in rows:
        if args.unity_id is not None:
            data_json = json.loads(row[1])
            if "metadata" not in data_json:
                logger.info("metadata not found in data column")
                continue
            if "identity" not in data_json["metadata"]:
                logger.info("identity not found in metadata")
                continue
            identity = decode_identity(data_json["metadata"]["identity"])["identity"]
            if (
                not identity
                or "user" not in identity
                or "username" not in identity["user"]
            ):
                logger.info("username not found in identity")
                continue
            unity_id = identity["user"]["username"]
            if unity_id != args.unity_id:
                continue
        # the DISTINCT query is not distinct on the sender_id anymore
        if row[0] not in sender_list:
            sender_list.append(row[0])

    if args.format == "csv":
        return export_csv(sender_list)

    return jsonify(sender_list)


def process_message(row):
    message = {}
    message["sender_id"] = row[0]
    message["type_name"] = row[1]
    message["intent_name"] = row[2]
    message["action_name"] = row[3]
    data_column = json.loads(row[4])

    for key in DATA_KEYS_TO_INCLUDE:
        message[key] = None
    message.update(
        {k: data_column[k] for k in data_column.keys() & DATA_KEYS_TO_INCLUDE}
    )

    parse_data = data_column["parse_data"] if "parse_data" in data_column else None
    if parse_data is not None:
        message["entities"] = parse_data["entities"]
        message["intent"] = parse_data["intent"]
        message["intent_ranking"] = parse_data["intent_ranking"]
        message["name"] = parse_data["name"] if "name" in parse_data else None
    else:
        # to be consistent
        message["entities"] = []
        message["intent"] = {}
        message["intent_ranking"] = []
        message["name"] = None
    return message

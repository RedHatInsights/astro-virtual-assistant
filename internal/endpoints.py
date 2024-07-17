from typing import Optional, List

from flask import Flask, Response, jsonify, request, send_from_directory, redirect
from sqlalchemy import and_, or_, true, asc, desc, func
from sqlalchemy.orm import sessionmaker, aliased
import json
import hashlib

from common import logging
from common.config import app

from internal.utils import read_arguments, export_csv
from internal.database.db import DB
from internal.database.models import Events

API_PREFIX = "/api/v1"

REMOVE_PATHS = [
    ("data", "event"),
    ("data", "timestamp"),
    ("data", "value", "email"),
    ("data", "value", "identity"),
    ("data", "metadata", "email"),
    ("data", "metadata", "identity"),
    ("data", "parse_data", "metadata", "email"),
    ("data", "parse_data", "metadata", "identity"),
]

flask_app = Flask(__name__)
db = DB()
engine = db.get_engine()
Session = sessionmaker(engine)
logger = logging.initialize_logging()


def start_internal_api():
    logger.info("Starting virtual assistant internal api...")
    flask_app.run(host="0.0.0.0", port=app.internal_api_port)


@flask_app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@flask_app.route(API_PREFIX + "/", methods=["GET"])
def serve_root():
    return redirect("./ui/index.html")


@flask_app.route(API_PREFIX + "/ui", methods=["GET"])
def serve_root_ui():
    return redirect("./ui/index.html")


@flask_app.route(API_PREFIX + "/ui/<path:path>", methods=["GET"])
def serve_static(path):
    return send_from_directory("public", path)


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
        return Response(str(args), status=400)

    type_names = args.type_name or []
    if args.unique is True:
        type_names.append("user")

    raw_messages, count = _get_messages(
        start_date=args.start_date,
        end_date=args.end_date,
        type_names=type_names,
        limit=args.limit,
        offset=args.offset,
        cursor=args.cursor,
    )

    messages = list(map(lambda m: process_message(m), raw_messages))

    if args.format == "csv":
        return export_csv(messages)
    
    response = {
        "count": count,
        "messages": messages
    }

    return jsonify(response)


# Returns complete conversation given a sender_id
# params:
#  - sender_id (required): sender_id of the conversation
#  - limit (optional): limit the number of messages returned; default is 100
#  - start_date (optional): only return messages sent after this date
#  - end_date (optional): only return messages sent before this date
#  - type_name (optional): only return messages of this type
#  - unique (optional): if true, only return unique messages (i.e. typed by the user, no commands)
#  - offset (optional): offset the returned messages; default is 0. If both offset and cursor are set the request fails
#  - cursor (optional): only return messages after this id - used for cursor pagination. If both offset and cursor are set the request fails
#  - format (optional): "csv" or "json" format; default is "json"
@flask_app.route(API_PREFIX + "/messages/<sender_id>", methods=["GET"])
def get_conversation_by_sender_id(sender_id):
    args = read_arguments()
    if isinstance(args, ValueError):
        return Response(str(args), status=400)

    type_names = args.type_name or []
    if args.unique is True:
        type_names.append("user")

    raw_messages, count = _get_messages(
        sender_id=sender_id,
        start_date=args.start_date,
        end_date=args.end_date,
        type_names=type_names,
        limit=args.limit,
        offset=args.offset,
        cursor=args.cursor,
    )

    messages = list(map(lambda m: process_message(m), raw_messages))

    if args.format == "csv":
        return export_csv(messages)
    
    response = {
        "count": count,
        "messages": messages
    }

    return jsonify(response)


# Returns list of sender_id
# params:
#  - username and org_id (optional): only return sender_id of this user's conversation; both needed
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

    OuterEvent = aliased(Events)

    conditions = []
    if args.start_date:
        conditions.append(OuterEvent.timestamp > args.start_date)
    if args.end_date:
        conditions.append(OuterEvent.timestamp < args.end_date)
    if args.org_id and args.username:
        hash = hashlib.sha256(
            "{org_id}-{username}".format(
                org_id=args.org_id, username=args.username
            ).encode()
        ).hexdigest()
        conditions.append(OuterEvent.sender_id == hash)
    conditions = and_(true(), *conditions)

    query_builder = (
        session.query(OuterEvent.sender_id)
        .distinct()
        .where(conditions)
    )
    count = query_builder.count()
    rows = (
        query_builder.limit(args.limit)
        .offset(args.offset).all()
    )

    sender_list = []
    for row in rows:
        sender_list.append({"sender_id": row[0]})

    if args.format == "csv":
        return export_csv(sender_list)
    
    response = {
        "senders": sender_list,
        "count": count
    }

    return jsonify(response)


def _get_messages(
    sender_id: Optional[str] = None,
    start_date: Optional[float] = None,
    end_date: Optional[float] = None,
    type_names: Optional[List[str]] = None,
    limit: int = 100,
    offset: Optional[int] = None,
    cursor: Optional[int] = None,
):
    session = Session()
    conditions = []

    if sender_id is not None:
        conditions.append(Events.sender_id == sender_id)

    if start_date is not None:
        conditions.append(Events.timestamp > start_date)

    if end_date is not None:
        conditions.append(Events.timestamp < end_date)

    if type_names is not None and len(type_names) > 0:
        conditions.append(Events.type_name.in_(type_names))

    if offset is None and cursor is None:
        offset = 0
    elif offset is not None and cursor is not None:
        raise ValueError("Should not specify both offset and cursor")

    if cursor is not None:
        conditions.append(Events.id < cursor)

    query_builder = (
        session.query(Events)
        .where(and_(true(), *conditions))
        .order_by(desc(Events.id))
    )
    count = query_builder.count()

    if offset is not None:
        query_builder = query_builder.offset(offset)
    
    messages = query_builder.limit(limit).all()

    return messages, count


def process_message(row):
    message = {
        "id": row.id,
        "sender_id": row.sender_id,
        "type_name": row.type_name,
        "timestamp": row.timestamp,
        "data": json.loads(row.data),
    }

    for path in REMOVE_PATHS:
        current = message
        for step in path[:-1]:
            if step in current and isinstance(current[step], dict):
                current = current[step]
            else:
                current = None
                break

        if current is not None and path[-1] in current:
            current.pop(path[-1])

    return message

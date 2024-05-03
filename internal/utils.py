from flask import request, Response
import csv
from io import StringIO


DEFAULT_LIMIT = 100
MAX_LIMIT = 1000


class Arguments:
    def __init__(
        self,
        limit=DEFAULT_LIMIT,
        offset=None,
        start_date=None,
        end_date=None,
        type_name=None,
        unique=False,
        org_id=None,
        username=None,
        cursor=None,
        format="json",
    ):
        self.limit = limit
        self.offset = offset
        self.start_date = start_date
        self.end_date = end_date
        self.type_name = type_name
        self.unique = unique in ["true", "True", "1"] or False
        self.org_id = org_id
        self.username = username
        self.format = format
        self.cursor = cursor


def read_arguments():
    limit = request.args.get("limit") or DEFAULT_LIMIT
    offset = request.args.get("offset") or None
    cursor = request.args.get("cursor") or None
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    type_name = request.args.get("type_name")
    unique = request.args.get("unique")
    org_id = request.args.get("org_id")
    username = request.args.get("username")
    format = request.args.get("format") or "json"

    if int(limit) > MAX_LIMIT:
        return ValueError("limit must be less than {}".format(MAX_LIMIT))
    if int(limit) < 0:
        return ValueError("limit must be greater than 0")

    if type_name is not None and len(type_name) > 0:
        type_name = type_name.split(",")

    if unique and type_name is not None:
        return ValueError(
            "Can not specify both unique and type_name in the same request"
        )

    if offset is not None and cursor is not None:
        return ValueError("Can not specify both offset and cursor in the same request")

    return Arguments(
        limit=limit,
        offset=offset,
        start_date=start_date,
        end_date=end_date,
        type_name=type_name,
        unique=unique,
        org_id=org_id,
        username=username,
        cursor=cursor,
        format=format,
    )


def export_csv(data):
    csv_io = StringIO()
    fieldnames = data[0].keys() if len(data) > 0 else []
    print(fieldnames)
    writer = csv.DictWriter(csv_io, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    csv_data = csv_io.getvalue()
    return Response(csv_data, mimetype="text/csv")

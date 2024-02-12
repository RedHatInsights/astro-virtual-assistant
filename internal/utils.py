from flask import request, Response
import csv
from io import StringIO


DEFAULT_LIMIT = 100
MAX_LIMIT = 1000


class Arguments:
    def __init__(
        self,
        limit=DEFAULT_LIMIT,
        offset=0,
        start_date=None,
        end_date=None,
        type_name=None,
        unique=False,
        unity_id=None,
        format="json",
    ):
        if int(limit) > MAX_LIMIT:
            return ValueError("limit must be less than {}".format(MAX_LIMIT))
        if int(limit) < 0:
            return ValueError("limit must be greater than 0")
        self.limit = limit
        self.offset = offset
        self.start_date = start_date
        self.end_date = end_date
        self.type_name = type_name
        self.unique = unique in ["true", "True", "1"] or False
        self.unity_id = unity_id
        self.format = format


def read_arguments():
    limit = request.args.get("limit") or DEFAULT_LIMIT
    offset = request.args.get("offset") or 0
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    type_name = request.args.get("type_name")
    unique = request.args.get("unique")
    unity_id = request.args.get("unity_id")
    format = request.args.get("format") or "json"
    return Arguments(
        limit, offset, start_date, end_date, type_name, unique, unity_id, format
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

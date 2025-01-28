from flask import Blueprint, jsonify, request
from pydantic import BaseModel, ValidationError
from typing import Optional

from watson.internal_watson_extension.functions import functions_map
from common.requests import send_console_request_watson

api_blueprint = Blueprint("internal_api", __name__)


class ExecuteFunctionRequest(BaseModel):
    session_id: str
    function_name: str
    metadata: Optional[dict] = None


def run_function(request_session_id, function_name, functions_map):
    if function_name not in functions_map:
        raise ValueError(f"Function '{function_name}' not found in functions_map")

    function_details = functions_map[function_name]
    console_request_args = function_details.get("console_request_args", {})
    normalizer = function_details.get("normalizer")

    # Ensure the normalizer is a callable function
    if not callable(normalizer):
        raise ValueError(
            f"The normalizer for function '{function_name}' is not callable"
        )

    # TODO: Handle auth + Redis interaction here to obtain the necessry headers

    try:

        # TODO: update this with a new function that can handle auth
        data = send_console_request_watson(**console_request_args)

        # Normalize the data using the provided normalizer function
        normalized_data = normalizer(data)

        return normalized_data
    except Exception as e:
        # Catch all other exceptions
        raise Exception(f"An unexpected error occurred: {e}")


@api_blueprint.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Ok"})


@api_blueprint.route("/execute_function", methods=["POST"])
def execute_function():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No request body"}), 400

    try:
        validated_data = ExecuteFunctionRequest(**data)
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400

    function_name = validated_data.function_name
    request_session_id = validated_data.session_id

    try:
        function_response = run_function(
            request_session_id, function_name, functions_map
        )
    except Exception as e:
        print(e)
        return (
            jsonify({"message": "internal error encountered while executing function"}),
            500,
        )

    return jsonify(function_response), 200

import json
from time import time

from flask import request, jsonify

from app.api import bp
from app.default.models import Machine, Activity
from app.extensions import db
from config import Config


@bp.route('/activity', methods=['POST'])
def machine_activity():
    """ Receives JSON data detailing a machine's activity and saves it to the database
    Assigns a simple activity code depending on machine state
    Example format:
    {
        "machine_id": 1,
        "machine_state": 1,
        "time_start": (DateTime),
        "time_end": (DateTime)
    }
    """
    # Return an error if the request is not in json format
    if not request.is_json:
        response = jsonify({"error": "Request is not in json format"})
        response.status_code = 400
        return response

    data = request.get_json()
    # I was getting an issue with get_json() sometimes returning a string and sometimes dict so I did this
    if isinstance(data, str):
        data = json.loads(data)

    # Get all of the arguments, respond with an error if not provided
    if 'machine_id' not in data:
        response = jsonify({"error": "No machine_id provided"})
        response.status_code = 400
        return response
    machine = Machine.query.get(data['machine_id'])
    if machine is None:
        response = jsonify({"error": "Could not find machine with ID " + str(data['machine_id'])})
        response.status_code = 400
        return response

    if 'machine_state' not in data:
        response = jsonify({"error": "No machine_state provided"})
        response.status_code = 400
        return response
    try:
        machine_state = int(data['machine_state'])
    except ValueError:
        response = jsonify({"error": "Could not understand machine_state"})
        response.status_code = 400
        return response

    if 'time_start' not in data:
        response = jsonify({"error": "No time_start provided"})
        response.status_code = 400
        return response
    time_start = data['time_start']

    if 'timestamp_end' not in data:
        response = jsonify({"error": "No timestamp_end provided"})
        response.status_code = 400
        return response
    timestamp_end = data['timestamp_end']

    if int(machine_state) == Config.MACHINE_STATE_RUNNING:
        activity_id = Config.UPTIME_CODE_ID
    else:
        activity_id = Config.UNEXPLAINED_DOWNTIME_CODE_ID

    # Create and save the activity
    new_activity = Activity(machine_id=machine.id,
                            machine_state=machine_state,
                            activity_code_id=activity_id,
                            time_start=time_start,
                            timestamp_end=timestamp_end)
    db.session.add(new_activity)
    db.session.commit()

    # Recreate the data and send it back to the client for confirmation
    response = jsonify({"machine_id": machine.id,
                        "machine_state": new_activity.machine_state,
                        "time_start": new_activity.time_start,
                        "timestamp_end": new_activity.timestamp_end})
    response.status_code = 201
    return response



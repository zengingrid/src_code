import urllib.request
import urllib.parse
import datetime
import re
from io import BytesIO
from zoneinfo import ZoneInfo

from flask import Blueprint, jsonify, send_file

backend_bp = Blueprint("backend", __name__)

@backend_bp.route("/")
def info():
    values = get_data()
    if not values["success"]:
        return jsonify(values), 500

    return jsonify({"message": "Welcome to the backend. The API has two endpoints: `json` and `image`."})

def get_data(filename="student.txt"):
    data = {
        "success": False
    }
    try:
        with open(filename, "r") as fp:
            lines = fp.readlines()
    except FileNotFoundError:
        data.update(msg=f"{filename} was not found.")
        return data
    except IsADirectoryError:
        data.update(msg=f"{filename} is a directory and should be a file.")
        return data

    if len(lines) < 2:
        data.update(msg=f"The contents of {filename} are incorrect.")
        return data
    
    name = lines[0].strip()
    student_id = lines[1].strip()
    student_id_matches = re.match("A\d{8}", student_id)

    if not name or not student_id_matches:
        data.update(msg=f"The contents of {filename} are incorrect.")
        return data

    data.update(success=True)
    data.update(student_id=student_id, student_name=name)
    return data

@backend_bp.route("/json")
def display():
    values = get_data()

    if not values["success"]:
        return jsonify(values), 500

    return jsonify(values)

@backend_bp.route("/image")
def qrcode():
    values = get_data()

    if not values["success"]:
        return jsonify(values), 500

    name = values["student_name"]
    student_id = values["student_id"]

    PST = ZoneInfo("America/Vancouver")
    cur_date = datetime.datetime.now().astimezone(PST).strftime("%d-%m-%Y %H:%M")
    url = "https://api.qrserver.com/v1/create-qr-code/?"
    params = {
        "size": "200x200",
        "data": "\n".join([name, student_id, cur_date]),
        "format": "png",
    }

    url += urllib.parse.urlencode(params)

    with urllib.request.urlopen(url) as response:
        image = response.read()

    return send_file(BytesIO(image), mimetype="image/png")


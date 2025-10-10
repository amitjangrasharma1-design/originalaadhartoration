import json
from flask import Flask, request, jsonify

from request_impds import (
    build_session_id,
    build_encrypted_id,
    make_request,
)
from request_ration_card import make_request as make_rc_request


app = Flask(__name__)


@app.route("/getrationcard", methods=["POST", "GET"])
def get_ration_card():
    try:
        if request.method == "GET":
            uid = request.args.get("uid")
            state_code = request.args.get("stateCode", "28")
            id_type = request.args.get("idType", "U")
            session_id = request.args.get("sessionId")
        else:
            data = request.get_json(force=True, silent=False) or {}
            uid = data.get("uid")
            state_code = data.get("stateCode")
            id_type = data.get("idType", "U")
            session_id = data.get("sessionId")

        if not uid or not state_code:
            return jsonify({
                "error": "Missing required fields: uid",
                "example": {"GET": "/getrationcard?uid=290961983263&stateCode=28", "POST": {"uid": "290961983263", "stateCode": "28", "idType": "U"}}
            }), 400

        status, text = make_request(uid, id_type, state_code, session_id)
        # Try to return JSON if server returns JSON, else raw text
        try:
            return jsonify({
                "status": status,
                "sessionId": session_id or build_session_id(state_code),
                "body": json.loads(text)
            }), status
        except Exception:
            return jsonify({
                "status": status,
                "sessionId": session_id or build_session_id(state_code),
                "body": text
            }), status
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/getrationcardbyrcid", methods=["POST", "GET"])
def get_ration_card_by_rc_id():
    try:
        if request.method == "GET":
            rc_id = request.args.get("rcId")
            state_code = request.args.get("stateCode", "28")
            id_type = request.args.get("idType", "R")
            session_id = request.args.get("sessionId")
        else:
            data = request.get_json(force=True, silent=False) or {}
            rc_id = data.get("rcId")
            state_code = data.get("stateCode")
            id_type = data.get("idType", "R")
            session_id = data.get("sessionId")

        if not rc_id or not state_code:
            return jsonify({
                "error": "Missing required fields: rcId",
                "example": {"GET": "/getrationcardbyrcid?rcId=077004047354&stateCode=28", "POST": {"rcId": "077004047354", "stateCode": "28", "idType": "R"}}
            }), 400

        status, text = make_rc_request(rc_id, id_type, state_code, session_id)
        # Try to return JSON if server returns JSON, else raw text
        try:
            return jsonify({
                "status": status,
                "sessionId": session_id or build_session_id(state_code),
                "body": json.loads(text)
            }), status
        except Exception:
            return jsonify({
                "status": status,
                "sessionId": session_id or build_session_id(state_code),
                "body": text
            }), status
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)



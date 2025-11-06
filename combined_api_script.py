#!/usr/bin/env python3
"""
Flask Combined API for Ration Card, Sale Transactions and IMPDS
This Flask API provides endpoints for all three APIs
"""

import json
import sys
import argparse
from datetime import datetime
from typing import Dict, Any, Tuple
from flask import Flask, request, jsonify

# Import functions from existing modules
from request_ration_card import make_request as make_rc_request, build_session_id
from request_sale_transactions import make_sale_transaction_request
from request_impds import make_request as make_impds_request

app = Flask(__name__)


def call_ration_card_api(rc_id: str, state_code: str = "28", id_type: str = "R", session_id: str = None) -> Dict[str, Any]:
    """
    Call the ration card API and return formatted response
    """
    print(f"🔍 Calling Ration Card API for ID: {rc_id}")
    print(f"   State Code: {state_code}, ID Type: {id_type}")
    
    try:
        status, response_text = make_rc_request(rc_id, id_type, state_code, session_id)
        
        result = {
            "api_name": "Ration Card",
            "status_code": status,
            "success": status == 200,
            "timestamp": datetime.now().isoformat(),
            "request_params": {
                "rc_id": rc_id,
                "state_code": state_code,
                "id_type": id_type,
                "session_id": session_id or build_session_id(state_code)
            }
        }
        
        # Try to parse JSON response
        try:
            result["response_data"] = json.loads(response_text)
        except json.JSONDecodeError:
            result["response_data"] = response_text
            result["raw_response"] = True
            
        return result
        
    except Exception as e:
        return {
            "api_name": "Ration Card",
            "status_code": 0,
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "request_params": {
                "rc_id": rc_id,
                "state_code": state_code,
                "id_type": id_type,
                "session_id": session_id
            }
        }


def call_sale_transactions_api(ration_card_id: str) -> Dict[str, Any]:
    """
    Call the sale transactions API and return formatted response
    """
    print(f"💰 Calling Sale Transactions API for Ration Card ID: {ration_card_id}")
    
    try:
        status, response_text = make_sale_transaction_request(ration_card_id)
        
        result = {
            "api_name": "Sale Transactions",
            "status_code": status,
            "success": status == 200,
            "timestamp": datetime.now().isoformat(),
            "request_params": {
                "ration_card_id": ration_card_id
            }
        }
        
        # Try to parse JSON response
        try:
            result["response_data"] = json.loads(response_text)
        except json.JSONDecodeError:
            result["response_data"] = response_text
            result["raw_response"] = True
            
        return result
        
    except Exception as e:
        return {
            "api_name": "Sale Transactions",
            "status_code": 0,
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "request_params": {
                "ration_card_id": ration_card_id
            }
        }


def call_impds_api(uid: str, state_code: str = "28", id_type: str = "U", session_id: str = None) -> Dict[str, Any]:
    """
    Call the IMPDS API and return formatted response
    """
    print(f"🔍 Calling IMPDS API for UID: {uid}")
    print(f"   State Code: {state_code}, ID Type: {id_type}")
    
    try:
        status, response_text = make_impds_request(uid, id_type, state_code, session_id)
        
        result = {
            "api_name": "IMPDS",
            "status_code": status,
            "success": status == 200,
            "timestamp": datetime.now().isoformat(),
            "request_params": {
                "uid": uid,
                "state_code": state_code,
                "id_type": id_type,
                "session_id": session_id or build_session_id(state_code)
            }
        }
        
        # Try to parse JSON response
        try:
            result["response_data"] = json.loads(response_text)
        except json.JSONDecodeError:
            result["response_data"] = response_text
            result["raw_response"] = True
            
        return result
        
    except Exception as e:
        return {
            "api_name": "IMPDS",
            "status_code": 0,
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "request_params": {
                "uid": uid,
                "state_code": state_code,
                "id_type": id_type,
                "session_id": session_id
            }
        }


def call_both_apis(rc_id: str) -> Dict[str, Any]:
    """
    Call both APIs and return combined results
    """
    print("=" * 60)
    print("🚀 Starting Combined API Calls")
    print("=" * 60)
    
    # Default parameters
    state_code = "28"
    id_type = "R"
    session_id = None
    
    # Call both APIs
    ration_card_result = call_ration_card_api(rc_id, state_code, id_type, session_id)
    sale_transactions_result = call_sale_transactions_api(rc_id)
    
    # Combine results
    combined_result = {
        "overall_success": ration_card_result["success"] and sale_transactions_result["success"],
        "timestamp": datetime.now().isoformat(),
        "apis_called": 2,
        "results": {
            "ration_card": ration_card_result,
            "sale_transactions": sale_transactions_result
        }
    }
    
    return combined_result


def print_results(results: Dict[str, Any], verbose: bool = False):
    """
    Print the results in a formatted way
    """
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    overall_success = results["overall_success"]
    print(f"Overall Success: {'✅ YES' if overall_success else '❌ NO'}")
    print(f"APIs Called: {results['apis_called']}")
    print(f"Timestamp: {results['timestamp']}")
    
    print("\n" + "-" * 40)
    print("📋 INDIVIDUAL API RESULTS")
    print("-" * 40)
    
    for api_name, result in results["results"].items():
        print(f"\n🔹 {result['api_name']}:")
        print(f"   Status: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"   HTTP Code: {result['status_code']}")
        
        if result.get("error"):
            print(f"   Error: {result['error']}")
        
        if verbose and result.get("response_data"):
            print(f"   Response Data:")
            if isinstance(result["response_data"], dict):
                print(json.dumps(result["response_data"], indent=4, ensure_ascii=False))
            else:
                print(f"   {result['response_data']}")


# Flask Routes

@app.route("/", methods=["GET"])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        "message": "Combined API Server",
        "endpoints": {
            "/ration-card": "Get ration card data by RC ID",
            "/sale-transactions": "Get sale transactions by RC ID", 
            "/impds": "Get ration card data by UID (IMPDS)",
            "/combined": "Get both ration card and sale transactions data",
            "/all": "Get all three APIs data"
        },
        "usage": {
            "ration-card": "GET /ration-card?rc_id=123456789104&state_code=28&id_type=R",
            "sale-transactions": "GET /sale-transactions?rc_id=123456789104",
            "impds": "GET /impds?uid=123456789142&state_code=28&id_type=U",
            "combined": "GET /combined?rc_id=123456789104",
            "all": "GET /all?rc_id=123456789104&uid=123456789142"
        }
    })


@app.route("/ration-card", methods=["GET", "POST"])
def get_ration_card():
    """Get ration card data by RC ID"""
    try:
        if request.method == "GET":
            rc_id = request.args.get("rc_id")
            state_code = request.args.get("state_code", "28")
            id_type = request.args.get("id_type", "R")
            session_id = request.args.get("session_id")
        else:
            data = request.get_json() or {}
            rc_id = data.get("rc_id")
            state_code = data.get("state_code", "28")
            id_type = data.get("id_type", "R")
            session_id = data.get("session_id")

        if not rc_id:
            return jsonify({"error": "rc_id is required"}), 400

        result = call_ration_card_api(rc_id, state_code, id_type, session_id)
        return jsonify(result), result["status_code"] if result["status_code"] > 0 else 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sale-transactions", methods=["GET", "POST"])
def get_sale_transactions():
    """Get sale transactions by RC ID"""
    try:
        if request.method == "GET":
            rc_id = request.args.get("rc_id")
        else:
            data = request.get_json() or {}
            rc_id = data.get("rc_id")

        if not rc_id:
            return jsonify({"error": "rc_id is required"}), 400

        result = call_sale_transactions_api(rc_id)
        return jsonify(result), result["status_code"] if result["status_code"] > 0 else 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/impds", methods=["GET", "POST"])
def get_impds():
    """Get ration card data by UID (IMPDS)"""
    try:
        if request.method == "GET":
            uid = request.args.get("uid")
            state_code = request.args.get("state_code", "28")
            id_type = request.args.get("id_type", "U")
            session_id = request.args.get("session_id")
        else:
            data = request.get_json() or {}
            uid = data.get("uid")
            state_code = data.get("state_code", "28")
            id_type = data.get("id_type", "U")
            session_id = data.get("session_id")

        if not uid:
            return jsonify({"error": "uid is required"}), 400

        result = call_impds_api(uid, state_code, id_type, session_id)
        return jsonify(result), result["status_code"] if result["status_code"] > 0 else 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/combined", methods=["GET", "POST"])
def get_combined():
    """Get both ration card and sale transactions data"""
    try:
        if request.method == "GET":
            rc_id = request.args.get("rc_id")
        else:
            data = request.get_json() or {}
            rc_id = data.get("rc_id")

        if not rc_id:
            return jsonify({"error": "rc_id is required"}), 400

        result = call_both_apis(rc_id)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/all", methods=["GET", "POST"])
def get_all():
    """Get all three APIs data"""
    try:
        if request.method == "GET":
            rc_id = request.args.get("rc_id")
            uid = request.args.get("uid")
            state_code = request.args.get("state_code", "28")
        else:
            data = request.get_json() or {}
            rc_id = data.get("rc_id")
            uid = data.get("uid")
            state_code = data.get("state_code", "28")

        if not rc_id or not uid:
            return jsonify({"error": "Both rc_id and uid are required"}), 400

        # Call all three APIs
        ration_card_result = call_ration_card_api(rc_id, state_code, "R")
        sale_transactions_result = call_sale_transactions_api(rc_id)
        impds_result = call_impds_api(uid, state_code, "U")

        combined_result = {
            "overall_success": all([ration_card_result["success"], sale_transactions_result["success"], impds_result["success"]]),
            "timestamp": datetime.now().isoformat(),
            "apis_called": 3,
            "results": {
                "ration_card": ration_card_result,
                "sale_transactions": sale_transactions_result,
                "impds": impds_result
            }
        }

        return jsonify(combined_result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    """
    Main function for command line usage
    """
    parser = argparse.ArgumentParser(
        description="Combined API Script for Ration Card and Sale Transactions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python combined_api_script.py 123456789104
  python combined_api_script.py 123456789104 --verbose
        """
    )
    
    parser.add_argument("rc_id", help="Ration Card ID to query")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed response data")
    
    args = parser.parse_args()
    
    try:
        # Call both APIs
        results = call_both_apis(args.rc_id)
        print_results(results, args.verbose)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Command line mode
        main()
    else:
        # Flask server mode
        print("🚀 Starting Flask Combined API Server...")
        print("📖 Available endpoints:")
        print("   GET  / - API documentation")
        print("   GET  /ration-card?rc_id=123456789104")
        print("   GET  /sale-transactions?rc_id=123456789104")
        print("   GET  /impds?uid=123456789142")
        print("   GET  /combined?rc_id=123456789104")
        print("   GET  /all?rc_id=123456789104&uid=123456789142")
        print("=" * 50)
        app.run(host="0.0.0.0", port=5000, debug=True)


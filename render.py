import json
from flask import Flask, request, jsonify
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from functools import wraps
from datetime import datetime
import threading

app = Flask(__name__)
Compress(app)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

API_KEY = "supersecret123"
TELEGRAM_BOT_TOKEN = "8258734086:AAE08ZEDESb592nylpdBucrFiGUNDYFVe4I"
TELEGRAM_CHAT_ID = "7713741930"

def send_telegram_message_async(message):
    def send_message():
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            }
            requests.post(url, data=payload, timeout=5)
        except Exception as e:
            print(f"❌ Telegram send error: {e}")
    thread = threading.Thread(target=send_message)
    thread.daemon = True
    thread.start()
    return True

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if not api_key or api_key != API_KEY:
            return jsonify({'status': 'error', 'message': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/aadhar_to_ration/<aadhar>', methods=['GET'])
@require_api_key
@limiter.limit("10 per minute")
def get_ration_by_aadhar(aadhar):
    start_time = datetime.now()
    try:
        # Validate aadhar
        aadhar_clean = ''.join(filter(str.isdigit, str(aadhar)))
        if len(aadhar_clean) != 12:
            return jsonify({'status': 'error', 'message': 'Aadhaar must be 12 digits'}), 400
        # External API call
        url = f"https://originalaadhartoration.onrender.com/getrationcard?uid={aadhar_clean}"
        response = requests.get(url, timeout=10)
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Better IP detection - check multiple headers for real client IP
        ip_address = (
            request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
            request.headers.get('X-Real-IP', '') or
            request.headers.get('CF-Connecting-IP', '') or
            request.headers.get('X-Forwarded', '') or
            request.headers.get('Forwarded-For', '') or
            request.headers.get('Forwarded', '') or
            request.environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or
            request.environ.get('HTTP_X_REAL_IP', '') or
            request.remote_addr or
            'Unknown'
        )
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if response.status_code == 200:
            data = response.json()
            result_message = f"""
🔍 <b>Aadhar to Ration Search</b>
⏰ <b>Time:</b> {timestamp}
🆔 <b>Aadhaar:</b> {aadhar_clean}
🌐 <b>IP:</b> {ip_address}
✅ <b>Success</b>
📊 <b>Records Found:</b> {len(data.get('body', {}).get('memberDetailsList', [])) if isinstance(data, dict) and 'body' in data else 1}
⏱️ <b>Response Time:</b> {response_time:.2f}ms
🔗 <b>User Agent:</b> {user_agent[:50]}...
            """
            send_telegram_message_async(result_message)
            return jsonify({'status': 'success', 'data': data, 'response_time_ms': response_time}), 200
        else:
            not_found_message = f"""
🔍 <b>Aadhar to Ration Search</b>
⏰ <b>Time:</b> {timestamp}
🆔 <b>Aadhaar:</b> {aadhar_clean}
🌐 <b>IP:</b> {ip_address}
❌ <b>No Results Found</b>
⏱️ <b>Response Time:</b> {response_time:.2f}ms
🔗 <b>User Agent:</b> {user_agent[:50]}...
            """
            send_telegram_message_async(not_found_message)
            return jsonify({'status': 'not found', 'message': 'No records found', 'response_time_ms': response_time}), 404
    except Exception as e:
        # Better IP detection for error cases too
        ip_address = (
            request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
            request.headers.get('X-Real-IP', '') or
            request.headers.get('CF-Connecting-IP', '') or
            request.headers.get('X-Forwarded', '') or
            request.headers.get('Forwarded-For', '') or
            request.headers.get('Forwarded', '') or
            request.environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or
            request.environ.get('HTTP_X_REAL_IP', '') or
            request.remote_addr or
            'Unknown'
        )
        error_message = f"""
🔍 <b>Aadhar to Ration Search</b>
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🆔 <b>Aadhaar:</b> {aadhar}
🌐 <b>IP:</b> {ip_address}
🔥 <b>Server Error</b>
❌ <b>Error:</b> {str(e)}
        """
        send_telegram_message_async(error_message)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.errorhandler(401)
def unauthorized_handler(e):
    return jsonify({'status': 'error', 'message': 'Invalid or missing API key'}), 401

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'status': 'error', 'message': f'Rate limit exceeded: {e.description}'}), 429

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', debug=False, port=port, threaded=True)
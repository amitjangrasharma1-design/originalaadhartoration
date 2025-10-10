import base64
import hashlib
import json
import sys
from datetime import datetime
from typing import Tuple

import requests
from Crypto.Cipher import AES


def derive_aes_key_from_seed(seed_string: str) -> bytes:
    """Mimics util/j.a(String) -> SecretKeySpec: SHA-256(seed) then first 16 bytes."""
    sha256 = hashlib.sha256(seed_string.encode("utf-8")).digest()
    return sha256[:16]


def md5_hex(s: str) -> str:
    return hashlib.md5(s.encode("iso-8859-1")).hexdigest()


def android_encrypt_double_base64(plaintext: str, key_seed: str, iv_str: str) -> str:
    """
    Implements util/j.a(String, String, String):
      - key = first 16 bytes of SHA-256(key_seed)
      - iv = iv_str bytes (no truncation here; AES block size is 16)
      - mode = AES/CBC/PKCS5Padding
      - result = base64(base64(ciphertext)) per smali (custom then Apache Base64)
    """
    key = derive_aes_key_from_seed(key_seed)
    iv = iv_str.encode()
    if len(iv) != 16:
        iv = iv[:16]

    cipher = AES.new(key, AES.MODE_CBC, iv)

    # PKCS5/7 padding
    block = 16
    data = plaintext.encode()
    pad_len = block - (len(data) % block)
    data += bytes([pad_len]) * pad_len

    ct = cipher.encrypt(data)
    b64_once = base64.b64encode(ct)
    b64_twice = base64.b64encode(b64_once)
    return b64_twice.decode()


def build_session_id(state_code: str) -> str:
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{state_code}{now}"


def build_encrypted_id(uid_plaintext: str, id_type: str, session_id: str) -> str:
    """Replicates CheckAadharSeeding logic for id encryption when idType == "U"."""
    # Default seed (not used when idType == "U"): md5(md5("AePDSImPDs") + "1333")
    seed = md5_hex("AePDSImPDs")
    seed = md5_hex(seed + "1333")

    if id_type == "U":
        # For U: seed = md5(md5("APIMPDS$9712Q") + sessionId)
        seed = md5_hex("APIMPDS$9712Q")
        seed = md5_hex(seed + session_id)

    iv = "AP4123IMPDS@12768F"
    return android_encrypt_double_base64(uid_plaintext, seed, iv)


def make_request(uid_plaintext: str, id_type: str, state_code: str, session_id: str = None) -> Tuple[int, str]:
    if session_id is None:
        session_id = build_session_id(state_code)

    enc_id = build_encrypted_id(uid_plaintext, id_type, session_id)

    url = "http://impds.nic.in/impdsmobileapi/api/getrationcard"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 15; V2356 Build/AP3A.240905.015.A2)",
        "Host": "impds.nic.in",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }
    body = {
        "id": enc_id,
        "idType": id_type,
        "userName": "IMPDS",
        "token": "91f01a0a96c526d28e4d0c1189e80459",
        "sessionId": session_id,
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
    return resp.status_code, resp.text


def main():
    if len(sys.argv) < 4:
        print("Usage: python request_impds.py <uid_plaintext> <state_code> <id_type=U> [sessionId]")
        sys.exit(1)

    uid_plaintext = sys.argv[1]
    state_code = sys.argv[2]
    id_type = sys.argv[3]
    session_id = sys.argv[4] if len(sys.argv) > 4 else None

    status, text = make_request(uid_plaintext, id_type, state_code, session_id)
    print(f"HTTP {status}")
    print(text)


if __name__ == "__main__":
    main()



import json
import sys
from datetime import datetime
from typing import Tuple

import requests


def make_sale_transaction_request(ration_card_id: str) -> Tuple[int, str]:
    """
    Make request to get ration card sale transactions for last 6 months
    """
    url = "http://impds.nic.in/IVR_Impds/getRcSaleTrans6MonthData"
    
    headers = {
        "userAuthentication": "adminHR,e83ab5b36c61a5997840b69d81a572e9",
        "rationcardid": ration_card_id,
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 15; V2356 Build/AP3A.240905.015.A2)",
        "Host": "impds.nic.in",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }
    
    # Empty body as Content-Length is 0
    resp = requests.post(url, headers=headers, data="", timeout=30)
    return resp.status_code, resp.text


def main():
    if len(sys.argv) < 2:
        print("Usage: python request_sale_transactions.py <ration_card_id>")
        print("Example: python request_sale_transactions.py 077004047354")
        sys.exit(1)

    ration_card_id = sys.argv[1]
    
    status, text = make_sale_transaction_request(ration_card_id)
    print(f"HTTP {status}")
    print(text)


if __name__ == "__main__":
    main()

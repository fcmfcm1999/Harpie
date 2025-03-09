import sys
import time

import requests
import json
from datetime import datetime, timedelta, timezone
from dateutil import parser
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout)  # 终端打印
    ],
)

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://harpie.io",
    "priority": "u=1, i",
    "referer": "https://harpie.io/app/dashboard/0x15D05A7E75C34F8A2D2f178A1647ceC2112C5E6B/?chainId=8453",
    "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

api_url = "https://harpie.io/api"

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def get_profile_info(_address, _chain_id, _proxy):

    url = f'{api_url}/hooks/get-leaderboard-info/'
    payload = {
        "address": _address,
        "chainId": _chain_id,
        "includeLeaderboard": False
    }
    proxies = {
        "http": _proxy,
        "https": _proxy
    }

    if _proxy:
        response = requests.post(url, json=payload, headers=headers, proxies=proxies)
    else:
        response = requests.post(url, json=payload, headers=headers)

    return response.json()

def get_last_scan_timestamp(_address, _proxy):
    walletconnect_headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,zh;q=0.8,zh-HK;q=0.7,zh-CN;q=0.6,zh-TW;q=0.5",
        "cache-control": "max-age=0",
        "dnt": "1",
        "origin": "https://harpie.io",
        "priority": "u=1, i",
        "referer": "https://harpie.io/",
        "sec-ch-ua": "\"Chromium\";v=\"133\", \"Not(A:Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    url = f'https://rpc.walletconnect.org/v1/identity/{_address}'
    querystring = {"projectId":"da1314eed7bfcf9f0b4d53d22b852b58"}
    proxies = {
        "http": _proxy,
        "https": _proxy
    }

    if _proxy:
        response = requests.get(url, headers=walletconnect_headers, params=querystring, proxies=proxies)
    else:
        response = requests.get(url, headers=walletconnect_headers, params=querystring)

    if response.status_code != 200:
        raise requests.HTTPError(f"Request failed with status {response.status_code}: {response.text}")

    return response.json()["resolvedAt"]

def scan_wallet(_address, _proxy, _chain_id):
    url = f'{api_url}/addresses/{_address}/queue-health'

    payload = {
        "chainId": _chain_id,
        "manualScan": True
    }

    proxies = {
        "http": _proxy,
        "https": _proxy
    }

    try:
        if _proxy:
            response = requests.post(url, json=payload, headers=headers, proxies=proxies)
        else:
            response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            logging.error(f"Request failed with status {response.status_code}: {response.text}")
            return None

        logging.info("Scan wallet successfully")
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP request error: {e}")
        return None


def process_account(_account):
    logging.info("=================================")
    logging.info(f'Begin handle for address: {_account["address"]}')
    address = _account["address"]
    proxy = _account["proxy"]
    # 1 ethereum; 137 polygon; 8453 base; 42161 arb
    chain_id = _account["chainId"]
    profile_info = get_profile_info(address, chain_id, proxy)
    points = profile_info["personalPoints"]
    logging.info(f'address {address} has {points} points now')
    # print(scan_wallet(address, proxy, chain_id))
    if profile_info["hasDoneDailyScan"]:
        last_time_str = get_last_scan_timestamp(address, proxy)
        time_obj = parser.isoparse(last_time_str)

        next_time = time_obj + timedelta(days=1, seconds=30)
        current_time = datetime.now(timezone.utc)
        time_diff_seconds = (next_time - current_time).total_seconds()
        logging.info(f"Address {address} has scanned wallet today; You need to wait {time_diff_seconds} seconds")
        logging.info("Waiting")
        time.sleep(time_diff_seconds)
        logging.info("Waiting finished")
    if scan_wallet(address, proxy, chain_id):
        logging.info(f'address {address} has {points + 250} points now')

accounts = config["wallets"]

if len(sys.argv) > 1:
    index = int(sys.argv[1])
    if 0 <= index < len(accounts):
        process_account(accounts[index])
    else:
        logging.error(f"Index {index} out of range.")
else:
    for account in accounts:
        process_account(account)

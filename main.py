import sys

import requests
import json

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


def scan_wallet(_address, _proxy):
    url = f'{api_url}/addresses/{_address}/queue-health'

    payload = {
        "chainId": 8453,
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
            print(f"Request failed with status {response.status_code}: {response.text}")
            return None

        print("Scan wallet successfully")
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
        return None


def process_account(_account):
    address = _account["address"]
    proxy = _account["proxy"]
    chain_id = _account["chainId"]
    profile_info = get_profile_info(address, chain_id, proxy)
    points = profile_info["personalPoints"]
    print(f'address {address} has {points} points now')
    if not profile_info["hasDoneDailyScan"]:
        scan_wallet(address, proxy)
    print(f'address {address} has {points + 250} points now')

accounts = config["wallets"]

if len(sys.argv) > 1:
    index = int(sys.argv[1])
    if 0 <= index < len(accounts):
        process_account(accounts[index])
    else:
        print(f"Index {index} out of range.")
else:
    for account in accounts:
        process_account(account)

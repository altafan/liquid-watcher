import os
import sys
import json
import time
import signal
import argparse
import requests
import threading
from flask import Flask
import wallycore as wally

def watch_balances(datadir, esplora_url, addresses, asset):
    update_balances(esplora_url, datadir, addresses, asset)
    block_height = get_block_height(esplora_url)

    while True:
        new_height = get_block_height(esplora_url)
        if new_height > block_height:
            block_height = new_height
            update_balances(esplora_url, datadir, addresses, asset)
        time.sleep(30)


def start_server(args):
    check_args(args)

    print("Starting asset watcher with configs:")
    print("  datadir:\t\t%s" % args.datadir)
    print("  address list:\t\t@datadir/addresses.json")
    print("  balance list:\t\t@datadir/balances.json")
    print("  network:\t\t%s" % args.network)
    print("  asset hash:\t\t%s" % args.asset)
    print("  esplora base url:\t%s" % args.esplora_url)

    wally_ca_prefix = get_wally_prefix(args.network)
    addresses = parse_confidential_addresses(args.datadir, wally_ca_prefix)

    t = threading.Thread(
        target = watch_balances,
        args = (args.datadir, args.esplora_url, addresses, args.asset)
    )
    t.start()

    app = Flask(__name__)

    signal.signal(signal.SIGINT, lambda x,y: sys.exit(0))

    @app.route("/balances")
    def getbalances():
        with open("%s/balances.json" % args.datadir) as f:
            return json.load(f)

    app.run(port=args.port, debug=args.verbose)
    

    
def check_args(args):
    if not os.path.isabs(args.datadir):
        raise Exception("Invalid argument: datadir must specify an absolute path")
    
    if args.network != "mainnet" and args.network != "testnet" and args.network != "regtest":
        raise Exception("Invalid argument: network must be one of 'mainnet', 'testnet' or 'regtest'")
    
    if args.esplora_url == None:
        raise Exception("Invalid argument: explorer base url not specified")
    
    if args.port <= 1024 or args.port > 65535:
        raise Exception("Invalid argument: server port out of range (1024, 65535)")

    ping(args.esplora_url)

def get_wally_prefix(network):
    if network == "regtest":
        return wally.WALLY_CA_PREFIX_LIQUID_REGTEST
    return wally.WALLY_CA_PREFIX_LIQUID

def ping(base_url):
    get_block_height(base_url)

def get_block_height(base_url):
    url = "%s/blocks/tip/height" % base_url
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception("Invalid argument: explorer is not reachable")
    return resp.text
    
def get_balance(base_url, address, asset):
    url = "%s/address/%s/utxo" % (base_url, address)
    resp = requests.get(url)
    utxos = resp.json()
    if len(utxos) > 0:
        return sum([x["value"] for x in utxos if x["asset"] == asset])
    return 0

def update_balances(base_url, datadir, addresses, asset):
    balances = {}
    for addr in addresses:
        balance = get_balance(base_url, addr, asset)
        balances[addr] =  balance
    with open("%s/balances.json" % datadir, "w") as f:
        json.dump(balances, f)

def parse_confidential_addresses(datadir, wally_ca_prefix):
    with open("%s/addresses.json" % datadir) as f:
        try:
            addresses = []
            caddrs = json.load(f)
            for caddr in caddrs:
                address = wally.confidential_addr_to_addr(caddr, wally_ca_prefix)
                addresses.append(address)
            return addresses
        except Exception as e:
            raise ValueError("Failed to parse confidential address") from e

def main():
    try:
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
        
        parser.add_argument("--datadir", help="absolute path of the directory used by the watcher", required=True)
        parser.add_argument("--esplora-url", help="explorer base API url", required=True)
        parser.add_argument("--asset", help="hash of the asset to watch", required=True)
        parser.add_argument("--port", type=int, help="server port", required=True)
        parser.add_argument("--network", help="either main, test or regression network")
        parser.add_argument("--verbose", action="store_true", help="enable debug mode")
        parser.set_defaults(fn=start_server, network="regtest", verbose=False)

        args = parser.parse_args()
        args.fn(args)
    except Exception as e:
        print(e)

main()
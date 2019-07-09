#!/usr/bin/env python3
import os
import sys
import json
import base64
import pprint
import argparse
import random
import hashlib
import binascii
import traceback
import urllib.request
import urllib.parse
import tempfile

vmscheme = "vmess://"
ssscheme = "ss://"

def parseLink(link):
    if link.startswith(ssscheme):
        return parseSs(link)
    elif link.startswith(vmscheme):
        return parseVmess(link)
    else:
        print("ERROR: found unsupported line: "+link)
        return None

def item2link(item):
    if item["net"] == "shadowsocks":
        ps = item["ps"]
        addr = item["add"]
        port = item["port"]
        method = item["aid"]
        password = ["id"]
        auth = base64.b64encode("{}:{}".format(method, password).encode()).decode()
        sslink = "ss://{}@{}:{}#{}".format(auth, addr, port, urllib.parse.quote(ps))
        return sslink
    else:
        return "vmess://{}".format(base64.b64encode(json.dumps(item).encode()).decode()) 


def parseSs(sslink):
    RETOBJ = {
        "v": "2",
        "ps": "",
        "add": "",
        "port": "",
        "id": "",
        "aid": "",
        "net": "shadowsocks",
        "type": "",
        "host": "",
        "path": "",
        "tls": ""
    }
    if sslink.startswith(ssscheme):
        info = sslink[len(ssscheme):]
        
        if info.rfind("#") > 0:
            info, _ps = info.split("#", 2)
            RETOBJ["ps"] = urllib.parse.unquote(_ps)
        
        if info.find("@") < 0:
            # old style link
            #paddings
            blen = len(info)
            if blen % 4 > 0:
                info += "=" * (4 - blen % 4)

            info = base64.b64decode(info).decode()

            atidx = info.rfind("@")
            method, password = info[:atidx].split(":", 2)
            addr, port = info[atidx+1:].split(":", 2)
        else:
            atidx = info.rfind("@")
            addr, port = info[atidx+1:].split(":", 2)

            info = info[:atidx]
            blen = len(info)
            if blen % 4 > 0:
                info += "=" * (4 - blen % 4)

            info = base64.b64decode(info).decode()
            method, password = info.split(":", 2)

        RETOBJ["add"] = addr
        RETOBJ["port"] = port
        RETOBJ["aid"] = method
        RETOBJ["id"] = password
        return RETOBJ


def parseVmess(vmesslink):
    """
    return:
{
  "v": "2",
  "ps": "remark",
  "add": "4.3.2.1",
  "port": "1024",
  "id": "xxx",
  "aid": "64",
  "net": "tcp",
  "type": "none",
  "host": "",
  "path": "",
  "tls": ""
}
    """
    if vmesslink.startswith(vmscheme):
        bs = vmesslink[len(vmscheme):]
        #paddings
        blen = len(bs)
        if blen % 4 > 0:
            bs += "=" * (4 - blen % 4)

        vms = base64.b64decode(bs).decode()
        return json.loads(vms)
    else:
        raise Exception("vmess link invalid")


def read_subscribe(sub_url):
    print("Reading from subscribe ...")
    with urllib.request.urlopen(sub_url) as response:
        _subs = response.read()
        return base64.b64decode(_subs).decode().splitlines()

def list_multiple(lines):
    vmesses = []
    for _v in lines:
        _vinfo = parseLink(_v)
        if _vinfo is not None:
            vmesses.append({ 
                "ps": "[{ps}] {add}:{port}/{net}".format(**_vinfo),
                "vm": _v,
                "info": _vinfo
            })

    while True:

        print("==============================================================")
        for i, item in enumerate(vmesses):
            print("[{}] - {}".format(i+1, item["ps"]))

        if not sys.stdin.isatty() and os.path.exists('/dev/tty'):
            sys.stdin.close()
            sys.stdin = open('/dev/tty', 'r')

        if sys.stdin.isatty():
            print("==============================================================")
            print("Enter index digit to edit")
            print("Or other commands: Sort(o), Sort by desc(d), Write and Exit(w), Delete XX(dXX)")
            print("Quit(q)")

            sel = input("Choose >>> ")
            if sel.isdigit():
                idx = int(sel) - 1
                edit_item(vmesses, idx)
                os.system("clear")
            elif sel == "o":
                vmesses = sorted(vmesses, key=lambda i:i["ps"])
            elif sel == "d":
                vmesses = sorted(vmesses, key=lambda i:i["ps"], reverse=True)
            elif sel == "w":
                output_item(vmesses)
                sys.exit(0)
            elif sel == "q":
                sys.exit(0)
            elif sel.startswith("d") and sel[1:].isdigit():
                idx = int(sel[1:])-1
                del vmesses[idx]
            else:
                print("Unreconized command.")

        else:
            raise Exception("Current session cant open a tty to select. Specify the index to --select argument.")


def edit_item(vmesses, idx):
    item = vmesses[idx]["info"]
    _, tfile = tempfile.mkstemp()
    with open(tfile, 'w') as f:
        json.dump(item, f, indent=4)

    os.system("vim {}".format(tfile))

    with open(tfile, 'r') as f:
        item = json.load(f)
        vmesses[idx]["info"] = item
        vmesses[idx]["vm"] = item2link(item)
        vmesses[idx]["ps"] = "[{ps}] {add}:{port}/{net}".format(**item)
    os.remove(tfile)

def output_item(vmesses):
    links = map(lambda x:x["vm"], vmesses)
    with open(option.edit[0].name, "w") as f:
        f.write("\n".join(links))

if __name__ == "__main__":
    # import ptvsd
    # ptvsd.enable_attach(address=('localhost', 5678), redirect_output=True)
    # ptvsd.wait_for_attach()

    parser = argparse.ArgumentParser(description="vmess subscribe file editor.")
    parser.add_argument('edit',
                        nargs=1,
                        type=argparse.FileType('r'),
                        help="a subscribe text file, base64 encoded or not")

    option = parser.parse_args()
    indata = option.edit[0].read()

    try:
        lines = base64.b64decode(indata).decode().splitlines()
    except (binascii.Error, UnicodeDecodeError):
        lines = indata.splitlines()
    finally:
        list_multiple(lines)

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
        print("ERROR: unsupported line: "+link)
        return None

def item2link(item):
    if item["net"] == "shadowsocks":
        auth = base64.b64encode("{method}:{password}".format(**item).encode()).decode()
        addr = "{add}:{port}".format(**item)
        sslink = "ss://{}@{}#{}".format(auth, addr, urllib.parse.quote(item["ps"]))
        return sslink
    else:
        return "vmess://{}".format(base64.b64encode(json.dumps(item).encode()).decode()) 


def parseSs(sslink):
    if sslink.startswith(ssscheme):
        ps = ""
        info = sslink[len(ssscheme):]
        
        if info.rfind("#") > 0:
            info, ps = info.split("#", 2)
        
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

        return dict(net="shadowsocks", add=addr, port=port, method=method, password=password, ps=ps)

def parseVmess(vmesslink):
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


def menu_item(vinfo):
    return "[{ps}] {add}:{port}/{net}".format(**vinfo)

def menu_loop(lines):
    vmesses = []
    for _v in lines:
        _vinfo = parseLink(_v)
        if _vinfo is not None:
            vmesses.append({ 
                "menu": menu_item(_vinfo),
                "link": _v,
                "info": _vinfo
            })

    while True:

        print("==============================================================")
        for i, item in enumerate(vmesses):
            print("[{:^3}] - {}".format(i, item["menu"]))

        print("""==============================================================
Enter index digit to edit:
Other commands: Sort(o), Sort by desc(d), Write(w), Delete XX(dXX)
Quit without saving(q)
""")

        try:
            sel = input("Choose >>> ")
            if sel.isdigit():
                idx = int(sel)
                edit_item(vmesses, idx)
            elif sel == "o":
                vmesses = sorted(vmesses, key=lambda i:i["ps"])
            elif sel == "d":
                vmesses = sorted(vmesses, key=lambda i:i["ps"], reverse=True)
            elif sel == "w":
                output_item(vmesses)
                return
            elif sel == "q":
                return
            elif sel.startswith("d") and sel[1:].isdigit():
                idx = int(sel[1:])
                del vmesses[idx]
            else:
                print("Error: Unreconized command.")
        except IndexError:
            print("Error input: Out of range")
        except EOFError:
            return




def edit_item(vmesses, idx):
    item = vmesses[idx]["info"]

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.close()
    with open(tfile.name, 'w') as f:
        json.dump(item, f, indent=4)

    os.system("vim {}".format(tfile.name))

    with open(tfile.name, 'r') as f:
        try:
            item = json.load(f)
        except json.decoder.JSONDecodeError:
            print("Error: json syntax error")
        else:
            vmesses[idx]["info"] = item
            vmesses[idx]["link"] = item2link(item)
            vmesses[idx]["menu"] = menu_item(item)

    os.remove(tfile.name)

def output_item(vmesses):
    links = map(lambda x:x["link"], vmesses)
    with open(option.edit[0].name, "w") as f:
        f.write("\n".join(links))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="vmess subscribe file editor.")
    parser.add_argument('edit',
                        nargs=1,
                        type=argparse.FileType('r'),
                        help="a subscribe text file, base64 encoded or not")

    option = parser.parse_args()
    indata = option.edit[0].read()
    option.edit[0].close()

    try:
        lines = base64.b64decode(indata).decode().splitlines()
    except (binascii.Error, UnicodeDecodeError):
        lines = indata.splitlines()
    finally:
        menu_loop(lines)

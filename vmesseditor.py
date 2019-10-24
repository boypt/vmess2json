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
            ps = urllib.parse.unquote(ps)
        
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



def menu_loop(lines):
    vmesses = []
    menu_item = lambda x: "[{ps}] {add}:{port}/{net}".format(**x)

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
Enter index digit XX to edit,
Other commands: Add(a), Delete XX(dXX), Sort by ps(s), Sort by ps desc(d),
Save Write(w), Quit without saving(q)
""")

        try:
            sel = input("Choose >>>")
            if sel.isdigit():
                idx = int(sel)
                try:
                    _edited = edit_item(vmesses[idx]["info"])
                except json.decoder.JSONDecodeError:
                    print("Error: json syntax error")
                else:
                    vmesses[idx] = {
                        "menu": menu_item(_edited),
                        "link": item2link(_edited),
                        "info": _edited
                    }

            elif sel == "a":
                _v = input("input >>>")
                _vinfo = parseLink(_v)
                if _vinfo is not None:
                    vmesses.append({ 
                        "menu": menu_item(_vinfo),
                        "link": _v,
                        "info": _vinfo
                    })
            elif sel == "s":
                vmesses = sorted(vmesses, key=lambda i:i["info"]["ps"])
            elif sel == "d":
                vmesses = sorted(vmesses, key=lambda i:i["info"]["ps"], reverse=True)
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


def edit_item(item):
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.close()
    with open(tfile.name, 'w') as f:
        json.dump(item, f, indent=4)

    editor = os.environ.get("EDITOR", "vi")
    os.system("{} {}".format(editor, tfile.name))

    with open(tfile.name, 'r') as f:
        try:
            _in = json.load(f)
        finally:
            os.remove(tfile.name)
        
        return _in

def output_item(vmesses):
    links = map(lambda x:x["link"], vmesses)
    with open(option.edit[0], "w") as f:
        f.write("\n".join(links))

def edit_single_link(vmess):
    _vinfo = parseLink(vmess)
    if _vinfo is None:
        return

    try:
        _vedited = edit_item(_vinfo)
    except json.decoder.JSONDecodeError as e:
        print("JSON format error:", e)
        return

    _link = item2link(_vedited)
    print("Edited Link:")
    print(_link)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="vmess subscribe file editor.")
    parser.add_argument('edit',
                        nargs=1,
                        type=str,
                        help="a subscribe text file, base64 encoded or not, or a single vmess:// ss:// link")

    option = parser.parse_args()
    arg = option.edit[0]
    if os.path.exists(arg):
        with open(arg) as f:
            indata = f.read().strip()
        try:
            blen = len(indata)
            if blen % 4 > 0:
                indata += "=" * (4 - blen % 4)
            lines = base64.b64decode(indata).decode().splitlines()
        except (binascii.Error, UnicodeDecodeError):
            lines = indata.splitlines()
        finally:
            menu_loop(lines)

    else:
        edit_single_link(arg)

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
vlessscheme = "vless://"
ssscheme = "ss://"


def parseLink(link):
    if link.startswith(ssscheme):
        return parseSs(link)
    elif link.startswith(vmscheme):
        return parseVmess(link)
    elif link.startswith(vlessscheme):
        return parseVless(link)
    else:
        print("ERROR: unsupported line: "+link)
        return None


def item2link(item):
    if item["net"] == "shadowsocks":
        auth = base64.b64encode(
            "{method}:{password}".format(**item).encode()).decode()
        addr = "{add}:{port}".format(**item)
        sslink = "ss://{}@{}#{}".format(auth,
                                        addr, urllib.parse.quote(item["ps"]))
        return sslink
    elif item["net"] == "vless":

        linkobj = urllib.parse.urlparse(item.get("link", ""))
        qs = urllib.parse.parse_qs(linkobj.query)

        is_changed = False
        if linkobj.hostname != item["add"] or linkobj.port != item["port"]:
            is_changed = True
            linkobj = linkobj._replace(
                netloc="{}@{}:{}".format(linkobj.username, item["add"], linkobj.port))

        if urllib.parse.unquote_plus(linkobj.fragment) != item["ps"]:
            is_changed = True
            linkobj = linkobj._replace(
                fragment=urllib.parse.quote_plus(item["ps"]))

        if qs["host"][0] != item["host"]:
            is_changed = True
            qs["host"] = [item["host"]]
            linkobj = linkobj._replace(
                query=urllib.parse.urlencode(qs, doseq=True))

        if is_changed:
            item["link"] = linkobj.geturl()

        return item["link"]
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
            # paddings
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


def parseVless(link):
    if link.startswith(vlessscheme):
        linkobj = urllib.parse.urlparse(link)
        qs = urllib.parse.parse_qs(linkobj.query)

        ret = dict(net="vless", link=link, port=linkobj.port,
                   add=linkobj.hostname, ps=urllib.parse.unquote(linkobj.fragment))
        if "host" in qs:
            ret["host"] = qs["host"][0]

        return ret


def parseVmess(vmesslink):
    if vmesslink.startswith(vmscheme):
        bs = vmesslink[len(vmscheme):]
        # paddings
        blen = len(bs)
        if blen % 4 > 0:
            bs += "=" * (4 - blen % 4)

        vms = base64.b64decode(bs).decode()
        return json.loads(vms)
    else:
        raise Exception("vmess link invalid")


def menu_loop(lines):
    vmesses = []

    def menu_item(x):
        return "[{ps}] {net}/{add}:{port}".format(**x)

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
Commands need index as the arg (example: `edit 3')
del, edit, dup

Commands needs no args: 
add, sort, sortdesc, save, quit, help
""")

        try:
            command = input("Choose >>>").split(" ", maxsplit=1)

            if len(command) == 2:
                act, _idx = command
                act = act.lower()
                try:
                    idx = int(_idx)
                except ValueError:
                    idx = -1
                if idx >= len(vmesses):
                    raise ValueError("Index Error", idx)

            elif len(command) == 1:
                act = command[0]
                _idx = ""

            if act == "help":
                print_help()
            elif act == "edit":
                if idx < 0:
                    raise ValueError("Index Error")
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

            elif act == "add":
                if _idx == "":
                    _v = input("input >>>")
                else:
                    _v = _idx
                _vinfo = parseLink(_v)
                if _vinfo is not None:
                    vmesses.append({
                        "menu": menu_item(_vinfo),
                        "link": _v,
                        "info": _vinfo
                    })
            elif act == "sort":
                vmesses = sorted(vmesses, key=lambda i: i["info"]["ps"])
            elif act == "sortdesc":
                vmesses = sorted(
                    vmesses, key=lambda i: i["info"]["ps"], reverse=True)
            elif act == "save":
                output_item(vmesses)
                return
            elif act == "quit":
                return
            elif act == "del":
                if idx < 0:
                    raise ValueError("Index Error")
                del vmesses[idx]
            elif act == "dup":
                if idx < 0:
                    raise ValueError("Index Error")
                cp = vmesses[idx]["info"].copy()
                cp["ps"] += ".dup"
                vmesses.append({
                    "menu": menu_item(cp),
                    "link": item2link(cp),
                    "info": cp
                })
            else:
                print("Error: Unreconized command.")
        except ValueError as e:
            print(e)
        except IndexError:
            print("Error input: Out of range")
        except KeyboardInterrupt:
            return
        except EOFError:
            return


def print_help():
    print("""
* del  -  Delete an item, example: del 12
* edit -  Edit an item in an external editor (defaultly vi, via $EDITOR env variable) will be run for the json format.
* dup  -  Duplicate an item, with the 'ps' appended a suffix .dup
* add  -  Input a new vmess item in to the subscribtion.
* sort -  Sort the items by the 'ps'.
* sortdesc -  Sort the items by the 'ps' in descedent order. (reversed order)
* save -  Save and quit.
* quit -  Quit without saveing (same as pressing Ctrl+C). 

Press Enter to return to the items menu.
""")
    input()


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
    links = map(lambda x: x["link"], vmesses)
    with open(option.edit[0], "w") as f:
        f.write("\n".join(links)+"\n")


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

    parser = argparse.ArgumentParser(
        description="vmess subscribe file editor.")
    parser.add_argument('edit',
                        nargs=1,
                        type=str,
                        help="a subscribe text file, base64 encoded or not, or a single vmess:// ss:// link")

    option = parser.parse_args()
    arg = option.edit[0]
    if os.path.exists(arg):
        with open(arg) as f:
            origdata = f.read().strip()
        try:
            lines = base64.b64decode(origdata).decode().splitlines()
        except (binascii.Error, UnicodeDecodeError):
            lines = origdata.splitlines()
        finally:
            menu_loop(lines)

    else:
        edit_single_link(arg)

    print("  Bye :)")

#!/usr/bin/env python3
import os
import re
import json
import base64
import argparse
import binascii

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

def sed_loop(lines):

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


    seds = {}
    if option.sed:
        for s in option.sed:
            key, sedcmd = s.split(":", maxsplit=1)
            spliter = sedcmd[1:2]
            _, pattern, repl, tags = sedcmd.split(spliter, maxsplit=4)

            reflag = 0
            if "i" in tags:
                reflag |= re.IGNORECASE
            seds[key] = [pattern, repl, reflag]

    for vm in vmesses:
        for key, opt in seds.items():
            val = vm["info"].get(key, None)
            if val is None:
                continue
            vm["info"][key] = re.sub(opt[0], opt[1], val, opt[2])

        vm["link"] = item2link(vm["info"])
        msg = lambda x: "{ps} / {net} / {add}:{port} / net:{net}/aid:{aid}/host:{host}/path:{path}/tls:{tls}/type:{type}".format(**x)
        print(msg(vm["info"]))

    if option.inplace:
        output_item(vmesses)

def output_item(vmesses):
    links = map(lambda x:x["link"], vmesses)
    with open(option.edit[0], "w") as f:
        f.write("\n".join(links)+"\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="vmess subscribe file editor.")
    parser.add_argument('-s', '--sed', action='append', help="the sed command, can be multiple, only the replace form is supported,"
        " example: -s 's/find/repl/i' -s 's#remove##' ")
    parser.add_argument('-i', '--inplace', action='store_false', help="edit the filein place, like -i to sed command")
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
            sed_loop(lines)

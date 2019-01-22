#!/usr/bin/env python3
import os
import sys
import json
import base64
import pprint

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
    vmscheme = "vmess://"
    if vmesslink.startswith(vmscheme):
        bs = vmesslink[len(vmscheme):]
        vms = base64.b64decode(bs)
        return json.loads(vms)
    else:
        raise Exception("vmess link invalid")

def load_json(template_file):
    scriptDir = os.path.dirname(__file__)
    with open(os.path.join(scriptDir, 'template', 'client', template_file)) as f:
        return json.load(f)

def fill_basic(_c, _v):
    _c["outbounds"][0]["settings"]["vnext"][0]["address"]               = _v["add"]
    _c["outbounds"][0]["settings"]["vnext"][0]["port"]                  = _v["port"]
    _c["outbounds"][0]["settings"]["vnext"][0]["users"][0]["id"]        = _v["id"]
    _c["outbounds"][0]["settings"]["vnext"][0]["users"][0]["alterId"]   = int(_v["aid"])
    _c["outbounds"][0]["streamSettings"]["network"]                     = _v["net"]
    if _v["tls"] == "tls":
        _c["outbounds"][0]["streamSettings"]["security"] = "tls"
    return _c, _v

def fill_tcp_http(_c, _v):
    _c["outbounds"][0]["streamSettings"]["tcpSettings"]["header"]["type"] = _v["type"]
    
    if _v["host"]  != "":
        _c["outbounds"][0]["streamSettings"]["tcpSettings"]["header"]["request"]["headers"]["Host"] = \
            [ _v["host"] ]
    else:
        del _c["outbounds"][0]["streamSettings"]["tcpSettings"]["header"]["request"]["headers"]["Host"]

    if _v["path"]  != "":
        _c["outbounds"][0]["streamSettings"]["tcpSettings"]["header"]["request"]["path"] = \
            [ _v["path"] ]
    else:
        del _c["outbounds"][0]["streamSettings"]["tcpSettings"]["header"]["request"]["path"]

    return _c

def fill_kcp(_c, _v):
    _c["outbounds"][0]["streamSettings"]["kcpSettings"]["header"]["type"] = _v["type"]
    return _c

def fill_ws(_c, _v):
    _c["outbounds"][0]["streamSettings"]["wsSettings"]["path"] = _v["path"]
    _c["outbounds"][0]["streamSettings"]["wsSettings"]["headers"]["Host"] = _v["host"]
    return _c

def fill_h2(_c, _v):
    _c["outbounds"][0]["streamSettings"]["httpSettings"]["path"] = _v["path"]
    _c["outbounds"][0]["streamSettings"]["httpSettings"]["host"] = [ _v["host"] ]
    return _c

def vmess2client(_v):
    template_file = None
    if _v["net"] == "kcp":
        return fill_kcp(*fill_basic(load_json("kcp.json"), _v))
    elif _v["net"] == "ws":
        return fill_ws(*fill_basic(load_json("ws.json"), _v))
    elif _v["net"] == "h2":
        return fill_h2(*fill_basic(load_json("h2.json"), _v))
    elif _v["net"] == "tcp":
        if _v["type"] == "http":
            return fill_tcp_http(*fill_basic(load_json("http.json"), _v))
        else:
            _c, _ = fill_basic(load_json("tcp.json"), _v)
            return _c
    else:
        pprint.pprint(_v)
        raise Exception("this link seem invalid to the script, please report to dev.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("{} vmess://....".format(sys.argv[0]))
        sys.exit(1)

    vc = parseVmess(sys.argv[1])
    cc = vmess2client(vc)
    s = json.dumps(cc, indent=4)
    print(s)


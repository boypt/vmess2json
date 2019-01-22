#!/usr/bin/env python3
import sys
import json
import base64
import pprint
import argparse

TPL = {}
TPL["CLIENT"] = """
{
	"log": {
		"access": "",
		"error": "",
		"loglevel": "error"
	},
	"inbounds": [
		{
			"port": 1080,
			"listen": "::",
			"protocol": "socks",
			"settings": {
				"auth": "noauth",
				"udp": true,
				"ip": "127.0.0.1"
			},
			"streamSettings": null
		},
		{
			"port": 3128,
			"listen": "::",
			"protocol": "http"
		}
	],
	"outbounds": [
		{
			"protocol": "vmess",
			"settings": {
				"vnext": [
					{
						"address": "host.host",
						"port": 1234,
						"users": [
							{
								"id": "<TOBEFILLED>",
								"alterId": 0,
								"security": "auto"
							}
						]
					}
				]
			},
			"streamSettings": {
				"security": "",
				"tlsSettings": {},
				"wsSettings": {},
				"httpSettings": {},
				"network": "tcp",
				"kcpSettings": {},
				"tcpSettings": {},
				"quicSettings": {}
			},
			"mux": {
				"enabled": true
			}
		},
		{
			"protocol": "freedom",
			"settings": {
				"response": null
			},
			"tag": "direct"
		}
	],
	"dns": {
		"servers": [
			"8.8.8.8",
			"8.8.4.4",
			"1.1.1.1"
		]
	},
	"routing": {
		"domainStrategy": "AsIs",
		"rules": [
			{
				"type": "field",
				"ip": [
					"geoip:private"
				],
				"outboundTag": "direct"
			},
			{
				"type": "field",
				"domain": [
					"geosite:cn"
				],
				"outboundTag": "direct"
			},
			{
				"type": "field",
				"domain": [
					"geoip:cn"
				],
				"outboundTag": "direct"
			}
		]
	}
}
"""

# tcpSettings
TPL["http"] = """
{
    "header": {
        "type": "http",
        "request": {
            "version": "1.1",
            "method": "GET",
            "path": [
                "/"
            ],
            "headers": {
                "Host": [
                    "www.cloudflare.com",
                    "www.amazon.com"
                ],
                "User-Agent": [
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"
                ],
                "Accept": [
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
                ],
                "Accept-language": [
                    "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4"
                ],
                "Accept-Encoding": [
                    "gzip, deflate, br"
                ],
                "Cache-Control": [
                    "no-cache"
                ],
                "Pragma": "no-cache"
            }
        }
    }
}
"""

# kcpSettings
TPL["kcp"] = """
{
    "mtu": 1350,
    "tti": 50,
    "uplinkCapacity": 12,
    "downlinkCapacity": 100,
    "congestion": false,
    "readBufferSize": 2,
    "writeBufferSize": 2,
    "header": {
        "type": "wechat-video"
    }
}
"""

# wsSettings
TPL["ws"] = """
{
    "connectionReuse": true,
    "path": "/path",
    "headers": {
        "Host": "host.host.host"
    }
}
"""


# httpSettings
TPL["h2"] = """
{
    "host": [
        "host.com"
    ],
    "path": "/host"
}
"""


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

def load_TPL(stype):
    s = TPL[stype]
    return json.loads(s)

def fill_basic(_c, _v):
    _c["outbounds"][0]["settings"]["vnext"][0]["address"]               = _v["add"]
    _c["outbounds"][0]["settings"]["vnext"][0]["port"]                  = _v["port"]
    _c["outbounds"][0]["settings"]["vnext"][0]["users"][0]["id"]        = _v["id"]
    _c["outbounds"][0]["settings"]["vnext"][0]["users"][0]["alterId"]   = int(_v["aid"])
    _c["outbounds"][0]["streamSettings"]["network"]                     = _v["net"]
    if _v["tls"] == "tls":
        _c["outbounds"][0]["streamSettings"]["security"] = "tls"
    return _c

def fill_tcp_http(_c, _v):
    tcps = load_TPL("http")
    tcps["header"]["type"] = _v["type"]
    if _v["host"]  != "":
        tcps["header"]["request"]["headers"]["Host"] = [ _v["host"] ]

    if _v["path"]  != "":
        tcps["header"]["request"]["path"] = [ _v["path"] ]

    return _c

def fill_kcp(_c, _v):
    kcps = load_TPL("kcp")
    kcps["header"]["type"] = _v["type"]
    _c["outbounds"][0]["streamSettings"]["kcpSettings"] = kcps
    return _c

def fill_ws(_c, _v):
    wss = load_TPL("ws")
    wss["path"] = _v["path"]
    wss["headers"]["Host"] = _v["host"]
    _c["outbounds"][0]["streamSettings"]["wsSettings"] = wss
    return _c

def fill_h2(_c, _v):
    h2s = load_TPL("h2")
    h2s["path"] = _v["path"]
    h2s["host"] = [ _v["host"] ]
    _c["outbounds"][0]["streamSettings"]["httpSettings"] = h2s
    return _c

def vmess2client(_t, _v):
    _c = fill_basic(_t, _v)

    _net = _v["net"]
    _type = _v["type"]

    if _net == "kcp":
        return fill_kcp(_c, _v)
    elif _net == "ws":
        return fill_ws(_c, _v)
    elif _net == "h2":
        return fill_h2(_c, _v)
    elif _net == "tcp":
        if _type == "http":
            return fill_tcp_http(_c, _v)
        return _c
    else:
        pprint.pprint(_v)
        raise Exception("this link seem invalid to the script, please report to dev.")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="vmess2json convert vmess link to client json config.")
    parser.add_argument('-o', '--output',
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help="write output to file. default to stdout")
    parser.add_argument('vmess',
                        nargs='?',
                        help="vmess://...")

    option = parser.parse_args()
    if option.vmess is not None:
        vc = parseVmess(option.vmess)
        cc = vmess2client(load_TPL("CLIENT"), vc)
        json.dump(cc, option.output, indent=4)
    else:
        parser.print_help()


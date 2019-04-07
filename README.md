# Vmess2Json

Simple script parses `vmess://` links into client v2ray config json.

Currently supports only V2rayN/NG links.

## Usage
```
usage: vmess2json.py [-h] [-m] [-o OUTPUT] [-b] [-i INBOUNDS] [-s SECRET]
                     [vmess]

vmess2json convert vmess link to client json config.

positional arguments:
  vmess                 A vmess:// link. If absent, reads a line from stdin.

optional arguments:
  -h, --help            show this help message and exit
  -m, --multiple        read multiple lines from stdin, each write to a json
                        file named by remark, saving in current dir (PWD).
  -o OUTPUT, --output OUTPUT
                        write output to file. default to stdout
  -b, --outbound        only output as an outbound object.
  -i INBOUNDS, --inbounds INBOUNDS
                        inbounds usage, default: "socks:1080,http:8123".
                        Available proto: socks,http,dns,mt,transparent
  -s SECRET, --secret SECRET
                        mtproto secret code. if unsepecified, a random one
                        will be generated.
```

## Example
```
# manualy check on a link
echo "vmess://ABCDEFGabcdefg1234567890..." | vmess2json.py | vim -

# write one file with http and socks inbounds
vmess2json.py --inbounds http:8123,socks:7070,mt:8888 -o /etc/v2ray/config.json vmess://ABCDEFGabcdefg1234567890...

# wirte multiple
cat vmess_list.txt | vmess2json.py -m

# from a subscribe source
curl -L https://vmess.subscribe.domian/sub | base64 -d | vmess2json.py -m

# transparent proxy for router gateways with api (v2ctl StatsService)
vmess2json.py --inbounds transparent:1080,dns:53,api:10005 -o /etc/v2ray/config.json vmess://ABCDEFGabcdefg1234567890...
```

## Reference
 * [V2Ray 一键安装脚本 by 233boy](https://github.com/233boy/v2ray)
 * [V2ray多用户管理脚本 by Jrohy](https://github.com/Jrohy/multi-v2ray)
 * [V2RayN by 2dust](https://github.com/2dust/v2rayN/blob/master/v2rayN/v2rayN/Handler/V2rayConfigHandler.cs)

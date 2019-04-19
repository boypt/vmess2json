# Vmess2Json

Simple script parses `vmess://` links into client v2ray config json.

Currently supports only V2rayN/NG links.

## Usage
```
usage: vmess2json.py [-h] [-m] [-s [SELECT]] [-o OUTPUT] [--outbound]
                     [--inbounds INBOUNDS] [--secret SECRET]
                     [--subscribe SUBSCRIBE]
                     [vmess]

vmess2json convert vmess link to client json config.

positional arguments:
  vmess                 A vmess:// link. If absent, reads a line from stdin.

optional arguments:
  -h, --help            show this help message and exit
  -m, --multiple        read multiple lines from stdin, each write to a json
                        file named by remark, saving in current dir (PWD).
  -s [SELECT], --select [SELECT]
                        use together with -m/--multiple or --subscribe. Select
                        one of the vmess link from inputs. Argument is the
                        index(1,2,3...).
  -o OUTPUT, --output OUTPUT
                        write output to file. default to stdout
  --outbound            only output as an outbound object.
  --inbounds INBOUNDS   inbounds usage, default: "socks:1080,http:8123".
                        Available proto: socks,http,dns,mt,tproxy
  --secret SECRET       mtproto secret code. if unsepecified, a random one
                        will be generated.
  --subscribe SUBSCRIBE
                        read from a subscribe url, output a menu to choose
                        from.
```

## Example
```
# manualy check on a link (checkout outbound info)
vmess2json.py --outbound vmess://ABCDEFGabcdefg1234567890...
echo "vmess://ABCDEFGabcdefg1234567890..." | vmess2json.py --outbound

# write to file with http and socks inbounds
vmess2json.py --inbounds http:8123,socks:7070,mt:8888 -o /etc/v2ray/config.json vmess://ABCDEFGabcdefg1234567890...

# wirte multiple files (per line)
cat vmess_list.txt | vmess2json.py -m

# choose from a subscribe source
vmess2json.py --subscribe https://vmess.subscribe.domian/sub  -o /etc/v2ray/config.json

# or rather from a local source.
cat source.txt | vmess2json.py --subscribe -  -o /etc/v2ray/config.json

# transparent proxy for router gateways with api (v2ctl StatsService)
vmess2json.py --inbounds tproxy:1080,dns:53,api:10005 -o /etc/v2ray/config.json vmess://ABCDEFGabcdefg1234567890...
```

## Reference
 * [V2Ray 一键安装脚本 by 233boy](https://github.com/233boy/v2ray)
 * [V2ray多用户管理脚本 by Jrohy](https://github.com/Jrohy/multi-v2ray)
 * [V2rayN/NG 分享链接格式说明](https://github.com/2dust/v2rayN/wiki/%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5%E6%A0%BC%E5%BC%8F%E8%AF%B4%E6%98%8E(ver-2)) 
 * [V2rayN/NG 订阅功能说明](https://github.com/2dust/v2rayN/wiki/%E8%AE%A2%E9%98%85%E5%8A%9F%E8%83%BD%E8%AF%B4%E6%98%8E)
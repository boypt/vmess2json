# Vmess2Json

Simple script parses `vmess://` links into client v2ray config json. (`ss://` links also supported)
Currently only V2rayN/NG format is supported.

## Usage
```
usage: vmess2json.py [-h] [--parse_all] [--subscribe SUBSCRIBE] [-o OUTPUT]
                     [-u UPDATE] [--outbound] [--inbounds INBOUNDS]
                     [--secret SECRET]
                     [vmess]

vmess2json convert vmess link to client json config.

positional arguments:
  vmess                 A vmess:// link. If absent, reads a line from stdin.

optional arguments:
  -h, --help            show this help message and exit
  --parse_all           parse all input vmess lines and write each into .json
                        files
  --subscribe SUBSCRIBE
                        read from a subscribe url, output a menu to choose
                        from.
  -o OUTPUT, --output OUTPUT
                        write output to file. default to stdout
  -u UPDATE, --update UPDATE
                        update a config.json, only change the first outbound
                        object.
  --outbound            only output the outbound object.
  --inbounds INBOUNDS   inbounds usage, default: "socks:1080,http:8123".
                        Available proto: socks,http,dns,mt,tproxy
  --secret SECRET       mtproto secret code. if unsepecified, a random one
                        will be generated.
```

## Example

Common usage is to choose node from a subscribe source.
```
wget https://vmess.subscribe.domian/sub.txt
cat sub.txt | vmess2json.py --inbounds http:8123,socks:7070 --output /etc/v2ray/config.json
systemctl restart v2ray
```

Or just update the `outbound` object for a well written `config.json`.
```
cat sub.txt | vmess2json.py --update /etc/v2ray/config.json
systemctl restart v2ray
```

And many more other usages...
```
# manualy check on a link (checkout outbound info)
vmess2json.py --outbound vmess://ABCDEFGabcdefg1234567890...
echo "vmess://ABCDEFGabcdefg1234567890..." | vmess2json.py --outbound

# convert a vmess link into a config.json with some inbounds.
vmess2json.py --inbounds http:8123,socks:7070,mt:8888 -o /etc/v2ray/config.json vmess://ABCDEFGabcdefg123456...

# wirte multiple .json (per line)
cat vmess_list.txt | vmess2json.py --parse_all

# choose from an online subscribe source
vmess2json.py --subscribe https://vmess.subscribe.domian/sub.txt -o /etc/v2ray/config.json
```

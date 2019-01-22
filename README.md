# Vmess2Json

Simple script parses `vmess://` links into client v2ray config json.

Currently supports only V2rayN/NG links.

## Usage
```
usage: vmess2json.py [-h] [-m] [-o OUTPUT] [vmess]

vmess2json convert vmess link to client json config.

positional arguments:
  vmess                 A vmess:// link. If absent, reads a line from stdin.

optional arguments:
  -h, --help            show this help message and exit
  -m, --multiple        read multiple lines from stdin, each write to a json
                        file named by remark, saving in current dir (PWD).
  -o OUTPUT, --output OUTPUT
                        write output to file. default to stdout
```

## Example
```
# manualy check on a link
echo "vmess://ABCDEFGabcdefg1234567890..." | vmess2json.py | vim -

# write one file
vmess2json.py -o /etc/v2ray/config.json vmess://ABCDEFGabcdefg1234567890...

# wirte multiple
cat vmess_list.txt | vmess2json.py -m

# parse a subscribe source
curl -L https://vmess.subscribe.domian/sub | base64 -d | vmess2json.py -m
```

## Reference
 * [V2Ray 一键安装脚本 by 233boy](https://github.com/233boy/v2ray)
 * [V2ray多用户管理脚本 by Jrohy](https://github.com/Jrohy/multi-v2ray)
 * [V2RayN by 2dust](https://github.com/2dust/v2rayN/blob/master/v2rayN/v2rayN/Handler/V2rayConfigHandler.cs)

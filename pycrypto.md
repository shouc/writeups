## PyCrypto Writeup

To begin with, there is a very easy crypto chall. By solving it with collision, we can get:

```
key = "ASIS2020_W3bcrypt_ChAlLeNg3!@#%^"
```

Then, leverage this vuln (https://github.com/trentm/python-markdown2/issues/348) to make `/ticket` to have XSS.

Finally, since we can only submit URL starts with `76.74.170.201`, an iframe of `http://127.0.0.1:8080/ticket` could be injected to 
`/ticket` to get to make sure we are at same origin with `http://127.0.0.1:8080/flag`. Yet, `/ticket` prevents
any connection on `127.0.0.1`. So we can conduct DNS rebinding:
```
[DOMAIN] => [127.0.0.1, 76.74.170.201]
```
Now using `http://[DOMAIN]/ticket` could get the flag. 

ASIS{Y0U_R3binded_DN5_f0r_SSRF}

Didn't get up early enough to solve the last part before it ends : (

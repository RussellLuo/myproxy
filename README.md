# MyProxy

An asynchronous and configurable proxy server implemented in Python.


## Installation

MyProxy requires Python 3.5 or later.

Install MyProxy with pip:

```
$ pip install MyProxy
```

Install development version from GitHub:

```
$ pip install -e git+https://github.com/RussellLuo/myproxy.git#egg=myproxy
```


## Getting started

Prepare a configuration file to add a header `Alpha: true` when requesting the path `/` of the domain `www.example.com`:

```
# myproxy.conf

server = www.example.com {
    location = / {
        set_header Alpha true;
    }
}
```

Run the proxy server:

```
$ myproxy -c myproxy.conf
Serving on ('0.0.0.0', 8080)
```

Send HTTP request via the proxy server:

```
$ http_proxy=localhost:8080 curl www.example.com
```

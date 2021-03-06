# This project is licensed under a Creative Commons Attribution-NonCommercial
# 3.0 Unported License available at
# http://creativecommons.org/licenses/by-nc/3.0/
# Permissions beyond the scope of this license may be available at <andre@laszlo.nu>

import http.client as httplib
import urllib.parse as urllib
import re
from html.entities import name2codepoint


class Browser:

    UA_DEFAULT = None
    UA_CHROME = "Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.475.0 Safari/534.3"
    MAX_RETRIES = 3

    def __init__(self, domain=None, user_agent=UA_DEFAULT, debug=False, https=False):
        self._cookie = None
        self._domain = domain
        self._ua = user_agent
        self._debug = debug
        self._https = https
        self._conn = None

    def _connect(self, domain=None):
        if domain is None:
            domain = self._domain
        if self._https:
            conn = httplib.HTTPConnection(domain)
        else:
            conn = httplib.HTTPSConnection(domain)
        self._conn = conn
        return conn

    def _print(self, *msg):
        if self._debug:
            print(*msg)

    def decode(self, html): # decode html entities
        return re.sub('&(%s);' % '|'.join(name2codepoint),
                      lambda m: chr(name2codepoint[m.group(1)]), html)

    def request(self, url, data=None, method="GET", retries=0):
        self._print("%s request '%s'" % (method, url))
        conn = self._connect()

        request_params = {'method' : method,
                          'url': url}

        # add headers
        headers = dict()
        if self._cookie is not None:
            headers["Cookie"] = self._cookie
        if self._ua is not None:
            headers['User-Agent'] = self._ua
        if headers:
            request_params['headers'] = headers

        if data is not None:
            body = "&".join(map(lambda x: x[0]+"="+urllib.quote_plus(x[1]), data.items()))
            request_params['body'] = body

        try:
            conn.request(**request_params)
        except Exception as e:
            if retries < self.MAX_RETRIES:
                self._print("Got exception %s, retrying (%s)" % (str(e), retries+1))
                return self.request(url, data, method, retries+1)
            else:
                raise e

        self._print("Request parameters:", str(request_params))
        f = open("request_params.txt", 'a')
        f.write("\n")
        f.write(str(request_params))
        f.close()

        response = conn.getresponse()
        data = response.read()
        cookie = response.getheader("Set-Cookie", "")
        if cookie:
            self._print("Got cookie:", str(cookie))
            self._cookie = cookie
        self._print("Response %s" % response.status)
        self._print("Data: %s" % len(data))
        conn.close()
        return (response, data)

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = False
        if value:
            self._debug = True

    def info(self):
        print("Domain:     ", self._domain)
        print("Connection: ", self._conn)
        print("Cookie:     ", str(self._cookie).replace(';', "\n" + " "*13))
        print("User-Agent: ", str(self._ua))

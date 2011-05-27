import http.client as httplib
from http.client import ResponseNotReady
import urllib.parse as urllib

class Browser:
    
    UA_DEFAULT = None
    UA_CHROME = "Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.475.0 Safari/534.3"
    MAX_RETRIES = 3

    def __init__(self, domain = None, user_agent = UA_DEFAULT):
        self._cookie = None
        self._domain = domain
        self._ua = user_agent

    def connect(self, domain = None):
        if domain == None:
            domain = self._domain
        conn = httplib.HTTPConnection(domain)
        self._conn = conn
        return conn

    def request(self, url, data = None, method="GET", retries=0):
        #print("%s request '%s'" % (method, url))
        conn = self.connect()

        request_params = {'method' : method,
                          'url': url}

        # add headers
        headers = dict()
        if self._cookie is not None:
            headers["Cookie"] = self._cookie
        if self._ua is not None:
            headers['User-Agent'] = self._ua
        if len(headers) > 0:
            request_params['headers'] = headers

        if data is not None:
            body = "&".join(map(lambda x: x[0]+"="+urllib.quote_plus(x[1]), data.items()))
            request_params['body'] = body

        try:
            conn.request(**request_params)
        except Exception as e:
            if retries < self.MAX_RETRIES:
                print("Got exception %s, retrying (%s)" % (str(e), retries+1))
                return self.request(url, data, method, retries+1)
            else:
                raise e

        #print("Request parameters:", str(request_params))
        f = open("request_params.txt", 'a')
        f.write("\n")
        f.write(str(request_params))
        f.close()

        response = conn.getresponse()
        data = response.read()
        cookie = response.getheader("Set-Cookie","")
        if cookie:
            print("Got cookie:", str(cookie))
            self._cookie = cookie
        #print("Response %s" % response.status)
        #print("Data: %s" % len(data))
        conn.close()
        return (response, data)

    def debug(self):
        print("Domain:     ", self._domain)
        print("Connection: ", self._conn)
        print("Cookie:     ", str(self._cookie).replace(';', "\n" + " "*13))
        print("User-Agent: ", str(self._ua))

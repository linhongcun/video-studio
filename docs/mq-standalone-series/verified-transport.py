"""Verified canonical HTTP adapter for Chromium in this managed environment.

No TLS bypass: urllib uses the configured system/proxy CA bundle. Chromium keeps
the canonical origin while Playwright fulfills its requests with those response
bytes. Range and Content-Type are forwarded, and APIRequestContext.get is routed
through the same verified transport. This is a QA adapter, not production code.
"""
from dataclasses import dataclass
import hashlib
import json
import threading
import urllib.error
import urllib.request


@dataclass
class VerifiedResponse:
    url: str
    status: int
    headers: dict
    data: bytes

    @property
    def ok(self):
        return 200 <= self.status < 300

    def body(self):
        return self.data

    def text(self):
        return self.data.decode('utf-8')

    def json(self):
        return json.loads(self.text())

    def dispose(self):
        pass


class VerifiedTransport:
    def __init__(self, origin='https://linhongcun.github.io', timeout=40):
        self.origin = origin.rstrip('/')
        self.timeout = timeout
        self.entries = []
        self.cache = {}
        self.lock = threading.RLock()
        self.pages = 0

    def get(self, url, *, headers=None, timeout=None, **unused):
        return self.fetch(url, method='GET', headers=headers, timeout=timeout)

    def fetch(self, url, *, method='GET', headers=None, timeout=None):
        if not (url == self.origin or url.startswith(self.origin + '/')):
            raise ValueError('VerifiedTransport only serves the configured canonical origin')
        if method not in {'GET', 'HEAD'}:
            raise ValueError('VerifiedTransport is read-only')
        lower = {k.lower(): v for k, v in (headers or {}).items()}
        request_headers = {'Accept-Encoding': 'identity'}
        for key in ['range', 'accept', 'accept-language']:
            if key in lower:
                request_headers[key] = lower[key]
        cache_key = (method, url, lower.get('range', ''))
        with self.lock:
            response = self.cache.get(cache_key)
        if response is not None:
            return response
        request = urllib.request.Request(url, method=method, headers=request_headers)
        # Playwright timeout is milliseconds; native urllib default is seconds.
        seconds = self.timeout if timeout is None else max(.1, timeout / 1000)
        try:
            remote = urllib.request.urlopen(request, timeout=seconds)
        except urllib.error.HTTPError as error:
            remote = error
        with remote:
            data = remote.read()
            # Response bytes retain their encoding; headers remain truthful.
            response_headers = {k.lower(): v for k, v in remote.headers.items()
                                if k.lower() not in {'connection', 'transfer-encoding'}}
            response = VerifiedResponse(remote.geturl(), remote.status, response_headers, data)
        if not response.url.startswith(self.origin + '/'):
            raise ValueError('Unexpected redirect away from canonical origin')
        with self.lock:
            self.cache[cache_key] = response
            self.entries.append({
                'url': url, 'finalUrl': response.url, 'method': method,
                'range': lower.get('range'), 'status': response.status,
                'contentType': response.headers.get('content-type'),
                'contentRange': response.headers.get('content-range'),
                'acceptRanges': response.headers.get('accept-ranges'),
                'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                'tlsVerified': True,
            })
        return response

    def install_page(self, page):
        def handle(route):
            request = route.request
            response = self.fetch(request.url, method=request.method,
                                  headers=request.headers)
            route.fulfill(status=response.status, headers=response.headers,
                          body=response.data)
        page.route(self.origin + '/**', handle)
        # Python Playwright wrappers allow instance method overrides. The actual
        # page.request context is stable for the lifetime of this page/context.
        page.request.get = self.get
        self.pages += 1
        return page

    def install_browser(self, browser):
        original = browser.new_page
        def new_page(*args, **kwargs):
            page = original(*args, **kwargs)
            return self.install_page(page)
        browser.new_page = new_page
        return self

    def report(self):
        return {'mode': 'Canonical-origin Chromium requests fulfilled with ordinary urllib GET/HEAD responses using the configured CA bundle; HTTPS verification was not disabled.',
                'pages': self.pages, 'networkResponses': len(self.entries),
                'rangeResponses': sum(x['status'] == 206 for x in self.entries),
                'responses': self.entries}


def install_verified_transport(page, **kwargs):
    transport = VerifiedTransport(**kwargs)
    transport.install_page(page)
    return transport


def install_browser_transport(browser, **kwargs):
    return VerifiedTransport(**kwargs).install_browser(browser)

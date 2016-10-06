import io
import logging
import urllib.parse

import aiohttp
import aiohttp.server


logger = logging.getLogger(__name__)


class ProxyProtocol(aiohttp.server.ServerHttpProtocol):

    def __init__(self, manipulation_rules, **kwargs):
        super().__init__(**kwargs)
        self.manipulation_rules = manipulation_rules

    def manipulate_request(self, message):
        url_parsed = urllib.parse.urlparse(message.path)
        domain = url_parsed.netloc
        path = url_parsed.path

        if domain in self.manipulation_rules:
            manipulation_headers = self.manipulation_rules[domain]
            if path in manipulation_headers:
                for field, value in manipulation_headers[path]:
                    message.headers[field] = value
        return message

    def manipulate_response(self, response):
        return response

    async def handle_request(self, message, payload):
        message = self.manipulate_request(message)

        method = message.method
        url = message.path
        headers = message.headers

        logger.info('{} {}'.format(method, url.lower()))

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers) as resp:
                proxy_resp = aiohttp.Response(self.writer,
                                              resp.status, resp.version)
                for header in resp.headers.items():
                    proxy_resp.add_header(*header)
                proxy_resp.send_headers()

                proxy_resp = self.manipulate_response(proxy_resp)

                while True:
                    chunk = await resp.content.read(io.DEFAULT_BUFFER_SIZE)
                    if not chunk:
                        break
                    proxy_resp.write(chunk)
                await proxy_resp.write_eof()

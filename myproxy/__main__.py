import argparse
import asyncio
import logging

from .confparser import parse
from .myproxy import ProxyProtocol


def run_proxy(host, port, manipulation_rules):
    loop = asyncio.get_event_loop()

    server_future = loop.create_server(
        lambda: ProxyProtocol(manipulation_rules, debug=True),
        host, port
    )
    server = loop.run_until_complete(server_future)
    print('Serving on', server.sockets[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0',
                        help='hostname, defaults to "0.0.0.0"')
    parser.add_argument('--port', type=int, default=8080,
                        help='listen port, defaults to 8080')
    parser.add_argument('-l', '--log-level', default='INFO',
                        choices=('DEBUG', 'INFO', 'WARNING',
                                 'ERROR', 'CRITICAL'),
                        help='logging level, defaults to "INFO"')
    parser.add_argument('-c', '--config', default='myproxy.conf',
                        help='the path of configuration file, '
                             'defaults to "myproxy.conf"')
    args = parser.parse_args()

    manipulation_rules = parse(args.config)
    logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s',
                        level=args.log_level)
    run_proxy(args.host, args.port, manipulation_rules)


if __name__ == '__main__':
    main()

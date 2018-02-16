#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from thingview import app
import argparse
import os


if __name__ == '__main__':
    # parse argument
    parser = argparse.ArgumentParser(description='ThingView server')
    parser.add_argument('-b', '--bind', type=str, default='0.0.0.0',
                        help='bind address (default is "0.0.0.0")')
    parser.add_argument('-p', '--port', type=int, default=8080,
                        help='listen port')
    parser.add_argument('-k', '--secret-key', type=str, default=None,
                        help='secret key')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='set debug mode')
    args = parser.parse_args()
    # flask session secret-key
    if args.secret_key:
        app.secret_key = args.secret_key
    # auto-reload when templates dir is update
    if args.debug:
        extra_dirs = ['./thingview/templates',]
        extra_files = extra_dirs[:]
        for extra_dir in extra_dirs:
            for dirname, dirs, files in os.walk(extra_dir):
                for filename in files:
                    filename = os.path.join(dirname, filename)
                    if os.path.isfile(filename):
                        extra_files.append(filename)
    else:
        extra_files = []
    # define SSL
    ssl_ctx = ('/etc/iot.things.srv/ssl.cert', '/etc/iot.things.srv/ssl.key')
    # start flask with auto-reload
    app.run(host=args.bind, port=args.port, ssl_context=ssl_ctx, extra_files=extra_files, debug=args.debug)

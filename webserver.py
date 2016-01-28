#!/usr/bin/python2

import sys
import getopt

import BaseHTTPServer
from urllib import unquote_plus

from tatomecab import TatoMeCab

class TatoMecabHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    tatomecab = TatoMeCab()

    def log_request(code='-', size='-'):
        pass

    def xmlize(self, tokens):
        res = '<?xml version="1.0" encoding="UTF-8"?>\n<root>\n<parse>\n'
        for subtokens in tokens:
            res = res + '<token>'
            for kanjis, reading in subtokens:
                if reading is None:
                    res = res + '<![CDATA[' + kanjis + ']]>'
                else:
                    res = res + '<reading furigana="%s"><![CDATA[%s]]></reading>' % (reading, kanjis)
            res = res + '</token>\n'
        res = res + '</parse>\n</root>\n'
        return res

    def parse_query(self):
        d_args = {}
        method = self.path
        try:
            method, args = self.path.split('?', 1)
            for arg in args.split('&'):
                try:
                    var, val = arg.split('=', 1)
                except ValueError:
                    continue
                d_args[var] = unquote_plus(val)
        except ValueError:
            pass
        return method, d_args

    def do_GET(self):
        method, args = self.parse_query()
        if method == '/furigana':
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            try:
                parsed = self.tatomecab.parse(args['str'])
            except IndexError:
                self.send_error(400, "Parameter 'str' is mandatory.")
                return
            xml = self.xmlize(parsed)
            self.wfile.write(xml.encode('utf-8'))
        else:
            self.send_error(404, 'Service not found')

if __name__ == '__main__':
    host = "127.0.0.1"
    port = 8842
    opts, args = getopt.getopt(sys.argv[1:], 'h:p:')
    for opt, optarg in opts:
        if opt == '-h':
            host = optarg
        elif opt == '-p':
            port = int(optarg)

    httpd = BaseHTTPServer.HTTPServer((host, port), TatoMecabHandler)
    httpd.allow_reuse_address = True
    httpd.serve_forever()


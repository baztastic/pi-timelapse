#from SimpleHTTPServer import test, SimpleHTTPRequestHandler
#test(SimpleHTTPRequestHandler)
import sys
port=sys.argv[1]

if sys.version_info < (3, 0):
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from BaseHTTPServer import HTTPServer
else:
    from http.server import HTTPServer, SimpleHTTPRequestHandler

httpd = HTTPServer(("timelapse.local", int(port)), SimpleHTTPRequestHandler)
print("Serving HTTP on localhost port " + port + " (http://localhost:" + port + "/) ...")
httpd.serve_forever()

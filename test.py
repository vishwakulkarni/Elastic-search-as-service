import BaseHTTPServer, SimpleHTTPServer
import ssl

httpd = BaseHTTPServer.HTTPServer(('localhost', 4443), SimpleHTTPServer.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket (httpd.socket, certfile='/Users/i334502/Documents/elastic-search/elasticsearch-6.2.3/rootCA.pem', server_side=True)
httpd.serve_forever()
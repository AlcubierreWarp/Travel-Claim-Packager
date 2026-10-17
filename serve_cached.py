import http.server, functools, sys
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "max-age=600")  # like GitHub Pages
        super().end_headers()
    def log_message(self, *a): pass
# python serve_cached.py <folder> [port]   (test_live.py starts these for you)
http.server.ThreadingHTTPServer(("127.0.0.1", int(sys.argv[2]) if len(sys.argv) > 2 else 8767), functools.partial(H, directory=sys.argv[1])).serve_forever()

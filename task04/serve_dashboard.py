#!/usr/bin/env python3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os

def main():
    repo_root = Path(__file__).resolve().parents[1]
    os.chdir(repo_root)
    addr = ("0.0.0.0", 8000)
    print("Serving from:", repo_root)
    print("Open: http://localhost:8000/task04/dashboard/")
    ThreadingHTTPServer(addr, SimpleHTTPRequestHandler).serve_forever()

if __name__ == "__main__":
    main()

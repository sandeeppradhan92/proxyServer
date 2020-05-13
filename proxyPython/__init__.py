import json

from main import Proxy

config = {}


def start_server():
    with open("config.json", "r") as fo:
        config = json.load(fo)
    proxy = Proxy(config)
    proxy.run()


__all__ = [start_server]

start_server()

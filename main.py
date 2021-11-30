import json
import logging
import os
import sys

import asyncio
import time

import requests

import websockets

from generate import generate

args = sys.argv[1:]
sources = [
    {"minGroundSpacing": int(minGroundSpacing), "path": sourcePath}
    for minGroundSpacing, sourcePath in zip(args[::2], args[1::2])
]


async def main():
    while True:
        try:
            await server()
        except Exception as e:
            logging.exception(e)
            time.sleep(1)


async def server():
    async with websockets.connect("wss://layouts.painkillergis.com/v1/awaiting_heightmap") as ws:
        while True:
            await ws.send("")
            layout = json.loads(await ws.recv())
            heightmap = generate(sources, layout, 'JPEG')
            with open(heightmap, 'rb') as f:
                requests.put(f"https://layouts.painkillergis.com/v1/layouts/{layout['id']}/heightmap.jpg", f.read())
            os.remove(heightmap)
            os.remove(f"{heightmap}.aux.xml")
            await ws.send("")


asyncio.run(main())

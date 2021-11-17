import os
import sys

import requests
import time

from generate import generate

args = sys.argv[1:]
sources = [
    {"minGroundSpacing": int(minGroundSpacing), "path": sourcePath}
    for minGroundSpacing, sourcePath in zip(args[::2], args[1::2])
]


def main():
    while True:
        try:
            tick("https://layouts.painkillergis.com")
        except Exception as e:
            print("Failed to process heightmap", e, file=sys.stderr)
        time.sleep(2.5)


def tick(baseURL):
    response = requests.get(f"{baseURL}/v1/layouts?excludeLayoutsWithHeightmap=true")
    if response.status_code != 200:
        raise Exception(f"Got non-2xx status code: {response.status_code}")
    for layout in response.json():
        heightmap = generate(sources, layout)
        with open(heightmap, 'rb') as f:
            requests.put(f"{baseURL}/v1/layouts/{layout['id']}/heightmap.jpg", f.read())
        os.remove(heightmap)
        os.remove(f"{heightmap}.aux.xml")


main()

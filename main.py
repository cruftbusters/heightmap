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
        tick("https://layouts.painkillergis.com")
        time.sleep(2.5)


def tick(baseURL):
    try:
        response = requests.get(f"{baseURL}/v1/layouts?excludeLayoutsWithHeightmap=true")
        if response.status_code == 200:
            for layout in response.json():
                heightmap = generate(sources, layout)
                with open(heightmap, 'rb') as f:
                    requests.put(f"{baseURL}/v1/layouts/{layout['id']}/heightmap.jpg", f.read())
                os.remove(heightmap)
                os.remove(f"{heightmap}.aux.xml")
        else:
            print(
                "Failed to communicate with layout service",
                f"got status code: {response.status_code}",
                file=sys.stderr,
            )
    except requests.exceptions.RequestException as e:
        print("Failed to communicate with layout service", e, file=sys.stderr)


main()

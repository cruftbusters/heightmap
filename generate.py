import json
import sys
import tempfile

from osgeo import gdal, gdalconst


def generate(sourcePath, metadata):
    left = metadata['position']['left']
    top = metadata['position']['top']
    right = left + 10000
    bottom = top - 10000
    if left == 0 and top == 0:
        left = metadata['bounds']['left']
        top = metadata['bounds']['top']
        right = metadata['bounds']['right']
        bottom = metadata['bounds']['bottom']

    warp = tempfile.mktemp()
    translate = tempfile.mktemp()

    gdal.Warp(
        warp,
        sourcePath,
        options=gdal.WarpOptions(
            outputBounds=[left, top, right, bottom],
            outputBoundsSRS="EPSG:3857",
            width=metadata['size']['width'],
            height=metadata['size']['height'],
        )
    )

    warpSource = gdal.Open(warp)
    band = warpSource.GetRasterBand(1)
    stats = band.GetStatistics(True, True)
    minimum = stats[0]
    maximum = stats[1]

    gdal.Translate(
        translate,
        warp,
        options=gdal.TranslateOptions(
            format='JPEG',
            outputType=gdalconst.GDT_Byte,
            scaleParams=[[minimum, maximum, 0, 255]],
        )
    )

    return translate


if __name__ == "__main__":
    source = '/home/arctair/ws/cruftbusters/heightmap/3dep13/n46w106.img'
    with open(generate(source, json.load(sys.stdin)), 'rb') as f:
        sys.stdout.buffer.write(f.read())

import json
import os
import sys
import tempfile

from osgeo import gdal, gdalconst


def generate(sources, layout):
    width = layout['size']['width']
    height = layout['size']['height']
    left = layout['bounds']['left']
    top = layout['bounds']['top']
    right = layout['bounds']['right']
    bottom = layout['bounds']['bottom']

    sourcePath = selectSourceByGroundSpacing(
        sources,
        min((right - left) / width, (top - bottom) / height),
    )

    warpPath = f"/vsimem/{layout['id']}.warp.tif"
    gdal.Warp(
        warpPath,
        sourcePath,
        options=gdal.WarpOptions(
            outputBounds=[left, bottom, right, top],
            outputBoundsSRS="EPSG:3857",
            outputType=gdalconst.GDT_UInt16,
            width=width,
            height=height,
        )
    )

    warpSource = gdal.Open(warpPath)
    band = warpSource.GetRasterBand(1)
    stats = band.GetStatistics(True, True)
    minimum = stats[0]
    maximum = stats[1]

    preview = tempfile.mktemp()
    gdal.Translate(
        preview,
        warpSource,
        options=gdal.TranslateOptions(
            format="JPEG",
            outputType=gdalconst.GDT_Byte,
            scaleParams=[[minimum, maximum, 0, 255]],
        )
    )

    heightmap = tempfile.mktemp()
    gdal.Translate(
        heightmap,
        warpSource,
        options=gdal.TranslateOptions(
            format="GTiff",
            outputType=gdalconst.GDT_UInt16,
            scaleParams=[[minimum, maximum, 0, 65535]],
        )
    )

    del warpSource
    gdal.GetDriverByName('GTiff').Delete(warpPath)

    return [preview, heightmap]


def selectSourceByGroundSpacing(sources, groundSpacing):
    sourcePath = ''
    for source in sources:
        if groundSpacing >= source['minGroundSpacing']:
            sourcePath = source['path']
    if sourcePath == '':
        raise f'no suitable source for map with ground spacing = {groundSpacing}'
    else:
        return sourcePath


if __name__ == "__main__":
    sources = [
        {
            "minGroundSpacing": 0,
            "path": '/home/arctair/ws/cruftbusters/heightmap/3dep13/n46w106.img',
        },
        {
            "minGroundSpacing": 30,
            "path": '/home/arctair/ws/cruftbusters/heightmap/3dep1/n46w105.img',
        },
    ]
    [preview, heightmap] = generate(sources, json.load(sys.stdin))
    with open(heightmap, 'rb') as f:
        sys.stdout.buffer.write(f.read())
    os.remove(heightmap)
    os.remove(f"{heightmap}.aux.xml")

# Copyright 2019 Alistair Buxton <a.j.buxton@gmail.com>

# * License: This program is free software; you can redistribute it and/or
# * modify it under the terms of the GNU General Public License as published
# * by the Free Software Foundation; either version 3 of the License, or (at
# * your option) any later version. This program is distributed in the hope
# * that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.

from itertools import groupby


from PIL import ImageOps


class Polygon(object):
    def __init__(self):
        self._start = None
        self._end = None
        self._edges = []

    def insert(self, e):
        if e[0] == self._end or self._end is None:
            if self._start is None:
                self._start = e[0]
            self._edges.append(e)
            self._end = e[1]
            return True
        return False

    def closed(self):
        return self._start == self._end

    def build(self):
        edge_direction = lambda e: tuple(b - a for a, b in zip(*e))
        edges = [(g[0], next(g[1])) for g in groupby(self._edges, key=edge_direction)]
        points = [e[1][0] for e in edges[1:]]
        if edges[0][0] != edges[-1][0]:
            points.append(edges[0][1][0])
        return points


def outliner(orig_image):
    image = ImageOps.expand(orig_image, 1, 255)
    ix, iy = image.size
    data = image.load()

    edges = set()

    for y in range(iy):
        for x in range(ix):
            if data[x, y] == 0:
                pts = [(x,y), (x-1,y), (x-1,y-1), (x, y-1), (x, y)]
                for a, b in zip(pts, pts[1:]):
                    if (b, a) in edges:
                        edges.remove((b, a))
                    else:
                        edges.add((a, b))

    polys = []
    poly = Polygon()
    while edges:
        for e in edges:
            if poly.insert(e):
                edges.remove(e)
                if poly.closed():
                    polys.append(poly.build())
                    poly = Polygon()
                break
        else:
            raise Exception("Polygon could not be closed.")

    return polys

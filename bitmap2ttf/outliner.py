# Copyright 2019 Alistair Buxton <a.j.buxton@gmail.com>

# * License: This program is free software; you can redistribute it and/or
# * modify it under the terms of the GNU General Public License as published
# * by the Free Software Foundation; either version 3 of the License, or (at
# * your option) any later version. This program is distributed in the hope
# * that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.


from PIL import ImageOps


class PolygonBuilder(object):
    def __init__(self):
        self._edges = set()

    def add(self, edge):
        edge = tuple(sorted(edge))
        if edge in self._edges:
            self._edges.remove(edge)
        else:
            self._edges.add(edge)

    def build(self):
        edges = self._edges.copy()

        polys = []
        while edges:
            poly = []
            a, b = edges.pop()
            #TODO: implement the rest of this
            pass

        return polys


def outliner(orig_image):
    image = ImageOps.expand(orig_image, 1, 255)
    print(image)
    ix, iy = image.size
    data = image.load()

    pb = PolygonBuilder()

    for y in range(iy):
        for x in range(ix):
            if data[x, y] == 0:
                pts = [(x,y), (x+1,y), (x+1,y+1), (x, y+1), (x, y)]
                for a, b in zip(pts, pts[1:]):
                    pb.add((a, b))

    return pb.build()

# Copyright 2019 Alistair Buxton <a.j.buxton@gmail.com>

# * License: This program is free software; you can redistribute it and/or
# * modify it under the terms of the GNU General Public License as published
# * by the Free Software Foundation; either version 3 of the License, or (at
# * your option) any later version. This program is distributed in the hope
# * that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.

from collections import defaultdict

from PIL import ImageOps


def outliner(orig_image):
    image = ImageOps.expand(orig_image, 1, 255)
    ix, iy = image.size
    data = image.load()

    edges = set()

    for y in range(iy):
        for x in range(ix):
            if data[x, y] == 0:
                pts = [(x,y), (x+1,y), (x+1,y+1), (x, y+1), (x, y)]
                for a, b in zip(pts, pts[1:]):
                    if (b, a) in edges:
                        edges.remove((b, a))
                    else:
                        edges.add((a, b))

    polys = defaultdict(list)
    for a, b in edges:
        polys[a].append(b)
        polys[b] = polys[a]
        del polys[a]

    print(list(polys.values()))

    return list(polys.values())

try:
    from PIL import Image, ImageOps
except ImportError:
    import Image, ImageOps

# ccw & intersect from:
# http://www.bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
# Note: does not handle colinearity, but does not matter here because our 
# polygons are grid aligned and we can choose a test line which is not.

# Everything else:

# Copyright 2011 Alistair Buxton <a.j.buxton@gmail.com>

# * License: This program is free software; you can redistribute it and/or
# * modify it under the terms of the GNU General Public License as published
# * by the Free Software Foundation; either version 3 of the License, or (at
# * your option) any later version. This program is distributed in the hope
# * that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.

def ccw(A,B,C):
    return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def inside(A, polygon):
    B = (-0.5,A[1])
    count = 0
    for i in range(len(polygon)):
        C = polygon[i]
        D = polygon[(i+1)%len(polygon)]
        if intersect(A,B,C,D):
            count +=1
    return count&1 == 1

def invert_pixels(image, polygon):
    (x, y) = image.size
    data = image.load()
    for py in range(y):
        for px in range(x):
            if inside((px+0.5, py+0.5), polygon):
                data[px,py] ^= 255

def find_first(image):
    (x, y) = image.size
    data = image.load()
    for py in range(y):
        for px in range(x):
            if data[px,py] == 0:
                return (px,py)
    # not found...
    return (-1, -1)

def outliner(orig_image):
    orig_data = orig_image.load()
    image = ImageOps.expand(orig_image, 1, 255)
    
    polygons = []

    ds = [(1,0), (0,1), (-1,0), (0,-1)]
    ns = [(0,0), (-1,0), (-1,-1), (0,-1)]

    data = image.load()

    while True:
        polygon = []
        d = 0
        (px, py) = find_first(image)
        if (px, py) == (-1, -1):
            # no more black pixels, terminate
            return polygons
        polygon.append((px, py))
        done = False
        while not done:
            (x,y) = map(sum, zip((px,py),ns[d]))
            (x1,y1) = map(sum, zip((px,py),ns[(d+3)%4]))
            nextr = data[x,y]
            nextl = data[x1,y1]
            if nextl == nextr:
                polygon.append((px,py))
                if nextr > 0:   # both white, turn right
                    d = (d+1)%4
                else:           # both black, turn left
                    d = (d+3)%4

                (px,py) = map(sum, zip((px,py),ds[d]))

            else:
                if nextl > 0:   # left white, right black - go straight
                    (px,py) = map(sum, zip((px,py),ds[d])) # dont append
                else: # turning dilemma, go ... left
                    polygon.append((px, py))
                    d = (d+3)%4
                    (px,py) = map(sum, zip((px,py),ds[d]))
            if (px, py) == polygon[0]:
                done = True

        invert_pixels(image, polygon)

        polygons.append([tuple(map(sum, zip(x,(-1,-1)))) for x in polygon])


if __name__ == '__main__':
    import sys
    image = Image.open(sys.argv[1]).convert("L")
    polygons = outliner(image)
    data = image.load()
    for p in polygons:
        print p


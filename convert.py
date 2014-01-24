#! /usr/bin/env python

# licenced GPL v2
# Copyright (c) 2010 Kyle Keen
# Copyright (c) 2011 Alistair Buxton <a.j.buxton@gmail.com>

# * License: This program is free software; you can redistribute it and/or
# * modify it under the terms of the GNU General Public License as published
# * by the Free Software Foundation; either version 3 of the License, or (at
# * your option) any later version. This program is distributed in the hope
# * that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.

import tempfile, os, subprocess, shutil, optparse
try:
    from PIL import Image, ImageChops, ImageOps
except ImportError:
    import Image, ImageChops, ImageOps
from itertools import *
from math import sqrt, floor, ceil

join = os.path.join
basename = os.path.basename
splitext = os.path.splitext

import sys

from outliner import outliner

# requires Python Image Library, Fontforge

def xml_wrap(tag, inner, **kwargs):
    kw = ' '.join('%s="%s"' % (k, str(v)) for k,v in kwargs.items())
    if inner is None:
        return '<%s %s/>' % (tag, kw)
    return '<%s %s>%s</%s>\n' % (tag, kw, inner, tag)

def path(polys, xdim, ydim, par):
    d = ""
    for poly in polys:
        d += 'M '+ 'L '.join(['%d %d ' % (int(x*par*1000.0/ydim),int(y*1000.0/ydim)) for (x,y) in poly]) + 'Z\n'

    fill = 'currentColor'

    return xml_wrap('path', None, d=d, fill=fill)

def path_to_svg(polys, xdim, ydim, par):
    xml_path = path(polys, xdim, ydim, par)
    svg = ''
    svg = svg + xml_path
    svg = xml_wrap('svg', svg, width=par*xdim*1000.0/ydim, height=1000)
    svg = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/SVG/DTD/svg10.dtd">\n' + svg
    svg = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + svg
    return svg

def call_status(cmd):
    "returns exit status"
    spp = subprocess.PIPE
    return subprocess.Popen(cmd, shell=True, stdout=spp, stderr=spp).wait()


def convert(glyphs, name, par=1):

    ttf = name+'.ttf'
    path = tempfile.mkdtemp()
    print path

    for i,v in glyphs.iteritems():
        img = ImageOps.invert(v.convert("L"))
        polygons = outliner(img)
        (xdim, ydim) = img.size
        svg = path_to_svg(polygons, xdim, ydim, par)
        open(join(path, '%05d.svg' % i), 'w').write(svg)

    pe = open(join(path, ttf+'.pe'), 'w')
    pe.write('New()\n')
    pe.write('SetFontNames("%s", "%s", "%s")\n' % (name, name, name))
    pe.write('SetTTFName(0x409, 1, "%s")\n' % name)
    pe.write('SetTTFName(0x409, 2, "Medium")\n')
    pe.write('SetTTFName(0x409, 4, "%s")\n' % name)
    pe.write('SetTTFName(0x409, 5, "1.0")\n')
    pe.write('SetTTFName(0x409, 6, "%s")\n' % name)
    pe.write('Reencode("unicode")\n')

    for i,v in glyphs.iteritems():
        (xdim, ydim) = v.size
        pe.write('SelectSingletons(UCodePoint(%d))\n' % i)
        pe.write('Import("%s/%05d.svg", 0)\n' % (path, i))
        pe.write('SetWidth(%d)\n' % int(par*xdim*1000/ydim))
        pe.write('SetVWidth(1000)\n')

    print xdim, ydim

    #pe.write('Save("%s")\n' % ttf)
    pe.write('Generate("%s")\n' % ttf)
    pe.close()

    call_status('fontforge -script %s' % join(path, ttf+'.pe'))
    shutil.rmtree(path)

    print ttf



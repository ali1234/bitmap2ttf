# licenced GPL v2
# Copyright (c) 2010 Kyle Keen
# Copyright (c) 2011-2019 Alistair Buxton <a.j.buxton@gmail.com>

# * License: This program is free software; you can redistribute it and/or
# * modify it under the terms of the GNU General Public License as published
# * by the Free Software Foundation; either version 3 of the License, or (at
# * your option) any later version. This program is distributed in the hope
# * that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.

import os
import shutil
import subprocess
import tempfile
from functools import wraps

import click
from PIL import ImageOps


from tqdm import tqdm

from .outliner import outliner


def xml_wrap(tag, inner, **kwargs):
    kw = ' '.join('%s="%s"' % (k, str(v)) for k,v in kwargs.items())
    if inner is None:
        return '<%s %s/>' % (tag, kw)
    return '<%s %s>%s</%s>\n' % (tag, kw, inner, tag)


def path(polys, xdim, ydim, par):
    d = '\n'.join(
        'M ' + 'L '.join(
            '%d %d ' % (int(x * par * 1000.0 / ydim), int(y * 1000.0 / ydim)) for (x, y) in poly
        ) + 'Z' for poly in polys
    )
    return xml_wrap('path', None, d=d, fill='currentColor')


def path_to_svg(polys, xdim, ydim, par):
    return '\n'.join([
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/SVG/DTD/svg10.dtd">',
        xml_wrap('svg', path(polys, xdim, ydim, par), width=par * xdim * 1000.0 / ydim, height=1000),
    ])


def convert(glyphs, name, par=1):

    ttf = name
    path = tempfile.mkdtemp()

    pe = open(os.path.join(path, ttf+'.pe'), 'w')
    pe.write('New()\n')
    pe.write('SetFontNames("%s", "%s", "%s")\n' % (name, name, name))
    pe.write('SetTTFName(0x409, 1, "%s")\n' % name)
    pe.write('SetTTFName(0x409, 2, "Medium")\n')
    pe.write('SetTTFName(0x409, 4, "%s")\n' % name)
    pe.write('SetTTFName(0x409, 5, "1.0")\n')
    pe.write('SetTTFName(0x409, 6, "%s")\n' % name)
    pe.write('Reencode("unicode")\n')

    for i,v in tqdm(glyphs.items()):
        img = ImageOps.invert(v.convert("L"))
        polygons = outliner(img)
        (xdim, ydim) = img.size
        svg = path_to_svg(polygons, xdim, ydim, par)
        open(os.path.join(path, '%04x.svg' % i), 'w').write(svg)

        pe.write('SelectSingletons(UCodePoint(%d))\n' % i)
        pe.write('Import("%s/%04x.svg", 0)\n' % (path, i))
        pe.write('SetWidth(%d)\n' % int(par*xdim*1000/ydim))
        pe.write('SetVWidth(1000)\n')

    pe.write('Generate("%s")\n' % ttf)
    pe.close()

    subprocess.check_call(['fontforge', '-script', os.path.join(path, ttf+'.pe')])
    shutil.rmtree(path)


def converter(f):
    @click.argument('ttf', type=click.Path(exists=False), required=True)
    @wraps(f)
    def _convert(ttf, *args, **kwargs):
        convert(f(*args, **kwargs), ttf)
    return _convert


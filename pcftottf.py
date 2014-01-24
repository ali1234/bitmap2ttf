#!/usr/bin/env python

# * Copyright 2011 Alistair Buxton <a.j.buxton@gmail.com>
# *
# * License: This program is free software; you can redistribute it and/or
# * modify it under the terms of the GNU General Public License as published
# * by the Free Software Foundation; either version 3 of the License, or (at
# * your option) any later version. This program is distributed in the hope
# * that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.

try:
    from PIL.PcfFontFile import *
except ImportError:
    from PcfFontFile import *

class PcfFontFileUnicode(PcfFontFile):
    def __init__(self, fp):

        magic = l32(fp.read(4))
        if magic != PCF_MAGIC:
            raise SyntaxError, "not a PCF file"

        FontFile.FontFile.__init__(self)

        count = l32(fp.read(4))
        self.toc = {}
        for i in range(count):
            type = l32(fp.read(4))
            self.toc[type] = l32(fp.read(4)), l32(fp.read(4)), l32(fp.read(4))

        self.fp = fp

        self.info = self._load_properties()

        metrics = self._load_metrics()
        bitmaps = self._load_bitmaps(metrics)
        encoding = self._load_encoding()

        # recreate glyph structure

        self.glyph = {}

        c = 0
        cu = 0

        for ch,ix in encoding.iteritems():
            if ix is not None:
                x, y, l, r, w, a, d, f = metrics[ix]
                glyph = (w, 0), (l, d-y, x+l, d), (0, 0, x, y), bitmaps[ix]
                c += 1
                if ch > 256:
                    cu += 1
                self.glyph[ch] = glyph

        print c, "glyphs,", cu, "unicode."

    def _load_encoding(self):

        # map character code to bitmap index
        encoding = {}

        fp, format, i16, i32 = self._getformat(PCF_BDF_ENCODINGS)

        firstCol, lastCol = i16(fp.read(2)), i16(fp.read(2))
        firstRow, lastRow = i16(fp.read(2)), i16(fp.read(2))

        default = i16(fp.read(2))

        nencoding = (lastCol - firstCol + 1) * (lastRow - firstRow + 1)

        for i in range(nencoding):
            encodingOffset = i16(fp.read(2))
            if encodingOffset != 0xFFFF:
                try:
                    encoding[i+firstCol] = encodingOffset
                except IndexError:
                    break # only load ISO-8859-1 glyphs

        return encoding


if __name__ == '__main__':
    import sys
    from convert import convert
    for filename in sys.argv[1:]:
        p = PcfFontFileUnicode(file(filename))
        glyphmap = {}
        for k,v in p.glyph.iteritems():
            glyphmap[k] = v[3]
        convert(glyphmap, filename[:-4])

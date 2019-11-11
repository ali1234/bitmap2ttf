Bitmap2ttf converts (monochrome) bitmap fonts into ttf fonts.

There are three parts:

outliner.py:
  - Traces each bitmap into a series of polygons.

convert.py:
  - makes the polygons into svg files, and writes a script for font forge
    to convert the svgs into a ttf font.

loader of your choice/implementation:
  - currently there is only one loader:

    pcftotty.py:
      - loader for PCF bitmap fonts. 
        usage: ./pcftottf.py font.pcf

    amigatottf.py
      - loader for amiga diskfonts (eg topaz)
        usage: ./amigatottf.py topaz/11
        Amiga diskfonts are multiple files in a directory. 
        The output will be named after the directory.

The program is structured to make it easy to implement a loader for a font 
format of your choice. All you need is to supply a dict object to convert.py
which contains contains the key=>value pairs: 

character unicode value => Image

Scaling

When a ttf font is displayed at a certain size, that size is the vertical
size from the top of the tallest character to the bottom of the lowest
descender. It is not usually possible to set the character width independently.

Assuming a fixed font with character bitmaps 20 tall and 12 wide, then
the resulting ttf should be set to 20px height. It will then be 12px wide
and the strokes will exactly line up to screen pixels. (Assuming device
pixel ratio is 1, but that is a whole other matter.)

However, there is a problem: many bitmap fonts are not designed for
square pixels. There are two situations where this is important:

1. When the font is designed for a half-height progressive screen mode
like 720x256. In a screen mode like this the pixels are twice as tall
as they are wide. When displayed on a modern computer they will appear
vertically squashed. This is easy to fix - just double the vertical
size of each character shape before conversions.

2. When the font is designed for a display system that doesn't use exactly
square pixels, such as PAL. In the PAL format, pixels are around 1.2 to 1.333
times wider than they are tall. Fonts like this will appear narrower than
they should on a modern PC. This can also be fixed by scaling the character
shapes. However, because the scaling factor is not an integer this leads
to a problem: suppose the character is 20x12 and you scale the width by 1.2.
1.2 * 12 = 14.4. Now the character won't fit horizontally on the pixel grid
when it is displayed at 20 pixels tall. This causes aliasing which makes
the font look bad. There isn't really any solution for this - you have
to choose whether you want the font to have pixel perfect outlines, or
whether a particular body of text should have the right aspect ratio.
Depending on the font renderer and intended purpose of the font, you
might get better results with one or the other.

The bitmap2ttf converters accept a horizontal and vertical scaling factor.
Note however that only the ratio between them is important. A font will
always be displayed 20px tall and with the horizontal width scaled to
match regardless of its internal dimensions. So scaling 2x in both directions
will have no visible effect on the resulting font.

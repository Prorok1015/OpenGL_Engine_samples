#!/usr/bin/env python3
"""Writes the textures of the card sample (engine issue #1197): card_face.png, card_back.png, card_frame.png.

Standard library only (zlib + struct write the PNGs), so the output is the same on every machine.
Run from anywhere: python3 card/tools/gen_card_textures.py [OUT_DIR]   (default: the card/ folder)

The colours are part of the CI check of the engine (tools/headless/check_card.sh, "Editor visual smoke (Linux)"):
- card_face.png:  opaque (alpha 255 everywhere: scene.frag discards alpha < 1), a red field with a yellow diamond;
- card_back.png:  opaque, dominant blue with a lighter blue lattice (the check looks for blue > red, green);
- card_frame.png: an opaque gold band at the border, then a gold strip whose alpha falls from 255 to 0, then a fully
                  transparent centre (alpha 0), so what lies behind the frame shows through it.

The layout of card/card_demo.desc that the engine's check_card.sh regions assume (keep both in sync): the editor's
Scene view camera sits at the origin looking down -Z (fov 60, vertical), the capture is about 1.79:1. Light: direction
(0, -0.3, -1), so the lit colours are close to the texture colours.
- "Card (face)"  at (-1.3, 0, -2.2), rotated 75 deg about X: face and front frame toward the camera; image x ~0.15-0.28.
- "Card (back)"  at ( 1.3, 0, -2.2), rotated -105 deg about X: back and back frame toward the camera; image x ~0.72-0.85.
- "Backdrop"     at (0, 0, -2.4), a green plane 2.0 x 1.8 (card_backdrop.mat.desc); image x ~0.30-0.70.
- "Frame probe"  at (0, 0, -2.2), a lone card_frame plane 1.0 x 1.4 in front of the backdrop; image x ~0.39-0.61,
                 its transparent centre x ~0.43-0.57: the backdrop's green must show there.
- Nothing else: the corners of the image are the clear colour.
"""
import os
import struct
import sys
import zlib

WIDTH, HEIGHT = 256, 356

RED_FIELD = (200, 40, 50)
CREAM = (245, 235, 210)
YELLOW = (255, 215, 40)
BLUE = (35, 60, 180)
BLUE_LINE = (95, 135, 235)
GOLD = (235, 190, 60)

FRAME_BAND = 24      # opaque border, px
FRAME_FADE = 20      # alpha gradient strip inside the band, px


def write_png(path, width, height, pixel):
	"""pixel(x, y) -> (r, g, b, a); writes 8-bit RGBA, non-interlaced."""
	raw = bytearray()
	for y in range(height):
		raw.append(0)  # filter: none
		for x in range(width):
			raw.extend(pixel(x, y))

	def chunk(kind, data):
		body = kind + data
		return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

	ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
	png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
	with open(path, "wb") as out:
		out.write(png)


def face(x, y):
	cx, cy = (WIDTH - 1) / 2, (HEIGHT - 1) / 2
	# A thin cream line inside the edge, a yellow diamond in the middle and a small one in two corners.
	if 10 <= min(x, y, WIDTH - 1 - x, HEIGHT - 1 - y) <= 13:
		return (*CREAM, 255)
	if abs(x - cx) / 70 + abs(y - cy) / 105 <= 1:
		return (*YELLOW, 255)
	for px, py in ((40, 46), (WIDTH - 41, HEIGHT - 47)):
		if abs(x - px) / 14 + abs(y - py) / 20 <= 1:
			return (*YELLOW, 255)
	return (*RED_FIELD, 255)


def back(x, y):
	# A diagonal lattice, 3 px lines every 24 px: the field stays the dominant colour.
	if (x + y) % 24 < 3 or (x - y) % 24 < 3:
		return (*BLUE_LINE, 255)
	return (*BLUE, 255)


def frame(x, y):
	edge = min(x, y, WIDTH - 1 - x, HEIGHT - 1 - y)
	if edge < FRAME_BAND:
		alpha = 255
	elif edge < FRAME_BAND + FRAME_FADE:
		alpha = round(255 * (1 - (edge - FRAME_BAND + 1) / (FRAME_FADE + 1)))
	else:
		alpha = 0
	# The colour stays gold where alpha is 0 too, so linear filtering blends no dark fringe in.
	return (*GOLD, alpha)


def main():
	out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	for name, pixel in (("card_face.png", face), ("card_back.png", back), ("card_frame.png", frame)):
		path = os.path.join(out_dir, name)
		write_png(path, WIDTH, HEIGHT, pixel)
		print(f"wrote {path}")


if __name__ == "__main__":
	main()

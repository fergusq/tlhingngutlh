from tqdm import tqdm

import itertools
import os.path

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("variant", nargs="?", type=str, default="")
args = parser.parse_args()

FRONT_words = [
    "b",
    "ch",
    "D",
    "gh",
    "H",
    "j",
    "l",
    "m",
    "n",
    "ng",
    "p",
    "k",
    "Q",
    "r",
    "S",
    "t",
    "tlh",
    "v",
    "w",
    "y",
    "z"
]

MIDDLE_words = [
    "a",
    "e",
    "I",
    "o",
    "u",
]

BACK_words = [
    "",
    "b",
    "ch",
    "D",
    "gh",
    "rgh",
    "H",
    "j",
    "l",
    "m",
    "n",
    "ng",
    "p",
    "k",
    "Q",
    "r",
    "S",
    "t",
    "tlh",
    "v",
    "w",
    "wz",
    "y",
    "yz",
    "z"
]

HORIZONTAL_CONSONANTS = {"gh", "y", "yz"}
HORIZONTAL_VOWELS = {"I", "u"}
VERTICAL_CONSONANTS = {"b", "n", "v", "H", "m"}

missing = set()

words = [f+m+b for f, m, b in itertools.product(FRONT_words, MIDDLE_words, BACK_words)]
#words = ["ghun"]

import fontforge
import psMat

font = fontforge.font()

def createGlyph(i, name, filename):
	glyph = font.createChar(i, name)
	glyph.width = glyph.vwidth = 1000
	glyph.importOutlines(filename)
	return glyph

mapping = {
	"lainausmerkki1": 0xF8FB,
	"lainausmerkki2": 0xF8FC,
	"piste": 0xF8FE,
	"pilkku": 0xF8FD,
}

glyphs = []

i = 0xF0000
for word in tqdm(words):
	mapping[word] = i
	name = "KLINGON WORD " + word.replace("k", "q").replace("Q", "QH").upper()
	filename = f"lopulliset/{word}.svg"
	glyphs.append(createGlyph(i, name, filename))
	i += 1

i = 0xF8D0
for word in ["a", "b", "ch", "D", "e", "gh", "H", "I", "j", "l", "m", "n", "ng", "o", "p", "k", "Q", "r", "S", "t", "tlh", "u", "v", "w", "y", "z"]:
	mapping[word] = i
	name = "KLINGON LETTER " + word.replace("k", "q").replace("Q", "QH").upper()
	filename = f"lopulliset/{word}.svg"
	glyphs.append(createGlyph(i, name, filename))
	i += 1
	
createGlyph(0xF8FB, "KLINGON TOP QUOTATION MARK", "lopulliset/lainausmerkki1.svg")
createGlyph(0xF8FC, "KLINGON BOTTOM QUOTATION MARK", "lopulliset/lainausmerkki2.svg")
createGlyph(0xF8FD, "KLINGON COMMA", "lopulliset/pilkku.svg")
createGlyph(0xF8FE, "KLINGON FULL STOP", "lopulliset/piste.svg")

font.correctDirection()

contour = None
n = 0

def near(a, b):
	return abs(a-b) <= 5

def nextPoint(j):
	return contour[(i+j)%n]

def setPoint(j, p):
	if isinstance(p, tuple):
		if p[0] is None:
			p = (nextPoint(j).x, p[1])
		
		if p[1] is None:
			p = (p[0], nextPoint(j).y)

	contour[(i+j)%n] = p

def nextPoints(js):
	return [nextPoint(j) for j in js]

variant = args.variant

if variant == "mIng":
	for glyph in tqdm(list(font.glyphs())):
		if glyph.glyphname in {"KLINGON COMMA", "KLINGON FULL STOP", "KLINGON TOP QUOTATION MARK", "KLINGON BOTTOM QUOTATION MARK"}:
			continue

		for key in glyph.layers:
			layer = glyph.layers[key]
			for c_id, contour in enumerate(layer):
				i = 0
				n = len(contour)
				while i < n:
					if not contour[i].on_curve:
						i += 1
						continue
					
					# Tee päätteet yläreunaan
					if all([p.on_curve for p in nextPoints([1, 2, 3, 4])]) and \
						contour[i].y < nextPoint(1).y and near(contour[i].x, nextPoint(1).x) and \
						near(nextPoint(1).y, nextPoint(2).y) and nextPoint(1).x < nextPoint(2).x and \
						near(nextPoint(2).y, nextPoint(3).y) and nextPoint(2).x < nextPoint(3).x and \
						nextPoint(3).y > nextPoint(4).y and near(nextPoint(3).x, nextPoint(4).x) and \
						50 <= abs(nextPoint(1).x - nextPoint(3).x) <= 70:
						
						setPoint(2, (None, nextPoint(2).y - 15))
						
						i += 3
					
					# Tee päätteet alareunaan
					if all([p.on_curve for p in nextPoints([1, 2, 3, 4])]) and \
						contour[i].y > nextPoint(1).y and near(contour[i].x, nextPoint(1).x) and \
						near(nextPoint(1).y, nextPoint(2).y) and nextPoint(1).x > nextPoint(2).x and \
						near(nextPoint(2).y, nextPoint(3).y) and nextPoint(2).x > nextPoint(3).x and \
						nextPoint(3).y < nextPoint(4).y and near(nextPoint(3).x, nextPoint(4).x) and \
						50 <= abs(nextPoint(1).x - nextPoint(3).x) <= 70:
						
						setPoint(2, (None, nextPoint(2).y - 15))
						
						i += 3
					
					y = contour[i].y
					
					nar = False
					if nextPoint(1).on_curve and near(nextPoint(1).y, y) and nextPoint(1).x > contour[i].x:
						nar = True
						contour[i] = (contour[i].x, y-20)
					#	if nextPoint(-1).on_curve and nextPoint(-2).on_curve and \
					#		nextPoint(-1).y > y-20 and nextPoint(-2).y < y-20 and \
					#		near(contour[i].x, nextPoint(-1).x) and near(nextPoint(-1).x, nextPoint(-2).x):
					#		setPoint(-1, (None, nextPoint(-1).y-20))
					elif not nextPoint(1).on_curve and nextPoint(1).x > contour[i].x:
						contour[i] = (contour[i].x, y-20)
						setPoint(1, (nextPoint(1).x, nextPoint(1).y-20, False))
						if not nextPoint(-1).on_curve and nextPoint(-1).x < contour[i].x:
							setPoint(-1, (nextPoint(-1).x, nextPoint(-1).y-10, False))
							
					
					# Kavenna vaakaviivoja
					while nextPoint(1).on_curve and near(nextPoint(1).y, y) and nextPoint(1).x > contour[i].x:
						setPoint(1, (None, y-20))
						i += 1
					
					#if nar and nextPoint(1).on_curve and nextPoint(2).on_curve and \
					#	nextPoint(1).y > contour[i].y and nextPoint(2).y < contour[i].y and \
					#	near(contour[i].x, nextPoint(1).x) and near(nextPoint(1).x, nextPoint(2).x):
					#	setPoint(1, (None, nextPoint(1).y-20))
					
					i -= 1
					
					# Tee päätteet oikeaan reunaan
					if all([p.on_curve for p in nextPoints([1, 2, 3, 4])]) and \
						near(nextPoint(1).y, contour[i].y) and contour[i].x < nextPoint(1).x and \
						nextPoint(1).y > nextPoint(2).y and near(nextPoint(1).x, nextPoint(2).x) and \
						nextPoint(2).y > nextPoint(3).y and near(nextPoint(2).x, nextPoint(3).x) and \
						near(nextPoint(3).y, nextPoint(4).y) and nextPoint(3).x > nextPoint(4).x and \
						30 <= abs(nextPoint(1).y - nextPoint(3).y) <= 50:
						
						if abs(contour[i].x - nextPoint(1).x) > 80:
							setPoint(1, (nextPoint(1).x - 80, None))
							setPoint(2, (nextPoint(2).x - 45, None))
							setPoint(2, (None, nextPoint(2).y + 40))
						else:
							setPoint(2, (nextPoint(2).x + 15, None))
						
						i += 1
					
					# Tee päätteet vasempaan reunaan
					if all([p.on_curve for p in nextPoints([1, 2, 3, 4])]) and \
						near(nextPoint(1).y, contour[i].y) and contour[i].x > nextPoint(1).x and \
						nextPoint(1).y < nextPoint(2).y and near(nextPoint(1).x, nextPoint(2).x) and \
						nextPoint(2).y < nextPoint(3).y and near(nextPoint(2).x, nextPoint(3).x) and \
						near(nextPoint(3).y, nextPoint(4).y) and nextPoint(3).x < nextPoint(4).x and \
						30 <= abs(nextPoint(1).y - nextPoint(3).y) <= 50:
						
						setPoint(2, (nextPoint(2).x + 15, None))
						
						i += 1
					
					i += 2
				
				layer[c_id] = contour
				
			glyph.layers[key] = layer

if variant:
	variant = " " + variant

font.fontname = "tlhIngngutlh-HanDI'" + variant.replace(" ", "-")
font.familyname = "tlhIngngutlh HanDI'" + variant
font.fullname = "tlhIngngutlh HanDI'" + variant
font.copyright = "Copyright (c) 2020, Kaneli Kalliokoski and Iikka Hauhio"

font.generate(f"tlhIngngutlh HanDI'{variant}.ttf")

import json
with open("mapping.json", "w") as f:
	json.dump(mapping, f)


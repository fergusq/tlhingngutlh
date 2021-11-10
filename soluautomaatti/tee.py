import sys
from threading import Thread
import imageio
import numpy as np
from tqdm.cli import tqdm
import multiprocessing

def irange(a, b, s=1) -> range:
    return range(a, b+1 if s > 0 else b-1, s)

def parseImage(filename, ans, wspans):
    img = imageio.imread(filename)

    def detectSpans(img, dir, small, replace, ans):
        stopcol = False
        yn, xn, _an = img.shape
        for i in (irange(0, yn-1) if dir == "^" else
                irange(0, xn-1) if dir == "<" else
                irange(yn-1, 0, -1) if dir == "v" else
                irange(xn-1, 0, -1)):
            spans = []
            spanstart = -1
            for j in range(xn) if dir in "^v" else range(yn):
                if dir in "^v":
                    x, y = j, i
                
                else:
                    x, y = i, j
                
                if (x, y) not in ans and img[y, x, 3]:
                    ans[(x, y)] = "#"

                if stopcol:
                    continue

                if img[y, x, 3] and spanstart == -1:
                    spanstart = j
                
                elif not img[y, x, 3] and spanstart != -1:
                    spans.append((spanstart, j))
                    spanstart = -1

            if not stopcol and spans:
                
                if dir in "<>" and "w_" in filename:
                    cspans = spans

                elif dir in "<>":
                    cspans = [spans[-1]]
                
                else:
                    cspans = [spans[0]]

                if small:
                    c = lambda l: l > 5 and l < 20
                else:
                    c = lambda l: l > 30
                
                for span in cspans:
                    if c(span[1] - span[0]):
                        if not small:
                            span = span[0]+15, span[1]-15
                        
                        wspan = []

                        for j in range(span[0], span[1]):
                            if dir in "^v":
                                x, y = j, i
                            
                            else:
                                x, y = i, j
                            
                            ans[(x, y)] = replace
                            wspan.append((x, y))
                        
                        if small:
                            wspans.append(wspan)
                        
                        stopcol = True
                    
                # ignoraa o:n ja ng:n lyhyt yläviiva etsittäessä pitkiä viivoja
                if not small and dir in "<" and ("o_" in filename or "ng_" in filename):
                    continue
                
                stopcol = True

    detectSpans(img, "^", False, "%", ans)
    detectSpans(img, "v", False, "%", ans)
    detectSpans(img, ">", False, "%", ans)
    detectSpans(img, "<", False, "%", ans)
    if "D_" not in filename:
        detectSpans(img, "^", True, "^", ans)
        detectSpans(img, "v", True, "v", ans)
        if "o_" not in filename and "ng_" not in filename:
            detectSpans(img, ">", True, ">", ans)
            detectSpans(img, "<", True, "<", ans)
    
    return ans

img = imageio.imread("automaattimerkit/k_yv.svg.png")
yn, xn, _an = img.shape

def expand(ans, wspans):
    def findWall(x0, y0, dx, dy):
        x, y = x0, y0
        while x >= 0 and y >= 0 and x < xn and y < yn:
            x += dx
            y += dy
            if ans.get((x, y), " ") == "%":
                return True

            elif ans.get((x, y), " ") != " ":
                #print("Not found for ", x0, y0, dx, dy)
                return False
        
        else:
            #print("Not found for ", x0, y0, dx, dy)
            return False
    
    def fillToWall(x0, y0, dx, dy):
        x, y = x0, y0
        while ans.get((x, y), " ") != "%":
            ans[(x, y)] = "#"
            if ans.get((x-dx*16, y-dy*16), " ") == "%":
                ans[(x-dx*15, y-dy*15)] = "%"
            x += dx
            y += dy

    changed = True
    while changed:
        changed = False
        for wspan in wspans:
            x, y = wspan[0]
            if ans[(x, y)] == ">":
                dx, dy = 1, 0
            
            elif ans[(x, y)] == "<":
                dx, dy = -1, 0
            
            elif ans[(x, y)] == "^":
                dx, dy = 0, -1
            
            elif ans[(x, y)] == "v":
                dx, dy = 0, 1
            
            else:
                continue
            
            if all(findWall(x, y, dx, dy) for x, y in wspan):
                for x, y in wspan:
                    fillToWall(x, y, dx, dy)
                    changed = True

import itertools
import os.path

FRONT_words = [
    "b",
    "ch",
    "D",
    "gh",
    "H",
    "H",
    "j",
    "k",
    "l",
    "m",
    "n",
    "ng",
    "p",
    "q",
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
    "H",
    "j",
    "k",
    "l",
    "m",
    "n",
    "ng",
    "p",
    "q",
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

words = list(itertools.product(FRONT_words, MIDDLE_words, BACK_words))
#words = [("gh", "u", "n")]

def drawWord(f, m, b):
    if b == "":
        if f in VERTICAL_CONSONANTS:
            symbols = [f + "_kv", m + "_ko"]

        elif f in HORIZONTAL_CONSONANTS or m in HORIZONTAL_VOWELS:
            symbols = [f + "_ky", m + "_ka"]
        
        else:
            symbols = [f + "_kv", m + "_ko"]
    
    elif f in HORIZONTAL_CONSONANTS and m in HORIZONTAL_VOWELS and b in HORIZONTAL_CONSONANTS:
        symbols = [f + "_yy", m + "_kk", b + "_aa"]
    
    elif f in HORIZONTAL_CONSONANTS:
        symbols = [f + "_ky", m + "_av", b + "_ao"]
    
    elif b in HORIZONTAL_CONSONANTS:
        symbols = [f + "_yv", m + "_yo", b + "_ka"]
    
    elif f in VERTICAL_CONSONANTS:
        symbols = [f + "_kv", m + "_yo", b + "_ao"]
    
    elif b in VERTICAL_CONSONANTS:
        symbols = [f + "_yv", m + "_av", b + "_ko"]
    
    else:
        symbols = [f + "_kv", m + "_yo", b + "_ao"]
    
    files = []
    for symbol in symbols:
        file = f"automaattimerkit/{symbol}.svg.png"
        if not os.path.isfile(file):
            missing.add(file)
        
        else:
            files.append(file)

    ans = {}
    wspans = []
    for file in files:
        parseImage(file, ans, wspans)
    
    expand(ans, wspans)

    arr = np.zeros((yn, xn, 4), dtype=np.uint8)

    for y in range(yn):
        if len(words) == 1: print("%4d" % (y), end="")
        for x in range(xn):
            if (x, y) in ans:
                if len(words) == 1: print(ans[(x, y)], end="")
                arr[(y, x, 3)] = 255
            else:
                if len(words) == 1: print(" ", end="")
        
        if len(words) == 1: print()

    imageio.imwrite(f"generoidut/{f}{m}{b}.png".replace("q", "Q"), arr)

if len(words) == 1:
    drawWord(*words[0])
    sys.exit(0)

from tqdm.contrib.concurrent import process_map

def dw(w): drawWord(*w)

process_map(dw, words, max_workers=8, chunksize=3)

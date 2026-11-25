#!/bin/bash
# deploy.sh [startup] - build the FORTH beta disk from build/ products.
# "startup" also puts STARTUP on the disk, so it turnkeys.
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
BUILD="$ROOT/build"
CP2="D:/cp2_1.2.0_win-x64_sc/cp2.exe"
IMG="D:/AppleWin1.32.0.0/FORTH.po"
SRCIMG="D:/AppleWin1.32.0.0/COBOL32.po"     # only for its copy of PRODOS
cd "$BUILD"
if tasklist 2>/dev/null | grep -qi applewin; then echo "AppleWin is running - not deploying"; exit 1; fi
rm -rf stage && mkdir -p stage
"$CP2" extract "$SRCIMG" PRODOS >/dev/null
mv PRODOS "stage/PRODOS#ff0000"
cp FORTH.SYSTEM "stage/FORTH.SYSTEM#ff2000"
cp FORTH.GFX    "stage/FORTH.GFX#060000"
cp FORTH.SND    "stage/FORTH.SND#060000"
cp SHAPES.SHP   "stage/SHAPES.SHP#060000"
cp TUNES.SND    "stage/TUNES.SND#060000"
txt () { sed 's/\r$//' "$1" | tr '\n' '\r' > "stage/$2#040000"; }   # ProDOS wants CR
txt "$ROOT/FORTH.WORDS.txt" FORTH.WORDS
txt "$ROOT/SAMPLE_01.txt" MATH
txt "$ROOT/SAMPLE_02.txt" MONEY
txt "$ROOT/SAMPLE_03.txt" SCREEN
txt "$ROOT/SAMPLE_04.txt" BITS
txt "$ROOT/SAMPLE_05.txt" SEQ
txt "$ROOT/SAMPLE_06.txt" MUSIC
txt "$ROOT/SAMPLE_07.txt" PADDLE
txt "$ROOT/CHOOSER.txt" CHOOSER
[ "$1" = "startup" ] && txt "$ROOT/STARTUP.txt" STARTUP
rm -f "$IMG"                       # fresh every time: no stale file can confuse a test
"$CP2" cdi "$IMG" 800k prodos >/dev/null
"$CP2" mv "$IMG" : FORTH >/dev/null          # ":" selects the volume itself
cd stage && "$CP2" add --overwrite --from-naps "$IMG" $(ls) >/dev/null
"$CP2" catalog "$IMG" | sed -n '2p'

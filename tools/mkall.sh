#!/bin/bash
# mkall.sh - assemble kernel, both modules and both data files.
# Run from anywhere: paths come from this script's own location.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
BUILD="$ROOT/build"
M32="D:/Merlin32/v1.2/Merlin32_v1.2_b2/Windows/Merlin32.exe"
mkdir -p "$BUILD" && cd "$BUILD" || exit 1
ok=1
asm () {   # asm <source> <output> <type> <where to put TYP/DSK>
  rm -f T.S "$2"
  cp "$ROOT/$1" T.S || { echo "missing $1"; ok=0; return; }
  if [ "$4" = "xc" ]; then
    python - "$2" "$3" <<'PY'
import sys
out,typ=sys.argv[1],sys.argv[2]
s=open('T.S',encoding='utf-8',errors='surrogateescape').read().split('\n')
i=[n for n,l in enumerate(s) if l.split(';')[0].strip().lower()=='xc'][0]
s[i+1:i+1]=[' typ '+typ,' dsk '+out]
open('T.S','w',encoding='utf-8',errors='surrogateescape').write('\n'.join(s))
PY
  else
    sed -i "1i\ typ $3\n dsk $2" T.S
  fi
  local r; r=$("$M32" -V . T.S 2>&1)
  if echo "$r" | grep -qE "\[Error\]|\[Bad |Can't find"; then
    echo "FAIL $2"; echo "$r" | grep -E "\[Error\]|\[Bad |Can't find" | head -3; ok=0
  else
    printf "  %-14s %6s bytes\n" "$2" "$(stat -c %s "$2")"
  fi
}
asm TEST038.S.txt    FORTH.SYSTEM '$ff' xc
asm FORTH.GFX.S.txt  FORTH.GFX    '$06' xc
asm FORTH.SND.S.txt  FORTH.SND    '$06' xc
asm SHAPES.SHP.S.txt SHAPES.SHP   '$06' top
asm TUNES.SND.S.txt  TUNES.SND    '$06' top
rm -f T.S
[ $ok = 1 ] && echo "  all assembled" || { echo "  ASSEMBLY FAILED"; exit 1; }

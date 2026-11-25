#!/bin/bash
# mk8.sh - regenerate merlin8/ and prove it is the same program.
#
# Merlin 8 cannot load a source file over about 24K, so the kernel and
# the graphics module are split into PUT segments for assembly on the
# Apple.  merlin8/ is a BUILD PRODUCT: this script rewrites it from the
# single-file sources every time, so the two can never drift.
#
# It then assembles the split version and compares the objects with the
# ones tools/mkall.sh builds from the monolithic sources.  They must be
# byte for byte the same.
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
M32="D:/Merlin32/v1.2/Merlin32_v1.2_b2/Windows/Merlin32.exe"

echo "--- regenerating merlin8/ ---"
rm -rf "$ROOT/merlin8"
python "$HERE/split.py"

echo "--- assembling the split version ---"
cd "$ROOT/merlin8"
python - <<'PY'
import io
for root, typ, obj in [("FORTH.S", "$ff", "FORTH.SYSTEM"),
                       ("GFX.S",   "$06", "FORTH.GFX")]:
    s = io.open(root, encoding="ascii", newline="").read().split("\n")
    i = [n for n, l in enumerate(s) if l.split(";")[0].strip().lower() == "xc"][0]
    s[i+1:i+1] = [" typ " + typ, " dsk " + obj]
    io.open("T_" + root, "w", encoding="ascii", newline="\n").write("\n".join(s))
PY
fail=0
for r in T_FORTH.S T_GFX.S; do
  out=$("$M32" -V . "$r" 2>&1) || true
  if echo "$out" | grep -qE "\[Error\]|\[Bad |Can't find"; then
    echo "  FAIL $r"; echo "$out" | grep -E "\[Error\]|\[Bad |Can't find" | head -3; fail=1
  fi
done
rm -f T_FORTH.S T_GFX.S *_Output.txt *_Symbols.txt *_Output_Error.txt error_output.txt 2>/dev/null

echo "--- comparing with the monolithic build ---"
bash "$HERE/mkall.sh" >/dev/null
for o in FORTH.SYSTEM FORTH.GFX; do
  if cmp -s "$ROOT/build/$o" "$ROOT/merlin8/$o"; then
    printf "  %-14s identical  %s bytes\n" "$o" "$(stat -c%s "$ROOT/merlin8/$o")"
  else
    echo "  $o DIFFERS - the split is not the same program"; fail=1
  fi
done
[ $fail = 0 ] && echo "  merlin8/ is good" || { echo "  MERLIN8 BUILD FAILED"; exit 1; }

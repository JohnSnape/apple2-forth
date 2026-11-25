# FORTH for the enhanced Apple IIe

> **Enhanced IIe or later, 128K, and a SmartPort device.** The kernel is a
> ProDOS 8 system program and uses 65C02 opcodes, so it needs an enhanced
> IIe, a IIc or a IIGS. It gives up text page 2 to live at `$0800`, keeps
> its source log in `$6000`–`$76FF`, and its dictionary runs to `$BEFF`.

A 16-bit indirect-threaded FORTH written from scratch in 65C02 assembly.
It boots as `FORTH.SYSTEM`, loads a file of FORTH definitions over itself,
and gives you a prompt in 5,788 bytes. Graphics and sound are separate
relocatable modules loaded on demand, so a program that never draws never
pays for the drawing code.

158 words: 65 in the kernel, 68 compiled from FORTH source at boot, 21 in
the graphics module and 4 in the sound module.

```
2 3 + .                     5
: SQUARE DUP * ;  7 SQUARE .  49
1 GREN                      load the graphics module
HGR  0 0 279 159 HPLOT      a line, corner to corner
```

## What it is

**Indirect threaded.** A compiled word is a list of addresses; the inner
interpreter at `$080C` walks it. A code field holding `DOCOL` makes a word
a list, `DOVAR` makes it a variable, and `DODOES` makes it whatever its
parent said it was.

**`CREATE` and `DOES>` work.** `: ARRAY CREATE 2 * ALLOT DOES> SWAP 2 * + ;`
is the whole of an array type, and defining words of your own cost nothing
beyond that line.

**The dictionary is one chain**, from `$8300` upwards, with the modules'
words spliced in when they load. Each header is a 2-byte link, a count
byte whose bit 7 is the immediate flag, the name, the code field and then
the body.

**The modules relocate themselves.** Each is assembled at `ORG 0` and
loaded wherever the dictionary happens to start; a fixup list at the end
of the image names every internal address, and the loader adds the load
address to each one. Calls back into the kernel go through a jump table
frozen at `$0800`, so the kernel can grow and move without the modules
caring.

**Nineteen of the 68 FORTH-source words are the compiler extending
itself.** `IMMEDIATE` sets bit 7 of a count byte in one line of FORTH, and
`RECURSE`, `LITERAL`, `[` and `]` follow from it. Before `IMMEDIATE` a word
could not call itself at all.

## Memory

| | |
|---|---|
| `$0800`–`$1E9B` | The kernel. Text page 2 is given up for it. 356 bytes free below `$2000`. |
| `$2000`, `$4000` | Hi-res pages 1 and 2, when the graphics module is loaded |
| `$6000`–`$76FF` | The source log: every line you type, so `SAVE` can write out a session |
| `$7800`–`$79FF` | Catalogue buffer |
| `$7C00`–`$7FFF` | The ProDOS I/O buffer. 1K and page-aligned, as ProDOS insists, and it cannot double as a data buffer. |
| `$8000`, `$8100` | The data stack: 256 cells, low bytes in one page and high bytes in the other |
| `$8200`–`$82FF` | Pathname, `ON_LINE` buffer, number buffer, and the loop stack (16 frames of 4 bytes) |
| `$8300`–`$BEFF` | The dictionary, and the modules when they load |
| Zero page | `$06`–`$1F`, `$A4`–`$C9`, `$E0`–`$FC` |

## Building

[Merlin32](https://brutaldeluxe.fr/products/crossdevtools/merlin/), from
Brutal Deluxe, builds everything on a PC in seconds:

```sh
bash tools/mkall.sh
```

That produces `FORTH.SYSTEM` (5,788), `FORTH.GFX` (2,077), `FORTH.SND`
(581), `SHAPES.SHP` (46) and `TUNES.SND` (70) in `build/`. Set the path to
`Merlin32.exe` at the top of the script, and likewise the paths in
`tools/deploy.sh`, which builds an 800K ProDOS disk with
[CiderPress II](https://github.com/fadden/CiderPress2).

**Merlin 8 on the Apple is the assembler of record**, and it will not load
a source file over about 24K. `TEST038.S.txt` is 53K and
`FORTH.GFX.S.txt` is 30K, so:

```sh
bash tools/mk8.sh
```

cuts both into `PUT` segments under `merlin8/`, assembles the split
version, and checks the objects come out byte for byte identical to the
one-file build. The single-file sources stay canonical; `merlin8/` is a
build product and regenerates every time.

### The checkers

Run these before every assembly. Each one exists because of a bug that
reached a disk.

| | |
|---|---|
| `python tools/bcheck.py TEST038.S.txt` | Every out-of-range relative branch at once. Merlin stops at the first, so without this you fix one per assembly. |
| `python tools/fixchk.py FORTH.GFX.S.txt` | Internal references with **no** fixup entry. A missed one keeps its `ORG 0` address and jumps into the stack page. |
| `python tools/modver.py FORTH.GFX.S.txt` | The other direction: every listed fixup names a real relocatable site, and the declared count matches. |

### Traps worth knowing

- **Merlin32 silently drops division in an expression.** `nrel equ
  (relend-relst)/2` assembled as the *byte* count, so the loader ran twice
  as many fixups as there were and wrecked its own dictionary. State such
  counts outright and check them with `modver.py`.
- **State a count before the line that reads it.** Merlin 8 resolves an
  `EQU` on its first pass, so a count declared at the foot of the file is
  garbage to a header at the top. `nrel` sits above `ORG 0` in both
  modules for that reason.
- **In a module at `ORG 0`, a label in the first 256 bytes is a zero-page
  address.** `lda thing` where `thing` is at `$17` assembles two bytes
  long, and a fixup list that assumes three patches the wrong byte. Module
  variables go past `$100`.
- **A source file must end with a line terminator**, or the assembler
  drops the last line.
- **Relative branches reach ±127 bytes.** When the target is on the far
  side of a long routine, invert the test and `jmp`. This has bitten four
  times.

## What is tested, and what is not

Assembled with Merlin32 and run in [AppleWin](https://github.com/AppleWin/AppleWin):
boot and auto-prefix, the FORTH source loading over the kernel at startup,
arithmetic, `WORDS` over the whole chain, `VARIABLE`/`CONSTANT`/`ARRAY`,
`CREATE`/`DOES>`, strings and comments, `DIR`/`NAME$`/`RUN`,
`SAVE`/`LOAD`/`CLEAR`/`DELETE`, `RND` and `SEED`, both modules loading and
relocating, hi-res lines, lo-res, block shapes with XOR erase, double
buffering, all seven sample programs, and a turnkey disk.

Still owed:

- **a pass through real Merlin 8 on the Apple.** Merlin32 matched it byte
  for byte on another project, but it models neither the 24K limit nor
  forward-referenced `EQU`s, and it gives `*` a precedence Merlin 8 does
  not.
- the sound actually *listened to* — every word runs and returns, and a
  tune played from two different load addresses would show the pitch does
  not move with the module;
- `PDL` and `BTN` against a real knob and button.

**Eleven standard words are missing**, and all eleven need assembly rather
than FORTH, because each reaches something the language has no word for —
the 6502's own stack, the innards of a `DO` loop, the dictionary search:
`>R`, `R>`, `R@`, `+LOOP`, `LEAVE`, `J`, `EXIT`, `'`, `EXECUTE`, `FORGET`
and `KEY?`. They belong in a loadable module; there are only 356 bytes
left under `$2000`.

## The files

| | |
|---|---|
| `TEST038.S.txt` | The kernel. The name is its revision number — it is the 38th. |
| `FORTH.WORDS.txt` | 68 words in FORTH source, loaded over the kernel at boot |
| `FORTH.GFX.S.txt` | Hi-res and lo-res graphics, shapes, paddles and buttons. `1 GREN` loads it. |
| `FORTH.SND.S.txt` | `TIMBRE`, `NOTE`, `REST`, `PLAY`. `1 SREN` loads it. |
| `SHAPES.SHP.S.txt`, `TUNES.SND.S.txt` | Sample data for the two modules |
| `SAMPLE_01.txt` … `SAMPLE_07.txt` | Sample programs, as ProDOS text files |
| `STARTUP.txt`, `CHOOSER.txt` | What a turnkey disk runs |
| `tools/` | The build kit, the three checkers, and the AppleWin configuration for an enhanced IIe |

## Acknowledgements

The sound module carries the music routine from Apple's *Programmer's Aid
#1* (Gary J. Shannon, 1978), which lived at `$D717` in a ROM most machines
never had. The block-shape words use Richard T. Simoni Jr.'s method from
Byte, August 1983 — the shape is stored the way the screen stores it, so
stamping it is a byte move rather than a walk through a vector list. Both
are named in the source headers where they are used. The fig-FORTH
glossary was the reference for word names and stack effects.

## Licence

MIT, for the code in this repository. See [`LICENSE`](../LICENSE).

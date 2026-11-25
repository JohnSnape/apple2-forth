TOOLS - assembling and testing FORTH on the PC
(built 2026-11-08; every bug found that day was found this way)

THE LOOP
  bash tools/mkall.sh     assemble the kernel, both modules and both
                          data files with Merlin32 - seconds, not an
                          evening of typing.  Reports sizes, stops on
                          the first error.
  tools\aw.ps1 stop       AppleWin must be closed before the image
                          can be written.
  bash tools/deploy.sh    rebuild FORTH.po from scratch: PRODOS,
                          FORTH.SYSTEM, the modules, the data files
                          and every sample as a ProDOS TXT.
                          Add "startup" to include STARTUP so the
                          disk turnkeys.
  tools\aw.ps1 start D:\AppleWin1.32.0.0\FORTH.po
  tools\aw.ps1 keys '2 3 + .~'
                          ~ is RETURN.  Typing goes through the
                          clipboard: plain key events never reach the
                          emulated keyboard.  Run aw.ps1 from
                          PowerShell in the FOREGROUND - backgrounded,
                          its clipboard calls can hang.
  tools\aw.ps1 shot out.png
                          screenshot; works even when the window is
                          covered.

CHECKERS - run these before every assembly
  python tools/bcheck.py TEST038.S.txt
        every out-of-range relative branch at once.  Merlin stops at
        the first one, so without this you fix them one per assembly.
  python tools/fixchk.py FORTH.GFX.S.txt
        internal references with NO fixup entry.  A missed one keeps
        its ORG-0 address and jumps into the stack page.  Three were
        missing in FORTH.GFX on 2026-11-08 and that is exactly what
        happened - 140 96 HPLOT dropped into the monitor.
        It also lists the two header "da" lines, which are
        deliberate offsets and must NOT be relocated.
  python tools/modver.py FORTH.GFX.S.txt
        the other direction: every listed fixup names a real
        relocatable site, no duplicates, no branches listed, and
        NREL equals the number of entries.

MERLIN32 TRAPS
  - needs a TYP line and a bare DSK name.  mkall.sh inserts both into
    a scratch copy; the real sources never carry them.
  - division in an expression is silently dropped.  NREL EQU
    (RELEND-RELST)/2 came out as the byte count, so the loader ran
    twice as many fixups and wrecked the image.  State counts
    outright and check them with modver.py.
  - it REFUSES (dirp),y when dirp is not in zero page.  Merlin 8
    assembles it quietly as ($A4),y - the low byte only - which is
    how that bug survived all the way to TEST037.
  - a final pass through REAL Merlin 8 in AppleWin is still owed:
    Merlin32 models neither the 24K PUT limit nor forward-referenced
    EQUs, and Merlin 8 gives * no precedence.

WHERE THINGS ARE
  D:\Merlin32\v1.2\Merlin32_v1.2_b2\Windows\Merlin32.exe
  D:\cp2_1.2.0_win-x64_sc\cp2.exe          (CiderPress II)
  D:\AppleWin1.32.0.0\AppleWin.exe
  D:\AppleWin1.32.0.0\FORTH.po             the disk deploy.sh builds
  D:\AppleWin1.32.0.0\COBOL32.po           only for its copy of PRODOS

import sys,re
BR={'bcc','bcs','beq','bne','bmi','bpl','bvc','bvs','bra'}
src=open(sys.argv[1],encoding='utf-8',errors='surrogateescape').read().split('\n')
# labels defined in the file
defined=set(); equ=set()
for L in src:
    if L and L[0] not in ' \t*':
        t=L.split()
        if len(t)>1 and t[1].lower()=='equ': equ.add(t[0].lower())
        else: defined.add(t[0].lower())
# the fixup list: entries like " da xNN" or " da xNN+1"
infix=set()
inlist=False
for L in src:
    if L.startswith('relst'): inlist=True; continue
    if L.startswith('relend'): inlist=False; continue
    if inlist:
        m=re.match(r'\s*da\s+(\w+)',L)
        if m: infix.add(m.group(1).lower())
missing=[]
for i,L in enumerate(src,1):
    if not L.strip() or L.lstrip().startswith('*'): continue
    if L[0] not in ' \t':
        t=L.split(None,2); lab=t[0].lower(); op=(t[1].lower() if len(t)>1 else ''); oper=(t[2] if len(t)>2 else '')
    else:
        t=L.split(None,1); lab=None; op=(t[0].lower() if t else ''); oper=(t[1] if len(t)>1 else '')
    if op in ('equ','org','typ','dsk','xc','dfb','hex','asc','ds'): continue
    if op in BR: continue
    oper=oper.split(';')[0].strip()
    if not oper or oper.startswith('#'): continue
    base=re.split(r'[,+\-\s\)]',oper.lstrip('('))[0].lower()
    if base not in defined or base in equ: continue
    # this line references an internal label -> needs relocation
    if lab and lab in infix: continue
    # inside the fixup list itself?
    missing.append((i,lab or '-',op,oper,L.strip()[:40]))
inlist=False
out=[]
for m in missing:
    # skip the fixup list's own da lines
    if m[2]=='da' and m[3].lower().lstrip().startswith('x') and re.match(r'^x\d+',m[3].strip().lower()): continue
    out.append(m)
for m in out: print(f"  line {m[0]:5d}  {m[2]:4s} {m[3]:22s} {m[4]}")
print(f"--- {len(out)} internal references with NO fixup entry ---")

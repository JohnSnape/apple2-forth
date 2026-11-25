import sys,re
BR={'bcc','bcs','beq','bne','bmi','bpl','bvc','bvs','bra'}
f=sys.argv[1]
src=open(f,encoding='utf-8',errors='surrogateescape').read().split('\n')
defined={}; equ=set(); dup=[]
for i,L in enumerate(src,1):
    if L and L[0] not in ' \t*':
        t=L.split()
        n=t[0].lower()
        if len(t)>1 and t[1].lower()=='equ': equ.add(n)
        if n in defined: dup.append((n,defined[n],i))
        defined[n]=i
listed=[]; inlist=False
for i,L in enumerate(src,1):
    if L.startswith('relst'): inlist=True; continue
    if L.startswith('relend'): inlist=False; continue
    if inlist:
        m=re.match(r'\s*da\s+(\w+)(\+1)?',L)
        if m: listed.append((i,m.group(1).lower(),bool(m.group(2))))
nrel=None
for L in src:
    m=re.match(r'^nrel\s+equ\s+(\d+)',L)
    if m: nrel=int(m.group(1))
print(f"{f.split('/')[-1]}")
print(f"  fixup entries : {len(listed)}")
print(f"  nrel declared : {nrel}  {'OK' if nrel==len(listed) else '*** MISMATCH ***'}")
seen={}; bad=0
for ln,name,plus in listed:
    if name in seen: print(f"  DUPLICATE entry {name} (lines {seen[name]},{ln})"); bad+=1
    seen[name]=ln
    if name not in defined:
        print(f"  entry {name} is NOT a defined label"); bad+=1
        continue
    # the labelled line must be relocatable and the +1/no+1 must match its kind
    src_line=src[defined[name]-1]
    t=src_line.split(None,2)
    op=(t[1].lower() if len(t)>1 else '')
    if op=='da' and plus: print(f"  {name}: 'da' field listed with +1"); bad+=1
    if op!='da' and not plus: print(f"  {name}: instruction listed without +1"); bad+=1
    if op in BR: print(f"  {name}: a BRANCH is listed (never relocate)"); bad+=1
for n,a,b in dup: print(f"  DUPLICATE LABEL {n} (lines {a},{b})"); bad+=1
print(f"  {'all consistent' if bad==0 else str(bad)+' problems'}")

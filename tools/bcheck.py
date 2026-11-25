import sys,re
BR={'bcc','bcs','beq','bne','bmi','bpl','bvc','bvs','bra'}
IMP={'rts','rti','nop','txs','tsx','tax','tay','txa','tya','dex','dey','inx','iny',
'pha','pla','php','plp','phx','plx','phy','ply','clc','sec','cld','sed','cli','sei',
'clv','brk','asl','lsr','rol','ror','inc','dec','dea','ina','xce','tcd','tdc'}
D3={'jmp','jsr','jml','jsl'}
src=open(sys.argv[1],encoding='utf-8',errors='surrogateescape').read().split('\n')
equ={}
for L in src:
    m=re.match(r'^(\S+)\s+equ\s+(\S+)',L,re.I)
    if m:
        v=m.group(2)
        try: equ[m.group(1).lower()]=int(v[1:],16) if v.startswith('$') else int(v)
        except: pass
def nbytes(sv):
    if sv.startswith('$'): return (len(sv)-1+1)//2
    return 1
rows=[];addr=0
for i,L in enumerate(src,1):
    if not L.strip() or L.lstrip().startswith('*'): rows.append((i,addr,None,None,L)); continue
    if L[0] not in ' \t':
        t=L.split(None,2); lab=t[0]; op=(t[1].lower() if len(t)>1 else ''); oper=(t[2] if len(t)>2 else '')
    else:
        t=L.split(None,1); lab=None; op=(t[0].lower() if t else ''); oper=(t[1] if len(t)>1 else '')
    oper=oper.split(';')[0].strip()
    rows.append((i,addr,lab,op,L))
    sz=0
    if op=='org':
        v=oper.lstrip('$'); 
        try: addr=int(v,16) if oper.startswith('$') else equ.get(oper.lower(),int(v))
        except: pass
        continue
    if op in ('equ','typ','dsk','xc','obj','lst','sav'): continue
    elif op=='da': sz=2*len([x for x in oper.split(',') if x.strip()])
    elif op=='dfb' or op=='db': sz=len([x for x in oper.split(',') if x.strip()])
    elif op=='ds':
        try: sz=int(oper)
        except: sz=0
    elif op=='hex': sz=sum(nbytes('$'+x.strip()) for x in oper.split(',') if x.strip())
    elif op=='asc':
        m=re.match(r'^(["\'])(.*?)\1',oper); sz=len(m.group(2)) if m else 0
    elif op in BR: sz=2
    elif op in D3: sz=3
    elif op in IMP and not oper: sz=1
    elif op:
        if oper.startswith('#'): sz=2
        else:
            base=re.split(r'[,+\-\s]',oper.lstrip('('))[0].lower()
            if base in equ and equ[base]<0x100: sz=2
            else: sz=3
    addr+=sz
lab={}
for i,a,l,o,L in rows:
    if l: lab[l.lower()]=a
bad=0
for i,a,l,o,L in rows:
    if o in BR:
        t=L.split(None,2)
        tgt=(t[2] if (L[0] not in ' \t' and len(t)>2) else (t[1] if (L[0] in ' \t' and len(t)>1) else ''))
        tgt=tgt.split(';')[0].strip().lower()
        if tgt in lab:
            d=lab[tgt]-(a+2)
            if d<-128 or d>127:
                print(f"line {i:5d}  {o} {tgt:12s} dist {d:+5d}   {L.strip()[:44]}")
                bad+=1
print(f"--- {bad} out-of-range branches; end address ${addr:04X} ---")

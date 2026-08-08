# rndsetup brand path migration: /sh-scientific /leadfluid /alicat -> /brands/
# Run at repo root on clean main:  python migrate_brands.py
import os, re, subprocess, sys
ROOT=os.getcwd(); B=['sh-scientific','leadfluid','alicat']
def run(c): print('>',c); subprocess.run(c,shell=True,check=True)
assert os.path.isfile('_build/build.py'), 'Run at rndsetup repo root'
def rd(p): return open(p,encoding='utf-8',newline='').read()
def wr(p,s): open(p,'w',encoding='utf-8',newline='').write(s)

if not os.path.isdir('brands'):
    os.makedirs('functions/brands',exist_ok=True); os.makedirs('brands',exist_ok=True)
    for b in B: run(f'git mv {b} brands/{b}')
    run('git mv functions/sh-scientific functions/brands/sh-scientific')
else: print('brands/ exists - skip move')

absp=[(f'rndsetup.com/{b}',f'rndsetup.com/brands/{b}') for b in B]
hrefp=[]
for b in B:
    for q in ['"',"'"]:
        hrefp+=[(f'href={q}/{b}/',f'href={q}/brands/{b}/'),(f'href={q}/{b}{q}',f'href={q}/brands/{b}{q}')]
def htmls():
    for dp,dn,fns in os.walk(ROOT):
        if os.sep+'.git' in dp or os.sep+'_build' in dp: continue
        for fn in fns:
            if fn.endswith('.html'): yield os.path.join(dp,fn)
ch=0
for p in htmls():
    s=rd(p); o=s
    for a,b in absp: s=s.replace(a,b)
    for a,b in hrefp: s=s.replace(a,b)
    if s!=o:
        if o.rstrip().endswith('</html>') and not s.rstrip().endswith('</html>'): raise SystemExit('integrity '+p)
        wr(p,s); ch+=1
print('HTML replaced:',ch)

bp='_build/build.py'; s=rd(bp)
for b in B: s=s.replace(f"'/{b}",f"'/brands/{b}").replace(f"('{b}/",f"('brands/{b}/")
wr(bp,s)

mp='functions/brands/sh-scientific/_middleware.js'
if os.path.isfile(mp):
    wr(mp, rd(mp).replace("const PREFIX = '/sh-scientific/catalog';","const PREFIX = '/brands/sh-scientific/catalog';"))

def fixjs(p):
    if not os.path.isfile(p): return
    s=rd(p); o=s
    s=s.replace('/img/leadfluid/','\x00L').replace('/img/sh/','\x00S').replace('/img/alicat/','\x00A')
    for b in B: s=s.replace(f'/{b}/',f'/brands/{b}/')
    s=s.replace('\x00L','/img/leadfluid/').replace('\x00S','/img/sh/').replace('\x00A','/img/alicat/')
    if s!=o: wr(p,s)
for f in ['assets/site.js','functions/admin/index.js','functions/api/admin/publish.js']: fixjs(f)

def fixdoc(p):
    s=rd(p); o=s
    s=s.replace('/img/leadfluid/','\x00L').replace('/pump/leadfluid/','\x00P')
    for b in B: s=s.replace(f'/{b}/',f'/brands/{b}/')
    s=s.replace('\x00P','/pump/leadfluid/').replace('\x00L','/img/leadfluid/')
    if s!=o: wr(p,s); return True
    return False
docs=['llms.txt','CLAUDE.md','qr/README.txt']
for p in htmls():
    s=rd(p)
    if re.search(r"(url=/(sh-scientific|leadfluid|alicat)/|location\.replace\('/(sh-scientific|leadfluid|alicat)/)",s):
        docs.append(os.path.relpath(p,ROOT))
for d in docs:
    if os.path.isfile(d) and fixdoc(d): print('doc updated:',d)

rp='_redirects'
if os.path.isfile(rp):
    lines=rd(rp).split('\n'); out=[]; done=any('/brands/sh-scientific/:splat' in l for l in lines)
    def ft(t):
        for b in B:
            if t.startswith(f'/{b}/') or t==f'/{b}': return '/brands'+t
        return t
    for ln in lines:
        if ln.strip()=='' or ln.lstrip().startswith('#'): out.append(ln); continue
        pr=ln.split()
        if len(pr)>=2: pr[1]=ft(pr[1]); out.append('  '.join(pr))
        else: out.append(ln)
    if not done:
        out+=['','# brand path consolidation 2026-08']
        for b in B: out+=[f'/{b}/*   /brands/{b}/:splat   301',f'/{b}    /brands/{b}/   301']
    wr(rp,'\n'.join(out))

print('running build.py ...'); subprocess.run([sys.executable,'_build/build.py'],check=True)

rem=0
for p in htmls():
    s=rd(p)
    for b in B: rem+=len(re.findall(f'href="/{b}/',s))+s.count(f'rndsetup.com/{b}/')
print('=== VERIFY old-brand links remaining =', rem, '(must be 0) ===')
print('DONE. Review with: git status  then commit & push.')
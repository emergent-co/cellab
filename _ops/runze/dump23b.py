import json,sys,re
B={p['slug']:p for p in json.load(open('_ops/runze/runze_batch23.json'))}
M=json.load(open('_ops/runze/img_meta23.json'))
O=json.load(open('_ops/runze/ocr23.json'))
for s in sys.argv[1:]:
    p=B[s]; body=p['body']
    for cut in ['Product Inquiry','GET PRICE']:
        i=body.find(cut)
        if i>0: body=body[:i]
    print('='*72); print('SLUG:',s,'| H1:',p['h1'])
    print('DESC:',p['desc'])
    print('PDF:',sorted(set(p['pdfs'])),'| VIDEO:',sorted(set(v for v in p['videos'] if v and 'youtu' in v)))
    print('GAL:',len(M[s]['gal']),'DET:',len(M[s]['det']))
    print('--- BODY ---'); print(body.strip())
    for i,t in enumerate(p['tables']): print('--- TABLE',i,'---'); print(json.dumps(t,ensure_ascii=False))
    print('--- DETAIL OCR (>250 chars only) ---')
    for i,r in enumerate(O[s]):
        t=re.sub(r'\n+','\n',r['txt'])
        print('[d%d] %s | h: %s | len=%d'%(i+1,r['src'],r['h'],len(t)))
        if len(t)>250: print(t[:1600])

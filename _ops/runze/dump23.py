import json,sys,re
B={p['slug']:p for p in json.load(open('_ops/runze/runze_batch23.json'))}
M=json.load(open('_ops/runze/img_meta23.json'))
O=json.load(open('_ops/runze/ocr23.json'))
for s in sys.argv[1:]:
    p=B[s]
    body=p['body']
    for cut in ['Product Inquiry','GET PRICE']:
        i=body.find(cut)
        if i>0: body=body[:i]
    print('='*72); print('SLUG:',s,'| H1:',p['h1'])
    print('TITLE:',p['title']); print('DESC:',p['desc'])
    pdf=[x for x in p['pdfs']]; vid=[v for v in p['videos'] if v and 'youtu' in v]
    print('PDF:',pdf,'| VIDEO:',vid)
    print('GAL:',M[s]['gal'])
    print('--- BODY ---'); print(body.strip())
    for i,t in enumerate(p['tables']): print('--- TABLE',i,'---'); print(json.dumps(t,ensure_ascii=False))
    print('--- DETAIL IMAGES (OCR) ---')
    for i,r in enumerate(O[s]):
        print('[d%d] %s | heading: %s'%(i+1,r['src'],r['h']))
        print(r['txt'][:1800])
        print('  .')

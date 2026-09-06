import json,os,sys
from PIL import Image
import pytesseract
from multiprocessing import Pool
B={p['slug']:p for p in json.load(open('_ops/runze/runze_batch23.json'))}
K=json.load(open('_ops/runze/keep23.json'))
H=json.load(open('_ops/runze/runze_img_headings.json'))
M=json.load(open('_ops/runze/img_meta23.json'))
P='_ops/runze/ocr23.json'
out=json.load(open(P)) if os.path.exists(P) else {}
def job(a):
    s,i,f,src,h=a
    im=Image.open('img/runze/'+f)
    if im.width<1400: im=im.resize((1400,round(im.height*1400/im.width)),Image.LANCZOS)
    try: t=pytesseract.image_to_string(im,config='--psm 6')
    except Exception as e: t='ERR '+str(e)
    return (s,i,{'f':f,'src':src,'h':h,'txt':'\n'.join(x.rstrip() for x in t.splitlines() if x.strip())})
if __name__=='__main__':
    a,b=int(sys.argv[1]),int(sys.argv[2])
    jobs=[]
    for s in K[a:b]:
        if s in out: continue
        det=B[s]['detailImgs']; hd=H.get(s,[])
        for i,src in enumerate(det):
            jobs.append((s,i,M[s]['det'][i],os.path.basename(src),hd[i] if i<len(hd) else ''))
    with Pool(6) as p: res=p.map(job,jobs)
    d={}
    for s,i,r in res: d.setdefault(s,{})[i]=r
    for s,v in d.items(): out[s]=[v[i] for i in sorted(v)]
    json.dump(out,open(P,'w'),ensure_ascii=False,indent=0)
    print('done slugs',len(d),'imgs',len(jobs),'| total',len(out))

import json,base64,io,os,sys,re
from PIL import Image,ImageChops
DL=os.path.expanduser('~/mnt/Downloads'); OUT='img/runze'
W,HH,FILL=800,600,0.86
meta=json.load(open('_ops/runze/img_meta23.json')) if os.path.exists('_ops/runze/img_meta23.json') else {}
DET=re.compile(r'-d\d+\.jpg$')
for f in sys.argv[1:]:
    D=json.load(open(os.path.join(DL,f))); meta.update(D['meta'])
    for name,b64 in D['img'].items():
        p=os.path.join(OUT,name)
        im=Image.open(io.BytesIO(base64.b64decode(b64))).convert('RGB')
        if DET.search(name):
            if im.width>1000: im=im.resize((1000,round(im.height*1000/im.width)),Image.LANCZOS)
            im.save(p,quality=78,optimize=True); continue
        px=im.load(); w,h=im.size
        cs=[px[0,0],px[w-1,0],px[0,h-1],px[w-1,h-1]]
        bg=tuple(sum(c[i] for c in cs)//4 for i in range(3))
        d=ImageChops.difference(im,Image.new('RGB',im.size,bg)).convert('L').point(lambda v:255 if v>16 else 0)
        bb=d.getbbox() or (0,0,w,h)
        bb=(max(0,bb[0]-4),max(0,bb[1]-4),min(w,bb[2]+4),min(h,bb[3]+4))
        c=im.crop(bb); cw,ch=c.size
        s=min(W*FILL/cw,HH*FILL/ch); nw,nh=max(1,round(cw*s)),max(1,round(ch*s))
        cv=Image.new('RGB',(W,HH),bg); cv.paste(c.resize((nw,nh),Image.LANCZOS),((W-nw)//2,(HH-nh)//2))
        cv.save(p,quality=88,optimize=True)
    print(f,'ok',len(D['img']),'fail',len(D['fail']))
json.dump(meta,open('_ops/runze/img_meta23.json','w'),ensure_ascii=False,indent=0)
print('meta slugs',len(meta))

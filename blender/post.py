import json, glob, os, sys
from PIL import Image
import numpy as np
groups={'hero':['hero_%s'%c for c in ('-4','-2','0','2','4')],'cart':['cart_0'],'right':['right_0'],'motor':['motor_0']}
os.makedirs('web',exist_ok=True); meta={}
for g,names in groups.items():
    ims={n:Image.open('out/%s.png'%n) for n in names if os.path.exists('out/%s.png'%n)}
    if not ims: continue
    boxes=[]
    for im in ims.values():
        a=np.array(im)[:,:,3]; ys,xs=np.where(a>200); boxes.append((xs.min(),ys.min(),xs.max(),ys.max()))
    x0=int(min(b[0] for b in boxes)); y0=int(min(b[1] for b in boxes)); x1=int(max(b[2] for b in boxes)); y1=int(max(b[3] for b in boxes))
    W,H=list(ims.values())[0].size; padx=int((x1-x0)*0.04); pady=int((y1-y0)*0.12)
    x0=max(0,x0-padx); y0=max(0,y0-pady); x1=min(W-1,x1+padx); y1=min(H-1,y1+pady); cw,ch=x1-x0,y1-y0
    for n,im in ims.items():
        im.crop((x0,y0,x1,y1)).save('web/%s.webp'%n,quality=90,method=6)
        an=json.load(open('out/%s.json'%n)); an={k:[round((v[0]*W-x0)/cw,4),round((v[1]*H-y0)/ch,4)] for k,v in an.items()}
        meta[n]=dict(w=cw,h=ch,anch=an,size=os.path.getsize('web/%s.webp'%n))
json.dump(meta,open('web/meta.json','w'),indent=1); print({k:(v['w'],v['h'],v['size']) for k,v in meta.items()})

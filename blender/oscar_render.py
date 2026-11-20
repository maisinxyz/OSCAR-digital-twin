import bpy, bmesh, math, sys, json, os
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFont

def arg(n,d):
    a=sys.argv
    return type(d)(a[a.index('--'+n)+1]) if '--'+n in a else d
CART=arg('cart',0.0); VIEW=arg('view','hero'); RX=arg('rx',900); RY=arg('ry',480); SMP=arg('s',24); OUT=arg('out','/tmp/t.png')
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
def mat(name,col,met=0.0,rough=0.5,**kw):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(col[0],col[1],col[2],1); b.inputs['Metallic'].default_value=met; b.inputs['Roughness'].default_value=rough
    for k,v in kw.items():
        k=k.replace('_',' ')
        if k in b.inputs:
            b.inputs[k].default_value=v if not isinstance(v,tuple) else (*v,1)
    return m
M=dict(
 anod=mat('anod',(0.020,0.020,0.023),0.85,0.34),
 anod2=mat('anod2',(0.030,0.030,0.034),0.8,0.45),
 panel=mat('panel',(0.008,0.008,0.009),0.0,0.7,Specular_IOR_Level=0.25),
 steel=mat('steel',(0.78,0.79,0.80),1.0,0.22),
 steeld=mat('steeld',(0.5,0.52,0.54),1.0,0.38),
 chrome=mat('chrome',(0.86,0.87,0.88),1.0,0.10),
 stainless=mat('stainless',(0.74,0.75,0.77),1.0,0.27),
 white=mat('white',(0.88,0.88,0.86),0.0,0.42,Coat_Weight=0.1),
 yellow=mat('yellow',(0.95,0.50,0.0),0.0,0.34,Coat_Weight=0.25,Coat_Roughness=0.1),
 red=mat('red',(0.60,0.008,0.006),0.0,0.16,Coat_Weight=0.5,Coat_Roughness=0.05),
 rubber=mat('rubber',(0.012,0.012,0.012),0.0,0.8),
 can=mat('can',(0.014,0.014,0.016),0.7,0.30),
 black=mat('black',(0.01,0.01,0.01),0.0,0.45),
 dark=mat('dark',(0.002,0.002,0.002),0.0,0.9),
 pcb=mat('pcb',(0.01,0.10,0.045),0.0,0.35),
 brass=mat('brass',(0.75,0.55,0.25),1.0,0.3),
 wire_o=mat('wire_o',(0.8,0.3,0.02),0.0,0.4),
 wire_w=mat('wire_w',(0.9,0.9,0.88),0.0,0.4),
 cable=mat('cable',(0.008,0.008,0.009),0.0,0.5),
)
# ruler texture
def ruler_tex(path):
    W,H=1480,140; im=Image.new('RGB',(W,H),(10,10,11)); d=ImageDraw.Draw(im)
    try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',46)
    except: f=ImageFont.load_default()
    labs=['-7','-6','-5','-4','-3','-2','-1','0','+1','+2','+3','+4','+5','+6','+7']
    x0=(W-(14*96))/2
    for i,t in enumerate(labs):
        x=x0+i*96; d.line([(x,8),(x,34)],fill=(235,235,235),width=5)
        for j in range(1,5): xx=x+j*19.2; d.line([(xx,8),(xx,20)],fill=(200,200,200),width=3)
        w=d.textlength(t,font=f); d.text((x-w/2,58),t,font=f,fill=(240,240,240))
    im.save(path)
ruler_tex('/tmp/ruler.png')
img=bpy.data.images.load('/tmp/ruler.png'); rm=bpy.data.materials.new('ruler'); rm.use_nodes=True
nt=rm.node_tree; b=nt.nodes['Principled BSDF']; t=nt.nodes.new('ShaderNodeTexImage'); t.image=img
nt.links.new(t.outputs['Color'],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.5; b.inputs['Metallic'].default_value=0.1
M['ruler']=rm

def finish(o,m,bevel=0.0,smooth_side=False):
    o.data.materials.append(m)
    if smooth_side:
        for p in o.data.polygons: p.use_smooth=abs(p.normal.z)<0.7
    if bevel>0:
        bm=o.modifiers.new('bev','BEVEL'); bm.width=bevel; bm.segments=2; bm.limit_method='ANGLE'; bm.angle_limit=math.radians(35)
    return o
def box(x0,x1,y0,y1,z0,z1,m,bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1,location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
    o=bpy.context.object; o.scale=(x1-x0,y1-y0,z1-z0); bpy.ops.object.transform_apply(scale=True)
    return finish(o,m,bevel)
def cyl(x,y,z0,r,h,m,axis='z',v=64,bevel=0.02):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=h,location=(0,0,0))
    o=bpy.context.object
    for p in o.data.polygons: p.use_smooth=abs(p.normal.z)<0.7
    if axis=='x': o.rotation_euler=(0,math.pi/2,0)
    if axis=='y': o.rotation_euler=(math.pi/2,0,0)
    bpy.ops.object.transform_apply(rotation=True)
    if axis=='z': o.location=(x,y,z0+h/2)
    elif axis=='x': o.location=(z0,y,x)   # for axis x: x param is the z-height, z0 the x-start (see below)
    return finish(o,m,bevel)
def cylx(x0,y,z,r,length,m,v=48,bevel=0.02):   # cylinder along +x starting x0
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=length,location=(0,0,0))
    o=bpy.context.object
    for p in o.data.polygons: p.use_smooth=abs(p.normal.z)<0.7
    o.rotation_euler=(0,math.pi/2,0); bpy.ops.object.transform_apply(rotation=True)
    o.location=(x0+length/2,y,z); return finish(o,m,bevel)
def lathe(name,prof,x,y,z,m,segs=96,closed=False):
    me=bpy.data.meshes.new(name); verts=[]; faces=[]; n=len(prof)
    for (r,h) in prof:
        for i in range(segs):
            a=2*math.pi*i/segs; verts.append((r*math.cos(a),r*math.sin(a),h))
    for j in range(n-1):
        for i in range(segs):
            a=j*segs+i; b=j*segs+(i+1)%segs; faces.append((a,b,b+segs,a+segs))
    if closed:
        for i in range(segs):
            a=(n-1)*segs+i; b=(n-1)*segs+(i+1)%segs; faces.append((a,b,b-(n-1)*segs,a-(n-1)*segs))
    me.from_pydata(verts,[],faces); me.update()
    bm=bmesh.new(); bm.from_mesh(me)
    # merge axis points
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5); bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    o=bpy.data.objects.new(name,me); sc.collection.objects.link(o); o.location=(x,y,z); o.data.materials.append(m); return o
# --- T-slot extrusion
def slot_profile(w=2.0):
    h=w/2; s=0.31; d=0.82; c=0.50; e=0.52  # slot half opening, lip depth, cavity half width, cavity floor depth
    side=[(-h,h),(-s,h),(-s,h-d),(-c,h-d),(-c,h-d-0.24),(c,h-d-0.24),(c,h-d),(s,h-d),(s,h)]  # one side, left→right on top edge
    pts=[]
    for k in range(4):
        a=k*math.pi/2; ca,sa=math.cos(a),math.sin(a)
        for (x,y) in side: pts.append((x*ca-y*sa,x*sa+y*ca))
    return pts
def extrude(name,prof,length,axis,origin,m,bevel=0.0):
    n=len(prof); verts=[]; faces=[]
    for z in (0,length):
        for (px,py) in prof: verts.append((px,py,z))
    for i in range(n): faces.append((i,(i+1)%n,n+(i+1)%n,n+i))
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    f0=bm.faces.new([bm.verts[i] for i in range(n)][::-1]); f1=bm.faces.new([bm.verts[n+i] for i in range(n)])
    bmesh.ops.triangulate(bm,faces=[f0,f1]); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); sc.collection.objects.link(o)
    if axis=='x': o.rotation_euler=(0,math.pi/2,0)
    if axis=='y': o.rotation_euler=(math.pi/2,0,0)
    o.location=origin; o.data.materials.append(m)
    if bevel: bm_=o.modifiers.new('bev','BEVEL'); bm_.width=bevel; bm_.segments=1; bm_.limit_method='ANGLE'; bm_.angle_limit=math.radians(50)
    return o
P20=slot_profile(2.0)
def ext_x(x0,x1,yc,zc,m=None): return extrude('ex',P20,x1-x0,'x',(x0,yc,zc),m or M['anod'],0.015)
def ext_z(xc,yc,z0,z1,m=None): return extrude('ez',P20,z1-z0,'z',(xc,yc,z0),m or M['anod'],0.015)
def ext_y(xc,y0,y1,zc,m=None): return extrude('ey',P20,y1-y0,'y',(xc,y1,zc),m or M['anod'],0.015)  # -y rot: extends toward -y so origin at y1

# ================= model (cm) =================
FL=45.0; FD=11.0
# frame
ext_x(0,FL,1.0,8.0); ext_x(0,FL,10.0,8.0); ext_x(0,FL,1.0,1.6); ext_x(0,FL,10.0,1.6)
for x in (1.0,FL-1.0):
    for y in (1.0,10.0): ext_z(x,y,2.6,7.0)
ext_y(1.0,1.0,10.0,8.0); ext_y(FL-1.0,1.0,10.0,8.0); ext_y(1.0,1.0,10.0,1.6); ext_y(FL-1.0,1.0,10.0,1.6)
box(2.0,FL-2.0,1.8,9.2,8.55,9.0,M['anod2'],0.02)          # top plate
for (a,b) in ((2.4,21.0),(21.6,FL-2.4)):
    box(a,b,0.55,0.75,2.75,6.85,M['panel'],0.02)             # recessed front panels
    box(a,b,11.25,11.45,2.75,6.85,M['panel'],0.02)
    box(a,b,2.0,9.0,2.45,2.65,M['panel'],0.02)               # base plate
for (x,y) in ((2.8,1.4),(FL-2.8,1.4),(2.8,10.6),(FL-2.8,10.6)): cyl(x,y,-0.7,1.0,0.7,M['rubber'],v=40,bevel=0.03)
# cable out of right end
bpy.ops.curve.primitive_bezier_curve_add(); cu=bpy.context.object
cu.data.splines[0].bezier_points[0].co=(FL-0.2,5.5,5.0); cu.data.splines[0].bezier_points[1].co=(FL+1.8,7.0,0.2)
for bp in cu.data.splines[0].bezier_points: bp.handle_left_type=bp.handle_right_type='AUTO'
cu.data.bevel_depth=0.2; cu.data.materials.append(M['cable'])
# ---- tall support (3 profiles side by side) + base bracket
for xc in (1.0,3.0,5.0): ext_z(xc,3.4,9.0,26.0)
box(0.6,6.4,1.5,5.3,9.0,13.0,M['anod'],0.05)
for (x,z) in ((1.6,10.0),(1.6,12.0),(4.6,10.3),(5.4,12.0)):
    c=cyl(x,1.5,z,0.26,0.16,M['steel'],v=24,bevel=0.01); c.rotation_euler=(math.pi/2,0,0); c.location=(x,1.5-0.0,z)
# eye bolt on support
cylx(6.0,3.4,14.2,0.16,1.5,M['steel'],v=16,bevel=0)
bpy.ops.mesh.primitive_torus_add(major_radius=0.34,minor_radius=0.06,major_segments=32,minor_segments=10,location=(7.6,3.4,14.2),rotation=(0,math.pi/2,0)); tor=bpy.context.object; tor.data.materials.append(M['steel'])
cyl(6.05,3.4,14.2,0.45,0.1,M['steel'],v=32,bevel=0.01).rotation_euler=(0,math.pi/2,0)
# ---- left small bracket + rail end
bm_=bpy.ops.mesh.primitive_cube_add  # placeholder
def tri(pts,y0,y1,m,bevel=0.03):  # polygon in x,z extruded in y
    n=len(pts); verts=[(x,y0,z) for x,z in pts]+[(x,y1,z) for x,z in pts]; faces=[tuple(range(n))[::-1],tuple(range(n,2*n))]
    for i in range(n): faces.append((i,(i+1)%n,n+(i+1)%n,n+i))
    me=bpy.data.meshes.new('tri'); me.from_pydata(verts,[],faces); me.update()
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new('tri',me); sc.collection.objects.link(o); return finish(o,m,bevel)
tri([(5.9,9.0),(5.9,11.8),(7.9,12.9),(9.2,12.9),(9.2,9.0)],1.8,5.2,M['anod'],0.04)
c=cyl(7.5,1.8,11.9,0.3,0.14,M['steel'],v=24,bevel=0.01); c.rotation_euler=(math.pi/2,0,0)
# ---- rails
box(7.0,29.0,2.9,4.1,9.0,9.35,M['anod2'],0.02)               # carrier
box(7.0,29.0,3.25,3.95,9.35,9.95,M['steel'],0.03)            # MGN9 rail
for i in range(11): c=cyl(7.9+i*2.0,3.6,9.95,0.2,0.012,M['dark'],v=24,bevel=0)
box(7.0,29.0,7.3,8.7,9.0,10.3,M['anod'],0.03)                # back bar
for i in range(11): box(7.6+i*2.05,9.1+i*2.05,7.4,8.6,10.3,10.9,M['white'],0.12)
box(11.0,25.8,0.35,1.75,9.0,9.18,M['black'],0.01)
bpy.ops.mesh.primitive_plane_add(size=1,location=(18.4,1.05,9.185)); rp=bpy.context.object; rp.scale=(14.8,1.4,1); bpy.ops.object.transform_apply(scale=True); rp.data.materials.append(M['ruler'])
# ---- right bracket (triangular gusset) + e-stop
tri([(33.4,9.0),(34.8,13.1),(38.0,13.1),(38.0,9.0)],4.2,5.7,M['anod'],0.05)
for (x,z) in ((36.6,10.4),(35.4,12.2)):
    c=cyl(x,4.2,z,0.28,0.16,M['steel'],v=24,bevel=0.01); c.rotation_euler=(math.pi/2,0,0)
box(37.2,FL-0.2,1.3,9.4,9.0,11.0,M['anod'],0.06)              # black base
box(37.6,FL-0.4,1.8,8.6,11.0,15.0,M['yellow'],0.28)           # yellow housing
box(38.4,FL-1.2,2.5,7.9,15.0,15.12,M['yellow'],0.05)
for (x,y) in ((38.7,2.6),(FL-1.5,2.6),(38.7,7.8),(FL-1.5,7.8)): cyl(x,y,15.0,0.28,0.12,M['steel'],v=24,bevel=0.02)
EX,EY=41.5,5.2
lathe('collar',[(0.0,15.0),(1.9,15.0),(1.9,15.25),(1.7,15.4),(1.7,15.9),(0.0,15.9)],EX,EY,0,M['black'])
mp=[(0.9,15.85),(1.15,15.95)]
dome=[(1.1,15.85),(1.5,15.9),(1.74,16.02),(1.82,16.16)]
import numpy as np
for t in np.linspace(0.0,math.pi/2,18)[1:]:
    dome.append((1.82*math.cos(t)**0.62,16.16+1.12*math.sin(t)**0.55))
dome[-1]=(0.0,dome[-1][1])
lathe('mush',dome,EX,EY,0,M['red'])
# ---- motor (vertical, behind)
MX,MY=30.3,7.6
box(27.9,32.7,8.9,10.2,9.0,16.6,M['anod'],0.05)
lathe('gear',[(0,14.7),(1.55,14.7),(1.55,17.4),(0,17.4)],MX,MY,0,M['steel'])
lathe('can',[(0,17.4),(1.85,17.4),(1.85,22.0),(1.7,22.3),(0,22.3)],MX,MY,0,M['can'])
for z in (17.9,22.0): lathe('ring',[(1.86,z),(1.9,z),(1.9,z+0.1),(1.86,z+0.1)],MX,MY,0,M['steeld'],closed=True)
lathe('boss',[(0,22.3),(0.8,22.3),(0.8,22.6),(0,22.6)],MX,MY,0,M['steel'])
lathe('shaft',[(0,13.9),(0.22,13.9),(0.22,14.7),(0,14.7)],MX,MY,0,M['steel'])
lathe('crank',[(0,13.7),(1.05,13.7),(1.05,13.95),(0,13.95)],MX,MY,0,M['steel'])
lathe('pin',[(0,13.95),(0.18,13.95),(0.18,14.7),(0,14.7)],MX,MY-0.8,0,M['steel'])
# link from crank pin to spring end tab
tab=(35.8,3.4,14.2)
def link(a,b,r,m):
    a=Vector(a); b=Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
link((MX,MY-0.8,14.2),tab,0.06,M['steel'])
box(35.4,36.3,3.0,3.8,13.8,14.6,M['steel'],0.05)
cyl(35.8,3.4,13.8,0.0,0.0,M['steel']) if False else None
# ---- spring
def spring(xa,xb,y,z,turns,R=0.36,wire=0.06):
    pts=[(xa,y,z),(xa+0.25,y,z)]; N=int(turns*18)
    xs=xa+0.25; xe=xb-0.25
    for i in range(N+1):
        t=i/N; ph=2*math.pi*turns*t
        pts.append((xs+(xe-xs)*t,y+R*math.cos(ph)*0.0+R*math.sin(ph),z+R*math.cos(ph)))
    pts+=[(xb-0.25,y,z),(xb,y,z)]
    cu=bpy.data.curves.new('sp','CURVE'); cu.dimensions='3D'; s=cu.splines.new('POLY'); s.points.add(len(pts)-1)
    for p,(x,yy,zz) in zip(s.points,pts): p.co=(x,yy,zz,1)
    cu.bevel_depth=wire; cu.bevel_resolution=3; cu.resolution_u=1
    o=bpy.data.objects.new('spring',cu); sc.collection.objects.link(o); cu.materials.append(M['steel']); return o
# ---- cart (center x = CX)
CX=18.0+CART
box(CX-3.75,CX+3.75,1.6,6.6,9.7,11.4,M['anod'],0.05)           # lower block
box(CX-1.4,CX+1.4,2.7,4.5,9.55,11.0,M['steel'],0.04)           # carriage
box(CX-3.75,CX+3.75,1.9,6.4,11.4,13.7,M['anod'],0.06)          # upper block
box(CX-3.78,CX+3.78,1.55,6.65,11.35,11.5,M['steeld'],0.01)     # split line
box(CX-4.1,CX-3.75,2.6,5.6,10.0,13.0,M['anod2'],0.04); box(CX+3.75,CX+4.1,2.6,5.6,10.0,13.0,M['anod2'],0.04)
for (dx,z) in ((-3.0,12.0),(3.0,12.0),(-3.0,10.3),(3.0,10.3)):
    c=cyl(CX+dx,1.55,z,0.28,0.12,M['steel'],v=24,bevel=0.01); c.rotation_euler=(math.pi/2,0,0)
# thumbscrews (white) with spring hooks
for dx in (-2.9,2.9):
    cyl(CX+dx,3.4,13.7,0.42,1.0,M['white'],v=36,bevel=0.06)
    cyl(CX+dx,3.4,14.7,0.34,0.14,M['white'],v=36,bevel=0.03)
# mass posts + disks
for dx,n in ((-2.6,3),(0.0,2),(2.6,3)):
    cyl(CX+dx,5.4,13.7,0.2,0.4+1.45*n+1.1,M['steel'],v=20,bevel=0)
    for k in range(n):
        z=13.7+0.05+k*1.45
        lathe('disk',[(0.34,z),(1.14,z),(1.25,z+0.1),(1.25,z+1.28),(1.14,z+1.38),(0.34,z+1.38)],CX+dx,5.4,0,M['stainless'],segs=96,closed=True)
    ztop=13.7+0.05+n*1.45
    cyl(CX+dx,5.4,ztop,0.38,0.2,M['steeld'],v=24,bevel=0.02)
# springs
rest=18.0
spring(7.6+0.34,CX-2.9,3.4,14.2,turns=38*((CX-2.9)-7.94)/((rest-2.9)-7.94))
spring(CX+2.9,35.8,3.4,14.2,turns=38*(35.8-(CX+2.9))/(35.8-(rest+2.9)))
# ================= world / lights / camera =================
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; nt=w.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
tc=nt.nodes.new('ShaderNodeTexCoord'); sep=nt.nodes.new('ShaderNodeSeparateXYZ'); mp_=nt.nodes.new('ShaderNodeMapRange')
cr=nt.nodes.new('ShaderNodeValToRGB'); bg=nt.nodes.new('ShaderNodeBackground'); out=nt.nodes.new('ShaderNodeOutputWorld')
nt.links.new(tc.outputs['Generated'],sep.inputs[0]); nt.links.new(sep.outputs['Z'],cr.inputs['Fac'])
cr.color_ramp.elements[0].position=0.35; cr.color_ramp.elements[0].color=(0.10,0.10,0.11,1)
cr.color_ramp.elements[1].position=0.62; cr.color_ramp.elements[1].color=(1.0,1.0,1.0,1)
e=cr.color_ramp.elements.new(0.5); e.color=(0.55,0.56,0.58,1)
nt.links.new(cr.outputs['Color'],bg.inputs['Color']); bg.inputs['Strength'].default_value=0.9; nt.links.new(bg.outputs['Background'],out.inputs['Surface'])
def area(name,loc,tgt,size,energy,col=(1,1,1),shape='RECTANGLE',sy=None,cam=False):
    l=bpy.data.lights.new(name,'AREA'); l.energy=energy; l.size=size; l.color=col
    if sy: l.shape='RECTANGLE'; l.size_y=sy
    o=bpy.data.objects.new(name,l); sc.collection.objects.link(o); o.location=loc
    o.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); o.visible_camera=cam; return o
area('key',(-14,-46,58),(22,5,12),40,190000,(1.0,0.97,0.93),sy=26)
area('fill',(66,-40,30),(22,5,12),36,50000,(0.92,0.96,1.0),sy=20)
area('top',(22,10,80),(22,5,12),50,60000,sy=30)
area('rim',(22,48,38),(22,5,14),50,70000,sy=14)
# shadow catcher
bpy.ops.mesh.primitive_plane_add(size=400,location=(22,5,-0.7)); g=bpy.context.object; g.is_shadow_catcher=True
bpy.ops.mesh.primitive_plane_add(size=400,location=(22,5,-0.71)); 
cam=bpy.data.cameras.new('cam'); co=bpy.data.objects.new('cam',cam); sc.collection.objects.link(co); sc.camera=co
V=dict(hero=((36,-62,40),(22.5,4.8,12.8),42),cart=((CX+9,-30,25),(CX,4.5,15.0),50),right=((44,-30,28),(38,5.0,14.5),50),motor=((36,-26,26),(31,6,17),50))
loc,tgt,lens=V[VIEW]; cam.lens=lens; co.location=loc; co.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
cam.dof.use_dof=True; cam.dof.focus_distance=(Vector(tgt)-Vector(loc)).length; cam.dof.aperture_fstop=22
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=SMP; sc.cycles.use_denoising=True
try: sc.cycles.denoiser='OPENIMAGEDENOISE'
except: pass
sc.cycles.max_bounces=6; sc.cycles.glossy_bounces=5; sc.cycles.caustics_reflective=False; sc.cycles.caustics_refractive=False
sc.render.film_transparent=True; sc.render.resolution_x=RX; sc.render.resolution_y=RY; sc.render.resolution_percentage=100
sc.view_settings.view_transform='Khronos PBR Neutral'; sc.view_settings.exposure=0.0
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'; sc.render.filepath=OUT
# export projected anchors
from bpy_extras.object_utils import world_to_camera_view
anch=dict(support=(3,3.4,20),mass=(CX,5.4,17.5),spring0=((7.9+CX-2.9)/2,3.4,14.2),spring1=((CX+2.9+35.8)/2,3.4,14.2),motor=(MX,MY,20.2),estop=(EX,EY,16.9),brR=(35.6,4.9,11.5),brL=(7.2,3.5,11.5),rail=(12,3.6,9.7),frame=(24,0.5,5),cart=(CX,3.4,12.5),ruler=(18.4,1.0,9.2),thumb=(CX+2.9,3.4,14.2))
pr={}
for k,v in anch.items():
    p=world_to_camera_view(sc,co,Vector(v)); pr[k]=[round(p.x,4),round(1-p.y,4)]
json.dump(pr,open(OUT.replace('.png','.json'),'w'))
bpy.ops.render.render(write_still=True)
print('done',OUT)

"""Deterministic editable mesh sources. Y up, face towards -Z, Roblox stud scale.
Run with Python 3; no third-party packages. OBJ groups preserve editable components.
"""
import math, random, pathlib, json
ROOT=pathlib.Path(__file__).resolve().parents[1]/'assets'/'meshes'
ROOT.mkdir(parents=True,exist_ok=True)
PALETTE={'moss':(0.48,.62,.22),'moss_light':(.57,.69,.27),'cream':(.94,.86,.66),
 'eye':(.12,.085,.055),'glint':(1,.96,.82),'cheek':(.85,.51,.38),
 'wood':(.40,.25,.13),'bark':(.49,.31,.17),'bark_light':(.57,.38,.22),
 'cut':(.74,.55,.31),'leaf':(.39,.55,.17),'red':(.79,.27,.12),
 'stone':(.29,.29,.33),'stone_light':(.37,.36,.39),'copper':(1,.40,.09),'copper_light':(1,.64,.23)}
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def mul(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a):return mul(a,1/math.sqrt(dot(a,a)))
class Mesh:
 def __init__(self,name):self.name=name;self.v=[];self.faces=[]
 def face(self,points,group,mat):
  start=len(self.v);self.v.extend(points);self.faces.append((tuple(range(start,start+len(points))),group,mat))
 def ellipsoid(self,group,center,size,mat,segments=16,rings=10,rough=0,seed=1):
  rng=random.Random(seed);rows=[]
  for j in range(1,rings):
   lat=-math.pi/2+j*math.pi/rings;row=[]
   for i in range(segments):
    a=i*2*math.pi/segments;r=1+rng.uniform(-rough,rough)
    row.append(add(center,(math.cos(a)*math.cos(lat)*size[0]*r/2,math.sin(lat)*size[1]*r/2,math.sin(a)*math.cos(lat)*size[2]*r/2)))
   rows.append(row)
  top=add(center,(0,size[1]/2,0));bottom=add(center,(0,-size[1]/2,0))
  for i in range(segments):
   k=(i+1)%segments
   self.face([bottom,rows[0][i],rows[0][k]],group,mat)
   self.face([top,rows[-1][k],rows[-1][i]],group,mat)
   for j in range(len(rows)-1):
    a,b,c,d=rows[j][i],rows[j+1][i],rows[j+1][k],rows[j][k]
    self.face([a,b,c],group,mat);self.face([a,c,d],group,mat)
 def tube(self,group,a,b,r1,r2,mat,sides=8):
  direction=norm(sub(b,a));u=norm(cross(direction,(1,0,0) if abs(direction[1])>.95 else (0,1,0)));v=cross(direction,u)
  rings=[]
  for center,r in [(a,r1),(b,r2)]:
   rings.append([add(center,mul(add(mul(u,math.cos(i*math.tau/sides)),mul(v,math.sin(i*math.tau/sides))),r)) for i in range(sides)])
  for i in range(sides):
   k=(i+1)%sides
   self.face([rings[0][i],rings[0][k],rings[1][k],rings[1][i]],group,mat)
  self.face(list(reversed(rings[0])),group,mat);self.face(rings[1],group,mat)
 def leaf(self,group,a,b,width,mat='leaf'):
  mid=mul(add(a,b),.5);side=norm(cross(norm(sub(b,a)),(0,0,1)))
  left=add(mid,mul(side,width/2));right=sub(mid,mul(side,width/2));ridge=add(mid,(0,0,-.09))
  for p in [(a,left,ridge),(left,b,ridge),(b,right,ridge),(right,a,ridge),(a,right,b),(a,b,left)]:self.face(p,group,mat)
 def save(self):
  unique=[];lookup={};remap={}
  for i,p in enumerate(self.v):
   key=tuple(round(n,7) for n in p)
   if key not in lookup:lookup[key]=len(unique);unique.append(p)
   remap[i]=lookup[key]
  self.faces=[(tuple(remap[i] for i in f),g,m) for f,g,m in self.faces];self.v=unique
  target=ROOT/self.name;target.mkdir(exist_ok=True)
  path=target/(self.name+'.obj');lines=['# Y-up; front -Z; units: studs','mtllib ../shared/palette.mtl']
  lines+=['v '+' '.join(f'{x:.6f}' for x in p) for p in self.v]
  current=None
  for inds,group,mat in self.faces:
   if current!=(group,mat):lines+=['g '+group,'usemtl '+mat,'s off'];current=(group,mat)
   lines.append('f '+' '.join(str(i+1) for i in inds))
  path.write_text('\n'.join(lines),encoding='utf-8')
  for p in self.v:assert all(math.isfinite(x) for x in p)
  self.preview()
  return {'file':path.name,'triangles':sum(len(f[0])-2 for f in self.faces),'groups':len(set(f[1] for f in self.faces))}
 def preview(self):
  # Orthographic geometry proof, not a lighting or game-quality render.
  paths=[]
  for view,angle in enumerate([0,.65,math.pi]):
   ca,sa=math.cos(angle),math.sin(angle)
   def project(p):
    x,y,z=p;return (x*ca+z*sa,y,-x*sa+z*ca)
   faces=[]
   for inds,_,mat in self.faces:
    ps=[project(self.v[i]) for i in inds]
    normal=cross(sub(ps[1],ps[0]),sub(ps[2],ps[0]));ln=math.sqrt(dot(normal,normal))
    shade=.68+.32*abs(dot(normal,(.3,.65,-.7)))/(ln or 1)
    rgb=PALETTE[mat];color='#'+''.join(f'{min(255,int(c*255*shade)):02x}' for c in rgb)
    pts=' '.join(f'{200+view*400+p[0]*65:.2f},{390-p[1]*65:.2f}' for p in ps)
    faces.append((sum(p[2] for p in ps)/len(ps),f'<polygon points="{pts}" fill="{color}"/>'))
   paths += [p for _,p in sorted(faces,reverse=True)]
  svg='<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="440" viewBox="0 0 1200 440"><rect width="1200" height="440" fill="#d7d1c4"/>'+''.join(paths)+'</svg>'
  (ROOT/self.name/(self.name+'-views.svg')).write_text(svg,encoding='utf-8')
def moss():
 m=Mesh('MossCompanion');m.ellipsoid('body',(0,1.48,0),(2.65,2.62,2.40),'moss',24,16,rough=.025)
 m.ellipsoid('cream_face',(0,1.43,-.92),(1.96,1.79,.65),'cream',24,16)
 rng=random.Random(14)
 for i in range(100):
  a=rng.uniform(0,math.tau);lat=rng.uniform(-1,1.25)
  x=math.cos(a)*math.cos(lat)*1.25;y=1.48+math.sin(lat)*1.26;z=math.sin(a)*math.cos(lat)*1.13
  if z<-.55 and abs(x)<.95 and y<2.35:continue
  m.ellipsoid('moss_clumps',(x,y,z),(.32,.27,.31),'moss_light' if i%3==0 else 'moss',7,4)
 for sign in [-1,1]:
  x=sign*.43
  m.ellipsoid('eyes',(x,1.60,-1.247),(.29,.39,.17),'eye',16,12)
  m.ellipsoid('eye_glints',(x-.045,1.70,-1.324),(.062,.075,.025),'glint',8,6)
  m.ellipsoid('blush',(sign*.74,1.28,-1.17),(.29,.17,.065),'cheek',12,8)
  m.ellipsoid('feet',(sign*.63,.23,-.1),(.57,.46,.68),'wood',12,8)
  m.ellipsoid('paw_right' if sign==1 else 'paw_left',(sign*1.1,.91,-.25),(.42,.6,.45),'moss',12,8)
  a=(sign*.62,2.55,0);b=(sign*.81,3.26,.02);c=(sign*.76,3.51,.02)
  m.tube('antler',a,b,.13,.10,'wood');m.tube('antler',b,c,.1,.07,'wood')
  m.leaf('antler_leaf',b,(sign*1.32,3.56,.02),.43)
  m.leaf('antler_leaf',b,(sign*.42,3.75,.02),.36)
 for a,b in [((-.19,1.34,-1.265),(-.10,1.26,-1.28)),((-.10,1.26,-1.28),(0,1.32,-1.29)),((0,1.32,-1.29),(.1,1.26,-1.28)),((.1,1.26,-1.28),(.19,1.34,-1.265))]:m.tube('mouth',a,b,.025,.025,'eye',6)
 return m
def ore():
 m=Mesh('CopperOutcrop')
 for i,(p,s) in enumerate([((-1,1.5,.3),(2.3,3,2.5)),((.6,1.2,-.2),(2.4,2.4,2.5)),((.1,2.3,.6),(2,2.5,2)),((-1.5,.6,-.9),(1.7,1.2,1.6)),((1.5,.65,.1),(1.5,1.3,1.8))]):
  m.ellipsoid('rock_'+str(i),p,s,'stone_light' if i%2 else 'stone',7,5,.12,i+4)
 for i,p in enumerate([(-1.2,1.5,-.95),(-.4,.7,-1.25),(.8,1.7,-1.1),(1.5,.6,-.7),(-.1,2.9,-.1),(-1.7,.5,-.4)]):
  m.ellipsoid('copper_'+str(i),p,(.64,.85,.55),'copper',6,4,.12,i)
  m.ellipsoid('copper_highlight_'+str(i),add(p,(-.12,.15,-.18)),(.25,.35,.17),'copper_light',5,3)
 return m
def penkun():
 m=Mesh('Penkun');m.tube('trunk',(0,.7,0),(0,3.4,0),1.48,1.2,'wood',12)
 for i in range(12):
  a=i*math.tau/12;radius=1.29
  p=(math.sin(a)*radius,1.98,math.cos(a)*radius)
  m.ellipsoid('bark_panel_'+str(i),p,(.83,2.75,.57),'bark_light' if i%3==0 else 'bark',6,5,.04,i)
 m.tube('cut_surface',(0,3.39,0),(0,3.49,0),1.22,1.20,'cut',16)
 for r in [.35,.67,.98]:
  for i in range(24):
   a=i*math.tau/24;b=(i+1)*math.tau/24
   m.tube('growth_rings',(r*math.cos(a),3.505,r*math.sin(a)),(r*math.cos(b),3.505,r*math.sin(b)),.013,.013,'bark',4)
 m.ellipsoid('face_recess',(0,2.02,-1.42),(2.12,.83,.20),'eye',16,8)
 for sign in [-1,1]:
  m.ellipsoid('eye',(sign*.56,2.03,-1.53),(.47,.40,.12),'cream',12,8)
  m.ellipsoid('pupil',(sign*.56,2.06,-1.60),(.18,.30,.06),'eye',12,8)
  m.tube('angry_brow',(sign*.13,2.32,-1.6),(sign*1.04,2.69,-1.48),.20,.26,'bark',5)
  m.ellipsoid('foot',(sign*.77,.30,-.15),(1.02,.60,1.24),'wood',10,7)
  m.tube('leg',(sign*.77,.38,0),(sign*.77,1.0,0),.33,.29,'wood',8)
  a=(sign*1.32,2.65,0);b=(sign*1.94,1.75,-.1);c=(sign*2.05,1.13,-.4)
  m.tube('arm',a,b,.23,.17,'bark');m.tube('forearm',b,c,.17,.12,'wood')
  for j in range(3):m.tube('finger',c,(sign*(1.88+j*.14),.85,-.61+j*.12),.08,.045,'wood',6)
  m.leaf('arm_leaf',b,(sign*2.4,2.2,0),.35)
  m.ellipsoid('moss_patch',(sign*1.05,3.05,-.65),(.66,.20,.52),'moss',7,4)
 m.tube('sprout',(-.35,3.5,0),(-.35,4.52,0),.09,.055,'leaf')
 m.leaf('sprout_leaf',(-.35,3.95,0),(-.98,4.85,0),.55)
 m.leaf('sprout_leaf',(-.35,4.05,0),(.37,4.75,0),.55)
 m.tube('mushroom_stem',(.7,3.45,.15),(.81,4.0,.15),.15,.11,'cream')
 m.ellipsoid('mushroom_cap',(.81,4.02,.15),(1.05,.61,.95),'red',10,5)
 for x,z in [(.64,-.02),(.97,.2)]:m.ellipsoid('mushroom_spot',(x,4.29,z),(.16,.035,.18),'cream',7,4)
 return m
if __name__=='__main__':
 (ROOT/'shared').mkdir(exist_ok=True)
 (ROOT/'shared'/'palette.mtl').write_text('\n'.join(f'newmtl {name}\nKd {r} {g} {b}\nKa 0 0 0\nKs 0 0 0\nd 1\nillum 1\n' for name,(r,g,b) in PALETTE.items()),encoding='utf-8')
 result=[model.save() for model in [moss(),ore(),penkun()]]
 (ROOT/'manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

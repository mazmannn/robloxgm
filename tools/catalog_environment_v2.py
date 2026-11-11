from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,math
root=Path(__file__).resolve().parents[1]/'assets/meshes/EnvironmentV2'
items=json.loads((root/'manifest.json').read_text())
labels={'WayfarerTree':'Древо путников','BiomeGate':'Ворота к биомам','Pine':'Ель','BroadleafTree':'Лиственное дерево','Lantern':'Фонарь','Fence':'Ограда','Paving':'Мощение','Bridge':'Мост','RockCluster1':'Скалы A','RockCluster2':'Скалы B','RockCluster3':'Скалы C','HouseBrown':'Дом • дерево','HouseRed':'Дом • красная крыша','HouseBlue':'Дом • крыльцо','HouseGreen':'Дом • травы','Forge':'Кузница','Alchemist':'Алхимик','PetKeeper':'Смотритель питомцев','ResourceStall':'Торговец ресурсами'}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',34)
def sheet(selected,name,cols=4,cell=360):
 rows=math.ceil(len(selected)/cols)
 out=Image.new('RGB',(cols*cell,rows*(cell+50)+100),(229,225,213));d=ImageDraw.Draw(out)
 d.text((25,20),'RO B L O X  /  ENVIRONMENT V2'.replace('RO B L O X','ROBLOX'),font=title,fill=(57,63,57))
 d.text((27,65),'Новая геометрия • реальные рендеры Blender • без реалистичных текстур',font=small,fill=(80,86,77))
 for i,item in enumerate(selected):
  key=item['name'];x=(i%cols)*cell;y=100+(i//cols)*(cell+50)
  d.rounded_rectangle((x+8,y+8,x+cell-8,y+cell+42),radius=12,fill=(241,237,227))
  im=Image.open(root/key/(key+'.png')).convert('RGBA');im.thumbnail((cell-18,cell-18))
  out.paste(im,(x+(cell-im.width)//2,y+8),im)
  d.text((x+19,y+cell-3),labels[key],font=font,fill=(54,61,54))
  d.text((x+20,y+cell+24),f'{item["triangles"]:,} triangles / .blend + .glb',font=small,fill=(104,109,98))
 out.save(root/name)
sheet(items,'catalog.png')
sheet([i for i in items if i['name'] in ['Forge','Alchemist','PetKeeper','ResourceStall','HouseBrown','HouseRed','HouseBlue','HouseGreen']],'architecture.png',4,420)

from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,math
root=Path(__file__).resolve().parents[1]/'assets'/'meshes'/'Environment'
items=json.loads((root/'manifest.json').read_text())
sheet=Image.new('RGB',(1200,math.ceil(len(items)/5)*265),(220,216,203))
draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
for i,item in enumerate(items):
 name=item['name'];im=Image.open(root/name/(name+'.png')).convert('RGBA');im.thumbnail((232,232))
 x=(i%5)*240+(240-im.width)//2;y=(i//5)*265
 sheet.paste(im,(x,y),im);draw.text(((i%5)*240+10,y+237),name,font=font,fill=(35,42,35))
sheet.save(root/'catalog.png')

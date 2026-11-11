from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
base=Path(__file__).resolve().parents[1]
root=base/'assets/meshes/CopperOutcropV2'
sheet=Image.new('RGB',(1500,650),(224,221,216));d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26)
ref=Image.open(base.parent/'ideas/Концепт-лист светящейся медной руды.png').convert('RGBA').crop((10,45,575,585))
old=Image.open(base/'assets/meshes/CopperOutcrop/CopperOutcrop-blender.png').convert('RGBA')
new=Image.open(root/'CopperOutcropV2.png').convert('RGBA')
for i,(label,im) in enumerate([('Референс PNG',ref),('Предыдущая модель',old),('Новая модель V2',new)]):
 if i:im=im.crop(im.getbbox())
 im.thumbnail((470,540));sheet.paste(im,(i*500+(500-im.width)//2,80+(540-im.height)//2),im)
 d.text((i*500+25,25),label,font=font,fill=(42,40,44))
sheet.save(root/'comparison.png')

"""Rasterize our geometry proof SVGs; does not modify input reference images."""
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
folder=Path(__file__).resolve().parents[1]/'assets'/'meshes'
for file in folder.rglob('*-views.svg'):
    canvas=Image.new('RGB',(2400,880),'#d7d1c4');draw=ImageDraw.Draw(canvas)
    for node in ET.parse(file).getroot():
        if node.tag.endswith('polygon'):
            points=[tuple(float(n)*2 for n in p.split(',')) for p in node.attrib['points'].split()]
            draw.polygon(points,fill=node.attrib['fill'])
    canvas.resize((1200,440),Image.Resampling.LANCZOS).save(file.with_suffix('.png'))

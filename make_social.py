#!/usr/bin/env python3
"""Render a branded open-graph preview card from the licensed home photo."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
base=Path(__file__).parent/'docs'/'assets'
canvas=Image.new('RGB',(1200,630),'#0a5965')
photo=Image.open(base/'home.jpg')
photo=ImageOps.fit(photo,(530,630),method=Image.Resampling.LANCZOS,centering=(.5,.48))
canvas.paste(photo,(670,0))
d=ImageDraw.Draw(canvas)
large=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',65)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',25)
medium=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',27)
d.rounded_rectangle((65,65,122,122),radius=15,fill='#f5b44a')
d.ellipse((83,83,104,104),fill='#0a5965')
d.text((143,68),'SCHWERMAN',font=medium,fill='white')
d.text((143,99),'PLUMBING CO.',font=small,fill='#cce6e2')
d.text((67,230),'Plumbing help',font=large,fill='white')
d.text((67,314),'starts local.',font=large,fill='#f5b44a')
d.text((68,440),'Lindenhurst · Lake · Cook · DuPage',font=small,fill='#e1f3ef')
d.text((68,540),'INDEPENDENT WEBSITE PREVIEW',font=small,fill='#e1f3ef')
canvas.save(base/'schwerman-social.jpg',quality=86,optimize=True,progressive=True)
print(base/'schwerman-social.jpg', (base/'schwerman-social.jpg').stat().st_size)

#!/usr/bin/env python3
"""Download distinct, source-tracked illustrative Pexels photos for this preview.

License: https://www.pexels.com/license/ (free use; no implied endorsement).
Photographs are illustrative stock, never represented as Schwerman job photos.
"""
from pathlib import Path
import subprocess
from PIL import Image, ImageOps, ImageDraw
import json

HERE=Path(__file__).parent
DEST=HERE/'docs'/'assets'
PHOTO_IDS={
 'home':(6419128,'Plumber installing pipe fittings'),
 'story':(39885416,'Close-up of plumber working with copper pipe'),
 'about-us':(29226620,'Plumber installing a radiator pipe; illustrative of the trade, not the company'),
 'services':(14953886,'Wrench and pipes on sketch'),
 'emergency-plumbing':(18274115,'Leaking water pipe close-up'),
 'drain-cleaning':(220612,'Stainless steel sink drain'),
 'sewer-repair':(13961561,'Sewer entrance cap'),
 'water-main-repair':(12880833,'Workers repairing a pipe'),

 'water-heaters':(9551366,'Gray water heater in bathroom'),
 'remodeling':(40701258,'Modern bathroom renovation'),
 'new-construction':(8488035,'Metal pipes on wall'),
 'backflow-prevention':(12265849,'Valve on a pipe; not necessarily a backflow assembly'),
 'commercial-plumbing':(5711732,'Large pipes for industrial machinery'),
 'service-areas':(6690335,'Residential street; not represented as Lindenhurst'),
 'tips':(8488058,'Plumbers wrench on wood surface'),
 'faq':(28169591,'Copper plumbing fittings'),
 'contact-us':(8486978,'Handywoman holding plumbers wrench'),
}


def build():
    DEST.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for name,(photo_id,caption) in PHOTO_IDS.items():
        url=f'https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&w=1500'
        target=DEST/f'{name}.jpg'
        if not target.exists():
            temp=DEST/f'.{name}.download'
            subprocess.run(['curl','-fLsS','--max-time','30','-o',str(temp),url],check=True)
            image=ImageOps.exif_transpose(Image.open(temp)).convert('RGB')
            if min(image.size)<600:raise RuntimeError(f'Insufficient source resolution for {name}: {image.size}')
            image.thumbnail((1600,1600),Image.Resampling.LANCZOS)
            image.save(target,'JPEG',quality=82,optimize=True,progressive=True)
            temp.unlink()
        image=Image.open(target);print(name,photo_id,image.size,target.stat().st_size)
        manifest.append({'file':target.name,'photo_id':photo_id,'subject':caption,'source_page':f'https://www.pexels.com/photo/{photo_id}/','license':'https://www.pexels.com/license/','dimensions':list(image.size)})
    # Exact residential sump-pump image: author and CC BY-SA terms verified on Commons.
    commons_api='https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&pageids=135307237&iiprop=url%7Cextmetadata&iiurlwidth=1500&format=json'
    data=json.loads(subprocess.run(['curl','-fLsS','--max-time','30',commons_api],capture_output=True,text=True,check=True).stdout)
    info=data['query']['pages']['135307237']['imageinfo'][0]
    url=info.get('thumburl',info['url'])
    target=DEST/'sump-pumps.jpg'
    temp=DEST/'.sump-pumps.download'
    subprocess.run(['curl','-fLsS','--max-time','30','-o',str(temp),url],check=True)
    image=ImageOps.exif_transpose(Image.open(temp)).convert('RGB')
    if min(image.size)<600:raise RuntimeError(f'Insufficient sump photo resolution: {image.size}')
    image.thumbnail((1600,1600),Image.Resampling.LANCZOS)
    image.save(target,'JPEG',quality=82,optimize=True,progressive=True)
    temp.unlink()
    print('sump-pumps',135307237,image.size,target.stat().st_size)
    manifest.append({'file':target.name,'photo_id':'Wikimedia Commons 135307237','subject':'Newly-installed residential sump pump in New Jersey (not a Schwerman project)','source_page':info['descriptionurl'],'license':'https://creativecommons.org/licenses/by-sa/4.0/','author':'Famartin','changes':'Resized, recompressed and cropped in website display','dimensions':list(image.size)})
    (HERE/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    thumb_w,thumb_h=235,180
    sheet=Image.new('RGB',(thumb_w*3,210*6),'#f5f5f5');d=ImageDraw.Draw(sheet)
    for n,item in enumerate(manifest):
        image=Image.open(DEST/item['file']);image=ImageOps.fit(image,(thumb_w,thumb_h),method=Image.Resampling.LANCZOS)
        x=(n%3)*thumb_w;y=(n//3)*210
        sheet.paste(image,(x,y));d.text((x+5,y+183),item['file'],fill='#111')
    sheet.save(HERE/'contact-sheet.jpg',quality=85)
    print('Downloaded/verified',len(manifest),'unique image files')

if __name__=='__main__':build()

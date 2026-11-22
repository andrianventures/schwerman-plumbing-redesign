#!/usr/bin/env python3
"""Build-output checks for page parity, links, assets, metadata and schema."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json,sys
from content import PAGES

ROOT=Path(__file__).parent/'docs'
FILES=[ROOT/'index.html']+[ROOT/x/'index.html' for x in PAGES]
class Scan(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.images=[];self.meta={};self.h1=0;self.title=0;self.schemas=[];self.in_schema=False;self.buf='';self.ids=set()
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.add(d['id'])
  if tag=='a' and d.get('href'):self.links.append(d['href'])
  if tag=='img':self.images.append(d.get('src',''))
  if tag=='meta' and d.get('name'):self.meta[d['name']]=d.get('content')
  if tag=='title':self.title+=1
  if tag=='h1':self.h1+=1
  if tag=='script' and d.get('type')=='application/ld+json':self.in_schema=True;self.buf=''
 def handle_data(self,data):
  if self.in_schema:self.buf+=data
 def handle_endtag(self,tag):
  if tag=='script' and self.in_schema:self.schemas.append(json.loads(self.buf));self.in_schema=False

errs=[];photos=[];titles=[]
for f in FILES:
 if not f.exists():errs.append(f'Missing page {f}');continue
 html=f.read_text(encoding='utf-8');p=Scan();p.feed(html)
 titles.append(html.split('<title>',1)[-1].split('</title>',1)[0])
 if p.h1!=1 or p.title!=1:errs.append(f'{f}: expected one title/H1, got {p.title}/{p.h1}')
 if not p.meta.get('description'):errs.append(f'{f}: missing description')
 if p.meta.get('robots')!='noindex,nofollow':errs.append(f'{f}: preview noindex missing')
 if 'Firefly' in html:errs.append(f'{f}: stale template brand')
 if not p.schemas or not {'Plumber','WebPage','WebSite'}.issubset({node['@type'] for node in p.schemas[0]['@graph']}):errs.append(f'{f}: missing base schema')
 for url in p.images:
  parsed=urlparse(url)
  if '/assets/' not in parsed.path:errs.append(f'{f}: odd image URL {url}');continue
  name=parsed.path.split('/assets/',1)[1]
  if not (ROOT/'assets'/name).is_file():errs.append(f'{f}: broken image {name}')
  photos.append(name)
 for url in p.links:
  parsed=urlparse(url)
  if parsed.scheme in ('mailto','tel'):continue
  if parsed.netloc not in ('andrianventures.github.io','127.0.0.1'):continue
  if not parsed.path.startswith('/schwerman-plumbing-redesign/') and parsed.netloc!='127.0.0.1':continue
  path=parsed.path.removeprefix('/schwerman-plumbing-redesign/') if parsed.netloc!='127.0.0.1' else parsed.path.lstrip('/')
  target=ROOT/path/'index.html' if path.endswith('/') or not Path(path).suffix else ROOT/path
  if not target.is_file():errs.append(f'{f}: broken link {url}')
  if parsed.fragment and target.suffix=='.html' and f'id="{parsed.fragment}"' not in target.read_text(encoding='utf-8'):errs.append(f'{f}: missing anchor {url}')
if len(FILES)!=19:errs.append(f'Expected 19 pages, found {len(FILES)}')
if len(set(titles))!=len(titles):errs.append('Duplicate titles')
if len(photos)!=18 or len(set(photos))!=18:errs.append(f'Expected 18 unique in-page photos; got {len(photos)} placements / {len(set(photos))} distinct')
manifest=json.loads((Path(__file__).parent/'asset-manifest.json').read_text())
if {r['file'] for r in manifest}!=set(photos):errs.append('Asset manifest differs from rendered images')
print(f'Pages: {len(FILES)}; distinct titles: {len(set(titles))}; image placements: {len(photos)}; unique images: {len(set(photos))}; errors: {len(errs)}')
for err in errs:print('FAIL:',err)
sys.exit(bool(errs))

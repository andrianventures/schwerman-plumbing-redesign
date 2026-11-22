#!/usr/bin/env python3
"""Build the source-conscious, static Schwerman Plumbing proposal.

Set SCHWERMAN_BASE to the eventual HTTPS host before an owner-approved launch.
The default GitHub Pages build is noindex and cannot accept automatic forms.
"""
from pathlib import Path
from html import escape
import json, os, xml.etree.ElementTree as ET
from content import PAGES, AREAS

ROOT=Path(__file__).parent/'docs'
BASE=os.environ.get('SCHWERMAN_BASE','https://andrianventures.github.io/schwerman-plumbing-redesign/').rstrip('/')+'/'
PREVIEW='github.io' in BASE or BASE.startswith('http://localhost') or BASE.startswith('http://127.0.0.1')
NAME='Schwerman Plumbing Co.'
PHONE='+18477294244'
DISPLAY_PHONE='(847) 729-4244'
EMAIL='sales@schwermanplumbing.com'
FB='https://www.facebook.com/profile.php?id=100057115674045'
OFFICIAL='https://www.schwermanplumbing.com/'
NON_SERVICE={'about-us','services','service-areas','tips','faq','contact-us','privacy','accessibility'}
RELATED={
 'drain-cleaning':['sewer-repair','emergency-plumbing','services'],
 'sewer-repair':['drain-cleaning','sump-pumps','emergency-plumbing'],
 'sump-pumps':['water-main-repair','emergency-plumbing','services'],
 'water-heaters':['emergency-plumbing','remodeling','services'],
 'remodeling':['new-construction','water-heaters','services'],
 'new-construction':['commercial-plumbing','backflow-prevention','services'],
 'commercial-plumbing':['backflow-prevention','water-main-repair','services'],
 'backflow-prevention':['commercial-plumbing','new-construction','services'],
 'contact-us':['services','service-areas','faq'],
}

def u(slug=''): return BASE+(slug+'/' if slug else '')
def e(value): return escape(str(value),quote=True)
def l(slug,text,cls=''): return f'<a href="{u(slug)}" class="{cls}">{e(text)}</a>'
def img(file,alt,lazy=True,cls=''):
    return f'<img class="{cls}" src="{BASE}assets/{e(file)}" alt="{e(alt)}" width="1400" height="933" '+('loading="lazy"' if lazy else 'fetchpriority="high"')+'>'
def brand(): return '<span class="brand-mark" aria-hidden="true"></span><span class="brand-name">SCHWERMAN<small>PLUMBING CO.</small></span>'

def nav(active):
    links=[('services','Services'),('drain-cleaning','Drains'),('remodeling','Remodeling'),('service-areas','Service areas'),('about-us','About'),('contact-us','Contact')]
    items=''.join(f'<a href="{u(s)}"'+(' aria-current="page" class="current"' if s==active else '')+f'>{e(t)}</a>' for s,t in links)
    return f'''<a class="skip" href="#main">Skip to content</a><div class="utility"><div class="wrap"><span>Family-rooted plumbing · Northern Illinois</span><span>Need help? <a href="tel:{PHONE}">Call {DISPLAY_PHONE} <span aria-hidden="true">↗</span></a></span></div></div>
<header class="header"><div class="wrap head-inner"><a class="brand" href="{BASE}" aria-label="Schwerman Plumbing home">{brand()}</a><nav id="mainNav" class="main-nav" aria-label="Main navigation">{items}<a class="nav-cta" href="{u('contact-us')}#enquiry">Request service <span aria-hidden="true">↗</span></a></nav><div class="header-actions"><a class="header-book" href="{u('contact-us')}#enquiry">Request service <span aria-hidden="true">↗</span></a><a class="header-phone" href="tel:{PHONE}" aria-label="Call Schwerman Plumbing at {DISPLAY_PHONE}"><span aria-hidden="true">☎</span><span class="header-phone-text">{DISPLAY_PHONE}</span></a></div><button id="menuButton" class="menu-button" aria-expanded="false" aria-controls="mainNav" aria-label="Open menu"><span></span><span></span><span></span></button></div></header>'''

def footer():
    explore=[('services','All services'),('emergency-plumbing','Emergency plumbing'),('drain-cleaning','Drain rodding'),('sewer-repair','Sewer repairs'),('sump-pumps','Sump pumps'),('water-heaters','Water heaters')]
    company=[('about-us','About'),('service-areas','Service areas'),('tips','Tips'),('faq','FAQs'),('contact-us','Contact')]
    groups=[('Plumbing',explore),('Company',company)]
    group_html=''.join('<div><h2>'+e(label)+'</h2>'+''.join(l(s,t) for s,t in rows)+'</div>' for label,rows in groups)
    return f'''<footer class="footer"><div class="wrap"><div class="footer-top"><div class="footer-brand"><a class="brand" href="{BASE}">{brand()}</a><p>Plumbing repairs and projects across northern Illinois. Call to confirm coverage and availability.</p><a class="footer-phone" href="tel:{PHONE}">{DISPLAY_PHONE} <span aria-hidden="true">↗</span></a></div>{group_html}<div><h2>Contact</h2><a href="mailto:{EMAIL}">{EMAIL}</a><p>103 Hawthorne Drive<br>Lindenhurst, IL 60046<br>Call before visiting.</p><a href="{FB}" target="_blank" rel="noopener noreferrer">Facebook ↗</a></div></div><div class="footer-bottom"><span>© <span id="year"></span> {NAME}. Independent redesign preview; not yet approved by the business.</span><span>{l('privacy','Privacy')} · {l('accessibility','Accessibility')}</span></div></div></footer>'''

def schema(slug,title,desc,faq=None):
    business={'@type':'Plumber','@id':BASE+'#business','name':NAME,'url':BASE,'telephone':PHONE,'email':EMAIL,
      'address':{'@type':'PostalAddress','streetAddress':'103 Hawthorne Drive','addressLocality':'Lindenhurst','addressRegion':'IL','postalCode':'60046','addressCountry':'US'},
      'areaServed':[{'@type':'AdministrativeArea','name':x+' County, Illinois'} for x in ('Lake','Cook','DuPage')],
      'sameAs':[OFFICIAL,FB]}
    page={'@type':'WebPage','@id':u(slug)+'#webpage','url':u(slug),'name':title,'description':desc,'isPartOf':{'@id':BASE+'#website'},'about':{'@id':BASE+'#business'},'inLanguage':'en-US'}
    graph=[business,{'@type':'WebSite','@id':BASE+'#website','url':BASE,'name':NAME,'publisher':{'@id':BASE+'#business'}},page]
    if slug in PAGES and slug not in NON_SERVICE:
        graph.append({'@type':'Service','@id':u(slug)+'#service','name':title,'serviceType':title.split(' in ')[0],
          'provider':{'@id':BASE+'#business'},'areaServed':[{'@type':'AdministrativeArea','name':x+' County, Illinois'} for x in ('Lake','Cook','DuPage')]})
    if slug:
        graph.append({'@type':'BreadcrumbList','@id':u(slug)+'#breadcrumb','itemListElement':[
          {'@type':'ListItem','position':1,'name':'Home','item':BASE},
          {'@type':'ListItem','position':2,'name':title,'item':u(slug)}]})
    if faq:
        q,a=faq
        graph.append({'@type':'FAQPage','@id':u(slug)+'#faq','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}}]})
    return json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('</','<\\/')

def head(slug,title,desc,faq=None):
    full=title+' | '+NAME
    robots='noindex,nofollow' if PREVIEW or slug in ('privacy','accessibility') else 'index,follow,max-image-preview:large'
    social=BASE+'assets/schwerman-social.jpg'
    return f'''<!doctype html><html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(full)}</title><meta name="description" content="{e(desc)}"><meta name="robots" content="{robots}"><meta name="theme-color" content="#096f78"><link rel="canonical" href="{u(slug)}"><link rel="icon" type="image/svg+xml" href="{BASE}assets/favicon.svg"><link rel="stylesheet" href="{BASE}assets/style.css"><link rel="stylesheet" href="{BASE}assets/plumbing-theme.css"><meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}"><meta property="og:title" content="{e(full)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{u(slug)}"><meta property="og:image" content="{social}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Schwerman Plumbing website proposal"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(full)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{social}"><script type="application/ld+json">{schema(slug,title,desc,faq)}</script></head><body>{nav(slug)}'''

def end(): return f'{footer()}<script src="{BASE}assets/script.js" defer></script></body></html>'
def tiles(slugs):
    return '<div class="service-grid">'+''.join(f'<a class="service-card" href="{u(s)}"><span class="card-num">{n:02}</span><h3>{e(PAGES[s]["title"].split(" in ")[0].split(" | ")[0])}</h3><p>{e(PAGES[s]["desc"])}</p><span class="card-link">Explore service <span aria-hidden="true">↗</span></span></a>' for n,s in enumerate(slugs,1))+'</div>'

def inquiry(heading='Tell us what is going on.'):
    options=['Drain or sewer','Water heater','Sump pump / backup','Water main','Kitchen or bath remodel','New construction','Backflow','Other plumbing question']
    option_html='<option value="">Choose a service</option>'+''.join(f'<option>{e(x)}</option>' for x in options)
    return f'''<section class="inquiry" id="enquiry"><div class="wrap inquiry-grid"><div><span class="eyebrow light">START A CONVERSATION</span><h2>{e(heading)}</h2><p>Share the issue, your location and a way to reach you. For an active leak or sewer backup, please call instead.</p><a class="inquiry-phone" href="tel:{PHONE}">{DISPLAY_PHONE} <span aria-hidden="true">↗</span></a><p class="inquiry-aside">The original site advertises emergency service. Confirm current availability by phone.</p></div><form id="contactForm" action="/api/enquiries" method="post" novalidate><div class="honeypot" aria-hidden="true"><label>Leave empty<input name="website" tabindex="-1" autocomplete="off"></label></div><div class="fields"><label>Full name <em>*</em><input name="name" autocomplete="name" required maxlength="100"></label><label>Phone <em>*</em><input name="phone" type="tel" autocomplete="tel" required maxlength="30"></label><label>Email <em>*</em><input name="email" type="email" autocomplete="email" required maxlength="200"></label><label>City or ZIP <em>*</em><input name="location" autocomplete="address-level2" required maxlength="100"></label></div><label>What can we help with? <em>*</em><select name="service" required>{option_html}</select></label><label>Details <em>*</em><textarea name="message" rows="4" required maxlength="4000" placeholder="Fixture, symptoms, project stage or timing"></textarea></label><button type="submit" class="button amber">Prepare email draft <span aria-hidden="true">↗</span></button><div id="staticAlternatives" class="static-alternatives"><button type="button" id="smsRequest">Prepare text draft</button><button type="button" id="copyRequest">Copy request</button></div><p class="form-note" id="formMode">On this static preview, preparing a draft opens your email app. You must press Send there. You can also make a text draft or copy the request. Automatic delivery requires the bundled first-party Node server.</p><p class="form-status" role="status" aria-live="polite"></p></form></div></section>'''

def home():
    title='Plumber in Lindenhurst, IL | Lake County Plumbing Service'
    desc='Schwerman Plumbing Co. lists emergency repairs, drain and sewer work, sump pumps, water heaters, remodeling and new construction across Lake, Cook and DuPage counties. Call (847) 729-4244.'
    hero=f'''<main id="main"><section class="hero"><div class="hero-grid"><div class="hero-copy"><span class="eyebrow light">LINDENHURST, IL · PLUMBING SERVICE</span><h1>When plumbing gets complicated, <em>start local.</em></h1><p>From a blocked drain to a planned bathroom remodel, Schwerman Plumbing brings decades of published family history to northern Illinois. Tell us what needs attention.</p><div class="hero-actions"><a class="button amber hero-call" href="tel:{PHONE}"><span aria-hidden="true">☎</span> Call {DISPLAY_PHONE}</a><a class="button hero-request" href="{u('contact-us')}#enquiry">Request service <span aria-hidden="true">↗</span></a></div><div class="hero-proof"><span>Based in Lindenhurst</span><span>Lake · Cook · DuPage counties</span></div></div><div class="hero-visual">{img('home.jpg','Plumber working on a residential plumbing installation; illustrative stock photograph',False)}<span class="photo-tag">Illustrative stock photo</span></div></div></section>'''
    strip=f'''<div class="quick-strip"><div class="wrap"><div><span class="spark" aria-hidden="true">✳</span><p><b>Leak or backup right now?</b> The original site advertises same-day and emergency service. Call to confirm current availability.</p></div><a href="tel:{PHONE}">Call {DISPLAY_PHONE} <span aria-hidden="true">↗</span></a></div></div>'''
    services=f'''<section class="section services-section"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">WHAT WE CAN HELP WITH</span><h2>Repairs, projects<br><em>and the in-between.</em></h2></div><p>Choose the problem or project that sounds like yours. The team can confirm the next step and availability for your address.</p></div>{tiles(['emergency-plumbing','drain-cleaning','sewer-repair','sump-pumps','water-heaters','remodeling'])}<div class="section-tail">{l('services','Explore all plumbing services ↗')}</div></div></section>'''
    story=f'''<section class="split-story"><div class="story-photo">{img('story.jpg','Professional plumber working on water pipes; illustrative stock photograph')}<span class="photo-tag">Illustrative stock photo</span></div><div class="story-copy"><span class="eyebrow light">THE SCHWERMAN STORY</span><h2>Family roots. Practical plumbing.</h2><p>Schwerman’s published history begins with Robert H. Schwerman in 1954. Its service list has grown from everyday repairs to remodeling, new construction, sewer work and backflow questions.</p><ul><li>Describe what is happening, not a guessed fix</li><li>Ask what a proposed scope includes</li><li>Confirm availability before an urgent visit</li></ul>{l('about-us','Read the company story ↗','text-cta')}</div></section>'''
    areas=f'''<section class="areas-section section"><div class="wrap areas-grid"><div><span class="eyebrow">LINDENHURST & BEYOND</span><h2>One local address.<br><em>Three listed counties.</em></h2><p>The original contact page lists Lake, Cook and DuPage counties. Ask the team to confirm service at your exact address.</p>{l('service-areas','Explore the service area ↗','button outline')}</div><div class="area-list"><span>Lindenhurst</span><span>Lake County</span><span>Cook County</span><span>DuPage County</span><span>North Shore</span><span>Call to confirm</span></div></div></section>'''
    trust=f'''<section class="quote-section"><div class="wrap"><span class="eyebrow">A HISTORY FROM THE ORIGINAL SITE</span><blockquote>“The company you can count on.”</blockquote><p>Schwerman’s original website describes a family business founded in 1954. Its published customer comments are company-site testimonials, not independently verified Google reviews.</p>{l('about-us','Learn about Schwerman ↗')}</div></section>'''
    faq=f'''<section class="section faq-section"><div class="wrap faq-grid"><div><span class="eyebrow">QUICK ANSWERS</span><h2>Before you call.</h2><p>Useful details to have ready for a plumbing conversation.</p>{l('faq','See all FAQs ↗','text-cta')}</div><div><details open><summary>Do you handle emergency plumbing?</summary><p>The original Schwerman site advertises emergency and same-day service. Call {DISPLAY_PHONE} to confirm current availability.</p></details><details><summary>Which counties are listed?</summary><p>Its contact page lists Lake, Cook and DuPage counties. Call with your specific address.</p></details><details><summary>What can I include in a request?</summary><p>Your city or ZIP, the affected fixture or line, what you observe and the best number to reach you. For active flooding or sewage backups, call instead.</p></details></div></div></section>'''
    return head('',title,desc)+hero+strip+services+story+areas+trust+faq+inquiry('What needs attention?')+'</main>'+end()

def page(slug,data):
    title,desc=data['title'],data['desc']
    image=data['image']
    credit=('Photo: <a href="https://commons.wikimedia.org/wiki/Special:Redirect/page/135307237">Famartin / Wikimedia Commons</a> · <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> · resized for this page'
            if slug=='sump-pumps' else 'Illustrative stock photo')
    visual=f'<div class="inner-photo">{img(image,data["alt"],False)}<span class="photo-tag">{credit}</span></div>' if image else ''
    no_photo=' no-photo' if not image else ''
    hero=f'''<main id="main"><section class="inner-hero{no_photo}"><div class="wrap inner-grid"><div class="inner-copy"><div class="crumb"><a href="{BASE}">Home</a><span>/</span>{e(title)}</div><span class="eyebrow">SCHWERMAN · NORTHERN ILLINOIS</span><h1>{e(data['h1'])}</h1><p>{e(desc)}</p><div class="hero-actions"><a class="button amber" href="tel:{PHONE}">Call {DISPLAY_PHONE} <span aria-hidden="true">↗</span></a><a class="button outline" href="{u('contact-us')}#enquiry">Request service <span aria-hidden="true">↗</span></a></div></div>{visual}</div></section>'''
    paragraphs=''.join('<p>'+e(x)+'</p>' for x in data['text'])
    areas='<div class="area-list body-areas">'+''.join('<span>'+e(a)+'</span>' for a in AREAS)+'</div>' if slug=='service-areas' else ''
    body=f'''<section class="section body-section"><div class="wrap body-grid"><div><span class="eyebrow">{e(data['tag']).upper()}</span><h2>{e(title)}</h2>{paragraphs}{areas}</div><aside class="aside-panel"><span class="eyebrow light">GOOD TO KNOW</span><h3>Start with what matters.</h3><ul>{''.join('<li>'+e(x)+'</li>' for x in data['bullets'])}</ul><a href="tel:{PHONE}">Call {DISPLAY_PHONE} <span aria-hidden="true">↗</span></a></aside></div></section>'''
    if slug=='services':body+=f'''<section class="section related"><div class="wrap"><span class="eyebrow">EXPLORE BY SERVICE</span><h2>Find the right conversation.</h2>{tiles(['emergency-plumbing','drain-cleaning','sewer-repair','water-main-repair','sump-pumps','water-heaters','remodeling','new-construction','backflow-prevention','commercial-plumbing'])}</div></section>'''
    if slug=='faq':
        pairs=[('Is the service area limited to Lake County?','The original contact page lists Lake, Cook and DuPage counties, with the North Shore also mentioned on the about page. Call to confirm your address.'),('Do you handle sump pump backup systems?','Sump pumps and emergency backup systems appear on the company’s original service list. Confirm the current equipment and service scope.'),('Is the form an emergency line?','No. Call directly for a leak, sewage backup or other time-sensitive problem.'),('What if I am planning a remodel?','Share your current room, the changes you want, any plans or photos and your timeline. Ask for a project-specific scope.')]
        body+=f'''<section class="section faq-section"><div class="wrap faq-grid"><div><span class="eyebrow">MORE ANSWERS</span><h2>Good questions, clearer starts.</h2></div><div>{''.join('<details><summary>'+e(q)+'</summary><p>'+e(a)+'</p></details>' for q,a in pairs)}</div></div></section>'''
    q,a=data['faq']
    body+=f'''<section class="section single-faq"><div class="wrap"><span class="eyebrow">ONE QUICK ANSWER</span><h2>{e(q)}</h2><p>{e(a)}</p>{l('faq','More questions ↗')}</div></section>'''
    if slug not in ('services','privacy','accessibility','faq'):
        suggestions=RELATED.get(slug,['services','emergency-plumbing','service-areas'])
        body+=f'''<section class="section related"><div class="wrap"><span class="eyebrow">KEEP EXPLORING</span><h2>Related plumbing paths.</h2>{tiles(suggestions)}</div></section>'''
    form=inquiry('Send a non-urgent request.') if slug=='contact-us' else '' if slug in ('privacy','accessibility') else inquiry('Tell us what is going on.')
    return head(slug,title,desc,data['faq'])+hero+body+form+'</main>'+end()


def build():
    ROOT.mkdir(exist_ok=True)
    (ROOT/'index.html').write_text(home(),encoding='utf-8')
    for slug,data in PAGES.items():
        dest=ROOT/slug;dest.mkdir(exist_ok=True)
        (dest/'index.html').write_text(page(slug,data),encoding='utf-8')
    sm=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for slug in ['']+[s for s in PAGES if s not in ('privacy','accessibility')]:
        item=ET.SubElement(sm,'url');ET.SubElement(item,'loc').text=u(slug)
    ET.ElementTree(sm).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'sitemap.xml\n',encoding='utf-8')
    print('Generated',len(PAGES)+1,'HTML pages; base:',BASE,'preview noindex:',PREVIEW)

if __name__=='__main__':build()

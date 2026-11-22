// First-party, dependency-free form inbox for a Node-capable host.
// GitHub Pages cannot run this server; its form prepares visitor-sent drafts.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), 'docs');
const dataDir = process.env.SCHWERMAN_DATA_DIR || path.resolve(root, '..', '..', 'schwerman-private');
const password = process.env.SCHWERMAN_ADMIN_PASSWORD;
if (!password || password.length < 16) {
  console.error('Set SCHWERMAN_ADMIN_PASSWORD to a unique secret of 16+ characters.');
  process.exit(1);
}
fs.mkdirSync(dataDir, {recursive:true, mode:0o700});
const file = path.join(dataDir, 'enquiries.jsonl');
const mime = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.xml':'application/xml; charset=utf-8','.txt':'text/plain; charset=utf-8'};
const recent = new Map();
const escape = s => String(s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function reply(res, code, body, type='text/plain; charset=utf-8', extra={}) {
  res.writeHead(code, {'Content-Type':type,'X-Content-Type-Options':'nosniff','Referrer-Policy':'strict-origin-when-cross-origin',...extra});res.end(body);
}
function auth(req) {
  const h=req.headers.authorization || '';
  if (!h.startsWith('Basic ')) return false;
  let provided;
  try {provided=Buffer.from(h.slice(6),'base64').toString('utf8').split(':').slice(1).join(':');} catch {return false;}
  const a=crypto.createHash('sha256').update(provided).digest();
  const b=crypto.createHash('sha256').update(password).digest();
  return crypto.timingSafeEqual(a,b);
}
function inbox(req,res) {
  if (!auth(req)) return reply(res,401,'Owner sign-in required.','text/plain; charset=utf-8',{'WWW-Authenticate':'Basic realm="Schwerman owner inbox"','Cache-Control':'no-store'});
  const rows=fs.existsSync(file)?fs.readFileSync(file,'utf8').trim().split('\n').filter(Boolean).map(line=>JSON.parse(line)).reverse():[];
  const content=rows.map(r=>`<article><small>${escape(r.date)}</small><h2>${escape(r.name)}</h2><p><b>Phone:</b> ${escape(r.phone)}<br><b>Email:</b> ${escape(r.email)}<br><b>Location:</b> ${escape(r.location)}<br><b>Service:</b> ${escape(r.service)}</p><p class="message">${escape(r.message)}</p></article>`).join('');
  return reply(res,200,`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Schwerman owner inbox</title><style>body{font:16px/1.6 Arial;background:#f5f6f4;color:#132b38;max-width:800px;margin:30px auto;padding:16px}article{background:#fff;padding:24px;margin:20px 0;border:1px solid #ddd}.message{white-space:pre-wrap}small{color:#65737a}</style><h1>Schwerman owner inbox</h1><p>${rows.length} enquiries. Stored on this server; no email is sent.</p>${content||'<p>No enquiries yet.</p>'}</html>`,'text/html; charset=utf-8',{'Cache-Control':'no-store','X-Robots-Tag':'noindex, nofollow'});
}
async function submit(req,res) {
  if (req.headers.origin) {
    try {if (new URL(req.headers.origin).host !== req.headers.host) return reply(res,403,JSON.stringify({ok:false,error:'Invalid origin.'}),'application/json');}
    catch {return reply(res,403,JSON.stringify({ok:false,error:'Invalid origin.'}),'application/json');}
  }
  const ip=req.socket.remoteAddress || 'unknown';
  const now=Date.now();
  for (const [k,t] of recent) if (now-t>3600000) recent.delete(k);
  if (recent.has(ip) && now-recent.get(ip)<10000) return reply(res,429,JSON.stringify({ok:false,error:'Please wait before submitting again.'}),'application/json');
  let text='';
  try {for await (const chunk of req) {text+=chunk;if (text.length>16000) throw new Error('Too much content.');}}
  catch {return reply(res,413,JSON.stringify({ok:false,error:'Request too large.'}),'application/json');}
  if (!(req.headers['content-type']||'').startsWith('application/x-www-form-urlencoded')) return reply(res,415,JSON.stringify({ok:false,error:'Unsupported form encoding.'}),'application/json');
  const form=new URLSearchParams(text);
  if (form.get('website')) return reply(res,200,JSON.stringify({ok:true}),'application/json');
  const limits={name:100,phone:30,email:200,location:100,service:100,message:4000};
  const r={date:new Date().toISOString()};
  for (const [key,max] of Object.entries(limits)) {
    const val=(form.get(key)||'').trim();
    if (!val || val.length>max) return reply(res,400,JSON.stringify({ok:false,error:`Invalid ${key}.`}),'application/json');
    r[key]=val;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(r.email) || !/^[\d()+.\-\s]{7,30}$/.test(r.phone)) return reply(res,400,JSON.stringify({ok:false,error:'Check email and phone.'}),'application/json');
  try {fs.appendFileSync(file,JSON.stringify(r)+'\n',{mode:0o600});fs.chmodSync(file,0o600);recent.set(ip,now);}
  catch {return reply(res,503,JSON.stringify({ok:false,error:'The inbox is unavailable. Please call us.'}),'application/json');}
  return reply(res,201,JSON.stringify({ok:true}),'application/json',{'Cache-Control':'no-store'});
}
const server=http.createServer((req,res)=>{
  const pathname=new URL(req.url,'http://localhost').pathname;
  if (pathname==='/api/form-status') return req.method==='GET'?reply(res,200,JSON.stringify({firstParty:true}),'application/json; charset=utf-8',{'Cache-Control':'no-store'}):reply(res,405,'Method not allowed.');
  if (pathname==='/api/enquiries') return req.method==='POST'?submit(req,res):reply(res,405,'Method not allowed.');
  if (pathname==='/owner/inbox') return req.method==='GET'?inbox(req,res):reply(res,405,'Method not allowed.');
  if (!['GET','HEAD'].includes(req.method)) return reply(res,405,'Method not allowed.');
  let decoded;
  try {decoded=decodeURIComponent(pathname);} catch {return reply(res,400,'Bad request.');}
  if (decoded.includes('..') || decoded.includes('\\') || decoded.includes('\0')) return reply(res,403,'Forbidden.');
  const item=decoded.endsWith('/')?decoded+'index.html':decoded;
  const target=path.resolve(root,'.'+item);
  if (!(target===root || target.startsWith(root+path.sep)) || !mime[path.extname(target)] || target.endsWith('/build.py')) return reply(res,404,'Not found.');
  fs.stat(target,(err,st)=>{
    if (err || !st.isFile()) return reply(res,404,'Not found.');
    res.writeHead(200,{'Content-Type':mime[path.extname(target)],'Content-Length':st.size,'X-Content-Type-Options':'nosniff'});
    if (req.method==='HEAD') return res.end();
    fs.createReadStream(target).pipe(res);
  });
});
server.listen(Number(process.env.PORT||8080),process.env.HOST||'127.0.0.1',()=>console.log('Schwerman server ready on',server.address().address+':'+server.address().port));

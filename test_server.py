#!/usr/bin/env python3
"""End-to-end local test of first-party form storage and protected inbox."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode
import base64,json,os,secrets,socket,subprocess,sys,tempfile,time

ROOT=Path(__file__).parent
with socket.socket() as sock:
 sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}'
with tempfile.TemporaryDirectory(prefix='schwerman-test-',dir=os.environ.get('TMPDIR')) as tmp:
 password=secrets.token_urlsafe(32)
 env={**os.environ,'SCHWERMAN_BASE':base+'/','SCHWERMAN_ADMIN_PASSWORD':password,'SCHWERMAN_DATA_DIR':tmp,'PORT':str(port),'HOST':'127.0.0.1'}
 server=None
 try:
  subprocess.run([sys.executable,'build.py'],cwd=ROOT,env=env,check=True)
  server=subprocess.Popen(['node','server.mjs'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for attempt in range(50):
   try:
    with urlopen(base+'/api/form-status',timeout=1) as response:
     assert json.load(response)=={'firstParty':True};break
   except Exception:
    if server.poll() is not None:raise RuntimeError('Node server exited before readiness')
    time.sleep(.1)
  else:raise RuntimeError('Node server never became ready')
  data={'name':'Preview Test','phone':'8475550101','email':'preview-test@example.com','location':'Lindenhurst, IL','service':'Sump pump / backup','message':'Synthetic integration test; not a real customer request.'}
  request=Request(base+'/api/enquiries',data=urlencode(data).encode(),headers={'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','Accept':'application/json','Origin':base},method='POST')
  with urlopen(request,timeout=5) as response:
   assert response.status==201 and json.load(response)=={'ok':True}
  try:urlopen(base+'/owner/inbox',timeout=5)
  except HTTPError as exc:assert exc.code==401
  else:raise AssertionError('Unprotected inbox')
  token=base64.b64encode(('owner:'+password).encode()).decode()
  with urlopen(Request(base+'/owner/inbox',headers={'Authorization':'Basic '+token}),timeout=5) as response:
   inbox=response.read().decode();assert response.status==200 and 'Preview Test' in inbox and '1 enquiries' in inbox
  rows=(Path(tmp)/'enquiries.jsonl').read_text().splitlines()
  assert len(rows)==1 and json.loads(rows[0])['name']=='Preview Test'
  print('First-party form POST 201; private inbox 401 unauthenticated / 200 authenticated; one stored synthetic row.')
 finally:
  if server is not None:server.terminate();server.wait(timeout=5)
  subprocess.run([sys.executable,'build.py'],cwd=ROOT,env={k:v for k,v in os.environ.items() if k!='SCHWERMAN_BASE'},check=True)

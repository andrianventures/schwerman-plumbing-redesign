(() => {
  const menu=document.getElementById('menuButton');
  const nav=document.getElementById('mainNav');
  const closeMenu=()=>{menu?.setAttribute('aria-expanded','false');menu?.setAttribute('aria-label','Open menu');nav?.classList.remove('open')};
  menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?'Close menu':'Open menu');nav?.classList.toggle('open',open)});
  nav?.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
  document.addEventListener('keydown',event=>{if(event.key==='Escape')closeMenu()});
  document.getElementById('year')?.replaceChildren(String(new Date().getFullYear()));
  const form=document.getElementById('contactForm'); if(!form)return;
  const submit=form.querySelector('button[type=submit]');
  const note=document.getElementById('formMode');
  const status=form.querySelector('.form-status');
  const alternatives=document.getElementById('staticAlternatives');
  let serverMode=false;
  // The first-party Node host explicitly signals when automatic storage is available.
  if(location.protocol!=='file:')fetch('/api/form-status',{headers:{Accept:'application/json'},cache:'no-store'})
    .then(r=>r.ok?r.json():null).then(result=>{
      if(result?.firstParty!==true)return;
      serverMode=true;submit.firstChild.textContent='Send enquiry ';
      note.textContent='This form saves your enquiry in a private first-party owner inbox. It is not an emergency channel; call for urgent help.';
      alternatives.hidden=true;
    }).catch(()=>{});
  const PHONE='+18477294244', EMAIL='sales@schwermanplumbing.com';
  function requestText(data){return `Schwerman Plumbing service request\nName: ${data.get('name')}\nPhone: ${data.get('phone')}\nEmail: ${data.get('email')}\nCity/ZIP: ${data.get('location')}\nService: ${data.get('service')}\nDetails: ${data.get('message')}`}
  function valid(){if(!form.reportValidity())return false;if(form.elements.website.value)return false;return true}
  document.getElementById('smsRequest')?.addEventListener('click',()=>{
    if(!valid())return;
    const body=encodeURIComponent(requestText(new FormData(form)));
    status.textContent='Opening your messaging app. This page has NOT sent your request; press Send in your app. If it does not open, try Copy request or call.';
    location.href=`sms:${PHONE}?body=${body}`;
  });
  document.getElementById('copyRequest')?.addEventListener('click',async()=>{
    if(!valid())return;
    try{await navigator.clipboard.writeText(requestText(new FormData(form)));
      status.textContent='Copied. Paste into a message to (847) 729-4244 or an email to sales@schwermanplumbing.com and press Send.';
    }catch{status.textContent='Clipboard access was blocked. Select the form details manually or call (847) 729-4244.'}
  });
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(!valid())return;
    const data=new FormData(form);
    if(!serverMode){
      // Static GitHub Pages cannot deliver form submissions: visitor controls sending.
      const subject=encodeURIComponent('Schwerman Plumbing service request');
      const body=encodeURIComponent(requestText(data));
      status.textContent='Opening your email app. This page has NOT sent your request; press Send in your app. If it does not open, try Copy request or call.';
      location.href=`mailto:${EMAIL}?subject=${subject}&body=${body}`;
      return;
    }
    submit.disabled=true;status.textContent='Saving your enquiry…';
    try{
      const response=await fetch(form.action,{method:'POST',body:new URLSearchParams(data),headers:{Accept:'application/json','Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}});
      const result=await response.json();
      if(!response.ok||!result.ok)throw Error(result.error||'Unable to save.');
      status.textContent='Your enquiry was saved for the team. For an urgent problem, call (847) 729-4244.';
      form.reset();
    }catch(error){status.textContent=`${error.message} Please call (847) 729-4244 instead.`}
    finally{submit.disabled=false}
  });
})();

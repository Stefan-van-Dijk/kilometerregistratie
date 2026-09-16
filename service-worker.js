const CACHE='kmreg-shell-0.31.2';
const SHELL=['./','./index.html','./shell-ui.js','./shell-ui-fixes.js','./scroll-hotfix.js','./id-converter.html','./manifest.webmanifest','./app-icon.svg'];

function injectShellScript(response){
  if(!response)return response;
  const type=response.headers.get('content-type')||'';
  if(!type.includes('text/html'))return response;
  return response.text().then(html=>{
    let injection='';
    if(!html.includes('shell-ui.js'))injection+=`<style id="km-shell-bootstrap-style">body.km-shell-locations-mode #kmShellSettingsContent>#app{display:block!important}</style><script src="./shell-ui.js"></script><script>(()=>{let needs=false,saved=false,wasEditor=false;const setItem=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){const r=setItem.call(this,k,v);if(this===localStorage&&k==='kmreg-v4-data'&&needs)saved=true;return r};document.addEventListener('click',e=>{if(!e.target.closest?.('[data-action="save-location"]'))return;const f=document.getElementById('locationForm'),p=document.getElementById('kmShellParentId');if(!f||!p)return;let old='';try{const d=JSON.parse(localStorage.getItem('kmreg-v4-data')||'{}');old=(d.locations||[]).find(x=>x.id===f.elements.id?.value)?.parentId||''}catch(_){}needs=!!(old||p.value);saved=false;wasEditor=document.body.classList.contains('editor-view')});new MutationObserver(()=>{const editor=document.body.classList.contains('editor-view');if(needs&&saved&&wasEditor&&!editor){needs=false;localStorage.setItem('kmreg-shell-section-v1','locations');setTimeout(()=>location.reload(),100)}wasEditor=editor}).observe(document.body,{attributes:true,attributeFilter:['class']})})()</script>`;
    if(!html.includes('shell-ui-fixes.js'))injection+=`<script src="./shell-ui-fixes.js"></script>`;
    if(!html.includes('scroll-hotfix.js'))injection+=`<script src="./scroll-hotfix.js"></script>`;
    if(injection)html=html.replace('</body>',`${injection}</body>`);
    const headers=new Headers(response.headers);
    headers.delete('content-length');
    return new Response(html,{status:response.status,statusText:response.statusText,headers});
  });
}

self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(SHELL)).then(()=>self.skipWaiting()));
});

self.addEventListener('activate',event=>{
  event.waitUntil(
    caches.keys()
      .then(keys=>Promise.all(keys.filter(key=>key.startsWith('kmreg-shell-')&&key!==CACHE).map(key=>caches.delete(key))))
      .then(()=>self.clients.claim())
      .then(()=>self.clients.matchAll({type:'window'}))
      .then(clients=>Promise.all(clients.map(client=>client.navigate(client.url).catch(()=>null))))
  );
});

self.addEventListener('fetch',event=>{
  const req=event.request,url=new URL(req.url);
  if(req.method!=='GET'||url.origin!==self.location.origin)return;
  if(url.pathname.endsWith('/import.html'))return;
  if(url.pathname.endsWith('/id-converter.html')){
    event.respondWith(caches.match('./id-converter.html').then(cached=>cached||fetch(req)));
    return;
  }
  if(req.mode==='navigate'){
    event.respondWith(
      fetch(req)
        .then(resp=>{
          const copy=resp.clone();
          caches.open(CACHE).then(cache=>cache.put('./index.html',copy));
          return injectShellScript(resp);
        })
        .catch(async()=>injectShellScript(await caches.match('./index.html')))
    );
    return;
  }
  event.respondWith(caches.match(req).then(cached=>cached||fetch(req).then(resp=>{
    const copy=resp.clone();
    caches.open(CACHE).then(cache=>cache.put(req,copy));
    return resp;
  })));
});

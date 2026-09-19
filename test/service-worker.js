const CACHE='kmreg-test-shell-0.31.10-test.50';
const SHARED_UI='./log-ui.css?v=0.31.10-test.47';
const SHELL=['./','./index.html','./log-json-v2.js?v=2.0.0',SHARED_UI,'./shell-ui.js?v=0.31.10-test.34','./shell-ui-stable.js?v=0.31.10-test.47','./shell-gestures.js?v=0.31.10-test.47','./shell-time-layout.js?v=0.31.10-test.48','./shell-location-status.js?v=0.31.10-test.50','./id-converter.html','./manifest.webmanifest','./app-icon.svg','./config/modules.json','./time/index.html','./time/app.js','./time/styles.css','./time/home-layout.css','./time/home-layout.js','./time/home-top.css','./time/home-top.js'];

function injectShellScript(response){
  if(!response)return response;
  const type=response.headers.get('content-type')||'';
  if(!type.includes('text/html'))return response;
  return response.text().then(html=>{
    if(!html.includes('log-ui.css'))html=html.replace('</head>',`<link rel="stylesheet" href="./log-ui.css?v=0.31.10-test.47"></head>`);
    else html=html.replace(/log-ui\.css\?v=[^"'<>]+/g,'log-ui.css?v=0.31.10-test.47');
    html=html.replace(/shell-ui-stable\.js\?v=[^"'<>]+/g,'shell-ui-stable.js?v=0.31.10-test.47');
    html=html.replace(/shell-gestures\.js\?v=[^"'<>]+/g,'shell-gestures.js?v=0.31.10-test.47');
    html=html.replace(/shell-time-layout\.js\?v=[^"'<>]+/g,'shell-time-layout.js?v=0.31.10-test.48');
    html=html.replace(/shell-location-status\.js\?v=[^"'<>]+/g,'shell-location-status.js?v=0.31.10-test.50');
    let injection='';
    if(!html.includes('shell-ui.js'))injection+=`<style id="km-shell-bootstrap-style">#kmShellSettingsContent #app,#kmShellSettingsContent #timeAppFrame{display:block!important;visibility:visible!important;opacity:1!important}</style><script src="./shell-ui.js?v=0.31.10-test.34"></script><script>(()=>{let needs=false,saved=false,wasEditor=false;const setItem=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){const r=setItem.call(this,k,v);if(this===localStorage&&k==='kmreg-test-v4-data'&&needs)saved=true;return r};document.addEventListener('click',e=>{if(!e.target.closest?.('[data-action="save-location"]'))return;const f=document.getElementById('locationForm'),p=document.getElementById('kmShellParentId');if(!f||!p)return;let old='';try{const d=JSON.parse(localStorage.getItem('kmreg-test-v4-data')||'{}');old=(d.locations||[]).find(x=>x.id===f.elements.id?.value)?.parentId||''}catch(_){}needs=!!(old||p.value);saved=false;wasEditor=document.body.classList.contains('editor-view')});new MutationObserver(()=>{const editor=document.body.classList.contains('editor-view');if(needs&&saved&&wasEditor&&!editor){needs=false;localStorage.setItem('kmreg-test-shell-section-v1','locations');setTimeout(()=>location.reload(),100)}wasEditor=editor}).observe(document.body,{attributes:true,attributeFilter:['class']})})()</script>`;
    if(!html.includes('shell-ui-stable.js'))injection+=`<script src="./shell-ui-stable.js?v=0.31.10-test.47"></script>`;
    if(!html.includes('shell-gestures.js'))injection+=`<script src="./shell-gestures.js?v=0.31.10-test.47"></script>`;
    if(!html.includes('shell-time-layout.js'))injection+=`<script src="./shell-time-layout.js?v=0.31.10-test.48"></script>`;
    if(!html.includes('shell-location-status.js'))injection+=`<script src="./shell-location-status.js?v=0.31.10-test.50"></script>`;
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
      .then(keys=>Promise.all(keys.filter(key=>key.startsWith('kmreg-test-shell-')&&key!==CACHE).map(key=>caches.delete(key))))
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
  if(url.pathname.endsWith('/config/modules.json')){
    event.respondWith(
      fetch(req)
        .then(resp=>{
          if(!resp.ok)throw new Error('Menuconfiguratie niet beschikbaar');
          const copy=resp.clone();
          caches.open(CACHE).then(cache=>cache.put('./config/modules.json',copy));
          return resp;
        })
        .catch(()=>caches.match('./config/modules.json'))
    );
    return;
  }
  if(req.mode==='navigate'&&url.pathname.startsWith(new URL('./time/',self.registration.scope).pathname)){
    event.respondWith(
      fetch(req)
        .then(resp=>{
          const copy=resp.clone();
          caches.open(CACHE).then(cache=>cache.put('./time/index.html',copy));
          return resp;
        })
        .catch(()=>caches.match('./time/index.html'))
    );
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

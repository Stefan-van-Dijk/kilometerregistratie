const CACHE='kmreg-shell-0.31.0';
const SHELL=['./','./index.html','./shell-ui.js','./id-converter.html','./manifest.webmanifest','./app-icon.svg'];

function injectShellScript(response){
  if(!response)return response;
  const type=response.headers.get('content-type')||'';
  if(!type.includes('text/html'))return response;
  return response.text().then(html=>{
    if(!html.includes('shell-ui.js'))html=html.replace('</body>','<script src="./shell-ui.js"></script></body>');
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

const RESCUE='kmreg-rescue-2026-09-16-1';

self.addEventListener('install',event=>{
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate',event=>{
  event.waitUntil((async()=>{
    const keys=await caches.keys();
    await Promise.all(keys.filter(key=>key.startsWith('kmreg-shell-')).map(key=>caches.delete(key)));
    await self.clients.claim();
    const clients=await self.clients.matchAll({type:'window',includeUncontrolled:true});
    await Promise.all(clients.map(async client=>{
      try{
        const url=new URL(client.url);
        url.searchParams.set('_rescue',RESCUE);
        await client.navigate(url.href);
      }catch(_){ }
    }));
  })());
});

// Bewust geen fetch-handler: tijdens deze rescue wordt niets uit een service-worker-cache geserveerd.

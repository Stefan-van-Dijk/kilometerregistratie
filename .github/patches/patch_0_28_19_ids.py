from pathlib import Path

idx=Path('index.html')
s=idx.read_text()

repls=[]
repls.append(("document.getElementById('today').textContent=new Intl.DateTimeFormat('nl-NL',{weekday:'long',day:'numeric',month:'long'}).format(new Date())+' · 0.28.18';","document.getElementById('today').textContent=new Intl.DateTimeFormat('nl-NL',{weekday:'long',day:'numeric',month:'long'}).format(new Date())+' · 0.28.19';"))
repls.append(("function uid(){return window.crypto?.randomUUID?window.crypto.randomUUID():'id-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2)}","const ID_ALPHABET='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';\nfunction uid(){const bytes=new Uint8Array(12);if(window.crypto?.getRandomValues)window.crypto.getRandomValues(bytes);else for(let i=0;i<bytes.length;i++)bytes[i]=Math.floor(Math.random()*256);return Array.from(bytes,b=>ID_ALPHABET[b&63]).join('')}"))
repls.append(("else if(a==='merge-import')document.getElementById('mergeImportFile')?.click();else if(a==='csv')","else if(a==='merge-import')document.getElementById('mergeImportFile')?.click();else if(a==='id-converter')location.href='./id-converter.html';else if(a==='csv')"))
repls.append(("<button type=\"button\" class=\"btn secondary\" data-action=\"merge-import\">Gegevens toevoegen</button></div><div class=\"hint\" style=\"margin-top:10px\">","<button type=\"button\" class=\"btn secondary\" data-action=\"merge-import\">Gegevens toevoegen</button><button type=\"button\" class=\"btn secondary\" data-action=\"id-converter\">ID-converter</button></div><div class=\"hint\" style=\"margin-top:10px\">"))
old_track="function persistTrack(){if(!data.activeTrip||!gpsLatest)return;const minute=new Date().toISOString().slice(0,16),id=data.activeTrip.id+'_'+minute;if(data.trackPoints.some(x=>x.id===id))return;const point={id,tripId:data.activeTrip.id,time:new Date().toISOString(),lat:gpsLatest.lat,lng:gpsLatest.lng,accuracy:gpsLatest.accuracy??null};data.trackPoints.push(point);const pruned=data.trackPoints.length>20000;if(pruned)data.trackPoints=data.trackPoints.slice(-20000);try{save()}catch(e){}if(trackStoreReady)(pruned?replaceTrackStore(data.trackPoints):putTrackPoints([point])).catch(e=>console.warn('GPS-punt opslaan mislukt',e))}"
new_track="function trackMinuteKey(v){try{return new Date(v).toISOString().slice(0,16)}catch(_){return''}}\nfunction persistTrack(){if(!data.activeTrip||!gpsLatest)return;const minute=new Date().toISOString().slice(0,16);if(data.trackPoints.some(x=>x.tripId===data.activeTrip.id&&trackMinuteKey(x.time)===minute))return;const point={id:uid(),tripId:data.activeTrip.id,time:new Date().toISOString(),lat:gpsLatest.lat,lng:gpsLatest.lng,accuracy:gpsLatest.accuracy??null};data.trackPoints.push(point);const pruned=data.trackPoints.length>20000;if(pruned)data.trackPoints=data.trackPoints.slice(-20000);try{save()}catch(e){}if(trackStoreReady)(pruned?replaceTrackStore(data.trackPoints):putTrackPoints([point])).catch(e=>console.warn('GPS-punt opslaan mislukt',e))}"
repls.append((old_track,new_track))
old_point="let minute='';try{minute=new Date(candidate.time).toISOString().slice(0,16)}catch(_){}let id=minute?`${mappedTripId}_${minute}`:String(candidate.id||uid());if(pointIds.has(id)){stats.trackPointsSkipped++;continue}candidate.id=id;"
new_point="let id=String(candidate.id||'');if(!id||pointIds.has(id))id=uid();while(pointIds.has(id))id=uid();candidate.id=id;"
repls.append((old_point,new_point))

for old,new in repls:
    if old not in s:
        raise SystemExit('index marker not found: '+old[:100])
    s=s.replace(old,new,1)

if 'randomUUID' in s: raise SystemExit('randomUUID still present in index')
if 'migrateCoreIds' in s or 'CORE_ID_ALPHABET' in s: raise SystemExit('automatic migration code unexpectedly present')
idx.write_text(s)

imp=Path('import.html')
t=imp.read_text()
old_uid="""function uid(){
  return window.crypto?.randomUUID
    ?window.crypto.randomUUID()
    :'id-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2);
}"""
new_uid="""const ID_ALPHABET='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
function uid(){
  const bytes=new Uint8Array(12);
  if(window.crypto?.getRandomValues)window.crypto.getRandomValues(bytes);
  else for(let i=0;i<bytes.length;i++)bytes[i]=Math.floor(Math.random()*256);
  return Array.from(bytes,b=>ID_ALPHABET[b&63]).join('');
}"""
if old_uid not in t: raise SystemExit('import uid marker not found')
t=t.replace(old_uid,new_uid,1)
if 'randomUUID' in t: raise SystemExit('randomUUID still present in import')
imp.write_text(t)

sw=Path('service-worker.js')
w=sw.read_text()
if "kmreg-shell-0.28.18" not in w: raise SystemExit('old cache version not found')
w=w.replace("kmreg-shell-0.28.18","kmreg-shell-0.28.19",1)
old_shell="const SHELL=['./','./index.html','./manifest.webmanifest','./app-icon.svg'];"
new_shell="const SHELL=['./','./index.html','./id-converter.html','./manifest.webmanifest','./app-icon.svg'];"
if old_shell not in w: raise SystemExit('shell marker not found')
w=w.replace(old_shell,new_shell,1)
old_skip="if(url.pathname.endsWith('/import.html'))return;"
new_skip="if(url.pathname.endsWith('/import.html'))return;if(url.pathname.endsWith('/id-converter.html')){event.respondWith(caches.match('./id-converter.html').then(cached=>cached||fetch(req)));return;}"
if old_skip not in w: raise SystemExit('service worker navigation marker not found')
w=w.replace(old_skip,new_skip,1)
sw.write_text(w)

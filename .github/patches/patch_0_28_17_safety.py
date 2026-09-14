from pathlib import Path


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit(f'{label}: expected 1 exact match, got {text.count(old)}')
    return text.replace(old, new, 1)

p=Path('index.html')
s=p.read_text()
if ' · 0.28.17' not in s:
    raise SystemExit('0.28.17 feature code not found')

old="""const CORE_ID_ALPHABET='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_',CORE_ID_RE=/^[A-Za-z0-9_-]{12}$/;
function isCoreId(v){return CORE_ID_RE.test(String(v||''))}
function coreId(used=null){let id='';do{const bytes=new Uint8Array(12);if(window.crypto?.getRandomValues)window.crypto.getRandomValues(bytes);else for(let i=0;i<bytes.length;i++)bytes[i]=Math.floor(Math.random()*256);id=Array.from(bytes,b=>CORE_ID_ALPHABET[b&63]).join('')}while(used?.has(id));return id}
"""
new="""const CORE_ID_ALPHABET='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_',CORE_ID_RE=/^[A-Za-z0-9_-]{12}$/,CORE_ID_REMAP_KEY='kmreg-v4-core-id-remap-v1';
function isCoreId(v){return CORE_ID_RE.test(String(v||''))}
function coreId(used=null){let id='';do{const bytes=new Uint8Array(12);if(window.crypto?.getRandomValues)window.crypto.getRandomValues(bytes);else for(let i=0;i<bytes.length;i++)bytes[i]=Math.floor(Math.random()*256);id=Array.from(bytes,b=>CORE_ID_ALPHABET[b&63]).join('')}while(used?.has(id));return id}
function storedTripIdRemap(){try{const x=JSON.parse(localStorage.getItem(CORE_ID_REMAP_KEY)||'{}');return new Map(Object.entries(x).filter(([a,b])=>a&&isCoreId(b)))}catch(_){return new Map()}}
function persistTripIdRemap(map){if(map?.size)localStorage.setItem(CORE_ID_REMAP_KEY,JSON.stringify(Object.fromEntries(map)));else localStorage.removeItem(CORE_ID_REMAP_KEY)}
"""
s=replace_once(s,old,new,'persistent id-map helpers')

old="function load(){try{const raw=localStorage.getItem(KEY),out=raw?normalize(JSON.parse(raw)):clone(DEFAULT),migration=migrateCoreIds(out);pendingTripIdRemap=migration.tripMap;if(migration.changed)localStorage.setItem(KEY,JSON.stringify(out));return out}catch(e){console.error(e);pendingTripIdRemap=new Map();return clone(DEFAULT)}}"
new="function load(){try{const raw=localStorage.getItem(KEY),out=raw?normalize(JSON.parse(raw)):clone(DEFAULT),migration=migrateCoreIds(out),pending=storedTripIdRemap();for(const [oldId,newId] of migration.tripMap)pending.set(oldId,newId);pendingTripIdRemap=pending;if(migration.tripMap.size)persistTripIdRemap(pending);if(migration.changed)localStorage.setItem(KEY,JSON.stringify(out));return out}catch(e){console.error(e);pendingTripIdRemap=storedTripIdRemap();return clone(DEFAULT)}}"
s=replace_once(s,old,new,'persist migration map')

old="async function initTrackStore(){if(!('indexedDB' in window))return;try{const legacy=[...(data.trackPoints||[])];if(legacy.length)await putTrackPoints(legacy);let rows=await allTrackPoints();if(pendingTripIdRemap.size){rows=rows.map(p=>remapTrackPointTripId(p,pendingTripIdRemap));rows=[...new Map(rows.map(p=>[p.id,p])).values()];await replaceTrackStore(rows);pendingTripIdRemap.clear()}data.trackPoints=rows;trackStoreReady=true;save();render()}catch(e){console.warn('IndexedDB fallback',e);trackStoreReady=false}}"
new="async function initTrackStore(){if(!('indexedDB' in window)){pendingTripIdRemap.clear();persistTripIdRemap(pendingTripIdRemap);return}try{const legacy=[...(data.trackPoints||[])];if(legacy.length)await putTrackPoints(legacy);let rows=await allTrackPoints();if(pendingTripIdRemap.size){rows=rows.map(p=>remapTrackPointTripId(p,pendingTripIdRemap));rows=[...new Map(rows.map(p=>[p.id,p])).values()];await replaceTrackStore(rows);pendingTripIdRemap.clear();persistTripIdRemap(pendingTripIdRemap)}data.trackPoints=rows;trackStoreReady=true;save();render()}catch(e){console.warn('IndexedDB fallback',e);trackStoreReady=false}}"
s=replace_once(s,old,new,'durable indexeddb migration')

p.write_text(s)

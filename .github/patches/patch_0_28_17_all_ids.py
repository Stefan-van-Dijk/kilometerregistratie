from pathlib import Path
import re


def sub_once(text, pattern, repl, label, flags=0):
    out, n = re.subn(pattern, lambda m: repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, got {n}')
    return out


# ---- index.html ----
p = Path('index.html')
s = p.read_text()
if '0.28.17' not in s:
    raise SystemExit('expected 0.28.17 feature branch')

s = sub_once(
    s,
    r"function coreIdSet\(db=data\)\{.*?\}\nfunction newCoreId\(\)\{",
    "function coreIdSet(db=data){const ids=new Set();for(const group of [db?.locations,db?.trips,db?.events,db?.trackPoints])for(const x of group||[])if(x?.id)ids.add(String(x.id));if(db?.activeTrip?.id)ids.add(String(db.activeTrip.id));return ids}\nfunction newCoreId(){",
    'global core id set',
    re.S,
)

s = sub_once(
    s,
    r"function remapTrackPointTripId\(point,map\)\{.*?\}\nfunction migrateCoreIds",
    "function remapTrackPointTripId(point,map){if(!point||!point.tripId)return point;const next=map.get(String(point.tripId));return next&&next!==point.tripId?{...point,tripId:next}:point}\nfunction migrateCoreIds",
    'independent trackpoint ids',
    re.S,
)

new_migrate = """function migrateCoreIds(db){const used=new Set(),locationMap=new Map(),tripMap=new Map();let changed=false;const assign=(records,map=null)=>{for(const item of records||[]){if(!item||typeof item!=='object')continue;const old=String(item.id||'');let next=old;if(!isCoreId(next)||used.has(next))next=coreId(used);if(old!==next){item.id=next;changed=true;if(map&&old&&!map.has(old))map.set(old,next)}used.add(next)}};assign(db.locations,locationMap);assign(db.trips,tripMap);if(db.activeTrip){const old=String(db.activeTrip.id||'');let next=old;if(!isCoreId(next)||used.has(next))next=coreId(used);if(old!==next){db.activeTrip.id=next;changed=true;if(old&&!tripMap.has(old))tripMap.set(old,next)}used.add(next)}assign(db.events);assign(db.trackPoints);const remapLoc=loc=>{if(!loc||typeof loc!=='object'||!loc.id)return loc;const next=locationMap.get(String(loc.id));if(next&&next!==loc.id){loc.id=next;changed=true}return loc};for(const t of db.trips||[])for(const key of ['origin','destination','plannedDestination','expectedDestination'])if(t[key])remapLoc(t[key]);for(const ev of db.events||[]){if(ev?.location)remapLoc(ev.location);if(ev?.tripId&&tripMap.has(String(ev.tripId))){ev.tripId=tripMap.get(String(ev.tripId));changed=true}}if(db.activeTrip){for(const key of ['origin','expectedDestination','plannedDestination'])if(db.activeTrip[key])remapLoc(db.activeTrip[key])}if(db.lastEndpoint?.location)remapLoc(db.lastEndpoint.location);if(Array.isArray(db.trackPoints))db.trackPoints=db.trackPoints.map(p=>{const next=remapTrackPointTripId(p,tripMap);if(next!==p)changed=true;return next});return{changed,locationMap,tripMap}}"""
s = sub_once(
    s,
    r"function migrateCoreIds\(db\)\{.*?\}\nfunction load\(\)",
    new_migrate + "\nfunction load()",
    'migrate all persistent ids',
    re.S,
)

old_uid = "function uid(){return window.crypto?.randomUUID?window.crypto.randomUUID():'id-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2)}\n"
if old_uid not in s:
    raise SystemExit('legacy uid helper not found in index')
s = s.replace(old_uid, '', 1)
s = s.replace('uid()', 'newCoreId()')

new_init = """async function initTrackStore(){if(!('indexedDB' in window))return;try{const legacy=[...(data.trackPoints||[])];if(legacy.length)await putTrackPoints(legacy);let rows=await allTrackPoints(),changed=false;if(pendingTripIdRemap.size){rows=rows.map(p=>{const next=remapTrackPointTripId(p,pendingTripIdRemap);if(next!==p)changed=true;return next})}const unique=new Map();for(const p of rows){const lat=Number.isFinite(+p?.lat)?(+p.lat).toFixed(7):'',lng=Number.isFinite(+p?.lng)?(+p.lng).toFixed(7):'',key=[String(p?.tripId||''),String(p?.time||''),lat,lng].join('|');if(unique.has(key)){changed=true;continue}unique.set(key,p)}rows=[...unique.values()];const used=new Set();for(const group of [data.locations,data.trips,data.events])for(const item of group||[])if(item?.id)used.add(String(item.id));if(data.activeTrip?.id)used.add(String(data.activeTrip.id));rows=rows.map(p=>{let copy=p,id=String(p?.id||'');if(!isCoreId(id)||used.has(id)){copy={...p,id:coreId(used)};changed=true}used.add(String(copy.id));return copy});if(changed)await replaceTrackStore(rows);if(pendingTripIdRemap.size){pendingTripIdRemap.clear();clearStoredTripIdRemap()}data.trackPoints=rows;trackStoreReady=true;save();render()}catch(e){console.warn('IndexedDB fallback',e);trackStoreReady=false}}"""
s = sub_once(
    s,
    r"async function initTrackStore\(\)\{.*?\}\nfunction registerServiceWorker",
    new_init + "\nfunction registerServiceWorker",
    'indexeddb all-id migration',
    re.S,
)

new_persist = """function persistTrack(){if(!data.activeTrip||!gpsLatest)return;const minute=new Date().toISOString().slice(0,16);if(data.trackPoints.some(x=>x.tripId===data.activeTrip.id&&String(x.time||'').slice(0,16)===minute))return;const point={id:newCoreId(),tripId:data.activeTrip.id,time:new Date().toISOString(),lat:gpsLatest.lat,lng:gpsLatest.lng,accuracy:gpsLatest.accuracy??null};data.trackPoints.push(point);const pruned=data.trackPoints.length>20000;if(pruned)data.trackPoints=data.trackPoints.slice(-20000);try{save()}catch(e){}if(trackStoreReady)(pruned?replaceTrackStore(data.trackPoints):putTrackPoints([point])).catch(e=>console.warn('GPS-punt opslaan mislukt',e))}"""
s = sub_once(
    s,
    r"function persistTrack\(\)\{.*?\}\nfunction recognitionRadius",
    new_persist + "\nfunction recognitionRadius",
    'new trackpoint ids',
    re.S,
)

if 'uid()' in s or 'randomUUID' in s:
    raise SystemExit('legacy uid generation remains in index')
for needle in [
    "data.events.push({id:newCoreId()",
    "const point={id:newCoreId()",
    "assign(db.events);assign(db.trackPoints)",
]:
    if needle not in s:
        raise SystemExit(f'missing index verification: {needle}')
p.write_text(s)

# ---- import.html ----
p = Path('import.html')
s = p.read_text()
old_generator = """const CORE_ID_ALPHABET='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
function newCoreId(){const used=new Set([...db.locations,...db.trips,...(db.activeTrip?[db.activeTrip]:[])].map(x=>String(x?.id||'')).filter(Boolean));let id='';do{const bytes=new Uint8Array(12);if(window.crypto?.getRandomValues)window.crypto.getRandomValues(bytes);else for(let i=0;i<bytes.length;i++)bytes[i]=Math.floor(Math.random()*256);id=Array.from(bytes,b=>CORE_ID_ALPHABET[b&63]).join('')}while(used.has(id));return id}
function uid(){
  return window.crypto?.randomUUID
    ?window.crypto.randomUUID()
    :'id-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2);
}
"""
new_generator = """const CORE_ID_ALPHABET='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_',generatedCoreIds=new Set();
function newCoreId(){const used=new Set([...db.locations,...db.trips,...db.events,...db.trackPoints,...(db.activeTrip?[db.activeTrip]:[])].map(x=>String(x?.id||'')).filter(Boolean));for(const id of generatedCoreIds)used.add(id);let id='';do{const bytes=new Uint8Array(12);if(window.crypto?.getRandomValues)window.crypto.getRandomValues(bytes);else for(let i=0;i<bytes.length;i++)bytes[i]=Math.floor(Math.random()*256);id=Array.from(bytes,b=>CORE_ID_ALPHABET[b&63]).join('')}while(used.has(id));generatedCoreIds.add(id);return id}
"""
if old_generator not in s:
    raise SystemExit('import generator block not found')
s = s.replace(old_generator, new_generator, 1)
s = s.replace('uid()', 'newCoreId()')
if 'uid()' in s or 'randomUUID' in s:
    raise SystemExit('legacy uid generation remains in import')
if "db.events.push({id:newCoreId()" not in s:
    raise SystemExit('historical event does not use core id')
p.write_text(s)

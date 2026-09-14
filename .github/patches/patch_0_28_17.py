from pathlib import Path
import re


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit(f'{label}: expected 1 exact match, got {text.count(old)}')
    return text.replace(old, new, 1)


def sub_once(text, pattern, repl, label, flags=0):
    out, n = re.subn(pattern, lambda m: repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 regex match, got {n}')
    return out

# ---- index.html ----
p = Path('index.html')
s = p.read_text()
if ' · 0.28.16' not in s:
    raise SystemExit('index version 0.28.16 not found')

s = replace_once(
    s,
    "let data=load(),view='ride'",
    "let pendingTripIdRemap=new Map();\nlet data=load(),view='ride'",
    'pending trip-id map'
)
s = replace_once(s, "+' · 0.28.16';", "+' · 0.28.17';", 'index version')

old_core = """function clone(v){return JSON.parse(JSON.stringify(v))}
function normalize(x){return{settings:{...DEFAULT.settings,...(x.settings||{})},locations:Array.isArray(x.locations)?x.locations:[],trips:Array.isArray(x.trips)?x.trips:[],events:Array.isArray(x.events)?x.events:[],trackPoints:Array.isArray(x.trackPoints)?x.trackPoints:[],activeTrip:x.activeTrip||null,lastEndpoint:x.lastEndpoint||null}}
function load(){try{const raw=localStorage.getItem(KEY);return raw?normalize(JSON.parse(raw)):clone(DEFAULT)}catch(e){console.error(e);return clone(DEFAULT)}}
function save(){const local=trackStoreReady?{...data,trackPoints:[]}:data;localStorage.setItem(KEY,JSON.stringify(local));const raw=localStorage.getItem(KEY);if(!raw)throw new Error('Lokale opslag is mislukt.');JSON.parse(raw)}
function uid(){return window.crypto?.randomUUID?window.crypto.randomUUID():'id-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2)}
"""
new_core = """function clone(v){return JSON.parse(JSON.stringify(v))}
function normalize(x){return{settings:{...DEFAULT.settings,...(x.settings||{})},locations:Array.isArray(x.locations)?x.locations:[],trips:Array.isArray(x.trips)?x.trips:[],events:Array.isArray(x.events)?x.events:[],trackPoints:Array.isArray(x.trackPoints)?x.trackPoints:[],activeTrip:x.activeTrip||null,lastEndpoint:x.lastEndpoint||null}}
const CORE_ID_ALPHABET='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_',CORE_ID_RE=/^[A-Za-z0-9_-]{12}$/;
function isCoreId(v){return CORE_ID_RE.test(String(v||''))}
function coreId(used=null){let id='';do{const bytes=new Uint8Array(12);if(window.crypto?.getRandomValues)window.crypto.getRandomValues(bytes);else for(let i=0;i<bytes.length;i++)bytes[i]=Math.floor(Math.random()*256);id=Array.from(bytes,b=>CORE_ID_ALPHABET[b&63]).join('')}while(used?.has(id));return id}
function coreIdSet(db=data){const ids=new Set();for(const x of [...(db?.locations||[]),...(db?.trips||[])])if(x?.id)ids.add(String(x.id));if(db?.activeTrip?.id)ids.add(String(db.activeTrip.id));return ids}
function newCoreId(){return coreId(coreIdSet())}
function remapTrackPointTripId(point,map){if(!point||!point.tripId)return point;const old=String(point.tripId),next=map.get(old);if(!next)return point;const copy={...point,tripId:next};if(typeof copy.id==='string'&&copy.id.startsWith(old+'_'))copy.id=next+copy.id.slice(old.length);return copy}
function migrateCoreIds(db){const used=new Set(),locationMap=new Map(),tripMap=new Map();let changed=false;const assign=(records,map)=>{for(const item of records||[]){if(!item||typeof item!=='object')continue;const old=String(item.id||'');let next=old;if(!isCoreId(next)||used.has(next))next=coreId(used);if(old!==next){item.id=next;changed=true;if(old&&!map.has(old))map.set(old,next)}used.add(next)}};assign(db.locations,locationMap);assign(db.trips,tripMap);if(db.activeTrip){const old=String(db.activeTrip.id||'');let next=old;if(!isCoreId(next)||used.has(next))next=coreId(used);if(old!==next){db.activeTrip.id=next;changed=true;if(old&&!tripMap.has(old))tripMap.set(old,next)}used.add(next)}const remapLoc=loc=>{if(!loc||typeof loc!=='object'||!loc.id)return loc;const next=locationMap.get(String(loc.id));if(next&&next!==loc.id){loc.id=next;changed=true}return loc};for(const t of db.trips||[])for(const key of ['origin','destination','plannedDestination','expectedDestination'])if(t[key])remapLoc(t[key]);for(const ev of db.events||[]){if(ev?.location)remapLoc(ev.location);if(ev?.tripId&&tripMap.has(String(ev.tripId))){ev.tripId=tripMap.get(String(ev.tripId));changed=true}}if(db.activeTrip){for(const key of ['origin','expectedDestination','plannedDestination'])if(db.activeTrip[key])remapLoc(db.activeTrip[key])}if(db.lastEndpoint?.location)remapLoc(db.lastEndpoint.location);if(Array.isArray(db.trackPoints))db.trackPoints=db.trackPoints.map(p=>{const next=remapTrackPointTripId(p,tripMap);if(next!==p)changed=true;return next});return{changed,locationMap,tripMap}}
function load(){try{const raw=localStorage.getItem(KEY),out=raw?normalize(JSON.parse(raw)):clone(DEFAULT),migration=migrateCoreIds(out);pendingTripIdRemap=migration.tripMap;if(migration.changed)localStorage.setItem(KEY,JSON.stringify(out));return out}catch(e){console.error(e);pendingTripIdRemap=new Map();return clone(DEFAULT)}}
function save(){const local=trackStoreReady?{...data,trackPoints:[]}:data;localStorage.setItem(KEY,JSON.stringify(local));const raw=localStorage.getItem(KEY);if(!raw)throw new Error('Lokale opslag is mislukt.');JSON.parse(raw)}
function uid(){return window.crypto?.randomUUID?window.crypto.randomUUID():'id-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2)}
"""
s = replace_once(s, old_core, new_core, 'core id helpers')

old_init = "async function initTrackStore(){if(!('indexedDB' in window))return;try{const legacy=[...(data.trackPoints||[])];if(legacy.length)await putTrackPoints(legacy);data.trackPoints=await allTrackPoints();trackStoreReady=true;save();render()}catch(e){console.warn('IndexedDB fallback',e);trackStoreReady=false}}"
new_init = "async function initTrackStore(){if(!('indexedDB' in window))return;try{const legacy=[...(data.trackPoints||[])];if(legacy.length)await putTrackPoints(legacy);let rows=await allTrackPoints();if(pendingTripIdRemap.size){rows=rows.map(p=>remapTrackPointTripId(p,pendingTripIdRemap));rows=[...new Map(rows.map(p=>[p.id,p])).values()];await replaceTrackStore(rows);pendingTripIdRemap.clear()}data.trackPoints=rows;trackStoreReady=true;save();render()}catch(e){console.warn('IndexedDB fallback',e);trackStoreReady=false}}"
s = replace_once(s, old_init, new_init, 'indexeddb id migration')

# New IDs for newly created locations/trips.
s = replace_once(s, "data.activeTrip={id:uid(),", "data.activeTrip={id:newCoreId(),", 'active trip short id')
s = replace_once(s, "data.trips.push({id:uid(),origin:snap(o),destination:snap(d)", "data.trips.push({id:newCoreId(),origin:snap(o),destination:snap(d)", 'manual trip short id')
s = replace_once(s, "id=String(fd.get('id')||uid()),old=data.locations.find", "id=String(fd.get('id')||newCoreId()),old=data.locations.find", 'location short id')

# Restore import also normalizes legacy IDs before writing the track store.
s = replace_once(
    s,
    "data=normalize(x);if('indexedDB' in window){try{await replaceTrackStore(data.trackPoints);",
    "data=normalize(x);migrateCoreIds(data);if('indexedDB' in window){try{await replaceTrackStore(data.trackPoints);",
    'restore id migration'
)

# Merge-import can receive legacy UUIDs; normalize them before writing IndexedDB.
s = replace_once(
    s,
    "const stats=mergeBackupData(incoming);if(trackStoreReady&&stats.newTrackPoints.length){try{await putTrackPoints(stats.newTrackPoints)}catch(e){console.warn('GPS-samenvoeging gebruikt lokale fallback',e);trackStoreReady=false}}",
    "const stats=mergeBackupData(incoming),idMigration=migrateCoreIds(data);if(trackStoreReady&&(stats.newTrackPoints.length||idMigration.changed)){try{if(idMigration.changed)await replaceTrackStore(data.trackPoints);else await putTrackPoints(stats.newTrackPoints)}catch(e){console.warn('GPS-samenvoeging gebruikt lokale fallback',e);trackStoreReady=false}}",
    'merge import id migration'
)

# Add location merge actions to click handler.
s = replace_once(
    s,
    "else if(a==='delete-location')deleteLocation(el.closest('[data-id]').dataset.id);else if(a==='tank')",
    "else if(a==='delete-location')deleteLocation(el.closest('[data-id]').dataset.id);else if(a==='merge-location')openLocationMerge(el.dataset.id||el.closest('[data-id]')?.dataset.id);else if(a==='confirm-location-merge')confirmLocationMerge();else if(a==='tank')",
    'merge location click actions'
)

old_nav = "function editorNav(title,saveAction,dangerAction='',dangerId=''){return`<header class=\"editor-nav\"><button type=\"button\" class=\"editor-glass-button editor-back\" data-action=\"editor-back\" aria-label=\"Terug\">‹</button><div class=\"editor-nav-title\">${esc(title)}</div><div class=\"editor-nav-actions\"><button type=\"button\" class=\"editor-glass-button editor-save\" data-action=\"${attr(saveAction)}\" aria-label=\"Opslaan\">✓</button>${dangerAction?`<details class=\"editor-more\"><summary class=\"editor-glass-button\" aria-label=\"Meer opties\">•••</summary><div class=\"editor-more-menu\"><button type=\"button\" class=\"editor-menu-delete\" data-action=\"${attr(dangerAction)}\" data-id=\"${attr(dangerId)}\">Verwijderen</button></div></details>`:''}</div></header>`}"
new_nav = "function editorNav(title,saveAction,dangerAction='',dangerId='',secondaryAction='',secondaryLabel=''){const hasMenu=dangerAction||secondaryAction;return`<header class=\"editor-nav\"><button type=\"button\" class=\"editor-glass-button editor-back\" data-action=\"editor-back\" aria-label=\"Terug\">‹</button><div class=\"editor-nav-title\">${esc(title)}</div><div class=\"editor-nav-actions\"><button type=\"button\" class=\"editor-glass-button editor-save\" data-action=\"${attr(saveAction)}\" aria-label=\"Opslaan\">✓</button>${hasMenu?`<details class=\"editor-more\"><summary class=\"editor-glass-button\" aria-label=\"Meer opties\">•••</summary><div class=\"editor-more-menu\">${secondaryAction?`<button type=\"button\" class=\"editor-menu-action\" data-action=\"${attr(secondaryAction)}\" data-id=\"${attr(dangerId)}\">${esc(secondaryLabel)}</button>`:''}${dangerAction?`<button type=\"button\" class=\"editor-menu-delete\" data-action=\"${attr(dangerAction)}\" data-id=\"${attr(dangerId)}\">Verwijderen</button>`:''}</div></details>`:''}</div></header>`}"
s = replace_once(s, old_nav, new_nav, 'editor nav extra action')

s = replace_once(
    s,
    "${editorNav(title,'save-location',l?'delete-location':'',l?.id||'')}",
    "${editorNav(title,'save-location',l?'delete-location':'',l?.id||'',l&&data.locations.length>1?'merge-location':'',l&&data.locations.length>1?'Samenvoegen…':'')}",
    'location merge menu'
)

merge_functions = r"""
function openLocationMerge(id){const source=data.locations.find(x=>x.id===id);if(!source)throw new Error('Locatie niet gevonden.');const others=[...data.locations].filter(x=>x.id!==id).sort((a,b)=>a.name.localeCompare(b.name,'nl',{sensitivity:'base'}));if(!others.length)throw new Error('Er is geen andere locatie om mee samen te voegen.');openModal(`<div class="modal-head"><div><div class="kicker">Locaties beheren</div><h2>Locaties samenvoegen</h2></div><button class="close" data-action="close">×</button></div><form id="locationMergeForm" onsubmit="return false"><input type="hidden" name="sourceId" value="${attr(source.id)}"><div class="notice"><strong>${esc(source.name)}</strong><br><small>${esc(source.address||coords(source)||'Geen adres/GPS')}</small></div><div class="form-group"><label>Samenvoegen met</label><select name="otherId">${others.map(l=>`<option value="${attr(l.id)}">${esc(l.name)}${l.address?' · '+esc(l.address):''}</option>`).join('')}</select></div><div class="form-group"><label>Welke locatie blijft bestaan?</label><label class="checkrow"><input type="radio" name="keep" value="source" checked><span><strong>Deze locatie behouden</strong><br><small>${esc(source.name)}</small></span></label><label class="checkrow"><input type="radio" name="keep" value="other"><span><strong>Gekozen locatie behouden</strong><br><small>De huidige locatie wordt dan verwijderd.</small></span></label></div><div class="warning-item">Alle ritten, tank-/omrijpunten en actieve verwijzingen worden eerst naar de behouden locatie omgezet. Niet-opgeslagen wijzigingen in dit bewerkscherm worden niet meegenomen.</div><button type="button" class="btn full" data-action="confirm-location-merge">Samenvoegen</button></form>`)}
function mergeLocationSnapshot(loc,removeId,keep){return loc?.id===removeId?snap(keep):loc}
function confirmLocationMerge(){const f=document.getElementById('locationMergeForm');if(!f)throw new Error('Samenvoegformulier niet gevonden.');const fd=new FormData(f),source=data.locations.find(x=>x.id===String(fd.get('sourceId'))),other=data.locations.find(x=>x.id===String(fd.get('otherId')));if(!source||!other||source.id===other.id)throw new Error('Kies twee verschillende locaties.');const keep=String(fd.get('keep'))==='other'?other:source,remove=keep.id===source.id?other:source;if(!confirm(`“${remove.name}” samenvoegen met “${keep.name}”?\n\n${keep.name} blijft bestaan; ${remove.name} wordt verwijderd.`))return;if(!keep.address&&remove.address)keep.address=remove.address;if((keep.lat==null||keep.lng==null)&&remove.lat!=null&&remove.lng!=null){keep.lat=remove.lat;keep.lng=remove.lng}if((keep.type||'other')==='other'&&remove.type&&remove.type!=='other')keep.type=remove.type;keep.useCount=(+keep.useCount||0)+(+remove.useCount||0);if(!keep.createdAt||(remove.createdAt&&remove.createdAt<keep.createdAt))keep.createdAt=remove.createdAt;keep.updatedAt=new Date().toISOString();for(const t of data.trips)for(const key of ['origin','destination','plannedDestination','expectedDestination'])if(t[key])t[key]=mergeLocationSnapshot(t[key],remove.id,keep);for(const ev of data.events)if(ev.location)ev.location=mergeLocationSnapshot(ev.location,remove.id,keep);if(data.activeTrip){for(const key of ['origin','expectedDestination','plannedDestination'])if(data.activeTrip[key])data.activeTrip[key]=mergeLocationSnapshot(data.activeTrip[key],remove.id,keep)}if(data.lastEndpoint?.location)data.lastEndpoint.location=mergeLocationSnapshot(data.lastEndpoint.location,remove.id,keep);data.locations=data.locations.filter(x=>x.id!==remove.id);if(settingsLocationOriginId===remove.id)settingsLocationOriginId=keep.id;if(expandedLocationId===remove.id)expandedLocationId=keep.id;editingLocationId=keep.id;settingsLocationsOpen=true;save();closeModal();render();toast(`Locaties samengevoegd · ${keep.name} behouden.`)}
""".strip()
s = replace_once(s, "function deleteLocation(id){", merge_functions + "\nfunction deleteLocation(id){", 'location merge functions')

# Small styling additions for the neutral merge action and merge modal warning.
css_add = """
/* 0.28.17 — locatie samenvoegen */
.editor-more-menu .editor-menu-action{color:var(--text);border-bottom:1px solid var(--line);border-radius:8px 8px 4px 4px}
.editor-more-menu .editor-menu-delete{color:var(--bad)}
#locationMergeForm .checkrow{padding:7px 0;margin:0}
#locationMergeForm .checkrow+ .checkrow{border-top:1px solid var(--line)}
"""
s = replace_once(s, '</style>', css_add + '\n</style>', 'index merge css')

p.write_text(s)

# ---- import.html ----
p = Path('import.html')
s = p.read_text()
# Keep parser/temporary UUIDs, but persisted trip/location IDs use the new 12-char alphabet.
old_uid = "function uid(){return window.crypto?.randomUUID?window.crypto.randomUUID():'id-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2)}"
new_uid = "const CORE_ID_ALPHABET='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';\nfunction newCoreId(){const used=new Set([...db.locations,...db.trips,...(db.activeTrip?[db.activeTrip]:[])].map(x=>String(x?.id||'')).filter(Boolean));let id='';do{const bytes=new Uint8Array(12);if(window.crypto?.getRandomValues)window.crypto.getRandomValues(bytes);else for(let i=0;i<bytes.length;i++)bytes[i]=Math.floor(Math.random()*256);id=Array.from(bytes,b=>CORE_ID_ALPHABET[b&63]).join('')}while(used.has(id));return id}\n" + old_uid
s = replace_once(s, old_uid, new_uid, 'import core id helper')
s = replace_once(s, "const loc={id:uid(),name:", "const loc={id:newCoreId(),name:", 'historical location short id')
s = replace_once(s, "trip={id:uid(),origin:snap(o),destination:snap(d)", "trip={id:newCoreId(),origin:snap(o),destination:snap(d)", 'historical trip short id')
p.write_text(s)

# ---- service-worker.js ----
p = Path('service-worker.js')
s = p.read_text()
s = replace_once(s, "kmreg-shell-0.28.16", "kmreg-shell-0.28.17", 'service worker version')
p.write_text(s)

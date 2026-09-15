from pathlib import Path

p=Path('index.html')
s=p.read_text()

old="""function editorNav(title,saveAction,dangerAction='',dangerId=''){return`<header class=\"editor-nav\"><button type=\"button\" class=\"editor-glass-button editor-back\" data-action=\"editor-back\" aria-label=\"Terug\">‹</button><div class=\"editor-nav-title\">${esc(title)}</div><div class=\"editor-nav-actions\"><button type=\"button\" class=\"editor-glass-button editor-save\" data-action=\"${attr(saveAction)}\" aria-label=\"Opslaan\">✓</button>${dangerAction?`<details class=\"editor-more\"><summary class=\"editor-glass-button\" aria-label=\"Meer opties\">•••</summary><div class=\"editor-more-menu\"><button type=\"button\" class=\"editor-menu-delete\" data-action=\"${attr(dangerAction)}\" data-id=\"${attr(dangerId)}\">Verwijderen</button></div></details>`:''}</div></header>`}
"""
new="""function editorNav(title,saveAction,dangerAction='',dangerId='',secondaryAction='',secondaryLabel=''){const hasMenu=dangerAction||secondaryAction;return`<header class=\"editor-nav\"><button type=\"button\" class=\"editor-glass-button editor-back\" data-action=\"editor-back\" aria-label=\"Terug\">‹</button><div class=\"editor-nav-title\">${esc(title)}</div><div class=\"editor-nav-actions\"><button type=\"button\" class=\"editor-glass-button editor-save\" data-action=\"${attr(saveAction)}\" aria-label=\"Opslaan\">✓</button>${hasMenu?`<details class=\"editor-more\"><summary class=\"editor-glass-button\" aria-label=\"Meer opties\">•••</summary><div class=\"editor-more-menu\">${secondaryAction?`<button type=\"button\" class=\"editor-menu-action\" data-action=\"${attr(secondaryAction)}\" data-id=\"${attr(dangerId)}\">${esc(secondaryLabel)}</button>`:''}${dangerAction?`<button type=\"button\" class=\"editor-menu-delete\" data-action=\"${attr(dangerAction)}\" data-id=\"${attr(dangerId)}\">Verwijderen</button>`:''}</div></details>`:''}</div></header>`}
"""
if old not in s: raise SystemExit('editorNav block not found')
s=s.replace(old,new,1)

old_call="${editorNav(title,'save-location',l?'delete-location':'',l?.id||'')}"
new_call="${editorNav(title,'save-location',l?'delete-location':'',l?.id||'',l&&data.locations.length>1?'merge-location':'',l&&data.locations.length>1?'Samenvoegen…':'')}"
if old_call not in s: raise SystemExit('location editor nav call not found')
s=s.replace(old_call,new_call,1)

anchor="""function deleteLocation(id){if(!confirm('Locatie verwijderen? Bestaande ritten blijven intact.'))return;const wasEditing=view==='location-edit'&&editingLocationId===id,back=editorReturnView==='ride'?'ride':'settings';data.locations=data.locations.filter(x=>x.id!==id);if(expandedLocationId===id)expandedLocationId=null;settingsLocationsOpen=true;save();if(wasEditing){editingLocationId=null;editingLocationSeed=null;view=back}render();toast('Locatie verwijderd.')}
"""
merge_code="""function openLocationMerge(id){const source=data.locations.find(x=>x.id===id);if(!source)throw new Error('Locatie niet gevonden.');const others=[...data.locations].filter(x=>x.id!==id).sort((a,b)=>a.name.localeCompare(b.name,'nl',{sensitivity:'base'}));if(!others.length)throw new Error('Er is geen andere locatie om mee samen te voegen.');openModal(`<div class=\"modal-head\"><div><div class=\"kicker\">Locaties beheren</div><h2>Locaties samenvoegen</h2></div><button class=\"close\" data-action=\"close\">×</button></div><form id=\"locationMergeForm\" onsubmit=\"return false\"><input type=\"hidden\" name=\"sourceId\" value=\"${attr(source.id)}\"><div class=\"notice\"><strong>${esc(source.name)}</strong><br><small>${esc(source.address||coords(source)||'Geen adres/GPS')}</small></div><div class=\"form-group\"><label>Samenvoegen met</label><select name=\"otherId\">${others.map(l=>`<option value=\"${attr(l.id)}\">${esc(l.name)}${l.address?' · '+esc(l.address):''}</option>`).join('')}</select></div><div class=\"form-group\"><label>Welke locatie blijft bestaan?</label><label class=\"checkrow\"><input type=\"radio\" name=\"keep\" value=\"source\" checked><span><strong>Deze locatie behouden</strong><br><small>${esc(source.name)}</small></span></label><label class=\"checkrow\"><input type=\"radio\" name=\"keep\" value=\"other\"><span><strong>Gekozen locatie behouden</strong><br><small>De huidige locatie wordt dan verwijderd.</small></span></label></div><div class=\"warning-item\">Alle ritten, tank-/omrijpunten en actieve verwijzingen worden eerst naar de behouden locatie omgezet. Niet-opgeslagen wijzigingen in dit bewerkscherm worden niet meegenomen.</div><button type=\"button\" class=\"btn full\" data-action=\"confirm-location-merge\">Samenvoegen</button></form>`)}
function mergeLocationSnapshot(loc,removeId,keep){return loc?.id===removeId?snap(keep):loc}
function confirmLocationMerge(){const f=document.getElementById('locationMergeForm');if(!f)throw new Error('Samenvoegformulier niet gevonden.');const fd=new FormData(f),source=data.locations.find(x=>x.id===String(fd.get('sourceId'))),other=data.locations.find(x=>x.id===String(fd.get('otherId')));if(!source||!other||source.id===other.id)throw new Error('Kies twee verschillende locaties.');const keep=String(fd.get('keep'))==='other'?other:source,remove=keep.id===source.id?other:source;if(!confirm(`“${remove.name}” samenvoegen met “${keep.name}”?\n\n${keep.name} blijft bestaan; ${remove.name} wordt verwijderd.`))return;if(!keep.address&&remove.address)keep.address=remove.address;if((keep.lat==null||keep.lng==null)&&remove.lat!=null&&remove.lng!=null){keep.lat=remove.lat;keep.lng=remove.lng}if((keep.type||'other')==='other'&&remove.type&&remove.type!=='other')keep.type=remove.type;if((keep.shareRide||'never')==='never'&&['ask','always'].includes(remove.shareRide))keep.shareRide=remove.shareRide;keep.useCount=(+keep.useCount||0)+(+remove.useCount||0);if(!keep.createdAt||(remove.createdAt&&remove.createdAt<keep.createdAt))keep.createdAt=remove.createdAt;keep.updatedAt=new Date().toISOString();for(const t of data.trips)for(const key of ['origin','destination','plannedDestination','expectedDestination'])if(t[key])t[key]=mergeLocationSnapshot(t[key],remove.id,keep);for(const ev of data.events)if(ev.location)ev.location=mergeLocationSnapshot(ev.location,remove.id,keep);if(data.activeTrip){for(const key of ['origin','expectedDestination','plannedDestination'])if(data.activeTrip[key])data.activeTrip[key]=mergeLocationSnapshot(data.activeTrip[key],remove.id,keep)}if(data.lastEndpoint?.location)data.lastEndpoint.location=mergeLocationSnapshot(data.lastEndpoint.location,remove.id,keep);data.locations=data.locations.filter(x=>x.id!==remove.id);if(settingsLocationOriginId===remove.id)settingsLocationOriginId=keep.id;if(expandedLocationId===remove.id)expandedLocationId=keep.id;editingLocationId=keep.id;settingsLocationsOpen=true;save();closeModal();render();toast(`Locaties samengevoegd · ${keep.name} behouden.`)}
"""
if anchor not in s: raise SystemExit('deleteLocation anchor not found')
s=s.replace(anchor,merge_code+anchor,1)

old_click="else if(a==='delete-location')deleteLocation(el.closest('[data-id]').dataset.id);else if(a==='tank')"
new_click="else if(a==='delete-location')deleteLocation(el.closest('[data-id]').dataset.id);else if(a==='merge-location')openLocationMerge(el.dataset.id||el.closest('[data-id]')?.dataset.id);else if(a==='confirm-location-merge')confirmLocationMerge();else if(a==='tank')"
if old_click not in s: raise SystemExit('click handler anchor not found')
s=s.replace(old_click,new_click,1)

css_anchor=""".editor-more-menu button:active{background:rgba(255,103,103,.1)}
"""
css_new=css_anchor+".editor-more-menu .editor-menu-action{color:var(--text)}\n.editor-more-menu .editor-menu-action:active{background:rgba(77,163,255,.1)}\n"
if css_anchor not in s: raise SystemExit('editor menu CSS anchor not found')
s=s.replace(css_anchor,css_new,1)

if "· 0.28.16'" not in s: raise SystemExit('version marker not found')
s=s.replace("· 0.28.16'","· 0.28.18'",1)

for bad in ['CORE_ID_ALPHABET','migrateCoreIds','newCoreId()']:
    if bad in s: raise SystemExit(f'unexpected ID migration code present: {bad}')
for required in ['function openLocationMerge','function confirmLocationMerge',"data-action=\\\"confirm-location-merge\\\"",'function uid(){return window.crypto?.randomUUID']:
    if required not in s: raise SystemExit(f'missing expected marker: {required}')

p.write_text(s)

sw=Path('service-worker.js')
w=sw.read_text()
if "kmreg-shell-0.28.16" not in w: raise SystemExit('service worker cache version not found')
w=w.replace('kmreg-shell-0.28.16','kmreg-shell-0.28.18',1)
sw.write_text(w)

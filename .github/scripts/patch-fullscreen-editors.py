from pathlib import Path

index=Path('index.html')
text=index.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global text
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text=text.replace(old,new,1)

def replace_block(start,end,new,label):
    global text
    a=text.find(start)
    if a<0:
        raise SystemExit(f'{label}: start not found')
    b=text.find(end,a)
    if b<0:
        raise SystemExit(f'{label}: end not found')
    text=text[:a]+new+text[b:]

replace_once("+' · 0.28.4';","+' · 0.28.5';",'version')

old_state="let data=load(),view='ride',selectedWeek=new Date(),periodMode='week',gpsWatch=null,gpsTimer=null,gpsLatest=null,odoSwipe=null,periodGesture=null,periodLastTap=0,expandedTripId=null,tripSwipe=null,trackStoreReady=false,trackDbPromise=null,settingsLocationCheck=0,geocodeQueue=Promise.resolve(),geocodeLastAt=0,expandedLocationId=null,settingsLocationsOpen=false,settingsLocationOriginId=null,screenSwipe=null;"
new_state="let data=load(),view='ride',selectedWeek=new Date(),periodMode='week',gpsWatch=null,gpsTimer=null,gpsLatest=null,odoSwipe=null,periodGesture=null,periodLastTap=0,expandedTripId=null,tripSwipe=null,trackStoreReady=false,trackDbPromise=null,settingsLocationCheck=0,geocodeQueue=Promise.resolve(),geocodeLastAt=0,expandedLocationId=null,settingsLocationsOpen=false,settingsLocationOriginId=null,screenSwipe=null,editorReturnView='ride',editingTripId=null,editingLocationId=null,editingLocationSeed=null;"
replace_once(old_state,new_state,'editor state')

css=r'''
/* 0.28.5 — volwaardige bewerkpagina's */
.editor-view .top{display:none}
.editor-view .shell{max-width:820px;min-height:100dvh;padding:0 16px calc(78px + env(safe-area-inset-bottom))}
.editor-page{min-height:100dvh}
.editor-nav{position:sticky;top:0;z-index:24;display:grid;grid-template-columns:minmax(76px,1fr) auto minmax(76px,1fr);align-items:center;gap:8px;margin:0 -16px;padding:calc(8px + env(safe-area-inset-top)) 16px 9px;border-bottom:1px solid var(--line);background:var(--bg)}
.editor-nav-title{font-size:16px;font-weight:850;text-align:center;white-space:nowrap}
.editor-nav button{min-height:34px;padding:5px 0;border:0;background:transparent;font-size:12px;font-weight:800;cursor:pointer}
.editor-back{justify-self:start;color:var(--accent);text-align:left}
.editor-danger{justify-self:end;color:var(--bad);text-align:right}
.editor-nav-spacer{display:block}
.editor-content{width:100%;max-width:620px;margin:0 auto;padding:2px 0 10px}
.editor-page .edit-form{margin:0}
.editor-page .edit-section{padding:11px 0;border-top:1px solid var(--line)}
.editor-page .edit-section:first-of-type{padding-top:9px;border-top:0}
.editor-page .edit-section-head{margin-bottom:7px}
.editor-page .edit-section-head strong{font-size:14px}
.editor-page .edit-section-head small{font-size:9px}
.editor-page .edit-grid{gap:7px}
.editor-page .edit-form .form-group input,.editor-page .edit-form .form-group select,.editor-page .edit-form .form-group textarea{background:var(--card);border-color:var(--line);box-shadow:none}
.editor-page .edit-form .form-group textarea{min-height:48px;height:48px}
.editor-route-grid{grid-template-columns:1fr}
.editor-page .edit-trip-type span{background:var(--card)}
.editor-page .location-choice span{background:var(--card)}
.editor-link-action{display:inline-flex;align-items:center;gap:6px;margin:0 0 7px;padding:3px 0;border:0;background:transparent;color:var(--accent);font-size:11px;font-weight:800;cursor:pointer}
.editor-page .location-link-hint{margin-top:6px;padding-top:6px}
.editor-page .osm-attribution{margin-top:3px}
.editor-page .edit-warning{padding:7px 0 2px;border-top:1px solid var(--line)}
.editor-page .edit-status{min-height:0;margin:3px 0}
.editor-savebar{position:fixed;z-index:28;left:0;right:0;bottom:0;padding:8px 16px calc(8px + env(safe-area-inset-bottom));border-top:1px solid var(--line);background:var(--bg)}
.editor-savebar-inner{width:100%;max-width:620px;margin:0 auto}
.editor-savebar .btn{width:100%;min-height:44px}
@media(max-width:520px){
.editor-nav{grid-template-columns:76px 1fr 76px}.editor-nav-title{font-size:15px}.editor-content{max-width:none}
.editor-page .edit-grid.two.keep-two,.editor-page .edit-grid.two.editor-time-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.editor-page .edit-grid.two.editor-route-grid{grid-template-columns:1fr}
}
@media(max-height:920px){
.editor-view .shell{padding-bottom:calc(68px + env(safe-area-inset-bottom))}
.editor-nav{padding-top:calc(5px + env(safe-area-inset-top));padding-bottom:5px}.editor-nav button{min-height:30px}.editor-nav-title{font-size:14px}
.editor-page .edit-section{padding:7px 0}.editor-page .edit-section:first-of-type{padding-top:5px}.editor-page .edit-section-head{margin-bottom:4px}
.editor-page .edit-form .form-group input,.editor-page .edit-form .form-group select,.editor-page .edit-form .form-group textarea{min-height:35px;padding:6px 8px}
.editor-page .edit-form .form-group textarea{height:38px;min-height:38px}
.editor-page .edit-trip-type span{min-height:34px}.editor-page .location-choice span{min-height:42px}
.editor-link-action{margin-bottom:4px;padding:1px 0;font-size:10px}.editor-page .location-link-hint{margin-top:4px;padding-top:4px}.editor-page .osm-attribution{font-size:8px}
.editor-page .edit-warning{padding:4px 0 1px}.editor-savebar{padding-top:6px;padding-bottom:calc(6px + env(safe-area-inset-bottom))}.editor-savebar .btn{min-height:38px;padding:8px 10px}
}
@media (prefers-color-scheme:light){.editor-nav,.editor-savebar{background:var(--bg)}.editor-page .edit-form .form-group input,.editor-page .edit-form .form-group select,.editor-page .edit-form .form-group textarea,.editor-page .edit-trip-type span,.editor-page .location-choice span{background:#fff}}
'''
replace_once('\n</style>','\n'+css+'\n</style>','editor css')

old_render="function render(){document.body.classList.toggle('has-active-trip',view!=='settings'&&!!data.activeTrip);if(view==='settings'){topAction.dataset.action='home';topAction.textContent='←';topAction.setAttribute('aria-label','Terug');renderSettings()}else{view='ride';topAction.dataset.action='settings';topAction.textContent='⚙︎';topAction.setAttribute('aria-label','Instellingen');renderHome()}}"
new_render="function render(){const editor=view==='trip-edit'||view==='location-edit';document.body.classList.toggle('editor-view',editor);document.body.classList.toggle('has-active-trip',view==='ride'&&!!data.activeTrip);if(view==='trip-edit'){renderTripEditPage();return}if(view==='location-edit'){renderLocationEditPage();return}if(view==='settings'){topAction.dataset.action='home';topAction.textContent='←';topAction.setAttribute('aria-label','Terug');renderSettings()}else{view='ride';topAction.dataset.action='settings';topAction.textContent='⚙︎';topAction.setAttribute('aria-label','Instellingen');renderHome()}}"
replace_once(old_render,new_render,'render editors')

replace_once("if(a==='settings'){view='settings';render()}else if(a==='home'){view='ride';render()}else if(a==='close')closeModal();", "if(a==='settings'){view='settings';render()}else if(a==='home'){view='ride';render()}else if(a==='editor-back')leaveEditor();else if(a==='close')closeModal();", 'editor back action')
replace_once("else if(a==='period-now'){selectedWeek=new Date();render()}else if(a==='add-location')openLocation();else if(a==='current-location')await openLocation(null,true);", "else if(a==='period-now'){selectedWeek=new Date();render()}else if(a==='add-location')await openLocation();else if(a==='current-location')await openLocation(null,true);", 'await add location')
replace_once("else if(a==='save-location')await saveLocation();else if(a==='edit-location')openLocation(el.closest('[data-id]').dataset.id);", "else if(a==='save-location')await saveLocation();else if(a==='edit-location')await openLocation(el.closest('[data-id]').dataset.id);", 'await edit location')

old_direction="const direction=view==='ride'&&x>=width-SCREEN_EDGE_SWIPE_ZONE?'left':view==='settings'&&x<=SCREEN_EDGE_SWIPE_ZONE?'right':null;"
new_direction="const direction=view==='ride'&&x>=width-SCREEN_EDGE_SWIPE_ZONE?'left':(view==='settings'||view==='trip-edit'||view==='location-edit')&&x<=SCREEN_EDGE_SWIPE_ZONE?'right':null;"
replace_once(old_direction,new_direction,'editor edge swipe direction')
old_end="function screenSwipeEnd(e){const g=screenSwipe;if(!g||g.pointerId!==e.pointerId)return;screenSwipe=null;if(g.cancelled||!g.horizontal)return;const correct=g.direction==='left'?g.dx<=-SCREEN_EDGE_SWIPE_DISTANCE:g.dx>=SCREEN_EDGE_SWIPE_DISTANCE;if(!correct||Math.abs(g.dx)<Math.abs(g.dy)*1.2)return;if(g.direction==='left'&&view==='ride'){view='settings';render();return}if(g.direction==='right'&&view==='settings'){view='ride';render()}}"
new_end="function screenSwipeEnd(e){const g=screenSwipe;if(!g||g.pointerId!==e.pointerId)return;screenSwipe=null;if(g.cancelled||!g.horizontal)return;const correct=g.direction==='left'?g.dx<=-SCREEN_EDGE_SWIPE_DISTANCE:g.dx>=SCREEN_EDGE_SWIPE_DISTANCE;if(!correct||Math.abs(g.dx)<Math.abs(g.dy)*1.2)return;if(g.direction==='left'&&view==='ride'){view='settings';render();return}if(g.direction==='right'&&view==='settings'){view='ride';render();return}if(g.direction==='right'&&(view==='trip-edit'||view==='location-edit'))leaveEditor()}"
replace_once(old_end,new_end,'editor edge swipe end')

trip_page=r'''function editorNav(title,dangerAction='',dangerId=''){return`<header class="editor-nav"><button type="button" class="editor-back" data-action="editor-back" aria-label="Terug">‹ Terug</button><div class="editor-nav-title">${esc(title)}</div>${dangerAction?`<button type="button" class="editor-danger" data-action="${attr(dangerAction)}" data-id="${attr(dangerId)}">Verwijder</button>`:'<span class="editor-nav-spacer"></span>'}</header>`}
function editorSavebar(action,label){return`<div class="editor-savebar"><div class="editor-savebar-inner"><button type="button" class="btn" data-action="${attr(action)}">${esc(label)}</button></div></div>`}
function leaveEditor(){const back=editorReturnView==='settings'?'settings':'ride';if(editingTripId)expandedTripId=editingTripId;if(editingLocationId){expandedLocationId=editingLocationId;settingsLocationsOpen=true}editingTripId=null;editingLocationId=null;editingLocationSeed=null;view=back;render()}
function openTripEdit(id){const t=data.trips.find(x=>x.id===id);if(!t)throw new Error('Rit niet gevonden.');editorReturnView=view==='settings'?'settings':'ride';editingTripId=id;editingLocationId=null;editingLocationSeed=null;if(!modal.hidden)closeModal();view='trip-edit';render()}
function renderTripEditPage(){const t=data.trips.find(x=>x.id===editingTripId);if(!t){editingTripId=null;view=editorReturnView==='settings'?'settings':'ride';render();return}app.innerHTML=`<div class="editor-page">${editorNav('Rit aanpassen','delete-trip',t.id)}<div class="editor-content"><form id="tripEditForm" class="edit-form editor-form" onsubmit="return false"><input type="hidden" name="id" value="${t.id}"><section class="edit-section"><div class="edit-section-head"><strong>Route</strong><small>Vertrek en bestemming</small></div><div class="edit-grid two editor-route-grid"><div class="form-group"><label>Vertrek</label><select name="originId">${editOptions(t.origin)}</select></div><div class="form-group"><label>Bestemming</label><select name="destinationId">${editOptions(t.destination)}</select></div></div></section><section class="edit-section"><div class="edit-section-head"><strong>Kilometerstanden</strong><small>${km(t.actualKm)} km geregistreerd</small></div><div class="edit-grid two keep-two">${field('Startstand','startOdometer',t.startOdometer,'number')}${field('Eindstand','endOdometer',t.endOdometer,'number')}</div></section><section class="edit-section"><div class="edit-section-head"><strong>Datum & tijd</strong><small>Vertrek en aankomst</small></div><div class="edit-grid two editor-time-grid">${field('Vertrektijd','departureTime',localInput(t.departureTime),'datetime-local')}${field('Aankomsttijd','arrivalTime',localInput(t.arrivalTime||t.departureTime),'datetime-local')}</div></section><section class="edit-section"><div class="edit-section-head"><strong>Type rit</strong><small>Voor rapportage en totalen</small></div><div class="edit-trip-type-grid">${editTripCategoryOption('commute','Woon-werk',t.category)}${editTripCategoryOption('business','Zakelijk',t.category)}${editTripCategoryOption('private','Privé',t.category)}</div></section><section class="edit-section"><div class="edit-section-head"><strong>Toelichting</strong><small>Optioneel</small></div><div class="edit-grid">${field('Reden / omschrijving','reason',t.reason||'')}<div data-private-km-field ${t.category==='private'?'hidden':''}>${field('Privédeel km','privateKm',t.privateKm||0,'number')}</div></div></section><div class="edit-warning">Bij een historische wijziging worden aangrenzende ritten niet automatisch aangepast.</div><div id="tripEditStatus" class="edit-status"></div></form></div>${editorSavebar('save-trip-edit','Wijzigingen opslaan')}</div>`}
'''
replace_block('function openTripEdit(id){','function returnFromTripEdit',trip_page,'trip full page editor')

trip_save=r'''function returnFromTripEdit(id){if(id)editingTripId=id;leaveEditor()}
function saveTripEdit(){const f=document.getElementById('tripEditForm');if(!f)throw new Error('Ritformulier niet gevonden.');const fd=new FormData(f),id=String(fd.get('id')),old=data.trips.find(x=>x.id===id);if(!old)throw new Error('Rit niet gevonden.');const s=num(fd.get('startOdometer')),e=num(fd.get('endOdometer'));if(s==null||e==null||e<s)throw new Error('Controleer kilometerstanden.');const dep=new Date(String(fd.get('departureTime'))),arr=new Date(String(fd.get('arrivalTime')));if(Number.isNaN(dep.getTime())||Number.isNaN(arr.getTime())||arr<dep)throw new Error('Controleer vertrek- en aankomsttijd.');const oc=String(fd.get('originId')),dc=String(fd.get('destinationId')),o=oc==='__current__'?old.origin:data.locations.find(x=>x.id===oc),d=dc==='__unknown__'?null:dc==='__current__'?old.destination:data.locations.find(x=>x.id===dc);if(!o)throw new Error('Controleer het vertrekpunt.');const actual=e-s,cat=String(fd.get('category')),p=cat==='private'?actual:(num(fd.get('privateKm'))||0);if(p<0||p>actual)throw new Error('Privédeel is ongeldig.');const z=split(actual,cat,p),updated={...old,origin:snap(o),destination:snap(d),departureTime:dep.toISOString(),arrivalTime:arr.toISOString(),startOdometer:s,endOdometer:e,actualKm:actual,category:cat,reason:String(fd.get('reason')||'').trim(),privateKm:z.private,businessKm:z.business,commuteKm:z.commute,updatedAt:new Date().toISOString()};data.trips[data.trips.findIndex(x=>x.id===id)]=updated;rebuildLast();save();const stored=JSON.parse(localStorage.getItem(KEY)||'{}').trips?.find(x=>x.id===id);if(!stored||+stored.startOdometer!==s||+stored.endOdometer!==e)throw new Error('Wijziging niet teruggevonden in opslag.');expandedTripId=id;editingTripId=null;view=editorReturnView==='settings'?'settings':'ride';toast('Rit bijgewerkt.');render()}
'''
replace_block('function returnFromTripEdit','function deleteTrip',trip_save,'trip save page return')
old_delete_trip="function deleteTrip(id){if(!confirm('Deze rit verwijderen? Ook tankpunten en omrijpunten van deze rit worden verwijderd.'))return;if(expandedTripId===id)expandedTripId=null;data.trips=data.trips.filter(x=>x.id!==id);data.events=data.events.filter(x=>x.tripId!==id);data.trackPoints=data.trackPoints.filter(x=>x.tripId!==id);if(trackStoreReady)deleteTrackPointsForTrip(id).catch(e=>console.warn(e));rebuildLast();save();closeModal();render();toast('Rit en gekoppelde toevoegingen verwijderd.')}"
new_delete_trip="function deleteTrip(id){if(!confirm('Deze rit verwijderen? Ook tankpunten en omrijpunten van deze rit worden verwijderd.'))return;const wasEditing=view==='trip-edit'&&editingTripId===id,back=editorReturnView==='settings'?'settings':'ride';if(expandedTripId===id)expandedTripId=null;data.trips=data.trips.filter(x=>x.id!==id);data.events=data.events.filter(x=>x.tripId!==id);data.trackPoints=data.trackPoints.filter(x=>x.tripId!==id);if(trackStoreReady)deleteTrackPointsForTrip(id).catch(e=>console.warn(e));rebuildLast();save();if(wasEditing){editingTripId=null;view=back}closeModal();render();toast('Rit en gekoppelde toevoegingen verwijderd.')}"
replace_once(old_delete_trip,new_delete_trip,'delete trip editor')

location_page=r'''async function openLocation(id=null,current=false){settingsLocationsOpen=true;const l=id?data.locations.find(x=>x.id===id):null;if(id&&!l)throw new Error('Locatie niet gevonden.');editorReturnView=view==='settings'?'settings':'ride';editingTripId=null;editingLocationId=id;editingLocationSeed=null;if(current){try{editingLocationSeed=await getPosition()}catch(e){toast(e.message||'Huidige GPS kon niet worden opgehaald.')}}view='location-edit';render()}
function renderLocationEditPage(){const l=editingLocationId?data.locations.find(x=>x.id===editingLocationId):null,g=editingLocationSeed;if(editingLocationId&&!l){editingLocationId=null;view=editorReturnView==='settings'?'settings':'ride';render();return}const title=l?'Locatie aanpassen':'Locatie toevoegen';app.innerHTML=`<div class="editor-page">${editorNav(title,l?'delete-location':'',l?.id||'')}<div class="editor-content"><form id="locationForm" class="edit-form editor-form" onsubmit="return false"><input type="hidden" name="id" value="${l?.id||''}"><section class="edit-section"><div class="edit-section-head"><strong>Basisgegevens</strong><small>Naam en adres</small></div><div class="edit-grid">${field('Naam','name',l?.name||'')}${field('Adres','address',l?.address||'')}</div></section><section class="edit-section"><div class="edit-section-head"><strong>GPS-locatie</strong><small>Automatisch of handmatig</small></div><button type="button" class="editor-link-action" data-action="gps-location">⌖ Gebruik huidige GPS</button><div class="edit-grid two keep-two">${field('Latitude','lat',coordinateInputValue(l?.lat??g?.lat),'text')}${field('Longitude','lng',coordinateInputValue(l?.lng??g?.lng),'text')}</div><div class="location-link-hint"><strong>Adres ↔ GPS</strong><br>Ontbrekende gegevens worden automatisch aangevuld; huidige GPS vervangt alleen de coördinaten.</div><div class="osm-attribution">Adreszoeking via OpenStreetMap Nominatim · <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">© OpenStreetMap-bijdragers</a></div></section><section class="edit-section"><div class="edit-section-head"><strong>Gebruik</strong><small>Herkenning en delen</small></div><div class="edit-location-behaviour"><div class="form-group"><label>Type</label><div class="location-choice-grid type">${locationTypeOption('home','🏠','Thuis',l?.type||'other')}${locationTypeOption('work','🧰','Werk',l?.type||'other')}${locationTypeOption('business','🏢','Zakelijk',l?.type||'other')}${locationTypeOption('private','👤','Privé',l?.type||'other')}${locationTypeOption('other','📍','Overig',l?.type||'other')}</div></div><div class="form-group"><label>Rit delen</label><div class="location-choice-grid share">${locationShareOption('never','⊘','Nooit',l?.shareRide||'never')}${locationShareOption('ask','?','Vraag mij',l?.shareRide||'never')}${locationShareOption('always','↗','Altijd',l?.shareRide||'never')}</div><div class="hint" style="margin-top:4px">Vraag mij: eenmalige vraag na vertrek · Altijd: Deel rit blijft beschikbaar.</div></div></div></section><div id="locationStatus" class="edit-status"></div></form></div>${editorSavebar('save-location',l?'Locatie opslaan':'Locatie toevoegen')}</div>`;setTimeout(()=>autoCompleteLocationForm(),0)}
'''
replace_block('function openLocation(id=null,current=false){','async function fillGps',location_page,'location full page editor')

location_save=r'''async function saveLocation(){const f=document.getElementById('locationForm');if(!f)throw new Error('Locatieformulier niet gevonden.');await autoCompleteLocationForm();const fd=new FormData(f),id=String(fd.get('id')||uid()),old=data.locations.find(x=>x.id===id),rawName=String(fd.get('name')||'').trim(),address=String(fd.get('address')||'').trim(),lat=parseNum(fd.get('lat')),lng=parseNum(fd.get('lng'));if((lat==null)!=(lng==null))throw new Error('Vul beide GPS-coördinaten in of laat beide leeg.');if(lat!=null&&Math.abs(lat)>90)throw new Error('Latitude is ongeldig.');if(lng!=null&&Math.abs(lng)>180)throw new Error('Longitude is ongeldig.');if(!rawName&&!address&&lat==null)throw new Error('Vul minimaal naam, adres of GPS in.');const name=rawName||address||`Locatie ${lat.toFixed(5)}, ${lng.toFixed(5)}`,loc={id,name,address,lat,lng,type:String(fd.get('type')||'other'),shareRide:['ask','always'].includes(String(fd.get('shareRide')||''))?String(fd.get('shareRide')):'never',useCount:old?.useCount||0,createdAt:old?.createdAt||new Date().toISOString(),updatedAt:new Date().toISOString()},i=data.locations.findIndex(x=>x.id===id);if(i>=0)data.locations[i]=loc;else data.locations.push(loc);save();if(!JSON.parse(localStorage.getItem(KEY)||'{}').locations?.some(x=>x.id===id))throw new Error('Locatie niet teruggevonden in opslag.');expandedLocationId=id;settingsLocationsOpen=true;editingLocationId=null;editingLocationSeed=null;view=editorReturnView==='ride'?'ride':'settings';render();toast('Locatie opgeslagen: '+name)}
'''
replace_block('async function saveLocation(){','function deleteLocation',location_save,'location save page return')
old_delete_location="function deleteLocation(id){if(!confirm('Locatie verwijderen? Bestaande ritten blijven intact.'))return;data.locations=data.locations.filter(x=>x.id!==id);if(expandedLocationId===id)expandedLocationId=null;settingsLocationsOpen=true;save();render();toast('Locatie verwijderd.')}"
new_delete_location="function deleteLocation(id){if(!confirm('Locatie verwijderen? Bestaande ritten blijven intact.'))return;const wasEditing=view==='location-edit'&&editingLocationId===id,back=editorReturnView==='ride'?'ride':'settings';data.locations=data.locations.filter(x=>x.id!==id);if(expandedLocationId===id)expandedLocationId=null;settingsLocationsOpen=true;save();if(wasEditing){editingLocationId=null;editingLocationSeed=null;view=back}render();toast('Locatie verwijderd.')}"
replace_once(old_delete_location,new_delete_location,'delete location editor')

index.write_text(text,encoding='utf-8')

sw=Path('service-worker.js')
s=sw.read_text(encoding='utf-8')
if s.count("kmreg-shell-0.28.4")!=1:
    raise SystemExit('service worker version mismatch')
s=s.replace("kmreg-shell-0.28.4","kmreg-shell-0.28.5",1)
sw.write_text(s,encoding='utf-8')

script=text.split('<script>',1)[1].rsplit('</script>',1)[0]
Path('/tmp/kmreg-app.js').write_text(script,encoding='utf-8')

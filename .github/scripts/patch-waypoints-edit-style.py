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

replace_once("+' · 0.28.2';","+' · 0.28.3';",'version')

css=r'''
/* 0.28.3 — rustige bewerkvensters en tussenstops in locatieteller */
.edit-modal-head{padding-bottom:5px}.edit-modal-head .kicker{margin-bottom:3px}.edit-form{margin-top:2px}.edit-section{padding:15px 0;border-top:1px solid var(--line)}.edit-section:first-of-type{border-top:0;padding-top:8px}.edit-section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:11px}.edit-section-head strong{font-size:13px}.edit-section-head small{font-size:10px;color:var(--muted);text-align:right}.edit-grid{display:grid;gap:9px}.edit-grid.two{grid-template-columns:repeat(2,minmax(0,1fr))}.edit-form .form-group{margin:0}.edit-form .form-group label{margin-bottom:5px;color:var(--muted);font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.05em}.edit-form .form-group input,.edit-form .form-group select,.edit-form .form-group textarea{background:#10151c;border-color:var(--line);border-radius:10px}.edit-form .location-link-hint{margin-top:10px;padding:8px 0 0;border:0;border-top:1px solid var(--line);border-radius:0;background:transparent}.edit-form .osm-attribution{margin-top:5px}.edit-gps-action{margin:0 0 9px}.edit-trip-type-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px}.edit-trip-type{position:relative}.edit-trip-type input{position:absolute;opacity:0;pointer-events:none}.edit-trip-type span{display:flex;align-items:center;justify-content:center;min-height:44px;padding:9px 6px;border:1px solid var(--line);border-radius:10px;background:#10151c;color:var(--muted);font-size:11px;font-weight:800;cursor:pointer}.edit-trip-type input:checked+span{color:var(--text);background:rgba(77,163,255,.1);box-shadow:inset 0 0 0 1px var(--accent);border-color:var(--accent)}.edit-trip-type.commute input:checked+span{border-color:var(--commute);box-shadow:inset 0 0 0 1px var(--commute)}.edit-trip-type.business input:checked+span{border-color:var(--business);box-shadow:inset 0 0 0 1px var(--business)}.edit-trip-type.private input:checked+span{border-color:var(--private);box-shadow:inset 0 0 0 1px var(--private)}.edit-warning{padding:10px 0;color:var(--muted);font-size:11px;line-height:1.4;border-top:1px solid var(--line)}.edit-actions{display:grid;gap:8px;padding-top:4px}.edit-actions .btn{width:100%}.edit-delete{margin-top:3px;border:0;background:transparent;color:var(--bad);min-height:38px;font-weight:750;cursor:pointer}.edit-status{min-height:18px;margin:4px 0;color:var(--muted);font-size:11px}.edit-location-behaviour{display:grid;gap:14px}.edit-form .location-choice-grid{margin-top:2px}@media(max-width:520px){.edit-grid.route{grid-template-columns:1fr}.edit-grid.two.keep-two{grid-template-columns:repeat(2,minmax(0,1fr))}.edit-section-head small{display:none}}
'''
replace_once('\n</style>','\n'+css+'\n</style>','edit css')

old_counter="function locationRegisteredTripCount(l){return data.trips.reduce((count,t)=>count+((sameLoc(t.origin,l)||sameLoc(t.destination,l))?1:0),0)}"
new_counter="function locationRegisteredTripCount(l){const completed=new Set(data.trips.map(t=>t.id)),seen=new Set();for(const t of data.trips){if(sameLoc(t.origin,l)||sameLoc(t.destination,l))seen.add(t.id)}for(const ev of data.events){if(ev.tripId&&completed.has(ev.tripId)&&sameLoc(ev.location,l))seen.add(ev.tripId)}return seen.size}"
replace_once(old_counter,new_counter,'waypoint counter')

old_change="const categorySelect=e.target.matches?.('#tripEditForm select[name=\"category\"],#manualForm select[name=\"category\"]')?e.target:null;if(categorySelect){const wrap=categorySelect.form?.querySelector('[data-private-km-field]');if(wrap)wrap.hidden=categorySelect.value==='private'}"
new_change="const categorySelect=e.target.matches?.('#tripEditForm [name=\"category\"],#manualForm select[name=\"category\"]')?e.target:null;if(categorySelect){const wrap=categorySelect.form?.querySelector('[data-private-km-field]');if(wrap)wrap.hidden=categorySelect.value==='private'}"
replace_once(old_change,new_change,'trip category change handler')

trip_edit=r'''function editTripCategoryOption(value,label,current){return`<label class="edit-trip-type ${categoryClass(value)}"><input type="radio" name="category" value="${value}" ${current===value?'checked':''} required><span>${label}</span></label>`}
function openTripEdit(id){const t=data.trips.find(x=>x.id===id);if(!t)throw new Error('Rit niet gevonden.');openModal(`<div class="modal-head edit-modal-head"><div><div class="kicker">Rit bewerken</div><h2>Rit aanpassen</h2></div><button class="close" data-action="back-detail" data-id="${id}" aria-label="Sluiten">×</button></div><form id="tripEditForm" class="edit-form" onsubmit="return false"><input type="hidden" name="id" value="${id}"><section class="edit-section"><div class="edit-section-head"><strong>Route</strong><small>Vertrek en bestemming</small></div><div class="edit-grid two route"><div class="form-group"><label>Vertrek</label><select name="originId">${editOptions(t.origin)}</select></div><div class="form-group"><label>Bestemming</label><select name="destinationId">${editOptions(t.destination)}</select></div></div></section><section class="edit-section"><div class="edit-section-head"><strong>Kilometerstanden</strong><small>${km(t.actualKm)} km geregistreerd</small></div><div class="edit-grid two keep-two">${field('Startstand','startOdometer',t.startOdometer,'number')}${field('Eindstand','endOdometer',t.endOdometer,'number')}</div></section><section class="edit-section"><div class="edit-section-head"><strong>Tijd</strong><small>Vertrek en aankomst</small></div><div class="edit-grid two">${field('Vertrektijd','departureTime',localInput(t.departureTime),'datetime-local')}${field('Aankomsttijd','arrivalTime',localInput(t.arrivalTime||t.departureTime),'datetime-local')}</div></section><section class="edit-section"><div class="edit-section-head"><strong>Type rit</strong><small>Voor rapportage en totalen</small></div><div class="edit-trip-type-grid">${editTripCategoryOption('commute','Woon-werk',t.category)}${editTripCategoryOption('business','Zakelijk',t.category)}${editTripCategoryOption('private','Privé',t.category)}</div></section><section class="edit-section"><div class="edit-section-head"><strong>Toelichting</strong><small>Optioneel</small></div><div class="edit-grid">${field('Reden / omschrijving','reason',t.reason||'')}<div data-private-km-field ${t.category==='private'?'hidden':''}>${field('Privédeel km','privateKm',t.privateKm||0,'number')}</div></div></section><div class="edit-warning">Bij een historische wijziging worden aangrenzende ritten niet automatisch aangepast.</div><div id="tripEditStatus" class="edit-status"></div><div class="edit-actions"><button class="btn" type="button" data-action="save-trip-edit">Wijzigingen opslaan</button><button class="edit-delete" type="button" data-action="delete-trip" data-id="${id}">Rit verwijderen</button></div></form>`)}
'''
replace_block('function openTripEdit(id){','function returnFromTripEdit',trip_edit,'trip edit form')

location_edit=r'''function openLocation(id=null,current=false){settingsLocationsOpen=true;const l=id?data.locations.find(x=>x.id===id):null,build=g=>{openModal(`<div class="modal-head edit-modal-head"><div><div class="kicker">Locatie</div><h2>${l?'Locatie aanpassen':'Locatie toevoegen'}</h2></div><button class="close" data-action="close" aria-label="Sluiten">×</button></div><form id="locationForm" class="edit-form" onsubmit="return false"><input type="hidden" name="id" value="${l?.id||''}"><section class="edit-section"><div class="edit-section-head"><strong>Basisgegevens</strong><small>Naam en adres</small></div><div class="edit-grid">${field('Naam','name',l?.name||'')}${field('Adres','address',l?.address||'')}</div></section><section class="edit-section"><div class="edit-section-head"><strong>GPS-locatie</strong><small>Automatisch of handmatig</small></div><button type="button" class="btn secondary full edit-gps-action" data-action="gps-location">⌖ Gebruik huidige GPS</button><div class="edit-grid two keep-two">${field('Latitude','lat',l?.lat??g?.lat??'','text')}${field('Longitude','lng',l?.lng??g?.lng??'','text')}</div><div class="location-link-hint"><strong>Adres ↔ GPS</strong><br>Alleen ontbrekende gegevens worden automatisch aangevuld. Bestaande waarden blijven staan. Huidige GPS overschrijft bewust alleen de coördinaten om ze nauwkeuriger te maken.</div><div class="osm-attribution">Adreszoeking via OpenStreetMap Nominatim · <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">© OpenStreetMap-bijdragers</a></div></section><section class="edit-section"><div class="edit-section-head"><strong>Gebruik</strong><small>Herkenning en delen</small></div><div class="edit-location-behaviour"><div class="form-group"><label>Type</label><div class="location-choice-grid type">${locationTypeOption('home','🏠','Thuis',l?.type||'other')}${locationTypeOption('work','🧰','Werk',l?.type||'other')}${locationTypeOption('business','🏢','Zakelijk',l?.type||'other')}${locationTypeOption('private','👤','Privé',l?.type||'other')}${locationTypeOption('other','📍','Overig',l?.type||'other')}</div></div><div class="form-group"><label>Rit delen</label><div class="location-choice-grid share">${locationShareOption('never','⊘','Nooit',l?.shareRide||'never')}${locationShareOption('ask','?','Vraag mij',l?.shareRide||'never')}${locationShareOption('always','↗','Altijd',l?.shareRide||'never')}</div><div class="hint" style="margin-top:6px">Bij Vraag mij krijg je na vertrek een eenmalige vraag. Bij Altijd blijft Deel rit beschikbaar tijdens de actieve rit.</div></div></div></section><div class="hint">Vul minimaal naam, adres of GPS in.</div><div id="locationStatus" class="edit-status"></div><div class="edit-actions"><button type="button" class="btn" data-action="save-location">Locatie opslaan</button></div></form>`);setTimeout(()=>autoCompleteLocationForm(),0)};if(current)getPosition().then(build).catch(e=>{toast(e.message);build(null)});else build(null)}
'''
replace_block('function openLocation(id=null,current=false){','async function fillGps',location_edit,'location edit form')

index.write_text(text,encoding='utf-8')

sw=Path('service-worker.js')
s=sw.read_text(encoding='utf-8')
if s.count("kmreg-shell-0.28.2")!=1:
    raise SystemExit('service worker version mismatch')
s=s.replace("kmreg-shell-0.28.2","kmreg-shell-0.28.3",1)
sw.write_text(s,encoding='utf-8')

script=text.split('<script>',1)[1].rsplit('</script>',1)[0]
Path('/tmp/kmreg-app.js').write_text(script,encoding='utf-8')

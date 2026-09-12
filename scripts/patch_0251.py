from pathlib import Path
import re

p=Path('index.html')
s=p.read_text()

assert s.count(" · 0.25.0") == 1
s=s.replace(" · 0.25.0"," · 0.25.1",1)

old="function swipeDeleteEnabled(){return data.settings.swipeDeleteEnabled!==false}"
new="function swipeDeleteEnabled(){return data.settings.swipeDeleteEnabled===true}"
assert old in s
s=s.replace(old,new,1)

# Normaliseer oude/import-waarden expliciet naar boolean zodat '0' of 'false' nooit als ingeschakeld telt.
old="function normalize(x){return{settings:{...DEFAULT.settings,...(x.settings||{})},locations:Array.isArray(x.locations)?x.locations:[],trips:Array.isArray(x.trips)?x.trips:[],events:Array.isArray(x.events)?x.events:[],trackPoints:Array.isArray(x.trackPoints)?x.trackPoints:[],activeTrip:x.activeTrip||null,lastEndpoint:x.lastEndpoint||null}}"
new="function normalize(x){const settings={...DEFAULT.settings,...(x.settings||{})},rawSwipe=settings.swipeDeleteEnabled;settings.swipeDeleteEnabled=rawSwipe===true||rawSwipe===1||rawSwipe==='1'||rawSwipe==='true';return{settings,locations:Array.isArray(x.locations)?x.locations:[],trips:Array.isArray(x.trips)?x.trips:[],events:Array.isArray(x.events)?x.events:[],trackPoints:Array.isArray(x.trackPoints)?x.trackPoints:[],activeTrip:x.activeTrip||null,lastEndpoint:x.lastEndpoint||null}}"
assert old in s
s=s.replace(old,new,1)

# Swipeknoppen gebruiken een apart, bewaakt verwijderpad in plaats van de gewone verwijderacties.
pattern=r"function swipeActions\(kind,id\)\{.*?\nfunction inlineEventRow"
replacement="""function swipeActions(kind,id){const editAction=kind==='trip'?'edit-trip':kind==='event'?'edit-event':'edit-location';return`<div class=\"swipe-actions trip-swipe-actions\">${swipeDeleteEnabled()?`<button type=\"button\" class=\"swipe-action trip-swipe-action swipe-delete\" data-action=\"swipe-delete\" data-kind=\"${kind}\" data-id=\"${id}\">Verwijder</button>`:''}<button type=\"button\" class=\"swipe-action trip-swipe-action swipe-edit\" data-action=\"${editAction}\" data-id=\"${id}\">Bewerk</button></div>`}\nfunction inlineEventRow"""
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
assert n==1, f'swipeActions replacements: {n}'

old="function swipeDelete(kind,id){if(kind==='trip')deleteTrip(id);else if(kind==='event')deleteEvent(id);else if(kind==='location')deleteLocation(id)}"
new="function swipeDelete(kind,id){if(!swipeDeleteEnabled()){toast('Verwijderen met swipe staat uit.');return}if(kind==='trip')deleteTrip(id);else if(kind==='event')deleteEvent(id);else if(kind==='location')deleteLocation(id)}"
assert old in s
s=s.replace(old,new,1)

# Ook de aparte swipe-delete-knop loopt door dezelfde veiligheidscontrole.
needle="else if(a==='save-trip-edit')saveTripEdit();else if(a==='delete-trip')deleteTrip(el.dataset.id);"
replacement="else if(a==='save-trip-edit')saveTripEdit();else if(a==='swipe-delete')swipeDelete(el.dataset.kind,el.dataset.id);else if(a==='delete-trip')deleteTrip(el.dataset.id);"
assert needle in s
s=s.replace(needle,replacement,1)

# De lijst 'Onderweg geregistreerd' gebruikt dezelfde swipe-regels als tussenpunten in een opengeklapte rit.
pattern=r"function routePointList\(points,clickable=true\)\{.*?\nfunction openModal"
replacement="""function routePointList(points,clickable=true){if(clickable)return`<div class=\"route-points route-points-swipe\">${points.map(inlineEventRow).join('')}</div>`;return`<div class=\"route-points\">${points.map(x=>`<div class=\"route-point\" data-event-id=\"${x.id}\"><div class=\"route-point-icon\">${x.type==='tank'?'⛽':'↪'}</div><div class=\"route-point-main\"><strong>${x.type==='tank'?'Tanken':'Omrijpunt'} · ${esc(labelLoc(x.location)||'Locatie niet vastgelegd')}</strong><small>${dateTime(x.time)}${x.note?' · '+esc(x.note):''}</small></div>${x.odometer!=null?`<div class=\"route-point-km\">${odo(x.odometer)} km</div>`:''}</div>`).join('')}</div>`}\nfunction openModal"""
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
assert n==1, f'routePointList replacements: {n}'

# Verplaats de swipe-verwijderoptie uit Ritten naar een algemeen instellingenblok.
pattern=r'<details class="accordion"><summary><span class="accordion-title"><strong>Ritten</strong>.*?</details>\n<details class="accordion"><summary><span class="accordion-title"><strong>Navigatie</strong>'
replacement='''<details class="accordion"><summary><span class="accordion-title"><strong>Algemeen</strong><small>Bediening en veiligheidsopties</small></span><span class="accordion-arrow">›</span></summary><div class="accordion-body"><div class="form-group"><label>Verwijderen met swipe</label><select name="swipeDeleteEnabled"><option value="1" ${s.swipeDeleteEnabled===true?'selected':''}>Aan</option><option value="0" ${s.swipeDeleteEnabled!==true?'selected':''}>Uit</option></select><div class="hint">Bewerken met swipe blijft altijd actief. Alleen wanneer deze optie op Aan staat kan verder vegen een rit, tussenpunt of opgeslagen locatie verwijderen. Voor verwijderen blijft een bevestiging nodig.</div></div></div></details>\n<details class="accordion"><summary><span class="accordion-title"><strong>Ritten</strong><small>${privateDaysSummary(s.privateDays)}</small></span><span class="accordion-arrow">›</span></summary><div class="accordion-body"><div class="form-group"><label>Standaard privédagen</label><div class="day-grid">${privateDayOptions(s.privateDays)}</div><div class="hint">Op deze dagen stelt de app bij vertrek standaard Privé voor. Je kunt het rit-type altijd wijzigen.</div></div></div></details>\n<details class="accordion"><summary><span class="accordion-title"><strong>Navigatie</strong>'''
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
assert n==1, f'settings replacements: {n}'

# Opslaan altijd als echte boolean; ontbrekende/uit-waarde is false.
old="swipeDeleteEnabled:String(fd.get('swipeDeleteEnabled')||'1')!=='0'"
new="swipeDeleteEnabled:String(fd.get('swipeDeleteEnabled')||'0')==='1'"
assert old in s
s=s.replace(old,new,1)

p.write_text(s)

sw=Path('service-worker.js')
w=sw.read_text()
assert "kmreg-shell-0.25.0" in w
w=w.replace("kmreg-shell-0.25.0","kmreg-shell-0.25.1",1)
sw.write_text(w)

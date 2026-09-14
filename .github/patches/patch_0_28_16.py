from pathlib import Path
import re


def sub_once(text, pattern, repl, label, flags=0):
    out, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 replacement, got {n}')
    return out

# ---- index.html ----
p = Path('index.html')
s = p.read_text()
if ' · 0.28.15' not in s:
    raise SystemExit('index version 0.28.15 not found')
s = s.replace(' · 0.28.15', ' · 0.28.16', 1)

inline_new = r'''function eventTimeLabel(ev){return ev?.historicalTimeUnknown?'Tijd onbekend':time(ev.time)}
function eventDateTimeLabel(ev){return ev?.historicalTimeUnknown?(ev.time?shortDate(ev.time)+' · tijd onbekend':'Tijd onbekend'):dateTime(ev.time)}
function inlineEventRow(ev,fullDate=false){const loc=locationDisplay(ev.location),meta=[ev.odometer!=null?odo(ev.odometer)+' km':'',ev.note||''].filter(Boolean).join(' · '),day=fullDate&&ev.time?shortDate(ev.time):'',timeLabel=eventTimeLabel(ev);return`<div class="swipe-row inline-event-swipe" data-swipe-kind="event" data-id="${ev.id}">${swipeActions('event',ev.id)}<div class="swipe-surface inline-event-surface" data-action="event-detail" data-id="${ev.id}"><div class="inline-event-time">${day?`<span>${esc(day)}</span>`:''}<strong>${esc(timeLabel)}</strong></div><div class="inline-event-icon">${ev.type==='tank'?'⛽':'↪'}</div><div class="inline-event-main"><strong>${ev.type==='tank'?'Tankpunt':'Omrijpunt'} · ${esc(loc.label)}</strong>${loc.extra?`<small>${esc(loc.extra)}</small>`:''}${meta?`<small>${esc(meta)}</small>`:''}</div><div class="inline-event-km">›</div></div></div>`}
function tripInlineDetails'''
s = sub_once(s, r'function inlineEventRow\(ev,fullDate=false\)\{.*?\}\nfunction tripInlineDetails', inline_new, 'inlineEventRow', re.S)

open_detail_new = r'''function openEventDetail(id){const ev=data.events.find(x=>x.id===id);if(!ev)throw new Error('Rittoevoeging niet gevonden.');const trip=ev.tripId?data.trips.find(x=>x.id===ev.tripId):null;openModal(`<div class="modal-head"><div><div class="kicker">Rittoevoeging</div><h2>${ev.type==='tank'?'Tankpunt':'Omrijpunt'}</h2></div><button class="close" data-action="close">×</button></div><div class="detail-hero"><div class="detail-date">${esc(eventDateTimeLabel(ev))}</div><div class="detail-route">${ev.type==='tank'?'⛽':'↪'} ${esc(labelLoc(ev.location)||'Locatie niet vastgelegd')}</div>${ev.location?.address?`<div class="detail-address">${esc(ev.location.address)}</div>`:''}</div><div class="detail-grid"><div class="detail-item"><span>Kilometerstand</span><strong>${ev.odometer!=null?odo(ev.odometer)+' km':'—'}</strong></div><div class="detail-item"><span>Gekoppeld aan rit</span><strong>${trip?esc(labelLoc(trip.origin)||'Onbekend')+' → '+esc(labelLoc(trip.destination)||'Onbekend'):'Nee'}</strong></div></div><div class="detail-note"><div class="kicker" style="margin-bottom:5px">Notitie</div>${ev.note?esc(ev.note):'<span class="muted">Geen notitie.</span>'}</div><div class="event-actions"><button class="btn secondary" data-action="close">Sluiten</button><button class="btn" data-action="edit-event" data-id="${id}">Aanpassen</button></div>`)}
function eventLocationOptions'''
s = sub_once(s, r'function openEventDetail\(id\)\{.*?\}\nfunction eventLocationOptions', open_detail_new, 'openEventDetail', re.S)

open_edit_new = r'''function openEventEdit(id){const ev=data.events.find(x=>x.id===id);if(!ev)throw new Error('Rittoevoeging niet gevonden.');const historicalUnknown=ev.historicalTimeUnknown===true;openModal(`<div class="modal-head"><div><div class="kicker">Wijzigen</div><h2>${ev.type==='tank'?'Tankpunt':'Omrijpunt'} aanpassen</h2></div><button class="close" data-action="close">×</button></div><form id="eventEditForm" onsubmit="return false"><input type="hidden" name="id" value="${id}"><div class="form-group"><label>Locatie</label><select name="locationId">${eventLocationOptions(ev)}</select></div>${field(ev.type==='tank'?'Kilometerstand':'Kilometerstand (optioneel)','odometer',ev.odometer??'','number')}${field('Notitie','note',ev.note||'')}${field('Tijd','time',historicalUnknown?'':localInput(ev.time),'datetime-local')}${historicalUnknown?'<div class="hint">De oorspronkelijke notitie bevatte geen tijd voor dit tussenpunt. Laat leeg om “Tijd onbekend” te behouden.</div>':''}<div id="eventEditStatus" class="hint"></div><button type="button" class="btn full" data-action="save-event">Wijzigingen opslaan</button><div class="divider"></div><button type="button" class="btn danger full" data-action="delete-event" data-id="${id}">${ev.type==='tank'?'Tankpunt':'Omrijpunt'} verwijderen</button></form>`)}
function saveEventEdit'''
s = sub_once(s, r'function openEventEdit\(id\)\{.*?\}\nfunction saveEventEdit', open_edit_new, 'openEventEdit', re.S)

save_edit_new = r'''function saveEventEdit(){const f=document.getElementById('eventEditForm');if(!f)throw new Error('Formulier niet gevonden.');const fd=new FormData(f),id=String(fd.get('id')),ev=data.events.find(x=>x.id===id);if(!ev)throw new Error('Rittoevoeging niet gevonden.');const choice=String(fd.get('locationId')||'__current__'),location=choice==='__current__'?ev.location:data.locations.find(x=>x.id===choice);const odometer=num(fd.get('odometer'));if(ev.type==='tank'&&odometer==null)throw new Error('Vul de kilometerstand in.');const timeValue=String(fd.get('time')||'').trim();let eventTime=ev.time,historicalTimeUnknown=ev.historicalTimeUnknown===true;if(timeValue){const when=new Date(timeValue);if(Number.isNaN(when.getTime()))throw new Error('Controleer de tijd.');eventTime=when.toISOString();historicalTimeUnknown=false}else if(!historicalTimeUnknown)throw new Error('Controleer de tijd.');Object.assign(ev,{location:snap(location),odometer,note:String(fd.get('note')||'').trim(),time:eventTime,historicalTimeUnknown,updatedAt:new Date().toISOString()});save();if(ev.tripId)expandedTripId=ev.tripId;closeModal();render();toast('Rittoevoeging bijgewerkt.')}
function deleteEvent'''
s = sub_once(s, r'function saveEventEdit\(\)\{.*?\}\nfunction deleteEvent', save_edit_new, 'saveEventEdit', re.S)

old_route = "<small>${dateTime(x.time)}${x.note?' · '+esc(x.note):''}</small>"
new_route = "<small>${esc(eventDateTimeLabel(x))}${x.note?' · '+esc(x.note):''}</small>"
if old_route not in s:
    raise SystemExit('routePointList time marker not found')
s = s.replace(old_route, new_route, 1)
p.write_text(s)

# ---- import.html ----
p = Path('import.html')
s = p.read_text()

css_marker = '.trip-note.error{color:#ff9a9a}'
css_add = css_marker + '.note-drop{margin-top:10px;padding:16px;border:1.5px dashed var(--line);border-radius:14px;background:#101722;text-align:center;transition:.15s}.note-drop.drag{border-color:var(--accent);background:rgba(77,163,255,.09)}.note-drop strong,.note-drop small{display:block}.note-drop small{margin-top:4px}.note-drop .btn{margin-top:10px;min-height:38px;padding:8px 12px}.note-file-status{margin-top:7px;font-size:11px;color:var(--muted)}.trip-waypoints{grid-column:3/5;display:grid;gap:4px;margin-top:2px}.trip-waypoint{display:flex;gap:7px;align-items:center;font-size:11px;color:var(--muted)}.trip-waypoint strong{color:var(--text);font-size:11px}.trip-waypoint .wp-km{margin-left:auto;white-space:nowrap}'
if css_marker not in s:
    raise SystemExit('import CSS marker not found')
s = s.replace(css_marker, css_add, 1)
s = s.replace('.trip-note{grid-column:2/4}', '.trip-note{grid-column:2/4}.trip-waypoints{grid-column:2/4}', 1)

textarea_marker = '</textarea>\n    <div class="row" style="margin-top:10px">'
drop_html = '''</textarea>
    <div id="noteDrop" class="note-drop" tabindex="0" role="button" aria-label="Sleep of kies meerdere notitiebestanden">
      <strong>Sleep meerdere notities hierheen</strong>
      <small>Tekst, Markdown, HTML en RTF · of sleep tekst rechtstreeks vanuit Apple Notities</small>
      <button class="btn secondary" id="noteFilesBtn" type="button">Bestanden kiezen</button>
      <input id="noteFiles" type="file" multiple accept=".txt,.md,.markdown,.html,.htm,.rtf,text/plain,text/markdown,text/html,application/rtf" hidden>
    </div>
    <div id="noteFileStatus" class="note-file-status"></div>
    <div class="row" style="margin-top:10px">'''
if textarea_marker not in s:
    raise SystemExit('textarea marker not found')
s = s.replace(textarea_marker, drop_html, 1)

s = s.replace('Aankomsttijden worden als <strong>onbekend</strong> bewaard. De oude notities bevatten alleen een vertrektijd, dus de importer verzint geen tijd.', 'Aankomsttijden worden als <strong>onbekend</strong> bewaard. Ook bij Via- en tankpunten wordt geen tijd verzonnen als die niet in de oude notitie staat.', 1)

s = s.replace('let db=loadDb(),parsed=null;', 'let db=loadDb(),parsed=null,loadedNoteFiles=0;', 1)
s = s.replace("$('#clearBtn').addEventListener('click',()=>{sourceText.value='';parsed=null;preview.classList.add('hidden');done.classList.add('hidden');sourceText.focus()});", "$('#clearBtn').addEventListener('click',()=>{sourceText.value='';parsed=null;loadedNoteFiles=0;$('#noteFileStatus').textContent='';preview.classList.add('hidden');done.classList.add('hidden');sourceText.focus()});", 1)

listener_marker = "$('#importBtn').addEventListener('click',importSelected);\n\ndocument.addEventListener('change',e=>{if(e.target.matches('.trip-check'))updateImportSummary()});"
listener_new = r'''$('#importBtn').addEventListener('click',importSelected);
$('#noteFilesBtn').addEventListener('click',e=>{e.stopPropagation();$('#noteFiles').click()});
$('#noteFiles').addEventListener('change',async e=>{const files=[...(e.target.files||[])];e.target.value='';await ingestNoteFiles(files)});
const noteDrop=$('#noteDrop');
for(const type of ['dragenter','dragover'])noteDrop.addEventListener(type,e=>{e.preventDefault();noteDrop.classList.add('drag')});
for(const type of ['dragleave','drop'])noteDrop.addEventListener(type,e=>{e.preventDefault();noteDrop.classList.remove('drag')});
noteDrop.addEventListener('drop',async e=>{const files=[...(e.dataTransfer?.files||[])];if(files.length){await ingestNoteFiles(files);return}let text=e.dataTransfer?.getData('text/plain')||'';if(!text){const html=e.dataTransfer?.getData('text/html')||'';if(html)text=htmlToText(html)}if(text.trim()){appendNoteText(text,'Gesleepte notitie');loadedNoteFiles++;updateNoteFileStatus([],1)}});
noteDrop.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();$('#noteFiles').click()}});

async function ingestNoteFiles(files){if(!files.length)return;let added=0;const failed=[];for(const file of files){try{const text=await readNoteFile(file);if(!text.trim())throw new Error('leeg bestand');appendNoteText(text,file.name);added++;loadedNoteFiles++}catch(err){failed.push(`${file.name}: ${err.message||'niet leesbaar'}`)}}updateNoteFileStatus(failed,added);if(added)toast(`${added} ${added===1?'notitie':'notities'} toegevoegd.`)}
async function readNoteFile(file){const name=String(file.name||'').toLowerCase(),type=String(file.type||'').toLowerCase();if(name.endsWith('.pdf')||type==='application/pdf')throw new Error('PDF wordt hier niet automatisch gelezen');if(!(name.match(/\.(txt|md|markdown|html?|rtf)$/)||type.startsWith('text/')||type.includes('rtf')))throw new Error('bestandstype niet ondersteund');const raw=await file.text();if(name.match(/\.html?$/)||type==='text/html')return htmlToText(raw);if(name.endsWith('.rtf')||type.includes('rtf'))return rtfToText(raw);return raw}
function htmlToText(html){const doc=new DOMParser().parseFromString(String(html||''),'text/html');return (doc.body?.innerText||doc.body?.textContent||'').replace(/\u00a0/g,' ')}
function rtfToText(rtf){return String(rtf||'').replace(/\\par[d]?\b/g,'\n').replace(/\\tab\b/g,'\t').replace(/\\'[0-9a-fA-F]{2}/g,m=>{try{return String.fromCharCode(parseInt(m.slice(2),16))}catch(_){return''}}).replace(/\\[a-z]+-?\d* ?/gi,'').replace(/[{}]/g,'').replace(/\\([{}\\])/g,'$1')}
function appendNoteText(text,label){const clean=String(text||'').replace(/\r/g,'').trim();if(!clean)return;const sep=sourceText.value.trim()?`\n\n--- ${label||'Notitie'} ---\n\n`:'';sourceText.value+=sep+clean}
function updateNoteFileStatus(failed=[],added=0){const parts=[];if(loadedNoteFiles)parts.push(`${loadedNoteFiles} ${loadedNoteFiles===1?'notitie':'notities'} ingelezen`);if(failed.length)parts.push(`${failed.length} overgeslagen: ${failed.join(' · ')}`);$('#noteFileStatus').textContent=parts.join(' · ')}

document.addEventListener('change',e=>{if(e.target.matches('.trip-check'))updateImportSummary()});'''
if listener_marker not in s:
    raise SystemExit('listener marker not found')
s = s.replace(listener_marker, listener_new, 1)

parse_notes_new = r'''  const locations=buildLocationCandidates(trips);
  const existingByKey=new Map(db.trips.map(x=>[duplicateKey(x),x]));
  for(const t of trips){const existing=existingByKey.get(duplicateKey(t))||null;t.existingTripId=existing?.id||null;t.duplicate=!!existing;t.pendingWaypoints=(t.waypoints||[]).filter(w=>!existing||!waypointExists(existing,w));t.valid=Number.isFinite(t.startOdometer)&&Number.isFinite(t.endOdometer)&&t.endOdometer>=t.startOdometer&&!!t.originRaw&&!!t.destinationRaw;if(t.duplicate){if(t.pendingWaypoints.length)t.warnings.push(`Rit bestaat al; ${t.pendingWaypoints.length} ontbrekende ${t.pendingWaypoints.length===1?'tussenpunt wordt':'tussenpunten worden'} toegevoegd.`);else t.warnings.push('Deze rit inclusief tussenpunten lijkt al in de app te staan.')}if(!t.valid)t.warnings.push('Onvoldoende geldige gegevens om deze rit te importeren.')}
  return{metadata,trips,locations,warnings};'''
s = sub_once(s, r'  const locations=buildLocationCandidates\(trips\);\n  const existingKeys=new Set\(db\.trips\.map\(duplicateKey\)\);\n  for\(const t of trips\)\{.*?\n  return\{metadata,trips,locations,warnings\};', parse_notes_new, 'parseNotes duplicate block', re.S)

trip_parse_new = r'''function parseTripBlock(block){
  const warnings=[];const dt=parseDutchDateTime(block.header);if(!dt)warnings.push('Datum/tijd niet herkend.');
  let section=null,category=null,startOdometer=null,endOdometer=null,statedDistance=null,reason='',originLines=[],destinationLines=[],waypoints=[],currentWaypoint=null;
  const flushWaypoint=()=>{if(!currentWaypoint)return;const raw=cleanLocationText(currentWaypoint.lines.join(', '));const wp={type:currentWaypoint.type,raw,odometer:currentWaypoint.odometer,note:currentWaypoint.note||''};if(!raw)warnings.push(`${wp.type==='tank'?'Tanklocatie':'Omrijpunt'} zonder locatie.`);if(wp.odometer==null)warnings.push(`${wp.type==='tank'?'Tanklocatie':'Omrijpunt'} zonder kilometerstand.`);waypoints.push(wp);currentWaypoint=null};
  for(const line of block.lines){if(!line||/^---/.test(line))continue;
    if(/^Vertrek\s+adres\s*:/i.test(line)){flushWaypoint();section='origin';continue}
    if(/^(?:Via(?:\s+locatie)?|Omrijpunt)\s*:/i.test(line)){flushWaypoint();section='waypoint';currentWaypoint={type:'detour',lines:[],odometer:null,note:''};continue}
    if(/^(?:Tank\s*locatie|Tanklocatie|Tanken)\s*:/i.test(line)){flushWaypoint();section='waypoint';currentWaypoint={type:'tank',lines:[],odometer:null,note:''};continue}
    if(/^Aankomst\s+adres\s*:/i.test(line)){flushWaypoint();section='destination';continue}
    const cat=parseCategory(line);if(cat&&section==='origin'&&startOdometer==null){category=cat;continue}
    let m=line.match(/^Kilometerstand\s*:\s*([\d.,]+)/i);if(m){const v=toNumber(m[1]);if(section==='origin')startOdometer=v;else if(section==='destination')endOdometer=v;else if(section==='waypoint'&&currentWaypoint)currentWaypoint.odometer=v;continue}
    m=line.match(/^Ritafstand\s*:\s*([\d.,]+)/i);if(m){statedDistance=toNumber(m[1]);continue}
    m=line.match(/^(?:Reden|Notitie)\s*:\s*(.*)$/i);if(m){if(section==='waypoint'&&currentWaypoint)currentWaypoint.note=m[1].trim();else reason=m[1].trim();continue}
    if(section==='origin'&&startOdometer==null)originLines.push(line);else if(section==='destination'&&endOdometer==null)destinationLines.push(line);else if(section==='waypoint'&&currentWaypoint)currentWaypoint.lines.push(line);
  }
  flushWaypoint();
  const originRaw=cleanLocationText(originLines.join(', ')),destinationRaw=cleanLocationText(destinationLines.join(', '));
  const calculatedDistance=Number.isFinite(startOdometer)&&Number.isFinite(endOdometer)?endOdometer-startOdometer:null;
  if(!category)category='business';
  if(calculatedDistance!=null&&calculatedDistance<0)warnings.push('Eindkilometerstand ligt onder de startkilometerstand.');
  if(calculatedDistance!=null&&statedDistance!=null&&Math.abs(calculatedDistance-statedDistance)>.01)warnings.push(`Ritafstand in notitie is ${fmt(statedDistance)} km, terwijl de kilometerstanden ${fmt(calculatedDistance)} km geven. De kilometerstanden worden leidend.`);
  for(const wp of waypoints){if(wp.odometer!=null&&startOdometer!=null&&wp.odometer<startOdometer)warnings.push(`${wp.type==='tank'?'Tankpunt':'Omrijpunt'} ${odo(wp.odometer)} km ligt vóór de startstand.`);if(wp.odometer!=null&&endOdometer!=null&&wp.odometer>endOdometer)warnings.push(`${wp.type==='tank'?'Tankpunt':'Omrijpunt'} ${odo(wp.odometer)} km ligt na de eindstand.`)}
  if(!originRaw)warnings.push('Vertrekadres ontbreekt.');if(!destinationRaw)warnings.push('Aankomstadres ontbreekt.');if(startOdometer==null)warnings.push('Startkilometerstand ontbreekt.');if(endOdometer==null)warnings.push('Eindkilometerstand ontbreekt.');
  return{id:uid(),number:block.number,departureTime:dt?dt.toISOString():null,displayDate:dt?formatDateTime(dt):block.header,category,startOdometer,endOdometer,statedDistance,actualKm:calculatedDistance,reason,originRaw,destinationRaw,waypoints,warnings};
}'''
s = sub_once(s, r'function parseTripBlock\(block\)\{.*?\n\}', trip_parse_new, 'parseTripBlock', re.S)

waypoint_helpers = r'''function waypointExists(trip,w){if(!trip)return false;const key=locationKey(parseLocation(w.raw).address||w.raw);return db.events.some(ev=>{if(ev.tripId!==trip.id||ev.type!==w.type)return false;const evKey=locationKey(ev.location?.address||ev.location?.name||'');const sameOdo=(ev.odometer==null&&w.odometer==null)||(+ev.odometer===+w.odometer);return sameOdo&&!!key&&evKey===key})}

function buildLocationCandidates(trips){
  const map=new Map();
  for(const t of trips){const entries=[['origin',t.originRaw],['destination',t.destinationRaw],...(t.waypoints||[]).map(w=>['waypoint',w.raw])];for(const [role,raw] of entries){if(!raw)continue;const parsedLoc=parseLocation(raw),key=locationKey(parsedLoc.address||raw);if(!map.has(key))map.set(key,{key,raw,parsed:parsedLoc,count:0,roles:[],tripTypes:[],times:[]});const c=map.get(key);c.count++;c.roles.push(role);c.tripTypes.push(t.category);c.times.push({role,date:t.departureTime?new Date(t.departureTime):null});}}
  for(const c of map.values()){c.existing=findExistingLocation(c.parsed,c.raw);c.suggestedType=c.existing?.type||inferLocationType(c);c.suggestedName=c.existing?.name||c.parsed.name||c.parsed.address||c.raw}
  return[...map.values()];
}'''
s = sub_once(s, r'function buildLocationCandidates\(trips\)\{.*?\n\}', waypoint_helpers, 'buildLocationCandidates', re.S)
s = s.replace("function inferLocationType(c){let home=0,work=0,priv=0,biz=0;", "function inferLocationType(c){if(c.roles?.length&&c.roles.every(x=>x==='waypoint'))return'other';let home=0,work=0,priv=0,biz=0;", 1)

render_preview_new = r'''function renderPreview(){
  if(!parsed)return;
  const selected=parsed.trips.filter(t=>t.valid&&(!t.duplicate||t.pendingWaypoints.length)),newTrips=selected.filter(t=>!t.duplicate),totalKm=newTrips.reduce((s,t)=>s+(+t.actualKm||0),0),duplicates=parsed.trips.filter(t=>t.duplicate&&!t.pendingWaypoints.length).length,waypoints=selected.reduce((s,t)=>s+(t.pendingWaypoints?.length||0),0);
  $('#stats').innerHTML=stat('Gevonden',parsed.trips.length,'ritten')+stat('Nieuwe ritten',newTrips.length,'ritten')+stat('Tussenpunten',waypoints,'punten')+stat('Afstand',fmt(totalKm),'km')+stat('Dubbel',duplicates,'ritten');
  const m=parsed.metadata;$('#metadataWrap').innerHTML=(m.name||m.vehicleBrand||m.plate)?`<div class="meta"><div class="item"><span>Naam</span><strong>${esc(m.name||'—')}</strong></div><div class="item"><span>Automerk</span><strong>${esc(m.vehicleBrand||'—')}</strong></div><div class="item"><span>Kenteken</span><strong>${esc(m.plate||'—')}</strong></div></div>`:'';
  const uniqueWarnings=[...new Set(parsed.warnings)];$('#warningsWrap').innerHTML=uniqueWarnings.length?`<div class="warning-list">${uniqueWarnings.map(w=>`<div class="warning-item">⚠ ${esc(w)}</div>`).join('')}</div>`:`<div class="warning-item">✓ Geen gaten tussen opeenvolgende kilometerstanden gevonden in de geplakte gegevens.</div>`;
  $('#locations').innerHTML=parsed.locations.map(renderLocation).join('')||'<div class="empty">Geen locaties gevonden.</div>';
  $('#trips').innerHTML=parsed.trips.map(renderTrip).join('');
  $('#tripCountLabel').textContent=`${parsed.trips.length} ritten · ${parsed.trips.reduce((n,t)=>n+(t.waypoints?.length||0),0)} tussenpunten gevonden`;
  updateImportSummary();
}'''
s = sub_once(s, r'function renderPreview\(\)\{.*?\n\}', render_preview_new, 'renderPreview', re.S)

render_trip_new = r'''function renderTrip(t){const pending=t.pendingWaypoints?.length||0,importable=t.valid&&(!t.duplicate||pending>0),checked=importable?'checked':'',disabled=!importable?'disabled':'',notes=[...t.warnings],cls=['trip',t.duplicate&&!pending?'duplicate':'',!t.valid?'error':''].filter(Boolean).join(' '),wps=(t.waypoints||[]).map(w=>`<div class="trip-waypoint"><span>${w.type==='tank'?'⛽':'↪'}</span><strong>${w.type==='tank'?'Tankpunt':'Omrijpunt'}</strong><span>${esc(shortLoc(w.raw)||w.raw||'Locatie onbekend')}</span><span class="wp-km">${w.odometer!=null?odo(w.odometer)+' km':'stand onbekend'} · tijd onbekend</span></div>`).join('');return`<div class="${cls}"><input class="trip-check" type="checkbox" data-trip-id="${t.id}" ${checked} ${disabled}><div class="trip-date">${esc(t.displayDate)}</div><div class="trip-main"><strong>${esc(shortLoc(t.originRaw))} → ${esc(shortLoc(t.destinationRaw))}</strong><small>${esc(categoryLabel(t.category))}</small><small>${odo(t.startOdometer)} → ${odo(t.endOdometer)} km</small></div><div class="trip-km"><strong>${t.actualKm!=null?fmt(t.actualKm)+' km':'—'}</strong><small>${t.duplicate?(pending?`${pending} tussenpunt${pending===1?'':'en'}`:'al aanwezig'):t.valid?'importeren':'ongeldig'}</small></div>${wps?`<div class="trip-waypoints">${wps}</div>`:''}${notes.length?`<div class="trip-note ${!t.valid?'error':''}">${notes.map(esc).join(' · ')}</div>`:''}</div>`}'''
s = sub_once(s, r'function renderTrip\(t\)\{.*?\}\nfunction updateImportSummary', render_trip_new + '\nfunction updateImportSummary', 'renderTrip', re.S)

summary_new = r'''function updateImportSummary(){if(!parsed)return;const ids=new Set([...document.querySelectorAll('.trip-check:checked')].map(x=>x.dataset.tripId)),trips=parsed.trips.filter(t=>ids.has(t.id)&&t.valid&&(!t.duplicate||t.pendingWaypoints.length)),newTrips=trips.filter(t=>!t.duplicate),kmTotal=newTrips.reduce((s,t)=>s+(+t.actualKm||0),0),waypointCount=trips.reduce((s,t)=>s+(t.pendingWaypoints?.length||0),0),newLocKeys=new Set();for(const t of trips){const raws=[...(!t.duplicate?[t.originRaw,t.destinationRaw]:[]),...(t.pendingWaypoints||[]).map(w=>w.raw)];for(const raw of raws){const p=parseLocation(raw),key=locationKey(p.address||raw),c=parsed.locations.find(x=>x.key===key);if(c&&!c.existing)newLocKeys.add(key)}}$('#importSummary').innerHTML=`Klaar om <strong>${newTrips.length} nieuwe ${newTrips.length===1?'rit':'ritten'}</strong> (${fmt(kmTotal)} km), <strong>${waypointCount} ${waypointCount===1?'tussenpunt':'tussenpunten'}</strong> en <strong>${newLocKeys.size} nieuwe ${newLocKeys.size===1?'locatie':'locaties'}</strong> toe te voegen.`;$('#importBtn').disabled=!trips.length}'''
s = sub_once(s, r'function updateImportSummary\(\)\{.*?\}\n\nfunction importSelected', summary_new + '\n\nfunction importSelected', 'updateImportSummary', re.S)

import_new = r'''function importSelected(){
  if(!parsed)return;
  const ids=new Set([...document.querySelectorAll('.trip-check:checked')].map(x=>x.dataset.tripId)),
        trips=parsed.trips.filter(t=>ids.has(t.id)&&t.valid&&(!t.duplicate||t.pendingWaypoints.length));
  if(!trips.length)return;
  const newTripCount=trips.filter(t=>!t.duplicate).length,plannedEvents=trips.reduce((n,t)=>n+(t.pendingWaypoints?.length||0),0);
  if(!confirm(`${newTripCount} nieuwe historische ${newTripCount===1?'rit':'ritten'} en ${plannedEvents} ${plannedEvents===1?'tussenpunt':'tussenpunten'} importeren?`))return;
  try{
    const mapping=new Map();

    for(const c of parsed.locations){
      if(c.existing){mapping.set(c.key,c.existing);continue}
      const used=trips.some(t=>{const raws=[...(!t.duplicate?[t.originRaw,t.destinationRaw]:[]),...(t.pendingWaypoints||[]).map(w=>w.raw)];return raws.some(raw=>locationKey(parseLocation(raw).address||raw)===c.key)});
      if(!used)continue;
      const name=(document.querySelector(`[data-location-name="${cssEscape(c.key)}"]`)?.value||c.suggestedName||c.parsed.name||c.raw).trim();
      const type=document.querySelector(`[data-location-type="${cssEscape(c.key)}"]`)?.value||c.suggestedType||'other';
      const loc={id:uid(),name:name||c.parsed.address||c.raw,address:c.parsed.address||c.raw,lat:null,lng:null,type,useCount:0,createdAt:new Date().toISOString(),updatedAt:new Date().toISOString()};
      db.locations.push(loc);mapping.set(c.key,loc);
    }

    const existing=new Map(db.trips.map(x=>[duplicateKey(x),x]));
    let imported=0,importedEvents=0,totalKm=0;

    for(const t of trips){
      let trip=existing.get(duplicateKey(t))||null;
      if(!trip){
        const o=mapping.get(locationKey(parseLocation(t.originRaw).address||t.originRaw));
        const d=mapping.get(locationKey(parseLocation(t.destinationRaw).address||t.destinationRaw));
        if(!o||!d)throw new Error('Een vertrek- of bestemmingslocatie kon niet worden gekoppeld.');
        const actual=+t.actualKm||0,dist=split(actual,t.category);
        trip={id:uid(),origin:snap(o),destination:snap(d),departureTime:t.departureTime,arrivalTime:null,arrivalTimeKnown:false,startOdometer:t.startOdometer,endOdometer:t.endOdometer,actualKm:actual,proposedRouteKm:null,category:t.category,reason:t.reason||'',privateKm:dist.private,businessKm:dist.business,commuteKm:dist.commute,importedAt:new Date().toISOString(),importSource:'notes-text-v2',historicalArrivalUnknown:true,noteRitDistance:t.statedDistance??null};
        db.trips.push(trip);existing.set(duplicateKey(trip),trip);o.useCount=(o.useCount||0)+1;d.useCount=(d.useCount||0)+1;imported++;totalKm+=actual;
      }

      for(const [order,w] of (t.pendingWaypoints||[]).entries()){
        if(waypointExists(trip,w))continue;
        const loc=mapping.get(locationKey(parseLocation(w.raw).address||w.raw));
        if(!loc)throw new Error('Een Via- of tanklocatie kon niet worden gekoppeld.');
        db.events.push({id:uid(),type:w.type,tripId:trip.id,odometer:w.odometer,location:snap(loc),note:w.note||'',time:trip.departureTime,historicalTimeUnknown:true,historicalDateKnown:true,historicalOrder:order,importedAt:new Date().toISOString(),importSource:'notes-text-v2'});
        loc.useCount=(loc.useCount||0)+1;importedEvents++;
      }
    }

    if($('#fillSettings').checked){const m=parsed.metadata;if(!db.settings.name&&m.name)db.settings.name=m.name;if(!db.settings.vehicleBrand&&m.vehicleBrand)db.settings.vehicleBrand=m.vehicleBrand;if(!db.settings.plate&&m.plate)db.settings.plate=m.plate}
    rebuildLastEndpoint();saveDb();db=loadDb();refreshDbStatus();
    done.innerHTML=`<h2>Import voltooid</h2><p><strong>${imported} ${imported===1?'rit':'ritten'}</strong> en <strong>${importedEvents} ${importedEvents===1?'tussenpunt':'tussenpunten'}</strong> toegevoegd · ${fmt(totalKm)} nieuwe km.</p><div class="hint">Historische Via- en tankpunten zijn aan hun rit gekoppeld. Ontbrekende tijden worden als “Tijd onbekend” weergegeven; er is niets verzonnen.</div><div class="row" style="margin-top:14px"><button class="btn secondary" type="button" onclick="location.href='index.html'">Open kilometerregistratie</button><button class="btn secondary" type="button" onclick="location.reload()">Nog meer notities importeren</button></div>`;
    done.classList.remove('hidden');preview.classList.add('hidden');done.scrollIntoView({behavior:'smooth',block:'start'});
  }catch(e){console.error(e);alert('Import mislukt:\n\n'+(e.message||e))}
}'''
s = sub_once(s, r'function importSelected\(\)\{.*?\n\}\n\nfunction rebuildLastEndpoint', import_new + '\n\nfunction rebuildLastEndpoint', 'importSelected', re.S)

p.write_text(s)

# ---- service-worker.js ----
p = Path('service-worker.js')
s = p.read_text()
if "const CACHE='kmreg-shell-0.28.15';" not in s:
    raise SystemExit('service worker version not found')
s = s.replace("const CACHE='kmreg-shell-0.28.15';", "const CACHE='kmreg-shell-0.28.16';", 1)
old = "self.addEventListener('fetch',event=>{const req=event.request,url=new URL(req.url);if(req.method!=='GET'||url.origin!==self.location.origin)return;if(req.mode==='navigate')"
new = "self.addEventListener('fetch',event=>{const req=event.request,url=new URL(req.url);if(req.method!=='GET'||url.origin!==self.location.origin)return;if(url.pathname.endsWith('/import.html'))return;if(req.mode==='navigate')"
if old not in s:
    raise SystemExit('service worker fetch marker not found')
s = s.replace(old, new, 1)
p.write_text(s)

# Sanity markers
for path, markers in {
    'index.html':['0.28.16','historicalTimeUnknown','eventDateTimeLabel'],
    'import.html':['noteDrop','pendingWaypoints','Tanklocatie','notes-text-v2','historicalTimeUnknown'],
    'service-worker.js':['0.28.16',"endsWith('/import.html')"]
}.items():
    text=Path(path).read_text()
    for marker in markers:
        if marker not in text: raise SystemExit(f'{path}: missing {marker}')
print('patch 0.28.16 applied')

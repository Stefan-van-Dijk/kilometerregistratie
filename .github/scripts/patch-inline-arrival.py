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

replace_once("+' · 0.28.7';","+' · 0.28.8';",'version')

old_state="let data=load(),view='ride',selectedWeek=new Date(),periodMode='week',gpsWatch=null,gpsTimer=null,gpsLatest=null,odoSwipe=null,periodGesture=null,periodLastTap=0,expandedTripId=null,tripSwipe=null,trackStoreReady=false,trackDbPromise=null,settingsLocationCheck=0,geocodeQueue=Promise.resolve(),geocodeLastAt=0,expandedLocationId=null,settingsLocationsOpen=false,settingsLocationOriginId=null,screenSwipe=null,editorReturnView='ride',editingTripId=null,editingLocationId=null,editingLocationSeed=null,startDraft=null;"
new_state=old_state[:-1]+",arrivalDraft=null;"
replace_once(old_state,new_state,'arrival draft state')

replace_once("else if(a==='arrive')await openArrival();else if(a==='navigate-active')", "else if(a==='arrive')await openArrival();else if(a==='cancel-arrival'){arrivalDraft=null;render();}else if(a==='navigate-active')", 'cancel arrival action')

replace_block('function activeDock(a){','function startInlinePanel(){','', 'remove active dock function')
replace_once("function homePeriodOrStartPanel(trips,t){if(startDraft)return startInlinePanel();return", "function homePeriodOrStartPanel(trips,t){if(arrivalDraft&&data.activeTrip)return arrivalInlinePanel();if(startDraft)return startInlinePanel();return", 'arrival replaces period')
replace_once("<section class=\"hero ${a?'active-hero':startDraft?'start-preparing':''}\">", "<section class=\"hero ${a?(arrivalDraft?'active-hero arrival-preparing':'active-hero'):startDraft?'start-preparing':''}\">", 'arrival hero class')
replace_once('<button class="btn full arrival-main" data-action="arrive">Aankomst</button>', "${arrivalDraft?'<button class=\"btn secondary full arrival-main\" data-action=\"cancel-arrival\">Annuleer afronden</button>':'<button class=\"btn full arrival-main\" data-action=\"arrive\">Aankomst</button>'}", 'arrival hero button')
replace_once('${activeDock(a)}','', 'remove active dock render')

arrival_panel=r'''function arrivalInlinePanel(){
if(!arrivalDraft||!data.activeTrip)return'';
const a=data.activeTrip,{gps,arrivalChoice,suggested,proposals,initial,radius,planned,recognized,plannedDiff}=arrivalDraft,first=proposals[0]||null;
const locationText=suggested?`Voorstel: ${esc(labelLoc(suggested))}`:'Nog geen opgeslagen locatie herkend',locationReason=arrivalChoice.reason||'Controleer de bestemming.';
return`<section id="arrivalInlinePanel" class="arrival-inline-panel" aria-label="Rit afronden"><form id="arrivalForm"><input type="hidden" name="endOdometer" id="arrivalEndOdometer" value="${attr(initial)}"><input type="hidden" name="arrivalGpsJson" id="arrivalGpsJson" value='${attr(JSON.stringify(gps))}'><div class="arrival-inline-head"><div class="kicker">Aankomst</div><strong>Controleer bestemming en stand</strong></div><div class="arrival-location-card"><strong>${locationText}</strong><small>${esc(locationReason)}</small><span class="recognition-chip ${recognized?'good':'warn'}">Herkenningsstraal ${odo(radius)} m${arrivalChoice.distance!=null?' · '+odo(arrivalChoice.distance)+' m afstand':''}</span>${plannedDiff?`<div class="arrival-location-change">Gepland: ${esc(labelLoc(planned))} · huidige locatie wijst op ${esc(labelLoc(suggested))}</div>`:''}</div><div class="form-group"><label>Eindbestemming</label><select name="destinationChoice" id="arrivalDestination">${arrivalDestinationOptions(arrivalChoice,gps,a)}</select><div class="suggestion-note">Herkenning en ritgeschiedenis bepalen samen het voorstel.</div></div><div class="odo-card"><div class="odo-caption">Geschatte eindstand</div><div class="odo-display" id="odoDigits">${odometerDigits(initial)}</div><div class="odo-unit">KM</div><div class="odo-source-row"><div class="odo-source" id="odoSource">${esc(first?.label||'Nog geen betrouwbare schatting')}</div><button type="button" class="estimate-info-btn" data-action="arrival-info" aria-label="Uitleg over deze schatting">ⓘ</button></div><div class="odo-swipe-hint">Swipe een cijfer omhoog of omlaag voor een snelle correctie</div></div><div id="estimateListWrap">${estimateButtons(proposals)}</div><div class="odo-actions"><button type="submit" class="btn">${proposals.length?'Rit afronden':'Stand opslaan'}</button><button type="button" class="btn secondary" data-action="toggle-odometer-edit">Aanpassen</button></div><div class="odo-edit" id="odometerEdit" ${proposals.length?'hidden':''}><div class="form-group" style="margin:0"><label>Werkelijke eindstand</label><input id="arrivalCustomEnd" type="number" inputmode="numeric" value="${attr(initial)}"></div><div class="hint">Vul de kilometerstand van het dashboard in. De grote weergave hierboven verandert direct mee.</div></div><div class="arrival-note">Aankomsttijd wordt automatisch vastgelegd. De dashboardstand blijft leidend.</div><div id="arrivalInfoPopup" class="arrival-info-popup" hidden><div class="arrival-info-sheet"><div class="modal-head"><div><div class="kicker">Uitleg schatting</div><h2>Hoe is dit voorstel bepaald?</h2></div><button type="button" class="close" data-action="arrival-info-close">×</button></div><div id="arrivalInfoContent"></div></div></div></form></section>`
}
'''
replace_once('function homePeriodOrStartPanel(trips,t){',arrival_panel+'function homePeriodOrStartPanel(trips,t){','arrival inline helper')

open_arrival=r'''async function openArrival(){
const a=data.activeTrip;if(!a)throw new Error('Er is geen actieve rit.');
let gps=null;try{gps=await getPosition()}catch(e){}
const moment=new Date(),arrivalChoice=arrivalDestinationSuggestion(a,gps,moment),suggested=arrivalChoice.location||null;
const proposalActive={...a,plannedDestination:a.expectedDestination||null,expectedDestination:suggested||a.expectedDestination||null};
const proposals=endOdometerProposals(proposalActive,gps,moment),first=proposals[0]||null,initial=first?.value??a.startOdometer;
const radius=recognitionRadius(),planned=a.expectedDestination||null,recognized=arrivalChoice.recognized===true;
const plannedDiff=planned&&suggested&&!sameLoc(planned,suggested);
arrivalDraft={gps,arrivalChoice,suggested,proposals,initial,radius,planned,recognized,plannedDiff};
render();
requestAnimationFrame(()=>document.getElementById('arrivalInlinePanel')?.scrollIntoView({behavior:'smooth',block:'nearest'}));
}
'''
replace_block('async function openArrival(){','function saveArrival(fd){',open_arrival,'inline openArrival')
replace_once("data.trips.push(trip);data.lastEndpoint={location:snap(d),odometer:end,time:trip.arrivalTime};data.activeTrip=null;save();stopTracking();closeModal();render();toast(`Rit opgeslagen: ${km(actual)} km.`);", "data.trips.push(trip);data.lastEndpoint={location:snap(d),odometer:end,time:trip.arrivalTime};data.activeTrip=null;arrivalDraft=null;save();stopTracking();closeModal();render();toast(`Rit opgeslagen: ${km(actual)} km.`);", 'clear arrival draft after save')

css=r'''
/* 0.28.8 — aankomst inline en geen onderste ritbalk */
.has-active-trip .shell{padding-bottom:calc(28px + env(safe-area-inset-bottom))}
.hero.arrival-preparing .active-route,.hero.arrival-preparing .active-meta,.hero.arrival-preparing .smart-insight{opacity:.55;transition:opacity .2s ease}
.hero.arrival-preparing .ride-tools{opacity:.38;pointer-events:none;transition:opacity .2s ease}
.hero.arrival-preparing .arrival-main{background:transparent;border:1px solid var(--line);color:var(--muted);min-height:42px}
.arrival-inline-panel{padding:17px 0 19px;border-bottom:1px solid var(--line);animation:arrival-inline-in .26s cubic-bezier(.2,.8,.2,1)}
.arrival-inline-head{margin-bottom:11px}.arrival-inline-head strong{display:block;margin-top:2px;font-size:17px}
.arrival-inline-panel .arrival-location-card{margin:0 0 9px;padding:0 0 9px;border:0;border-bottom:1px solid var(--line);border-radius:0;background:transparent}
.arrival-inline-panel .form-group{margin:9px 0}.arrival-inline-panel .form-group>label{color:var(--muted);font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.06em}
.arrival-inline-panel select{min-height:42px;background:var(--card);border-color:var(--line)}
.arrival-inline-panel .odo-card{margin-top:11px}.arrival-inline-panel .estimate-list{margin-top:9px}.arrival-inline-panel .odo-actions{margin-top:9px}
.arrival-inline-panel .arrival-note{margin-top:7px;color:var(--muted);font-size:10px;line-height:1.35}
@keyframes arrival-inline-in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@media(max-height:760px){.arrival-inline-panel{padding:11px 0 13px}.arrival-inline-head{margin-bottom:7px}.arrival-inline-panel .odo-card{padding-top:12px;padding-bottom:10px}.arrival-inline-panel .odo-display{margin-top:7px;margin-bottom:5px}.arrival-inline-panel .odo-digit{height:50px}.arrival-inline-panel .suggestion-note,.arrival-inline-panel .arrival-note{font-size:9px}}
@media (prefers-color-scheme:light){.arrival-inline-panel select{background:#fff;color:var(--text)}}
'''
replace_once('\n</style>','\n'+css+'\n</style>','arrival inline css')

index.write_text(text,encoding='utf-8')

sw=Path('service-worker.js')
s=sw.read_text(encoding='utf-8')
if "kmreg-shell-0.28.7" not in s:
    raise SystemExit('service worker version not found')
s=s.replace("kmreg-shell-0.28.7","kmreg-shell-0.28.8",1)
sw.write_text(s,encoding='utf-8')

html=index.read_text(encoding='utf-8')
start=html.index('<script>')+len('<script>')
end=html.index('</script>',start)
Path('/tmp/kmreg-app.js').write_text(html[start:end],encoding='utf-8')

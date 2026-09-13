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

replace_once("+' · 0.28.6';","+' · 0.28.7';",'version')

old_state="let data=load(),view='ride',selectedWeek=new Date(),periodMode='week',gpsWatch=null,gpsTimer=null,gpsLatest=null,odoSwipe=null,periodGesture=null,periodLastTap=0,expandedTripId=null,tripSwipe=null,trackStoreReady=false,trackDbPromise=null,settingsLocationCheck=0,geocodeQueue=Promise.resolve(),geocodeLastAt=0,expandedLocationId=null,settingsLocationsOpen=false,settingsLocationOriginId=null,screenSwipe=null,editorReturnView='ride',editingTripId=null,editingLocationId=null,editingLocationSeed=null;"
new_state=old_state[:-1]+",startDraft=null;"
replace_once(old_state,new_state,'start draft state')

replace_once("else if(a==='start')await openStart();", "else if(a==='start')await openStart();else if(a==='cancel-start'){startDraft=null;render();}", 'cancel start action')
replace_once("if(e.target.id==='arrivalDestination')refreshArrivalEstimates();", "if(e.target.id==='arrivalDestination')refreshArrivalEstimates();if(e.target.id==='startDestination')refreshStartCategorySuggestion();", 'inline start destination change')

replace_once("<section class=\"hero ${a?'active-hero':''}\">", "<section class=\"hero ${a?'active-hero':startDraft?'start-preparing':''}\">", 'start preparing hero class')
replace_once("<button class=\"btn full\" data-action=\"start\">Vertrek registreren</button>", "${startDraft?'<button class=\"btn secondary full\" data-action=\"cancel-start\">Annuleer vertrek</button>':'<button class=\"btn full\" data-action=\"start\">Vertrek registreren</button>'}", 'start button mode')

helper=r'''function startInlinePanel(){if(!startDraft)return'';const origin=startDraft.origin,start=startDraft.start,suggestedId=startDraft.suggestedDestination?.id||'',suggestion=startDraft.destinationSuggestion,categorySuggestion=startDraft.categorySuggestion;return`<section id="startInlinePanel" class="start-inline-panel" aria-label="Rit starten"><form id="startForm"><input type="hidden" name="origin" value='${attr(JSON.stringify(origin))}'><div class="start-inline-choice"><div class="form-group"><label>Bestemming</label><select name="destinationId" id="startDestination"><option value="__unknown__" ${suggestedId?'':'selected'}>Nog onbekend</option>${locationNameOptions(suggestedId)}</select>${suggestedId?`<div class="start-suggestion">Voorstel: ${esc(labelLoc(startDraft.suggestedDestination))} · ${esc(suggestion.reason)}</div>`:`<div class="start-suggestion">Nog geen duidelijke bestemming uit je historie.</div>`}</div><div class="form-group"><label>Type rit</label><div class="trip-type-grid start-trip-type-grid">${startCategoryOption('commute','Woon-werk',categorySuggestion.value)}${startCategoryOption('business','Zakelijk',categorySuggestion.value)}${startCategoryOption('private','Privé',categorySuggestion.value)}</div><div class="start-suggestion" id="startTypeHint">Voorstel: ${esc(categoryLabel(categorySuggestion.value))} · ${esc(categorySuggestion.reason)}</div></div></div><button class="btn full start-confirm" type="submit">Rit starten</button><div class="start-inline-context">${esc(labelLoc(origin)||'Vertrekpunt')} · ${odo(start)} km</div></form></section>`}
function homePeriodOrStartPanel(trips,t){if(startDraft)return startInlinePanel();return`<section id="periodNavigator" class="period-navigator" aria-label="Periodeoverzicht"><div class="period-nav-head">${periodMode==='all'?'<span class="period-arrow-spacer"></span>':'<button type="button" class="mini" data-action="period-prev" aria-label="Vorige periode">‹</button>'}<div class="period-center"><div class="period-title-line"><strong>${esc(periodLabel())}</strong><button type="button" class="period-scale-button" data-action="period-choose" aria-label="Periodegrootte kiezen" title="Periodegrootte kiezen">⌄</button></div><small>${esc(periodSubLabel(trips))}</small></div>${periodMode==='all'?'<span class="period-arrow-spacer"></span>':'<button type="button" class="mini" data-action="period-next" aria-label="Volgende periode">›</button>'}</div>${summary(t,periodSummaryTitle(),trips.length)}</section>`}
'''
replace_once("function renderHome(){",helper+"function renderHome(){",'inline start helpers')

period_start='<section id="periodNavigator" class="period-navigator" aria-label="Periodeoverzicht">'
period_end='</section>\n<div class="section"><div class="section-title"><h2>Ritten</h2>'
a=text.find(period_start,text.find('function renderHome(){'))
if a<0: raise SystemExit('renderHome period start not found')
b=text.find(period_end,a)
if b<0: raise SystemExit('renderHome period end not found')
text=text[:a]+'${homePeriodOrStartPanel(trips,t)}\n<div class="section"><div class="section-title"><h2>Ritten</h2>'+text[b+len(period_end):]

open_start=r'''async function openStart(){
if(data.activeTrip)throw new Error('Er is al een actieve rit.');
if(!data.locations.length){view='settings';render();throw new Error('Voeg eerst een locatie toe.');}
let origin=data.lastEndpoint?.location||inferLast()?.location||null;
const start=data.lastEndpoint?.odometer??inferLast()?.odometer??num(data.settings.initialOdometer);
if(start==null){view='settings';render();throw new Error('Vul eerst de huidige kilometerstand in bij Bestuurder & auto.');}
if(!origin){try{const g=await getPosition();origin=matches(g)[0]?.location||currentLoc(g)}catch(e){}}
if(!origin)throw new Error('Geen vertrekpunt bekend. Geef locatietoegang of leg eerst een locatie vast.');
const destinationSuggestion=suggestDestination(origin,new Date()),suggestedDestination=destinationSuggestion.location,categorySuggestion=suggestTripCategory(origin,suggestedDestination,new Date());
startDraft={origin:snap(origin),start,suggestedDestination:snap(suggestedDestination),destinationSuggestion,categorySuggestion};
render();
requestAnimationFrame(()=>document.getElementById('startInlinePanel')?.scrollIntoView({behavior:'smooth',block:'nearest'}));
}
function refreshStartCategorySuggestion(){const f=document.getElementById('startForm'),select=document.getElementById('startDestination');if(!f||!select||!startDraft)return;const d=select.value==='__unknown__'?null:data.locations.find(x=>x.id===select.value)||null,s=suggestTripCategory(startDraft.origin,d,new Date());startDraft.categorySuggestion=s;const radio=f.querySelector(`[name="category"][value="${s.value}"]`);if(radio)radio.checked=true;const hint=document.getElementById('startTypeHint');if(hint)hint.textContent=`Voorstel: ${categoryLabel(s.value)} · ${s.reason}`}
'''
replace_block('async function openStart(){','async function saveStart(fd){',open_start,'inline openStart')
replace_once("save();closeModal();render();await startTracking();toast(d?'Rit gestart.':'Rit gestart zonder vaste bestemming.');", "save();startDraft=null;closeModal();render();await startTracking();toast(d?'Rit gestart.':'Rit gestart zonder vaste bestemming.');", 'clear start draft after save')

css=r'''
/* 0.28.7 — vertrekkeuzes inline op het hoofdscherm */
.hero.start-preparing .home-odometer,.hero.start-preparing p{opacity:.58;transition:opacity .2s ease}
.hero.start-preparing .btn.secondary{background:transparent;border:0;color:var(--muted);min-height:40px}
.start-inline-panel{padding:18px 0 19px;border-bottom:1px solid var(--line);animation:start-inline-in .26s cubic-bezier(.2,.8,.2,1)}
.start-inline-panel .form-group{margin:0}
.start-inline-choice{display:grid;gap:15px}
.start-inline-panel .form-group>label{margin-bottom:6px;color:var(--muted);font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.06em}
.start-inline-panel select{min-height:44px;background:var(--card);border-color:var(--line)}
.start-inline-panel .trip-type-grid{margin:0;gap:7px}
.start-inline-panel .trip-type-option span{min-height:44px;padding:8px 5px}
.start-suggestion{margin-top:5px;color:var(--muted);font-size:10px;line-height:1.35}
.start-confirm{margin-top:15px;min-height:48px}
.start-inline-context{margin-top:7px;text-align:center;color:var(--muted);font-size:10px}
.start-inline-choice>.form-group{animation:start-choice-in .3s ease both}.start-inline-choice>.form-group:nth-child(2){animation-delay:.045s}
@keyframes start-inline-in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes start-choice-in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
@media(max-height:760px){.start-inline-panel{padding:12px 0 13px}.start-inline-choice{gap:10px}.start-inline-panel select{min-height:39px}.start-inline-panel .trip-type-option span{min-height:38px}.start-confirm{margin-top:10px;min-height:42px}}
@media (prefers-color-scheme:light){.start-inline-panel select{background:#fff;color:var(--text)}}
'''
replace_once('\n</style>','\n'+css+'\n</style>','inline start css')

index.write_text(text,encoding='utf-8')

sw=Path('service-worker.js')
s=sw.read_text(encoding='utf-8')
if "kmreg-shell-0.28.6" not in s:
    raise SystemExit('service worker version not found')
s=s.replace("kmreg-shell-0.28.6","kmreg-shell-0.28.7",1)
sw.write_text(s,encoding='utf-8')

html=index.read_text(encoding='utf-8')
start=html.index('<script>')+len('<script>')
end=html.index('</script>',start)
Path('/tmp/kmreg-app.js').write_text(html[start:end],encoding='utf-8')

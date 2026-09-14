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

replace_once("+' · 0.28.8';","+' · 0.28.9';",'version')

old_buttons="""function estimateButtons(proposals){return proposals.length?`<div class=\"estimate-list\" id=\"estimateList\">${proposals.map((p,i)=>`<button type=\"button\" class=\"estimate-choice ${i===0?'active':''}\" data-action=\"select-odometer\" data-value=\"${p.value}\" data-label=\"${attr(p.label)}\"><strong>${odo(p.value)} km</strong><small>${esc(p.label)}</small></button>`).join('')}</div>`:`<div class=\"notice\">Er is nog geen betrouwbare schatting op basis van GPS, tijd en eerdere ritten. Pas de stand hieronder aan.</div>`}"""
new_buttons="""function estimateButtons(proposals){const alternatives=proposals.filter(p=>!p.primary).slice(0,4);return alternatives.length?`<div class=\"estimate-support-note\">Onderliggende signalen</div><div class=\"estimate-list\" id=\"estimateList\">${alternatives.map(p=>`<button type=\"button\" class=\"estimate-choice\" data-action=\"select-odometer\" data-value=\"${p.value}\" data-label=\"${attr(p.label)}\"><strong>${odo(p.value)} km</strong><small>${esc(p.label)}</small></button>`).join('')}</div>`:`<div class=\"notice\">De beste schatting is gebaseerd op de beschikbare ritinformatie. Controleer de dashboardstand.</div>`}"""
replace_once(old_buttons,new_buttons,'estimate buttons')

new_info=r'''function openArrivalInfo(){
const a=data.activeTrip,popup=document.getElementById('arrivalInfoPopup'),content=document.getElementById('arrivalInfoContent');if(!a||!popup||!content)return;
const destination=selectedArrivalDestination(),gps=JSON.parse(document.getElementById('arrivalGpsJson')?.value||'null'),model=compositeArrivalEstimate({...a,plannedDestination:a.expectedDestination||null},destination,gps,new Date()),ctx=model.ctx,end=num(document.getElementById('arrivalEndOdometer')?.value),distanceKm=end==null?null:Math.max(0,end-a.startOdometer),source=document.getElementById('odoSource')?.textContent||'Handmatige controle';
const stats=ctx.stats,plannedDifferent=ctx.destinationChanged&&ctx.planned,plannedLine=plannedDifferent?`<div class="arrival-info-note">Gepland bij vertrek: <strong>${esc(labelLoc(ctx.planned)||'Onbekend')}</strong>${a.proposedRouteKm!=null?` · ${km(a.proposedRouteKm)} km`:''}. Dit vertrekvoorstel wordt nu niet gebruikt, omdat de werkelijke bestemming anders is.</div>`:'';
const factorText=model.factor.factor!=null?model.factor.factor.toFixed(2).replace('.',',')+'×':model.factor.directKm!=null?'Nog niet geleerd':'Niet beschikbaar',coverageText=model.gpsCoverage!=null?Math.round(model.gpsCoverage*100)+'%':'Niet te bepalen',rangeText=model.rangeLow!=null&&model.rangeHigh!=null?`${km(model.rangeLow)}–${km(model.rangeHigh)} km`:'Nog niet betrouwbaar';
content.innerHTML=`<div class="arrival-info-grid"><div class="arrival-info-item"><span>Werkelijke bestemming</span><strong>${esc(labelLoc(destination)||'Nog onbekend')}</strong></div><div class="arrival-info-item"><span>Reistijd</span><strong>${formatTravelMinutes(ctx.elapsedMinutes)}</strong></div><div class="arrival-info-item"><span>A → B afstand</span><strong>${model.factor.directKm!=null?km(model.factor.directKm)+' km':'Geen GPS-paar beschikbaar'}</strong></div><div class="arrival-info-item"><span>Geleerde routefactor</span><strong>${factorText}</strong></div><div class="arrival-info-item"><span>GPS gemeten</span><strong>${ctx.gpsKm!=null?km(ctx.gpsKm)+' km':'Niet voldoende gemeten'}</strong></div><div class="arrival-info-item"><span>GPS-dekking</span><strong>${coverageText}</strong></div><div class="arrival-info-item"><span>Beste schatting</span><strong>${model.bestKm!=null?km(model.bestKm)+' km · '+odo(+a.startOdometer+model.bestKm)+' km':'Handmatig controleren'}</strong></div><div class="arrival-info-item"><span>Verwachte marge</span><strong>${rangeText}</strong></div>${stats.count?`<div class="arrival-info-item"><span>Routehistorie</span><strong>${stats.count} vergelijkbare rit${stats.count===1?'':'ten'}</strong></div><div class="arrival-info-item"><span>Gemiddelde afstand</span><strong>${km(stats.avgDistance)} km</strong></div><div class="arrival-info-item"><span>Gemiddelde reistijd</span><strong>${formatTravelMinutes(stats.avgDuration)}</strong></div>`:''}</div><div><span class="estimate-confidence ${model.confidence}">Betrouwbaarheid: ${model.confidenceLabel}</span></div><div class="arrival-info-reason"><strong>${esc(source)}</strong><br>${esc(model.reason)}</div>${plannedLine}<div class="arrival-info-note">A → B is alleen de geometrische ondergrens. De app leert uit werkelijk geregistreerde kilometers hoeveel langer deze route normaal is. Een onvolledige GPS-track wordt niet als hoofdschatting gebruikt.</div>`;
popup.hidden=false;
}
'''
replace_block('function openArrivalInfo(){','function endOdometerProposals(',new_info,'arrival info')

helpers=r'''function tripRouteFactor(trip){if(!trip?.origin||!trip?.destination||trip.origin.lat==null||trip.origin.lng==null||trip.destination.lat==null||trip.destination.lng==null)return null;const direct=distance(trip.origin,trip.destination)/1000,actual=+trip.actualKm;if(!Number.isFinite(direct)||direct<1||!Number.isFinite(actual)||actual<direct*.85||actual>direct*3.5)return null;return actual/direct}
function learnedRouteFactor(origin,destination){const directKm=origin?.lat!=null&&origin?.lng!=null&&destination?.lat!=null&&destination?.lng!=null?distance(origin,destination)/1000:null;if(!Number.isFinite(directKm)||directKm<1)return{directKm:null,factor:null,estimate:null,count:0,scope:'none'};const exact=routeTripsBetween(origin,destination).slice(0,12),reverse=routeTripsBetween(destination,origin).slice(0,8);let samples=[...exact,...reverse].map(tripRouteFactor).filter(Number.isFinite),scope='route';if(!samples.length){samples=[...data.trips].sort((a,b)=>new Date(b.arrivalTime||b.departureTime)-new Date(a.arrivalTime||a.departureTime)).slice(0,80).map(tripRouteFactor).filter(Number.isFinite);scope='algemeen'}const factor=median(samples);return{directKm,factor,estimate:factor==null?null:directKm*factor,count:samples.length,scope}}
function weightedSignalAverage(signals){let total=0,weight=0;for(const s of signals){if(!Number.isFinite(+s.distance)||!Number.isFinite(+s.weight)||+s.weight<=0)continue;total+=+s.distance*+s.weight;weight+=+s.weight}return weight?total/weight:null}
function compositeArrivalEstimate(active,destination,arrivalGps,moment=new Date()){
const ctx=arrivalEstimateContext(active,destination,arrivalGps,moment),factor=destination?learnedRouteFactor(active.origin,destination):{directKm:null,factor:null,estimate:null,count:0,scope:'none'},routeTrips=destination?routeTripsBetween(active.origin,destination):[],reverseTrips=destination?routeTripsBetween(destination,active.origin):[],pattern=destination?routePatternAnalysis(active.origin,destination):null,timed=routeTrips.length?timedRouteDistance(routeTrips,active,moment):null,recentMedian=routeTrips.length?median(routeTrips.slice(0,7).map(t=>+t.actualKm)):null,last=routeTrips[0]&&Number.isFinite(+routeTrips[0].actualKm)?+routeTrips[0].actualKm:null,reverseMedian=!routeTrips.length&&reverseTrips.length?median(reverseTrips.slice(0,7).map(t=>+t.actualKm)):null,planned=active.plannedDestination||active.expectedDestination||null,plannedMatches=!!(destination&&planned&&sameLoc(planned,destination)),signals=[];
const add=(key,distanceKm,weight,label)=>{if(Number.isFinite(+distanceKm)&&+distanceKm>=0&&Number.isFinite(+weight)&&+weight>0)signals.push({key,distance:+distanceKm,weight:+weight,label})};
if(ctx.zeroLikely){return{ctx,factor,signals:[{key:'same',distance:0,weight:10,label:'Zelfde locatie'}],bestKm:0,baselineKm:0,gpsCoverage:ctx.gpsKm!=null?1:null,gpsWeight:ctx.gpsKm!=null?5:0,rangeLow:0,rangeHigh:0,confidence:ctx.confidence,confidenceLabel:ctx.confidenceLabel,reason:ctx.reason,sourceLabel:`Beste schatting · zelfde locatie`}}
if(pattern?.shifted&&pattern.recentMedian!=null)add('pattern',pattern.recentMedian,5,pattern.detourCount>0?'Recente omleidingsroute':'Actueel routepatroon');
if(timed!=null)add('timed',timed,routeTrips.length>=3?5:3.5,'Vergelijkbare reistijd');
if(recentMedian!=null)add('history',recentMedian,pattern?.shifted?2.5:4,'Recente routehistorie');
if(factor.estimate!=null)add('factor',factor.estimate,factor.scope==='route'?(factor.count>=3?3:2):1,'A → B × routefactor');
if(last!=null)add('last',last,1.25,'Laatste rit op deze route');
if(reverseMedian!=null)add('reverse',reverseMedian,2,'Omgekeerde routehistorie');
if(active.proposedRouteKm!=null&&plannedMatches)add('departure',+active.proposedRouteKm,2,'Routevoorstel bij vertrek');
let baselineKm=weightedSignalAverage(signals);if(baselineKm==null&&factor.directKm!=null)baselineKm=factor.directKm;
let gpsCoverage=ctx.gpsKm!=null&&baselineKm>0?ctx.gpsKm/baselineKm:null,gpsWeight=0;
if(ctx.gpsKm!=null&&ctx.gpsKm>=.3){if(baselineKm>0){if(gpsCoverage>=.9&&gpsCoverage<=1.4)gpsWeight=5;else if(gpsCoverage>1.4)gpsWeight=3;else if(gpsCoverage>=.78)gpsWeight=1.5}else if(factor.directKm!=null){gpsWeight=ctx.gpsKm>=factor.directKm?2.5:1}else gpsWeight=2;if(gpsWeight>0)add('gps',ctx.gpsKm,gpsWeight,'GPS tijdens deze rit')}
let bestKm=weightedSignalAverage(signals);if(bestKm!=null&&factor.directKm!=null)bestKm=Math.max(bestKm,factor.directKm);const rangeSignals=signals.filter(s=>s.key!=='gps'||gpsWeight>=1.5).map(s=>s.distance),deviations=bestKm==null?[]:rangeSignals.map(v=>Math.abs(v-bestKm)),mad=median(deviations),margin=bestKm==null?null:Math.max(1,Number.isFinite(mad)?mad*1.5:1),rangeLow=bestKm==null?null:Math.max(factor.directKm||0,bestKm-margin),rangeHigh=bestKm==null?null:bestKm+margin;
let confidence='low',confidenceLabel='Controle nodig';if(routeTrips.length>=3&&margin!=null&&margin<=2.5){confidence='high';confidenceLabel='Hoog'}else if(routeTrips.length>=1||factor.scope==='route'&&factor.count>=2){confidence='medium';confidenceLabel='Redelijk'}else if(gpsWeight>=4){confidence='medium';confidenceLabel='Redelijk'}
const partialGps=gpsCoverage!=null&&gpsCoverage<.78,parts=[];if(factor.factor!=null)parts.push('A→B');if(timed!=null)parts.push('tijd');if(routeTrips.length)parts.push('historie');if(gpsWeight>=3)parts.push('GPS');const sourceLabel=`Beste schatting${parts.length?' · '+parts.slice(0,3).join(' + '):''}`;
let reason;if(partialGps){reason=`GPS heeft ongeveer ${Math.round(gpsCoverage*100)}% van de verwachte route vastgelegd en is daarom niet leidend. De schatting gebruikt vooral de A→B-routefactor en vergelijkbare eerdere ritten.`}else if(gpsWeight>=3&&routeTrips.length){reason='GPS dekt een groot deel van de verwachte route en wordt gecombineerd met de werkelijk geregistreerde afstand van eerdere vergelijkbare A→B-ritten.'}else if(routeTrips.length){reason='De schatting combineert de geometrische A→B-afstand met de geleerde routefactor, werkelijk geregistreerde kilometers en ritten met een vergelijkbare reistijd.'}else if(factor.factor!=null){reason='Voor deze route is nog weinig directe historie. De A→B-afstand wordt daarom opgeschaald met een geleerde routefactor uit beschikbare ritten.'}else{reason='Er is nog onvoldoende routehistorie; controleer de dashboardstand.'}if(ctx.destinationChanged)reason+=' Het voorstel bij vertrek wordt niet gebruikt omdat de werkelijke bestemming is gewijzigd.';
return{ctx,factor,signals,bestKm,baselineKm,gpsCoverage,gpsWeight,rangeLow,rangeHigh,confidence,confidenceLabel,reason,sourceLabel,timed,recentMedian,last,pattern,routeTrips,reverseMedian}
}
'''
replace_once('function endOdometerProposals(',helpers+'function endOdometerProposals(','composite helpers')

new_proposals=r'''function endOdometerProposals(active,arrivalGps,moment=new Date()){
const destination=active.expectedDestination||null,out=[],start=+active.startOdometer,model=compositeArrivalEstimate(active,destination,arrivalGps,moment),ctx=model.ctx;
const add=(distanceKm,label,primary=false)=>{if(!Number.isFinite(+distanceKm)||+distanceKm<0)return;const value=Math.round(start+(+distanceKm));if(value<start||out.some(x=>x.value===value&&x.label===label))return;out.push({value,label,distance:+distanceKm,primary})};
if(model.bestKm!=null)add(model.bestKm,model.sourceLabel,true);
if(ctx.gpsKm!=null&&ctx.gpsKm>=.3){const coverage=model.gpsCoverage!=null?Math.round(model.gpsCoverage*100):null,label=model.gpsCoverage!=null&&model.gpsCoverage<.78?`GPS deels gemeten · ${coverage}% dekking`:'GPS · gemeten tijdens deze rit';add(ctx.gpsKm,label)}
if(model.timed!=null)add(model.timed,'Vergelijkbare reistijd · eerdere A→B-ritten');
if(model.factor.estimate!=null){const factorLabel=model.factor.factor!=null?model.factor.factor.toFixed(2).replace('.',',')+'×':'geleerd';add(model.factor.estimate,`A→B × routefactor · ${factorLabel}`)}
if(model.pattern?.shifted&&model.pattern.recentMedian!=null)add(model.pattern.recentMedian,model.pattern.detourCount>0?`Recente omleidingsroute · ${model.pattern.recentCount} ritten`:`Actueel routepatroon · ${model.pattern.recentCount} recente ritten`);else if(model.recentMedian!=null)add(model.recentMedian,'Routehistorie · recente mediaan');
if(model.last!=null)add(model.last,'Laatste keer op deze route');
if(model.reverseMedian!=null)add(model.reverseMedian,'Historie · omgekeerde route');
return out;
}

'''
replace_block('function endOdometerProposals(','function routeTripsBetween(',new_proposals,'end odometer proposals')

css=r'''
/* 0.28.9 — samengestelde aankomstschatting */
.estimate-support-note{margin:10px 1px 6px;color:var(--muted);font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.06em}
'''
replace_once('\n</style>','\n'+css+'\n</style>','estimate css')

index.write_text(text,encoding='utf-8')

sw=Path('service-worker.js')
s=sw.read_text(encoding='utf-8')
if "kmreg-shell-0.28.8" not in s:
    raise SystemExit('service worker version not found')
s=s.replace("kmreg-shell-0.28.8","kmreg-shell-0.28.9",1)
sw.write_text(s,encoding='utf-8')

html=index.read_text(encoding='utf-8')
start=html.index('<script>')+len('<script>')
end=html.index('</script>',start)
Path('/tmp/kmreg-app.js').write_text(html[start:end],encoding='utf-8')

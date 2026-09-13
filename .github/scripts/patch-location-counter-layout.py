from pathlib import Path

index=Path('index.html')
text=index.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global text
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text=text.replace(old,new,1)

replace_once("+' · 0.28.1';","+' · 0.28.2';",'version')

css=r'''
/* 0.28.2 — locatie-details uit echte ritregistraties */
.location-inline-details{margin:0;padding:2px 2px 14px 13px;border:0;border-bottom:1px solid var(--line);border-radius:0;background:transparent}
.location-inline-gps{padding:9px 0 10px;border-bottom:1px solid var(--line)}
.location-inline-gps span,.location-inline-gps strong,.location-inline-field span,.location-inline-field strong{display:block}
.location-inline-gps span,.location-inline-field span,.location-inline-counter span{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.location-inline-gps strong,.location-inline-field strong{margin-top:3px;font-size:12px;overflow-wrap:anywhere}
.location-inline-pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;padding:10px 0}
.location-inline-counter{display:flex;align-items:end;justify-content:space-between;gap:12px;padding:10px 0 0;border-top:1px solid var(--line)}
.location-inline-counter strong{font-size:17px;line-height:1}
'''
replace_once('\n</style>','\n'+css+'\n</style>','location detail css')

old="function locationMomentScore(l,origin,moment=new Date(),suggested=null){let score=(+l.useCount||0)*.15;"
new="function locationRegisteredTripCount(l){return data.trips.reduce((count,t)=>count+((sameLoc(t.origin,l)||sameLoc(t.destination,l))?1:0),0)}\nfunction locationMomentScore(l,origin,moment=new Date(),suggested=null){let score=locationRegisteredTripCount(l)*.15;"
replace_once(old,new,'registered trip counter')

old_details="function locationInlineDetails(l){const gps=coords(l)||'Niet vastgelegd',address=String(l.address||'').trim()||'Niet vastgelegd';return`<div class=\"location-inline-details\"><div class=\"location-inline-grid\"><div class=\"location-inline-item\"><span>Type</span><strong>${locationTypeIcon(l.type)} ${esc(typeLabel(l.type))}</strong></div><div class=\"location-inline-item\"><span>Rit delen</span><strong>${esc(shareRideLabel(l.shareRide||'never'))}</strong></div><div class=\"location-inline-item\"><span>GPS</span><strong>${esc(gps)}</strong></div><div class=\"location-inline-item\"><span>Gebruikt</span><strong>${odo(l.useCount||0)}×</strong></div></div><div class=\"location-inline-address\"><strong>Adres</strong><br>${esc(address)}</div></div>`}"
new_details="function locationInlineDetails(l){const gps=coords(l)||'Niet vastgelegd',count=locationRegisteredTripCount(l);return`<div class=\"location-inline-details\"><div class=\"location-inline-gps\"><span>GPS-locatie</span><strong>${esc(gps)}</strong></div><div class=\"location-inline-pair\"><div class=\"location-inline-field\"><span>Type</span><strong>${locationTypeIcon(l.type)} ${esc(typeLabel(l.type))}</strong></div><div class=\"location-inline-field\"><span>Rit delen</span><strong>${esc(shareRideLabel(l.shareRide||'never'))}</strong></div></div><div class=\"location-inline-counter\"><span>Geregistreerde ritten</span><strong>${odo(count)}</strong></div></div>`}"
replace_once(old_details,new_details,'location inline layout')

replace_once("if(d?.id)incrementUse(d.id);save();closeModal();render();await startTracking();","save();closeModal();render();await startTracking();",'remove departure increment')
replace_once("data.activeTrip=null;if(d?.id)incrementUse(d.id);save();stopTracking();","data.activeTrip=null;save();stopTracking();",'remove arrival increment')
replace_once("function incrementUse(id){const l=data.locations.find(x=>x.id===id);if(l)l.useCount=(l.useCount||0)+1}\n",'', 'remove increment helper')

count=text.count("(b.useCount||0)-(a.useCount||0)")
if count!=5:
    raise SystemExit(f'useCount sort replacements: expected 5 matches, found {count}')
text=text.replace("(b.useCount||0)-(a.useCount||0)","locationRegisteredTripCount(b)-locationRegisteredTripCount(a)")
replace_once("score+=(loc.useCount||0)*.15;","score+=locationRegisteredTripCount(loc)*.15;",'arrival registered frequency')

index.write_text(text,encoding='utf-8')

sw=Path('service-worker.js')
s=sw.read_text(encoding='utf-8')
if s.count("kmreg-shell-0.28.1")!=1:
    raise SystemExit('service worker version mismatch')
s=s.replace("kmreg-shell-0.28.1","kmreg-shell-0.28.2",1)
sw.write_text(s,encoding='utf-8')

script=text.split('<script>',1)[1].rsplit('</script>',1)[0]
Path('/tmp/kmreg-app.js').write_text(script,encoding='utf-8')

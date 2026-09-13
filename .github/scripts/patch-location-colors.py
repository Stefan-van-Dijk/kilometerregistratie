from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)

replace_once("+' · 0.27.7';", "+' · 0.27.8';", 'version')

css = r'''
/* 0.27.8 — kleurmarkering locaties en compacte deelstatus */
:root{--home:#ff9f0a;--other:#8e8e93}
.location-type-home{--location-color:var(--home)}.location-type-work{--location-color:var(--commute)}.location-type-business{--location-color:var(--business)}.location-type-private{--location-color:var(--private)}.location-type-other{--location-color:var(--other)}
.location-swipe-surface.location-type-home,.location-swipe-surface.location-type-work,.location-swipe-surface.location-type-business,.location-swipe-surface.location-type-private,.location-swipe-surface.location-type-other{border-left:3px solid var(--location-color)!important;padding-left:10px}
.location-share-status{position:relative;display:inline-flex;align-items:center;justify-content:center;flex:0 0 26px;width:26px;height:26px;margin-left:auto;border:1px solid var(--line);border-radius:8px;color:var(--muted);font-size:15px;font-weight:800;line-height:1}.location-share-status.ask::after{content:'';position:absolute;right:3px;top:3px;width:5px;height:5px;border-radius:50%;background:var(--warn)}.location-share-status.always{border-color:rgba(77,163,255,.45);color:var(--accent);background:rgba(77,163,255,.10)}.location-share-status.never{opacity:.38}.location-share-status.never::after{content:'';position:absolute;width:18px;height:1.5px;background:currentColor;transform:rotate(-45deg);border-radius:999px}.location-swipe-surface .chev{margin-left:0}
@media (prefers-color-scheme:light){:root{--home:#b96800;--other:#6e6e73}}
'''
replace_once('\n</style>', '\n' + css + '\n</style>', 'location css')

old = "function locationSwipeRow(l){return`<div class=\"swipe-row location-swipe-row\" data-swipe-kind=\"location\" data-id=\"${l.id}\">${swipeActions('location',l.id)}<div class=\"swipe-surface location-item location-swipe-surface\" data-action=\"edit-location\" data-id=\"${l.id}\"><div class=\"location-main\"><strong>${esc(l.name)}</strong><small>${esc(l.address||coords(l)||'Geen adres/GPS')} · Delen: ${shareRideLabel(l.shareRide||'never')}</small></div><div class=\"chev\">›</div></div></div>`}"
new = "function locationTypeClass(type){return`location-type-${['home','work','business','private'].includes(type)?type:'other'}`}\nfunction locationShareStatus(value){const v=['ask','always'].includes(value)?value:'never',label=v==='ask'?'Rit delen: vraag mij':v==='always'?'Rit delen: altijd tonen':'Rit delen: nooit';return`<span class=\"location-share-status ${v}\" title=\"${attr(label)}\" aria-label=\"${attr(label)}\">↗</span>`}\nfunction locationSwipeRow(l){return`<div class=\"swipe-row location-swipe-row\" data-swipe-kind=\"location\" data-id=\"${l.id}\">${swipeActions('location',l.id)}<div class=\"swipe-surface location-item location-swipe-surface ${locationTypeClass(l.type)}\" data-action=\"edit-location\" data-id=\"${l.id}\"><div class=\"location-main\"><strong>${esc(l.name)}</strong><small>${esc(l.address||coords(l)||'Geen adres/GPS')}</small></div>${locationShareStatus(l.shareRide||'never')}<div class=\"chev\">›</div></div></div>`}"
replace_once(old, new, 'location row')

index.write_text(text, encoding='utf-8')

sw = Path('service-worker.js')
sw_text = sw.read_text(encoding='utf-8')
if sw_text.count("kmreg-shell-0.27.7") != 1:
    raise SystemExit('service worker: expected cache 0.27.7 once')
sw.write_text(sw_text.replace("kmreg-shell-0.27.7", "kmreg-shell-0.27.8", 1), encoding='utf-8')

script = text.split('<script>',1)[1].rsplit('</script>',1)[0]
Path('/tmp/kmreg-app.js').write_text(script, encoding='utf-8')

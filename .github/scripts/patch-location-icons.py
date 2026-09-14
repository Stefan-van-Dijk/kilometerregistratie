from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')

repls = []

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)

replace_once("+' · 0.28.11';", "+' · 0.28.12';", 'version')

old_type_icon = "function locationTypeIcon(type){return type==='home'?'🏠':type==='work'?'🧰':type==='business'?'🏢':type==='private'?'👤':'📍'}"
new_type_icon = r'''function locationTypeIcon(type){const t=['home','work','business','private'].includes(type)?type:'other',paths={home:'<path d="M4 11.5 12 5l8 6.5V20h-5v-5H9v5H4z"/>',work:'<path d="M4 8h16v11H4z"/><path d="M9 8V5h6v3M4 12h16M10 12v2h4v-2"/>',business:'<path d="M6 20V5h12v15M9 8h2m2 0h2M9 12h2m2 0h2M9 16h2m2 0h2"/>',private:'<circle cx="12" cy="8" r="3"/><path d="M5.5 20c.8-4 3-6 6.5-6s5.7 2 6.5 6"/>',other:'<path d="M12 21s6-6.2 6-12a6 6 0 1 0-12 0c0 5.8 6 12 6 12z"/><circle cx="12" cy="9" r="2"/>'};return`<svg class="location-type-glyph type-${t}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${paths[t]}</svg>`}'''
replace_once(old_type_icon, new_type_icon, 'locationTypeIcon')

old_share = "function locationShareStatus(value){const v=['ask','always'].includes(value)?value:'never',label=v==='ask'?'Rit delen: vraag mij':v==='always'?'Rit delen: altijd tonen':'Rit delen: nooit';return`<span class=\"location-share-status ${v}\" title=\"${attr(label)}\" aria-label=\"${attr(label)}\">↗</span>`}"
new_share = r'''function locationShareGlyph(filled=false){return filled?'<svg class="location-share-glyph" viewBox="0 0 24 24" aria-hidden="true"><path class="share-tray-fill" d="M5 10h14v10H5z"/><path class="share-arrow-on-fill" d="M12 14V3m0 0L8 7m4-4 4 4"/></svg>':'<svg class="location-share-glyph" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 10v10h14V10M12 14V3m0 0L8 7m4-4 4 4"/></svg>'}
function locationShareStatus(value){const v=['ask','always'].includes(value)?value:'never';if(v==='never')return'';const filled=v==='ask',label=filled?'Rit delen: vraag mij':'Rit delen: altijd beschikbaar';return`<span class="location-share-status ${filled?'filled':'outline'}" title="${attr(label)}" aria-label="${attr(label)}">${locationShareGlyph(filled)}</span>`}'''
replace_once(old_share, new_share, 'locationShareStatus')

old_status = "function locationStatusIcons(l){return`<div class=\"location-status-icons\">${locationShareStatus(l.shareRide||'never')}${locationLinkStatus(l)}</div>`}"
new_status = "function locationStatusIcons(l){const share=locationShareStatus(l.shareRide||'never');return share?`<div class=\"location-status-icons\">${share}</div>`:''}"
replace_once(old_status, new_status, 'locationStatusIcons')

old_type_option = "function locationTypeOption(value,icon,label,current){return`<label class=\"location-choice type-${value}\"><input type=\"radio\" name=\"type\" value=\"${value}\" ${current===value?'checked':''} required><span><b class=\"choice-icon\">${icon}</b>${label}</span></label>`}"
new_type_option = "function locationTypeOption(value,label,current){return`<label class=\"location-choice type-${value}\"><input type=\"radio\" name=\"type\" value=\"${value}\" ${current===value?'checked':''} required><span><b class=\"choice-icon\">${locationTypeIcon(value)}</b>${label}</span></label>`}"
replace_once(old_type_option, new_type_option, 'locationTypeOption')

old_share_option = "function locationShareOption(value,icon,label,current){return`<label class=\"location-choice\"><input type=\"radio\" name=\"shareRide\" value=\"${value}\" ${current===value?'checked':''} required><span><b class=\"choice-icon\">${icon}</b>${label}</span></label>`}"
new_share_option = "function locationShareOption(value,label,current){return`<label class=\"location-choice\"><input type=\"radio\" name=\"shareRide\" value=\"${value}\" ${current===value?'checked':''} required><span>${label}</span></label>`}"
replace_once(old_share_option, new_share_option, 'locationShareOption')

replace_once("${locationTypeOption('home','🏠','Thuis',l?.type||'other')}${locationTypeOption('work','🧰','Werk',l?.type||'other')}${locationTypeOption('business','🏢','Zakelijk',l?.type||'other')}${locationTypeOption('private','👤','Privé',l?.type||'other')}${locationTypeOption('other','📍','Overig',l?.type||'other')}", "${locationTypeOption('home','Thuis',l?.type||'other')}${locationTypeOption('work','Werk',l?.type||'other')}${locationTypeOption('business','Zakelijk',l?.type||'other')}${locationTypeOption('private','Privé',l?.type||'other')}${locationTypeOption('other','Overig',l?.type||'other')}", 'type option calls')
replace_once("${locationShareOption('never','⊘','Nooit',l?.shareRide||'never')}${locationShareOption('ask','?','Vraag mij',l?.shareRide||'never')}${locationShareOption('always','↗','Altijd',l?.shareRide||'never')}", "${locationShareOption('never','Nooit',l?.shareRide||'never')}${locationShareOption('ask','Vraag mij',l?.shareRide||'never')}${locationShareOption('always','Altijd',l?.shareRide||'never')}", 'share option calls')

css = r'''

/* 0.28.12 — minimalistische locatie- en deeliconen */
.location-type-glyph{display:inline-block;width:15px;height:15px;vertical-align:-2px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.location-type-glyph.type-home{color:var(--home)}
.location-type-glyph.type-work{color:var(--commute)}
.location-type-glyph.type-business{color:var(--business)}
.location-type-glyph.type-private{color:var(--private)}
.location-type-glyph.type-other{color:var(--other)}
.location-inline-field strong{display:flex;align-items:center;gap:5px}
.editor-page .location-choice-grid.type .choice-icon{display:inline-flex!important;align-items:center;justify-content:center;font-size:0;line-height:0}
.editor-page .location-choice-grid.type .choice-icon .location-type-glyph{width:14px;height:14px}
.editor-page .location-choice-grid.share .choice-icon{display:none!important}

/* In de locatielijst alleen een deelsymbool wanneer delen relevant is. */
.location-status-icons{display:flex;flex:0 0 auto;align-items:center;justify-content:center;margin-left:auto}
.location-share-status{display:inline-flex!important;align-items:center;justify-content:center;flex:0 0 24px!important;width:24px!important;height:24px!important;margin:0!important;padding:0!important;border:0!important;border-radius:0!important;background:transparent!important;color:var(--accent)!important;opacity:1!important}
.location-share-status::after{display:none!important}
.location-share-glyph{width:18px;height:18px;overflow:visible;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.location-share-status.filled .share-tray-fill{fill:currentColor;stroke:none}
.location-share-status.filled .share-arrow-on-fill{fill:none;stroke:var(--bg);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.location-share-status.outline .location-share-glyph{fill:none;stroke:currentColor}
.location-link-status{display:none!important}
'''
marker = '\n</style>'
if text.count(marker) != 1:
    raise SystemExit(f'style marker: expected 1 match, found {text.count(marker)}')
text = text.replace(marker, css + marker, 1)

index.write_text(text, encoding='utf-8')

sw = Path('service-worker.js')
s = sw.read_text(encoding='utf-8')
old_cache = "kmreg-shell-0.28.11"
new_cache = "kmreg-shell-0.28.12"
if s.count(old_cache) != 1:
    raise SystemExit(f'service worker: expected 1 match, found {s.count(old_cache)}')
sw.write_text(s.replace(old_cache, new_cache, 1), encoding='utf-8')

html = index.read_text(encoding='utf-8')
start = html.index('<script>') + len('<script>')
end = html.index('</script>', start)
Path('/tmp/kmreg-app.js').write_text(html[start:end], encoding='utf-8')

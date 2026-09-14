from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)

replace_once("+' · 0.28.12';", "+' · 0.28.13';", 'version')

old_share = r'''function locationShareGlyph(filled=false){return filled?'<svg class="location-share-glyph" viewBox="0 0 24 24" aria-hidden="true"><path class="share-tray-fill" d="M5 10h14v10H5z"/><path class="share-arrow-on-fill" d="M12 14V3m0 0L8 7m4-4 4 4"/></svg>':'<svg class="location-share-glyph" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 10v10h14V10M12 14V3m0 0L8 7m4-4 4 4"/></svg>'}'''
new_share = r'''function locationShareGlyph(filled=false){return filled?'<svg class="location-share-glyph" viewBox="0 0 24 24" aria-hidden="true"><rect class="share-box-fill" x="4" y="8" width="16" height="13" rx="3"/><path class="share-arrow-on-fill" d="M12 15V3m0 0L8.5 6.5M12 3l3.5 3.5"/></svg>':'<svg class="location-share-glyph" viewBox="0 0 24 24" aria-hidden="true"><rect class="share-box-outline" x="4.75" y="8.75" width="14.5" height="11.5" rx="2.5"/><path class="share-arrow-outline" d="M12 15V3m0 0L8.5 6.5M12 3l3.5 3.5"/></svg>'}'''
replace_once(old_share, new_share, 'locationShareGlyph')

old_status = "function locationStatusIcons(l){const share=locationShareStatus(l.shareRide||'never');return share?`<div class=\"location-status-icons\">${share}</div>`:''}"
new_status = "function locationStatusIcons(l){const share=locationShareStatus(l.shareRide||'never'),label=typeLabel(l.type);return`<div class=\"location-status-icons\">${share}<span class=\"location-type-status\" title=\"${attr(label)}\" aria-label=\"${attr(label)}\">${locationTypeIcon(l.type)}</span></div>`}"
replace_once(old_status, new_status, 'locationStatusIcons')

css = r'''

/* 0.28.13 — ruimere typekeuze, duidelijke deelstatus en correcte ritkleuren */
.editor-page .edit-trip-type.category-commute{--choice-color:var(--commute)}
.editor-page .edit-trip-type.category-business{--choice-color:var(--business)}
.editor-page .edit-trip-type.category-private{--choice-color:var(--private)}

/* Locatietype: pictogram boven, tekst eronder; selectiebol los in de hoek. */
.editor-page .location-choice-grid.type .location-choice span{position:relative;min-height:58px!important;flex-direction:column!important;gap:5px!important;padding:7px 2px 5px!important;font-size:9.5px!important}
.editor-page .location-choice-grid.type .location-choice span::before{position:absolute;top:5px;right:6px;display:block;flex:none;width:9px;height:9px;border-width:1.6px;margin:0}
.editor-page .location-choice-grid.type .choice-icon{min-height:21px}
.editor-page .location-choice-grid.type .choice-icon .location-type-glyph{width:20px;height:20px}

/* Rechts in iedere locatieregel altijd het type; delen alleen als het relevant is. */
.location-status-icons{display:flex;flex:0 0 auto;align-items:center;justify-content:flex-end;gap:4px;margin-left:auto}
.location-type-status{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;flex:0 0 24px}
.location-type-status .location-type-glyph{width:19px;height:19px}

/* Duidelijker iOS-achtig deelsymbool: gevuld bij 'Vraag mij', outline bij 'Altijd'. */
.location-share-status{flex-basis:26px!important;width:26px!important;height:26px!important}
.location-share-glyph{width:21px;height:21px;overflow:visible;fill:none;stroke:currentColor;stroke-width:1.65;stroke-linecap:round;stroke-linejoin:round}
.location-share-status.filled .share-box-fill{fill:currentColor;stroke:none}
.location-share-status.filled .share-arrow-on-fill{fill:none;stroke:#fff;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.location-share-status.outline .share-box-outline,.location-share-status.outline .share-arrow-outline{fill:none;stroke:currentColor}
'''
marker = '\n</style>'
if text.count(marker) != 1:
    raise SystemExit(f'style marker: expected 1 match, found {text.count(marker)}')
text = text.replace(marker, css + marker, 1)
index.write_text(text, encoding='utf-8')

sw = Path('service-worker.js')
s = sw.read_text(encoding='utf-8')
old_cache = 'kmreg-shell-0.28.12'
new_cache = 'kmreg-shell-0.28.13'
if s.count(old_cache) != 1:
    raise SystemExit(f'service worker: expected 1 match, found {s.count(old_cache)}')
sw.write_text(s.replace(old_cache, new_cache, 1), encoding='utf-8')

html = index.read_text(encoding='utf-8')
start = html.index('<script>') + len('<script>')
end = html.index('</script>', start)
Path('/tmp/kmreg-app.js').write_text(html[start:end], encoding='utf-8')

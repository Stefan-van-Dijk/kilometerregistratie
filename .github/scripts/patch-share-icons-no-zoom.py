from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)

replace_once("+' · 0.28.13';", "+' · 0.28.14';", 'version')

old_share = r'''function locationShareGlyph(filled=false){return filled?'<svg class="location-share-glyph" viewBox="0 0 24 24" aria-hidden="true"><rect class="share-box-fill" x="4" y="8" width="16" height="13" rx="3"/><path class="share-arrow-on-fill" d="M12 15V3m0 0L8.5 6.5M12 3l3.5 3.5"/></svg>':'<svg class="location-share-glyph" viewBox="0 0 24 24" aria-hidden="true"><rect class="share-box-outline" x="4.75" y="8.75" width="14.5" height="11.5" rx="2.5"/><path class="share-arrow-outline" d="M12 15V3m0 0L8.5 6.5M12 3l3.5 3.5"/></svg>'}'''
new_share = r'''function locationShareGlyph(filled=false){return`<svg class="location-share-glyph" viewBox="0 0 24 24" aria-hidden="true"><path class="share-symbol" d="M6 10v9.5h12V10M12 15V3m0 0L8.5 6.5M12 3l3.5 3.5"/></svg>`}'''
replace_once(old_share, new_share, 'locationShareGlyph')

css = r'''

/* 0.28.14 — duidelijke deelstatus en voorkom iOS-focuszoom */
.location-share-status{width:28px!important;height:28px!important;flex-basis:28px!important;border-radius:7px!important;border:1.5px solid var(--accent)!important;background:transparent!important;color:var(--accent)!important}
.location-share-status.filled{background:var(--accent)!important;border-color:var(--accent)!important;color:#fff!important}
.location-share-status.outline{background:transparent!important;border-color:var(--accent)!important;color:var(--accent)!important}
.location-share-status .location-share-glyph{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.location-share-status .share-symbol{fill:none;stroke:currentColor}

/* Safari op iPhone zoomt automatisch in op form controls onder 16px. */
@supports (-webkit-touch-callout:none){
  input,select,textarea{font-size:16px!important}
}
'''
marker = '\n</style>'
if text.count(marker) != 1:
    raise SystemExit(f'style marker: expected 1 match, found {text.count(marker)}')
text = text.replace(marker, css + marker, 1)
index.write_text(text, encoding='utf-8')

sw = Path('service-worker.js')
s = sw.read_text(encoding='utf-8')
old_cache = 'kmreg-shell-0.28.13'
new_cache = 'kmreg-shell-0.28.14'
if s.count(old_cache) != 1:
    raise SystemExit(f'service worker: expected 1 match, found {s.count(old_cache)}')
sw.write_text(s.replace(old_cache, new_cache, 1), encoding='utf-8')

html = index.read_text(encoding='utf-8')
start = html.index('<script>') + len('<script>')
end = html.index('</script>', start)
Path('/tmp/kmreg-app.js').write_text(html[start:end], encoding='utf-8')

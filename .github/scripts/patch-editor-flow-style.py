from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')

old_version = "+' · 0.28.9';"
new_version = "+' · 0.28.10';"
if text.count(old_version) != 1:
    raise SystemExit(f'version: expected 1 match, found {text.count(old_version)}')
text = text.replace(old_version, new_version, 1)

css = r'''

/* 0.28.10 — bewerkpagina's in dezelfde flow-stijl als vertrek en aankomst */
.editor-view .shell{padding-bottom:calc(24px + env(safe-area-inset-bottom))}
.editor-page{animation:editor-flow-page-in .24s cubic-bezier(.2,.8,.2,1)}
.editor-nav{border-bottom:1px solid var(--line);box-shadow:none}
.editor-nav-title{letter-spacing:-.01em}
.editor-content{padding:0;animation:editor-flow-content-in .28s cubic-bezier(.2,.8,.2,1)}
.editor-page .edit-section{padding:17px 0 18px;border-top:0;border-bottom:1px solid var(--line);animation:editor-flow-step-in .3s ease both}
.editor-page .edit-section:first-of-type{padding-top:15px;border-top:0}
.editor-page .edit-section:nth-of-type(2){animation-delay:.025s}
.editor-page .edit-section:nth-of-type(3){animation-delay:.05s}
.editor-page .edit-section:nth-of-type(4){animation-delay:.075s}
.editor-page .edit-section:nth-of-type(5){animation-delay:.1s}
.editor-page .edit-section-head{display:block;margin-bottom:10px}
.editor-page .edit-section-head strong{display:block;color:var(--muted);font-size:10px;font-weight:850;line-height:1.2;text-transform:uppercase;letter-spacing:.07em}
.editor-page .edit-section-head small{display:block;margin-top:3px;color:var(--muted);font-size:10px;line-height:1.3;text-align:left;text-transform:none;letter-spacing:0}
.editor-page .edit-grid{gap:10px}
.editor-page .edit-form .form-group{margin:0}
.editor-page .edit-form .form-group label{margin-bottom:6px;color:var(--muted);font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.06em}
.editor-page .edit-form .form-group input,.editor-page .edit-form .form-group select,.editor-page .edit-form .form-group textarea{min-height:44px;padding:10px 11px;border:1px solid var(--line);border-radius:11px;background:var(--card);color:var(--text);box-shadow:none}
.editor-page .edit-form .form-group textarea{min-height:58px;height:58px;resize:vertical}
.editor-page .edit-trip-type-grid{gap:7px;margin:0}
.editor-page .edit-trip-type span{min-height:44px;padding:8px 5px;border-radius:11px;background:var(--card);font-size:11px}
.editor-page .edit-location-behaviour{gap:16px}
.editor-page .location-choice-grid{gap:7px}
.editor-page .location-choice span{background:var(--card);border-radius:11px}
.editor-link-action{margin:0 0 9px;padding:2px 0;color:var(--accent);font-size:11px}
.editor-page .location-link-hint{margin-top:9px;padding:9px 0 0;border-top:1px solid var(--line);font-size:10px;line-height:1.4}
.editor-page .osm-attribution{margin-top:5px;font-size:9px;line-height:1.35}
.editor-page .edit-warning{margin-top:0;padding:10px 0 0;border-top:0;color:var(--muted);font-size:10px;line-height:1.4}
.editor-page .edit-status{min-height:0;margin:6px 0 0;color:var(--muted);font-size:10px}
.editor-savebar{position:static;width:100%;max-width:620px;margin:0 auto;padding:16px 0 calc(16px + env(safe-area-inset-bottom));border-top:0;background:transparent}
.editor-savebar-inner{width:100%;max-width:none;margin:0}
.editor-savebar .btn{min-height:48px;border-radius:13px}
@keyframes editor-flow-page-in{from{opacity:.88}to{opacity:1}}
@keyframes editor-flow-content-in{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:translateY(0)}}
@keyframes editor-flow-step-in{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:520px){
  .editor-page .edit-section-head small{display:block}
  .editor-page .edit-grid.two.editor-route-grid{grid-template-columns:1fr}
}
@media(max-height:920px){
  .editor-view .shell{padding-bottom:calc(18px + env(safe-area-inset-bottom))}
  .editor-page .edit-section{padding:12px 0 13px}
  .editor-page .edit-section:first-of-type{padding-top:10px}
  .editor-page .edit-section-head{margin-bottom:7px}
  .editor-page .edit-form .form-group input,.editor-page .edit-form .form-group select,.editor-page .edit-form .form-group textarea{min-height:40px;padding:8px 9px}
  .editor-page .edit-form .form-group textarea{min-height:46px;height:46px}
  .editor-page .edit-trip-type span{min-height:39px}
  .editor-page .location-choice span{min-height:43px}
  .editor-savebar{padding:11px 0 calc(11px + env(safe-area-inset-bottom))}
  .editor-savebar .btn{min-height:43px}
}
@media(max-height:760px){
  .editor-page .edit-section{padding:9px 0 10px}
  .editor-page .edit-section-head{margin-bottom:5px}
  .editor-page .edit-grid{gap:6px}
  .editor-page .edit-form .form-group input,.editor-page .edit-form .form-group select,.editor-page .edit-form .form-group textarea{min-height:37px;padding-top:7px;padding-bottom:7px}
  .editor-page .edit-trip-type span{min-height:36px}
  .editor-page .location-choice span{min-height:40px}
  .editor-savebar{padding-top:8px}
}
@media (prefers-color-scheme:light){
  .editor-page .edit-form .form-group input,.editor-page .edit-form .form-group select,.editor-page .edit-form .form-group textarea,.editor-page .edit-trip-type span,.editor-page .location-choice span{background:#fff;color:var(--text)}
}
@media (prefers-reduced-motion:reduce){
  .editor-page,.editor-content,.editor-page .edit-section{animation:none!important}
}
'''

marker = '\n</style>'
if text.count(marker) != 1:
    raise SystemExit(f'style marker: expected 1 match, found {text.count(marker)}')
text = text.replace(marker, css + marker, 1)
index.write_text(text, encoding='utf-8')

sw = Path('service-worker.js')
s = sw.read_text(encoding='utf-8')
old_cache = "kmreg-shell-0.28.9"
new_cache = "kmreg-shell-0.28.10"
if s.count(old_cache) != 1:
    raise SystemExit(f'service worker: expected 1 match, found {s.count(old_cache)}')
sw.write_text(s.replace(old_cache, new_cache, 1), encoding='utf-8')

html = index.read_text(encoding='utf-8')
start = html.index('<script>') + len('<script>')
end = html.index('</script>', start)
Path('/tmp/kmreg-app.js').write_text(html[start:end], encoding='utf-8')

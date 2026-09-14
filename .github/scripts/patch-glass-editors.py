from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')

old_version = "+' · 0.28.10';"
new_version = "+' · 0.28.11';"
if text.count(old_version) != 1:
    raise SystemExit(f'version: expected 1 match, found {text.count(old_version)}')
text = text.replace(old_version, new_version, 1)

old_nav = '''function editorNav(title,dangerAction='',dangerId=''){return`<header class="editor-nav"><button type="button" class="editor-back" data-action="editor-back" aria-label="Terug">‹ Terug</button><div class="editor-nav-title">${esc(title)}</div>${dangerAction?`<button type="button" class="editor-danger" data-action="${attr(dangerAction)}" data-id="${attr(dangerId)}">Verwijder</button>`:'<span class="editor-nav-spacer"></span>'}</header>`}'''
new_nav = '''function editorNav(title,saveAction,dangerAction='',dangerId=''){return`<header class="editor-nav"><button type="button" class="editor-glass-button editor-back" data-action="editor-back" aria-label="Terug">‹</button><div class="editor-nav-title">${esc(title)}</div><div class="editor-nav-actions"><button type="button" class="editor-glass-button editor-save" data-action="${attr(saveAction)}" aria-label="Opslaan">✓</button>${dangerAction?`<details class="editor-more"><summary class="editor-glass-button" aria-label="Meer opties">•••</summary><div class="editor-more-menu"><button type="button" class="editor-menu-delete" data-action="${attr(dangerAction)}" data-id="${attr(dangerId)}">Verwijderen</button></div></details>`:''}</div></header>`}'''
if text.count(old_nav) != 1:
    raise SystemExit(f'editorNav: expected 1 match, found {text.count(old_nav)}')
text = text.replace(old_nav, new_nav, 1)

old_trip_call = "${editorNav('Rit aanpassen','delete-trip',t.id)}"
new_trip_call = "${editorNav('Rit aanpassen','save-trip-edit','delete-trip',t.id)}"
if text.count(old_trip_call) != 1:
    raise SystemExit(f'trip nav call: expected 1 match, found {text.count(old_trip_call)}')
text = text.replace(old_trip_call, new_trip_call, 1)

old_location_call = "${editorNav(title,l?'delete-location':'',l?.id||'')}"
new_location_call = "${editorNav(title,'save-location',l?'delete-location':'',l?.id||'')}"
if text.count(old_location_call) != 1:
    raise SystemExit(f'location nav call: expected 1 match, found {text.count(old_location_call)}')
text = text.replace(old_location_call, new_location_call, 1)

css = r'''

/* 0.28.11 — glasnavigatie en rustige bewerkvelden */
.editor-view .shell{padding-bottom:calc(20px + env(safe-area-inset-bottom))}
.editor-nav{display:flex;align-items:center;justify-content:space-between;min-height:52px;border-bottom:0;background:rgba(13,17,23,.84);-webkit-backdrop-filter:blur(22px) saturate(165%);backdrop-filter:blur(22px) saturate(165%)}
.editor-nav-title{position:absolute;left:50%;transform:translateX(-50%);font-size:16px;font-weight:850;pointer-events:none}
.editor-nav-actions{display:flex;align-items:center;gap:8px;margin-left:auto}
.editor-glass-button{display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;min-height:38px!important;padding:0!important;border:1px solid rgba(255,255,255,.12)!important;border-radius:50%!important;background:rgba(255,255,255,.08)!important;color:var(--text)!important;box-shadow:0 5px 18px rgba(0,0,0,.14),inset 0 1px 0 rgba(255,255,255,.08);-webkit-backdrop-filter:blur(18px) saturate(170%);backdrop-filter:blur(18px) saturate(170%);font-size:20px!important;font-weight:800!important;line-height:1;cursor:pointer}
.editor-back{font-size:27px!important;padding-bottom:3px!important;color:var(--accent)!important}
.editor-save{font-size:20px!important;color:var(--accent)!important}
.editor-glass-button:active{transform:scale(.94);background:rgba(255,255,255,.14)!important}
.editor-more{position:relative}
.editor-more>summary{list-style:none}
.editor-more>summary::-webkit-details-marker{display:none}
.editor-more[open]>summary{background:rgba(255,255,255,.14)!important}
.editor-more-menu{position:absolute;z-index:45;top:45px;right:0;min-width:158px;padding:6px;border:1px solid rgba(255,255,255,.12);border-radius:15px;background:rgba(29,36,48,.88);box-shadow:0 14px 38px rgba(0,0,0,.24);-webkit-backdrop-filter:blur(24px) saturate(175%);backdrop-filter:blur(24px) saturate(175%)}
.editor-more-menu button{width:100%;min-height:40px;padding:8px 11px;border:0;border-radius:10px;background:transparent;color:var(--bad);font-size:13px;font-weight:800;text-align:left;cursor:pointer}
.editor-more-menu button:active{background:rgba(255,103,103,.1)}
.editor-savebar{display:none!important}

/* Velden ogen als informatie; onderlijn en focus tonen dat ze bewerkbaar zijn. */
.editor-page .edit-section-head small{display:none!important}
.editor-page .edit-section-head{margin-bottom:8px}
.editor-page .edit-grid{gap:10px}
.editor-page .edit-form .form-group{min-width:0}
.editor-page .edit-form .form-group label{margin-bottom:1px;font-size:9px;letter-spacing:.07em}
.editor-page .edit-form .form-group input,
.editor-page .edit-form .form-group select,
.editor-page .edit-form .form-group textarea{width:100%;min-height:38px!important;padding:6px 0 7px!important;border:0!important;border-bottom:1px solid var(--line)!important;border-radius:0!important;background-color:transparent!important;color:var(--text)!important;box-shadow:none!important;font-size:15px;line-height:1.3;outline:none}
.editor-page .edit-form .form-group textarea{min-height:42px!important;height:42px;resize:vertical}
.editor-page .edit-form .form-group:focus-within label{color:var(--accent)}
.editor-page .edit-form .form-group:focus-within input,
.editor-page .edit-form .form-group:focus-within select,
.editor-page .edit-form .form-group:focus-within textarea{border-bottom-color:var(--accent)!important}
.editor-page #locationForm input[name="lat"],.editor-page #locationForm input[name="lng"]{font-size:11.5px!important;letter-spacing:-.025em}
.editor-page #tripEditForm input[type="datetime-local"]{font-size:12px!important;letter-spacing:-.02em}
.editor-link-action{margin:1px 0 8px;padding:4px 0;border:0;background:transparent;color:var(--accent);font-size:11px;font-weight:800}

/* Eén selectietaal: kleur = type, gevuld bolletje = gekozen. */
.editor-page .edit-trip-type-grid,
.editor-page .location-choice-grid.type,
.editor-page .location-choice-grid.share{display:flex;grid-template-columns:none;align-items:center;justify-content:space-between;gap:5px;margin:0}
.editor-page .edit-trip-type,.editor-page .location-choice{flex:1 1 0;min-width:0;--choice-color:var(--accent)}
.editor-page .edit-trip-type.commute{--choice-color:var(--commute)}
.editor-page .edit-trip-type.business{--choice-color:var(--business)}
.editor-page .edit-trip-type.private{--choice-color:var(--private)}
.editor-page .location-choice.type-home{--choice-color:var(--home)}
.editor-page .location-choice.type-work{--choice-color:var(--commute)}
.editor-page .location-choice.type-business{--choice-color:var(--business)}
.editor-page .location-choice.type-private{--choice-color:var(--private)}
.editor-page .location-choice.type-other{--choice-color:var(--other)}
.editor-page .edit-trip-type span,
.editor-page .location-choice span{display:flex!important;min-height:31px!important;flex-direction:row!important;align-items:center;justify-content:center;gap:6px;padding:4px 1px!important;border:0!important;border-radius:0!important;background:transparent!important;color:var(--muted)!important;box-shadow:none!important;font-size:10.5px!important;font-weight:750;text-align:center;white-space:nowrap}
.editor-page .edit-trip-type span::before,
.editor-page .location-choice span::before{content:"";display:block;flex:0 0 11px;width:11px;height:11px;border:1.8px solid var(--choice-color);border-radius:50%;background:transparent;box-sizing:border-box}
.editor-page .edit-trip-type input:checked+span,
.editor-page .location-choice input:checked+span{border:0!important;background:transparent!important;color:var(--text)!important;box-shadow:none!important;font-weight:850}
.editor-page .edit-trip-type input:checked+span::before,
.editor-page .location-choice input:checked+span::before{background:var(--choice-color);border-color:var(--choice-color)}
.editor-page .location-choice .choice-icon{display:none!important}
.editor-page .edit-location-behaviour{gap:13px}
.editor-page .edit-location-behaviour .hint{margin-top:2px!important;font-size:9px;line-height:1.3}

@media(max-width:420px){
  .editor-nav{margin-left:-16px;margin-right:-16px;padding-left:16px;padding-right:16px}
  .editor-nav-actions{gap:6px}
  .editor-glass-button{width:36px;height:36px;min-height:36px!important}
  .editor-page .edit-trip-type span,.editor-page .location-choice span{gap:4px;font-size:9.5px!important}
  .editor-page .edit-trip-type span::before,.editor-page .location-choice span::before{flex-basis:10px;width:10px;height:10px}
}
@media(max-height:760px){
  .editor-page .edit-section{padding:8px 0 9px}
  .editor-page .edit-section-head{margin-bottom:4px}
  .editor-page .edit-form .form-group input,.editor-page .edit-form .form-group select,.editor-page .edit-form .form-group textarea{min-height:34px!important;padding-top:5px!important;padding-bottom:5px!important}
  .editor-page .edit-trip-type span,.editor-page .location-choice span{min-height:28px!important}
}
@media (prefers-color-scheme:light){
  .editor-nav{background:rgba(245,245,247,.86)}
  .editor-glass-button{border-color:rgba(255,255,255,.88)!important;background:rgba(255,255,255,.70)!important;box-shadow:0 4px 16px rgba(20,30,45,.10),inset 0 1px 0 rgba(255,255,255,.95)}
  .editor-glass-button:active,.editor-more[open]>summary{background:rgba(255,255,255,.92)!important}
  .editor-more-menu{border-color:rgba(255,255,255,.9);background:rgba(255,255,255,.84);box-shadow:0 14px 38px rgba(30,45,65,.16)}
}
'''
marker = '\n</style>'
if text.count(marker) != 1:
    raise SystemExit(f'style marker: expected 1 match, found {text.count(marker)}')
text = text.replace(marker, css + marker, 1)
index.write_text(text, encoding='utf-8')

sw = Path('service-worker.js')
s = sw.read_text(encoding='utf-8')
old_cache = "kmreg-shell-0.28.10"
new_cache = "kmreg-shell-0.28.11"
if s.count(old_cache) != 1:
    raise SystemExit(f'service worker: expected 1 match, found {s.count(old_cache)}')
sw.write_text(s.replace(old_cache, new_cache, 1), encoding='utf-8')

html = index.read_text(encoding='utf-8')
start = html.index('<script>') + len('<script>')
end = html.index('</script>', start)
Path('/tmp/kmreg-app.js').write_text(html[start:end], encoding='utf-8')

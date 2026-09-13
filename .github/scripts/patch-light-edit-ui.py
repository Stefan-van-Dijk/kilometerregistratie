from pathlib import Path

index=Path('index.html')
text=index.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global text
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text=text.replace(old,new,1)

replace_once("+' · 0.28.3';","+' · 0.28.4';",'version')
replace_once(".edit-form .form-group input,.edit-form .form-group select,.edit-form .form-group textarea{background:#10151c;border-color:var(--line);border-radius:10px}",".edit-form .form-group input,.edit-form .form-group select,.edit-form .form-group textarea{background:var(--card);border-color:var(--line);border-radius:10px;color:var(--text)}",'edit form theme background')
replace_once(".edit-trip-type span{display:flex;align-items:center;justify-content:center;min-height:44px;padding:9px 6px;border:1px solid var(--line);border-radius:10px;background:#10151c;color:var(--muted);font-size:11px;font-weight:800;cursor:pointer}",".edit-trip-type span{display:flex;align-items:center;justify-content:center;min-height:44px;padding:9px 6px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--muted);font-size:11px;font-weight:800;cursor:pointer}",'edit trip type theme background')
replace_once(".location-choice span{display:flex;min-height:58px;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:7px 3px;border:1px solid var(--line);border-radius:11px;background:#101722;color:var(--muted);font-size:10px;font-weight:800;text-align:center;cursor:pointer}",".location-choice span{display:flex;min-height:58px;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:7px 3px;border:1px solid var(--line);border-radius:11px;background:var(--card);color:var(--muted);font-size:10px;font-weight:800;text-align:center;cursor:pointer}",'location choice theme background')

css="""
/* 0.28.4 — consistente lichte bewerkvelden */
.edit-form input,.edit-form select,.edit-form textarea{color-scheme:inherit}
.edit-form .edit-grid.keep-two input{font-variant-numeric:tabular-nums}
@media (prefers-color-scheme:light){
.edit-form .form-group input,.edit-form .form-group select,.edit-form .form-group textarea,.edit-trip-type span,.location-choice span{background:#fff;color:var(--text)}
.edit-form .btn.secondary{background:var(--card2);color:var(--text)}
}
"""
replace_once('\n</style>','\n'+css+'\n</style>','light edit css')

old="<div class=\"edit-grid two keep-two\">${field('Latitude','lat',l?.lat??g?.lat??'','text')}${field('Longitude','lng',l?.lng??g?.lng??'','text')}</div>"
new="<div class=\"edit-grid two keep-two\">${field('Latitude','lat',coordinateInputValue(l?.lat??g?.lat),'text')}${field('Longitude','lng',coordinateInputValue(l?.lng??g?.lng),'text')}</div>"
replace_once(old,new,'coordinate display precision')
anchor="function locationTypeOption(value,icon,label,current){"
helper="function coordinateInputValue(value){const n=parseNum(value);return n==null?'':n.toFixed(6)}\n"
replace_once(anchor,helper+anchor,'coordinate helper')

index.write_text(text,encoding='utf-8')

sw=Path('service-worker.js')
s=sw.read_text(encoding='utf-8')
if s.count("kmreg-shell-0.28.3")!=1:
    raise SystemExit('service worker version mismatch')
s=s.replace("kmreg-shell-0.28.3","kmreg-shell-0.28.4",1)
sw.write_text(s,encoding='utf-8')

script=text.split('<script>',1)[1].rsplit('</script>',1)[0]
Path('/tmp/kmreg-app.js').write_text(script,encoding='utf-8')

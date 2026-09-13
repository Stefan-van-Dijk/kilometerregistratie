from pathlib import Path

index=Path('index.html')
text=index.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global text
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text=text.replace(old,new,1)

replace_once("+' · 0.28.5';","+' · 0.28.6';",'version')

old_center='''<div class="period-center"><button type="button" class="period-mode-chip" data-action="period-choose">${esc(periodModeLabel())}</button><strong>${esc(periodLabel())}</strong><small>${esc(periodSubLabel(trips))}</small></div>'''
new_center='''<div class="period-center"><div class="period-title-line"><strong>${esc(periodLabel())}</strong><button type="button" class="period-scale-button" data-action="period-choose" aria-label="Periodegrootte kiezen" title="Periodegrootte kiezen">⌄</button></div><small>${esc(periodSubLabel(trips))}</small></div>'''
replace_once(old_center,new_center,'period title control')

old_help='''<div class="hint" style="margin-top:12px">Je kunt op het overzicht ook knijpen: uit elkaar bewegen maakt de periode kleiner, naar elkaar toe maakt hem groter.</div>'''
new_help='''<div class="period-choice-help"><div>Knijp op het periodeoverzicht: uit elkaar bewegen maakt de periode kleiner, naar elkaar toe maakt hem groter.</div><div><strong>Dubbel tik</strong> op het periodeoverzicht om direct terug te gaan naar de huidige periode.</div></div>'''
replace_once(old_help,new_help,'period chooser help')

css='''\n/* 0.28.6 — subtiele periodegroottebediening */\n.period-title-line{display:flex;align-items:center;justify-content:center;gap:3px}\n.period-title-line strong{font-size:25px;letter-spacing:-.025em}\n.period-scale-button{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;margin-right:-25px;padding:0;border:0;background:transparent;color:var(--muted);font-size:18px;font-weight:800;line-height:1;cursor:pointer;border-radius:9px}\n.period-scale-button:active{background:var(--card2);color:var(--text)}\n.period-choice-help{display:grid;gap:7px;margin-top:12px;padding-top:10px;border-top:1px solid var(--line);color:var(--muted);font-size:11px;line-height:1.4}\n.period-choice-help strong{color:var(--text)}\n@media(max-width:520px){.period-title-line strong{font-size:23px}.period-scale-button{width:28px;height:28px;margin-right:-23px;font-size:17px}}\n'''
replace_once('\n</style>','\n'+css+'\n</style>','period css')

index.write_text(text,encoding='utf-8')

sw=Path('service-worker.js')
s=sw.read_text(encoding='utf-8')
if "kmreg-shell-0.28.5" not in s:
    raise SystemExit('service worker version not found')
s=s.replace("kmreg-shell-0.28.5","kmreg-shell-0.28.6",1)
sw.write_text(s,encoding='utf-8')

html=index.read_text(encoding='utf-8')
start=html.index('<script>')+len('<script>')
end=html.index('</script>',start)
Path('/tmp/kmreg-app.js').write_text(html[start:end],encoding='utf-8')

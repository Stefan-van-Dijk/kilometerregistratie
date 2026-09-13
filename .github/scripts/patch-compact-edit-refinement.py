from pathlib import Path

index=Path('index.html')
text=index.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global text
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text=text.replace(old,new,1)

replace_once("function coordinateInputValue(value){const n=parseNum(value);return n==null?'':n.toFixed(6)}","function coordinateInputValue(value){return value==null||value===''?'':String(value)}",'full coordinate display')
replace_once("f.elements.lat.value=result.lat.toFixed(6);f.elements.lng.value=result.lng.toFixed(6);","f.elements.lat.value=String(result.lat);f.elements.lng.value=String(result.lng);",'full forward geocode coordinates')
replace_once("f.elements.lat.value=(+g.lat).toFixed(6);f.elements.lng.value=(+g.lng).toFixed(6);","f.elements.lat.value=String(g.lat);f.elements.lng.value=String(g.lng);",'full current gps coordinates')
replace_once("Bij Vraag mij krijg je na vertrek een eenmalige vraag. Bij Altijd blijft Deel rit beschikbaar tijdens de actieve rit.","Vraag mij: eenmalige vraag na vertrek · Altijd: Deel rit blijft beschikbaar.",'short share hint')
replace_once("Alleen ontbrekende gegevens worden automatisch aangevuld. Bestaande waarden blijven staan. Huidige GPS overschrijft bewust alleen de coördinaten om ze nauwkeuriger te maken.","Alleen ontbrekende gegevens worden aangevuld. Bestaande waarden blijven staan; huidige GPS vervangt alleen de coördinaten.",'short gps hint')

css=r'''
/* 0.28.4 — compacte bewerkvensters op iPhone */
#locationForm input[name="lat"],#locationForm input[name="lng"]{font-size:11px;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
#tripEditForm input[type="datetime-local"]{width:100%;max-width:100%;min-width:0;font-size:12px;letter-spacing:-.025em;font-variant-numeric:tabular-nums;overflow:hidden}
#tripEditForm input[type="datetime-local"]::-webkit-date-and-time-value{text-align:left;margin:0;min-width:0}
#tripEditForm input[type="datetime-local"]::-webkit-datetime-edit{padding:0;min-width:0}
#tripEditForm .edit-grid.two>.form-group{min-width:0;overflow:hidden}
@media(max-height:920px){
.modal:has(.edit-form){padding:calc(5px + env(safe-area-inset-top)) 8px calc(6px + env(safe-area-inset-bottom))}
.modal-panel:has(.edit-form){margin:0 auto;padding:10px 12px;border-radius:18px}
.edit-modal-head{padding-bottom:2px}.edit-modal-head .kicker{font-size:9px;margin-bottom:1px}.edit-modal-head h2{font-size:19px;line-height:1.05}.edit-modal-head .close{width:34px;height:34px;font-size:20px}
.edit-form{margin-top:0}.edit-section{padding:8px 0}.edit-section:first-of-type{padding-top:5px}.edit-section-head{margin-bottom:5px}.edit-section-head strong{font-size:12px}.edit-section-head small{font-size:9px}
.edit-grid{gap:6px}.edit-form .form-group label{margin-bottom:3px;font-size:9px}.edit-form .form-group input,.edit-form .form-group select,.edit-form .form-group textarea{min-height:38px;padding:8px 9px;font-size:13px;border-radius:9px}.edit-form .form-group textarea{min-height:42px;height:42px}
#tripEditForm input[type="datetime-local"]{padding:8px 5px;font-size:11px}
#locationForm input[name="lat"],#locationForm input[name="lng"]{font-size:10.5px;padding-left:7px;padding-right:7px}
.edit-trip-type span{min-height:36px;padding:6px 4px;font-size:10px}.edit-trip-type-grid{gap:5px}
.edit-gps-action{min-height:38px;margin:0 0 6px;padding:8px 10px;font-size:12px}.edit-form .location-link-hint{margin-top:6px;padding-top:5px;font-size:9.5px;line-height:1.3}.edit-form .osm-attribution{margin-top:3px;font-size:8.5px;line-height:1.25}
.edit-location-behaviour{gap:8px}.edit-form .location-choice-grid{gap:5px}.location-choice span{min-height:46px;padding:4px 2px;gap:2px;font-size:8.5px}.location-choice .choice-icon{font-size:15px}
.edit-form .hint{font-size:9.5px;line-height:1.3}.edit-warning{padding:6px 0;font-size:9px;line-height:1.25}.edit-status{min-height:0;margin:2px 0;font-size:9px}.edit-actions{gap:4px;padding-top:2px}.edit-actions .btn{min-height:38px;padding:8px 10px;font-size:12px}.edit-delete{min-height:28px;margin-top:0;font-size:10px}
}
@media(max-height:760px){
.edit-section{padding:6px 0}.edit-section-head{margin-bottom:4px}.edit-form .form-group input,.edit-form .form-group select,.edit-form .form-group textarea{min-height:35px;padding-top:6px;padding-bottom:6px}.location-choice span{min-height:42px}.edit-trip-type span{min-height:34px}.edit-gps-action{min-height:35px}.edit-form .location-link-hint{line-height:1.2}.edit-warning{padding:4px 0}
}
'''
replace_once('\n</style>','\n'+css+'\n</style>','compact edit css')

index.write_text(text,encoding='utf-8')
script=text.split('<script>',1)[1].rsplit('</script>',1)[0]
Path('/tmp/kmreg-app.js').write_text(script,encoding='utf-8')

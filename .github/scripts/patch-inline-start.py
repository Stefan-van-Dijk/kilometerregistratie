from pathlib import Path

index=Path('index.html')
text=index.read_text(encoding='utf-8')
old='''function refreshStartCategorySuggestion(){const f=document.getElementById('startForm'),select=document.getElementById('startDestination');if(!f||!select||!startDraft)return;const d=select.value==='__unknown__'?null:data.locations.find(x=>x.id===select.value)||null,s=suggestTripCategory(startDraft.origin,d,new Date());startDraft.categorySuggestion=s;const radio=f.querySelector(`[name="category"][value="${s.value}"]`);if(radio)radio.checked=true;const hint=document.getElementById('startTypeHint');if(hint)hint.textContent=`Voorstel: ${categoryLabel(s.value)} · ${s.reason}`}'''
new='''function refreshStartCategorySuggestion(){const f=document.getElementById('startForm'),select=document.getElementById('startDestination');if(!f||!select||!startDraft)return;const d=select.value==='__unknown__'?null:data.locations.find(x=>x.id===select.value)||null,s=suggestTripCategory(startDraft.origin,d,new Date());startDraft.categorySuggestion=s;f.querySelectorAll('.start-trip-type-grid .trip-type-option').forEach(x=>x.classList.toggle('suggested',x.dataset.category===s.value));const radio=f.querySelector(`[name="category"][value="${s.value}"]`);if(radio)radio.checked=true;const hint=document.getElementById('startTypeHint');if(hint)hint.textContent=`Voorstel: ${categoryLabel(s.value)} · ${s.reason}`}'''
if text.count(old)!=1:
    raise SystemExit(f'refresh function: expected 1 match, found {text.count(old)}')
text=text.replace(old,new,1)
index.write_text(text,encoding='utf-8')
html=index.read_text(encoding='utf-8')
start=html.index('<script>')+len('<script>')
end=html.index('</script>',start)
Path('/tmp/kmreg-app.js').write_text(html[start:end],encoding='utf-8')

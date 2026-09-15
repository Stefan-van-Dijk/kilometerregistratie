from pathlib import Path
p=Path('index.html')
s=p.read_text()
old_css=".screen-swipe-edge-cue{position:fixed;right:0;top:46%;z-index:8;width:10px;height:48px;border-radius:10px 0 0 10px;background:color-mix(in srgb,var(--accent) 44%,transparent);opacity:.45;pointer-events:none}.editor-view .screen-swipe-edge-cue,.has-active-trip .screen-swipe-edge-cue{opacity:.28}"
new_css=".screen-swipe-edge-cue{position:fixed;top:46%;z-index:8;width:10px;height:48px;background:color-mix(in srgb,var(--accent) 44%,transparent);opacity:.45;pointer-events:none}.screen-swipe-edge-cue.right{right:0;border-radius:10px 0 0 10px}.screen-swipe-edge-cue.left{left:0;border-radius:0 10px 10px 0}.editor-view .screen-swipe-edge-cue,.has-active-trip .screen-swipe-edge-cue{opacity:.28}"
if old_css not in s: raise SystemExit('cue css marker not found')
s=s.replace(old_css,new_css,1)
old_ref="screenShell=document.getElementById('screenShell'),screenSwipeBackdrop=document.getElementById('screenSwipeBackdrop'),printReportEl=document.getElementById('printReport');"
new_ref="screenShell=document.getElementById('screenShell'),screenSwipeBackdrop=document.getElementById('screenSwipeBackdrop'),screenSwipeEdgeCue=document.getElementById('screenSwipeEdgeCue'),printReportEl=document.getElementById('printReport');"
if old_ref not in s: raise SystemExit('cue ref marker not found')
s=s.replace(old_ref,new_ref,1)
old_func="topAction.setAttribute('aria-label',inSettings?'Terug naar ritten':'Instellingen')}"
new_func="topAction.setAttribute('aria-label',inSettings?'Terug naar ritten':'Instellingen');screenSwipeEdgeCue.className='screen-swipe-edge-cue '+(inSettings?'left':'right')}"
if old_func not in s: raise SystemExit('render quickbar marker not found')
s=s.replace(old_func,new_func,1)
p.write_text(s)

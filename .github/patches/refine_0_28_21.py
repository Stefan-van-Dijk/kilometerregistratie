from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="@media(max-width:430px){.home-priority.compact{grid-template-columns:minmax(0,1fr) auto auto;gap:5px}.home-priority.compact .home-priority-action{padding-left:8px;padding-right:8px}.home-priority-settings span{display:none}.home-priority-settings{width:40px;padding-left:6px;padding-right:6px;font-size:16px}}"
new="@media(max-width:430px){.home-priority.compact{grid-template-columns:minmax(0,1fr) auto auto;gap:5px}.home-priority.compact .home-priority-action{padding-left:8px;padding-right:8px}.home-priority.compact .home-priority-settings{width:40px;padding-left:6px;padding-right:6px;font-size:16px}}"
if old not in s: raise SystemExit('mobile settings css marker missing')
s=s.replace(old,new,1)
old2="if(!g.visualStarted){if(complete&&g.sourceView==='trip-edit'||complete&&g.sourceView==='location-edit')leaveEditor();return}"
new2="if(!g.visualStarted){if(complete&&(g.sourceView==='trip-edit'||g.sourceView==='location-edit'))leaveEditor();return}"
if old2 not in s: raise SystemExit('settle condition marker missing')
s=s.replace(old2,new2,1)
p.write_text(s)

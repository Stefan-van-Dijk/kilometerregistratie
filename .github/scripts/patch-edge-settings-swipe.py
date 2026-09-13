from pathlib import Path

index=Path('index.html')
text=index.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global text
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text=text.replace(old,new,1)

replace_once("+' · 0.28.0';","+' · 0.28.1';",'version')
replace_once("const KEY='kmreg-v4-data',GEOCODE_CACHE_KEY='kmreg-geocode-cache-v1',GEOCODER_DEFAULT_BASE='https://nominatim.openstreetmap.org';","const KEY='kmreg-v4-data',GEOCODE_CACHE_KEY='kmreg-geocode-cache-v1',GEOCODER_DEFAULT_BASE='https://nominatim.openstreetmap.org',SCREEN_EDGE_SWIPE_ZONE=32,SCREEN_EDGE_SWIPE_DISTANCE=72;",'edge swipe constants')
replace_once("settingsLocationCheck=0,geocodeQueue=Promise.resolve(),geocodeLastAt=0,expandedLocationId=null,settingsLocationsOpen=false,settingsLocationOriginId=null;","settingsLocationCheck=0,geocodeQueue=Promise.resolve(),geocodeLastAt=0,expandedLocationId=null,settingsLocationsOpen=false,settingsLocationOriginId=null,screenSwipe=null;",'edge swipe state')

old_events="""document.addEventListener('pointercancel',()=>{odoSwipe=null});
document.addEventListener('pointerdown',tripSwipeStart);
document.addEventListener('pointermove',tripSwipeMove);
document.addEventListener('pointerup',tripSwipeEnd);
document.addEventListener('pointercancel',tripSwipeCancel);"""
new_events="""document.addEventListener('pointercancel',()=>{odoSwipe=null});
document.addEventListener('pointerdown',screenSwipeStart);
document.addEventListener('pointermove',screenSwipeMove);
document.addEventListener('pointerup',screenSwipeEnd);
document.addEventListener('pointercancel',screenSwipeCancel);
document.addEventListener('pointerdown',tripSwipeStart);
document.addEventListener('pointermove',tripSwipeMove);
document.addEventListener('pointerup',tripSwipeEnd);
document.addEventListener('pointercancel',tripSwipeCancel);"""
replace_once(old_events,new_events,'edge swipe event listeners')

old_start="function tripSwipeStart(e){if(e.button!=null&&e.button!==0)return;if(e.target.closest('button'))return;const surface=e.target.closest('.swipe-surface');"
new_start="function tripSwipeStart(e){if(screenSwipe?.pointerId===e.pointerId)return;if(e.button!=null&&e.button!==0)return;if(e.target.closest('button'))return;const surface=e.target.closest('.swipe-surface');"
replace_once(old_start,new_start,'row swipe edge guard')

screen_funcs="""function screenSwipeStart(e){
if(e.button!=null&&e.button!==0)return;if(!modal.hidden)return;
const width=Math.max(document.documentElement.clientWidth||0,window.innerWidth||0),x=e.clientX;
const direction=view==='ride'&&x>=width-SCREEN_EDGE_SWIPE_ZONE?'left':view==='settings'&&x<=SCREEN_EDGE_SWIPE_ZONE?'right':null;
if(!direction)return;
const target=e.target instanceof Element?e.target:null;if(target?.closest('input,select,textarea,[contenteditable=\"true\"]'))return;
closeTripSwipes();screenSwipe={pointerId:e.pointerId,startX:x,startY:e.clientY,dx:0,dy:0,direction,horizontal:false,cancelled:false,target};
try{target?.setPointerCapture?.(e.pointerId)}catch(_){}
}
function screenSwipeMove(e){const g=screenSwipe;if(!g||g.pointerId!==e.pointerId||g.cancelled)return;const dx=e.clientX-g.startX,dy=e.clientY-g.startY;g.dx=dx;g.dy=dy;if(!g.horizontal){if(Math.abs(dy)>12&&Math.abs(dy)>Math.abs(dx)){g.cancelled=true;return}if(Math.abs(dx)>10&&Math.abs(dx)>Math.abs(dy)*1.15)g.horizontal=true;else return}const correct=g.direction==='left'?dx<0:dx>0;if(!correct){if(Math.abs(dx)>18)g.cancelled=true;return}if(e.cancelable)e.preventDefault()}
function screenSwipeEnd(e){const g=screenSwipe;if(!g||g.pointerId!==e.pointerId)return;screenSwipe=null;if(g.cancelled||!g.horizontal)return;const correct=g.direction==='left'?g.dx<=-SCREEN_EDGE_SWIPE_DISTANCE:g.dx>=SCREEN_EDGE_SWIPE_DISTANCE;if(!correct||Math.abs(g.dx)<Math.abs(g.dy)*1.2)return;if(g.direction==='left'&&view==='ride'){view='settings';render();return}if(g.direction==='right'&&view==='settings'){view='ride';render()}}
function screenSwipeCancel(){screenSwipe=null}

"""
replace_once('function tripSwipeStart(e){',screen_funcs+'function tripSwipeStart(e){','screen swipe functions')

index.write_text(text,encoding='utf-8')

sw=Path('service-worker.js')
s=sw.read_text(encoding='utf-8')
if s.count("kmreg-shell-0.28.0")!=1:
    raise SystemExit('service worker version mismatch')
s=s.replace("kmreg-shell-0.28.0","kmreg-shell-0.28.1",1)
sw.write_text(s,encoding='utf-8')

script=text.split('<script>',1)[1].rsplit('</script>',1)[0]
Path('/tmp/kmreg-app.js').write_text(script,encoding='utf-8')

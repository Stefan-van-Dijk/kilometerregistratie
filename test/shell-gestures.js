(function(){
  'use strict';

  const BUILD='0.31.10-test.37';
  const EDGE_START=44;
  const SWIPE_TRIGGER=54;
  const HORIZONTAL_RATIO=1.25;
  const TIME_FRAME_ID='timeAppFrame';

  let scrollLocked=false;
  let lockedScrollY=0;
  let savedBodyStyle=null;
  let savedHtmlOverflow='';
  let gesture=null;
  const boundDocuments=new WeakSet();

  const $=(selector,root=document)=>root.querySelector(selector);

  function drawerOpen(){
    return document.body.classList.contains('km-shell-drawer-open')&&$('#kmShellDrawer')?.classList.contains('open');
  }

  function blockedByOverlay(){
    return document.body.classList.contains('km-shell-settings-open')||
      document.body.classList.contains('editor-view')||
      document.body.classList.contains('km-shell-time-settings-open');
  }

  function updateVersion(){
    const version=$('.km-shell-version-number');
    const badge=$('.km-shell-version');
    const today=$('#today');
    if(version&&version.textContent!==BUILD)version.textContent=BUILD;
    if(badge)badge.setAttribute('aria-label',`Geladen testversie ${BUILD}`);
    if(today){
      const date=new Intl.DateTimeFormat('nl-NL',{weekday:'long',day:'numeric',month:'long'}).format(new Date());
      const value=`${date} · ${BUILD}`;
      if(today.textContent!==value)today.textContent=value;
    }
  }

  function lockMainScroll(){
    if(scrollLocked)return;
    scrollLocked=true;
    lockedScrollY=Math.max(0,window.scrollY||window.pageYOffset||0);
    savedHtmlOverflow=document.documentElement.style.overflow;
    savedBodyStyle={
      position:document.body.style.position,
      top:document.body.style.top,
      left:document.body.style.left,
      right:document.body.style.right,
      width:document.body.style.width,
      overflow:document.body.style.overflow
    };
    document.documentElement.style.overflow='hidden';
    Object.assign(document.body.style,{
      position:'fixed',
      top:`-${lockedScrollY}px`,
      left:'0',
      right:'0',
      width:'100%',
      overflow:'hidden'
    });
  }

  function unlockMainScroll(){
    if(!scrollLocked)return;
    scrollLocked=false;
    document.documentElement.style.overflow=savedHtmlOverflow;
    if(savedBodyStyle)Object.assign(document.body.style,savedBodyStyle);
    const y=lockedScrollY;
    savedBodyStyle=null;
    requestAnimationFrame(()=>window.scrollTo(0,y));
  }

  function syncDrawerScrollLock(){
    if(drawerOpen())lockMainScroll();
    else unlockMainScroll();
  }

  function requestOpenDrawer(){
    if(drawerOpen()||blockedByOverlay())return;
    $('#kmShellMenuButton')?.click();
  }

  function requestCloseDrawer(){
    if(!drawerOpen())return;
    const backdrop=$('#kmShellBackdrop');
    if(backdrop){backdrop.click();return;}
    $('#kmShellMenuButton')?.click();
  }

  function isInteractiveTarget(target){
    return Boolean(target?.closest?.('input,textarea,select,button,a,[contenteditable="true"],[data-module-drag-handle]'));
  }

  function touchPoint(event){
    return event.touches?.[0]||event.changedTouches?.[0]||null;
  }

  function beginGesture(event){
    if(event.touches?.length!==1||gesture)return;
    const point=touchPoint(event);
    if(!point)return;
    const open=drawerOpen();
    if(!open&&(blockedByOverlay()||point.clientX>EDGE_START))return;
    if(!open&&isInteractiveTarget(event.target))return;
    gesture={
      startX:point.clientX,
      startY:point.clientY,
      dx:0,
      dy:0,
      mode:open?'close':'open',
      horizontal:false,
      cancelled:false
    };
  }

  function moveGesture(event){
    if(!gesture)return;
    const point=touchPoint(event);
    if(!point)return;
    gesture.dx=point.clientX-gesture.startX;
    gesture.dy=point.clientY-gesture.startY;
    const ax=Math.abs(gesture.dx),ay=Math.abs(gesture.dy);
    if(!gesture.horizontal){
      if(ay>10&&ay>ax){gesture=null;return;}
      if(ax<10||ax<ay*HORIZONTAL_RATIO)return;
      gesture.horizontal=true;
    }
    const correctDirection=gesture.mode==='open'?gesture.dx>0:gesture.dx<0;
    if(correctDirection&&event.cancelable)event.preventDefault();
  }

  function endGesture(){
    if(!gesture)return;
    const current=gesture;
    gesture=null;
    if(!current.horizontal)return;
    if(current.mode==='open'&&current.dx>=SWIPE_TRIGGER&&Math.abs(current.dx)>=Math.abs(current.dy)*HORIZONTAL_RATIO){
      requestOpenDrawer();
      return;
    }
    if(current.mode==='close'&&current.dx<=-SWIPE_TRIGGER&&Math.abs(current.dx)>=Math.abs(current.dy)*HORIZONTAL_RATIO){
      requestCloseDrawer();
    }
  }

  function cancelGesture(){gesture=null;}

  function bindGestureDocument(doc){
    if(!doc||boundDocuments.has(doc))return;
    boundDocuments.add(doc);
    doc.addEventListener('touchstart',beginGesture,{passive:true});
    doc.addEventListener('touchmove',moveGesture,{passive:false});
    doc.addEventListener('touchend',endGesture,{passive:true});
    doc.addEventListener('touchcancel',cancelGesture,{passive:true});
  }

  function bindTimeFrame(){
    const frame=$(`#${TIME_FRAME_ID}`);
    if(!frame)return;
    const bind=()=>{
      try{bindGestureDocument(frame.contentDocument);}catch(_){}
    };
    if(frame.dataset.logShellGestureBound!=='1'){
      frame.dataset.logShellGestureBound='1';
      frame.addEventListener('load',()=>requestAnimationFrame(bind),{passive:true});
    }
    bind();
  }

  function init(){
    bindGestureDocument(document);
    bindTimeFrame();
    updateVersion();
    syncDrawerScrollLock();

    const observer=new MutationObserver(()=>{
      updateVersion();
      syncDrawerScrollLock();
      bindTimeFrame();
    });
    observer.observe(document.body,{attributes:true,attributeFilter:['class'],childList:true,subtree:false});

    document.addEventListener('click',()=>setTimeout(updateVersion,0),{passive:true});
    window.addEventListener('pageshow',()=>{
      updateVersion();
      syncDrawerScrollLock();
      bindTimeFrame();
    });
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();

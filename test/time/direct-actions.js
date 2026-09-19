(function(){
  'use strict';

  const EDIT_THRESHOLD=36;
  let gesture=null;

  const $=(selector,root=document)=>root.querySelector(selector);

  function actionWidth(){return innerWidth<=520?78:84;}

  function resetRow(row,surface){
    if(surface){
      surface.style.transition='transform .18s cubic-bezier(.2,.8,.2,1)';
      surface.style.transform='translateX(0)';
      delete surface.dataset.swipeOpen;
    }
    row?.classList.remove('swipe-open','delete-armed');
  }

  function pointerDown(event){
    if(event.button!=null&&event.button!==0)return;
    if(event.target.closest?.('button,input,select,textarea'))return;
    const surface=event.target.closest?.('.activity-swipe-surface');
    if(!surface)return;
    const row=surface.closest('.activity-swipe-row[data-id]');
    if(!row)return;
    const edit=$('[data-swipe-action="edit"]',row);
    const lifecycle=$('[data-swipe-action="delete"]',row);
    if(!edit&&!lifecycle)return;
    gesture={pointerId:event.pointerId,startX:event.clientX,startY:event.clientY,dx:0,dy:0,horizontal:false,cancelled:false,row,surface,edit,lifecycle};
  }

  function pointerMove(event){
    const g=gesture;
    if(!g||g.pointerId!==event.pointerId||g.cancelled)return;
    g.dx=event.clientX-g.startX;
    g.dy=event.clientY-g.startY;
    if(!g.horizontal){
      if(Math.abs(g.dy)>10&&Math.abs(g.dy)>Math.abs(g.dx)){g.cancelled=true;return;}
      if(Math.abs(g.dx)>8&&Math.abs(g.dx)>Math.abs(g.dy))g.horizontal=true;
    }
  }

  function pointerUp(event){
    const g=gesture;
    if(!g||g.pointerId!==event.pointerId)return;
    gesture=null;
    if(g.cancelled||!g.horizontal||g.dx>-EDIT_THRESHOLD||Math.abs(g.dx)<=Math.abs(g.dy))return;
    const distance=Math.abs(g.dx);
    const lifecycleThreshold=actionWidth()+EDIT_THRESHOLD;
    const action=g.lifecycle&&(!g.edit||distance>=lifecycleThreshold)?g.lifecycle:g.edit;
    if(!action)return;
    setTimeout(()=>{
      if(!action.isConnected)return;
      resetRow(g.row,g.surface);
      action.click();
    },0);
  }

  function pointerCancel(event){
    if(!gesture||gesture.pointerId!==event.pointerId)return;
    gesture=null;
  }

  function updateHint(){
    const hint=$('#swipeDeleteEnabled')?.closest('.settings-toggle-row')?.querySelector('small');
    const text='Swipe links: kort voor Bewerken, verder voor Archiveer/Verwijder. Verwijderen vraagt eerst bevestiging.';
    if(hint&&hint.textContent!==text)hint.textContent=text;
  }

  function init(){
    document.addEventListener('pointerdown',pointerDown,true);
    document.addEventListener('pointermove',pointerMove,true);
    document.addEventListener('pointerup',pointerUp,true);
    document.addEventListener('pointercancel',pointerCancel,true);
    updateHint();
    new MutationObserver(updateHint).observe(document.body,{childList:true,subtree:true});
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();

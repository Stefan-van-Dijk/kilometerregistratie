(function(){
  'use strict';

  const BUILD='0.31.10-test.58';
  const POSITIVE_SWIPE_THRESHOLD=36;
  let decorateQueued=false;
  let positiveSwipe=null;

  const $=(selector,root=document)=>root.querySelector(selector);
  const $$=(selector,root=document)=>[...root.querySelectorAll(selector)];

  function resetRow(row){
    const surface=$('.activity-swipe-surface',row);
    if(surface){
      surface.style.transition='transform .18s cubic-bezier(.2,.8,.2,1)';
      surface.style.transform='translateX(0)';
    }
    row?.classList.remove('swipe-open','delete-armed');
  }

  function ensureLeftGroup(row){
    let group=$('.activity-swipe-actions-left',row);
    if(group)return group;
    group=document.createElement('div');
    group.className='activity-swipe-actions activity-swipe-actions-left';
    group.style.setProperty('--activity-action-count','1');
    row.insertBefore(group,row.firstChild);
    return group;
  }

  function activeThemeFor(entry){
    if(!entry)return null;
    return state.themes.find(theme=>String(theme.id)===String(entry.themeId))||
      state.themes.find(theme=>String(theme.name||'').trim()===String(entry.themeName||'').trim())||null;
  }

  function positiveActionForRow(row){
    return $('[data-swipe-action="reopen"]',row)||$('[data-log-start-task]',row)||null;
  }

  function decorateTaskActions(){
    if(typeof state==='undefined')return;
    const inactive=state.timer?.status==='inactive';

    for(const row of $$('.activity-swipe-row[data-id]')){
      const id=String(row.dataset.id||'');
      const entry=state.entries.find(item=>String(item.id)===id);
      if(!entry||entry.activityType==='interruption')continue;

      const nativeResume=$('[data-swipe-action="reopen"]',row);
      const canResume=inactive&&state.lastCompletion?.type==='task'&&String(state.lastCompletion.entryId)===id;
      if(nativeResume){
        if(nativeResume.textContent!=='Hervatten')nativeResume.textContent='Hervatten';
        nativeResume.setAttribute('aria-label','Taak hervatten');
        nativeResume.title='Hervatten';
      }

      let start=$('[data-log-start-task]',row);
      const theme=activeThemeFor(entry);
      const canStart=inactive&&!canResume&&Boolean(theme);
      if(!canStart){
        start?.remove();
      }else{
        const group=ensureLeftGroup(row);
        if(!start){
          start=document.createElement('button');
          start.type='button';
          start.className='activity-swipe-action activity-swipe-reopen log-quick-start';
          start.dataset.logStartTask=id;
          start.textContent='Start';
          group.appendChild(start);
        }
        start.setAttribute('aria-label',`${entry.themeName||theme.name||'Taak'} starten`);
        start.title='Start';
      }

      const group=$('.activity-swipe-actions-left',row);
      if(group){
        const count=group.querySelectorAll('.activity-swipe-action').length;
        if(count)group.style.setProperty('--activity-action-count',String(count));
        else group.remove();
      }
    }
  }

  function startTask(id,button){
    if(typeof state==='undefined'||state.timer?.status!=='inactive')return;
    const entry=state.entries.find(item=>String(item.id)===String(id)&&item.activityType!=='interruption');
    const theme=activeThemeFor(entry);
    if(!entry||!theme||typeof startTimer!=='function')return;
    const sub=state.subthemes.find(item=>String(item.id)===String(entry.subthemeId))||null;
    resetRow(button.closest('.activity-swipe-row'));
    startTimer(theme,sub,entry.locationName||'','');
  }

  function positiveSwipeStart(event){
    if(event.button!=null&&event.button!==0)return;
    if(event.target.closest?.('button,input,select,textarea'))return;
    const surface=event.target.closest?.('.activity-swipe-surface');
    if(!surface)return;
    const row=surface.closest('.activity-swipe-row[data-id]');
    const action=positiveActionForRow(row);
    if(!row||!action)return;
    positiveSwipe={pointerId:event.pointerId,startX:event.clientX,startY:event.clientY,dx:0,dy:0,horizontal:false,cancelled:false,row,action};
  }

  function positiveSwipeMove(event){
    const gesture=positiveSwipe;
    if(!gesture||gesture.pointerId!==event.pointerId||gesture.cancelled)return;
    gesture.dx=event.clientX-gesture.startX;
    gesture.dy=event.clientY-gesture.startY;
    if(!gesture.horizontal){
      if(Math.abs(gesture.dy)>10&&Math.abs(gesture.dy)>Math.abs(gesture.dx)){gesture.cancelled=true;return;}
      if(Math.abs(gesture.dx)>8&&Math.abs(gesture.dx)>Math.abs(gesture.dy))gesture.horizontal=true;
    }
  }

  function positiveSwipeEnd(event){
    const gesture=positiveSwipe;
    if(!gesture||gesture.pointerId!==event.pointerId)return;
    positiveSwipe=null;
    if(gesture.cancelled||!gesture.horizontal)return;
    const activate=gesture.dx>=POSITIVE_SWIPE_THRESHOLD&&Math.abs(gesture.dx)>Math.abs(gesture.dy);
    if(!activate)return;
    const action=gesture.action;
    queueMicrotask(()=>{
      if(!action?.isConnected)return;
      resetRow(gesture.row);
      action.click();
    });
  }

  function positiveSwipeCancel(event){
    if(!positiveSwipe||positiveSwipe.pointerId!==event.pointerId)return;
    positiveSwipe=null;
  }

  function scheduleDecorate(){
    if(decorateQueued)return;
    decorateQueued=true;
    requestAnimationFrame(()=>{
      decorateQueued=false;
      decorateTaskActions();
    });
  }

  function init(){
    scheduleDecorate();
    document.addEventListener('click',event=>{
      const button=event.target.closest?.('[data-log-start-task]');
      if(!button)return;
      event.preventDefault();
      event.stopImmediatePropagation();
      startTask(button.dataset.logStartTask,button);
    },true);
    document.addEventListener('pointerdown',positiveSwipeStart,true);
    document.addEventListener('pointermove',positiveSwipeMove,true);
    document.addEventListener('pointerup',positiveSwipeEnd,true);
    document.addEventListener('pointercancel',positiveSwipeCancel,true);
    const main=$('#main');
    if(main)new MutationObserver(scheduleDecorate).observe(main,{childList:true,subtree:true});
    window.addEventListener('pageshow',scheduleDecorate);
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();

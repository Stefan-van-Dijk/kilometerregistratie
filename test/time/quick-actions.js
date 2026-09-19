(function(){
  'use strict';

  const BUILD='0.31.10-test.57';
  let decorateQueued=false;

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
    const main=$('#main');
    if(main)new MutationObserver(scheduleDecorate).observe(main,{childList:true,subtree:true});
    window.addEventListener('pageshow',scheduleDecorate);
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();

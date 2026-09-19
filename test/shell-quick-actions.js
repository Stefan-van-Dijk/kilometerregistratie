(function(){
  'use strict';

  const BUILD='0.31.10-test.57';
  const DATA_KEY='kmreg-test-v4-data';
  let decorateQueued=false;
  let busy=false;

  const $=(selector,root=document)=>root.querySelector(selector);
  const $$=(selector,root=document)=>[...root.querySelectorAll(selector)];

  function readData(){
    try{
      const value=JSON.parse(localStorage.getItem(DATA_KEY)||'{}');
      return value&&typeof value==='object'?value:{};
    }catch(_){return {};}
  }

  function sameLocation(a,b){
    if(!a||!b)return false;
    if(a.id&&b.id)return String(a.id)===String(b.id);
    const aa=String(a.address||'').trim().toLocaleLowerCase('nl-NL');
    const ba=String(b.address||'').trim().toLocaleLowerCase('nl-NL');
    if(aa&&ba)return aa===ba;
    if(a.lat!=null&&a.lng!=null&&b.lat!=null&&b.lng!=null){
      const dy=(Number(a.lat)-Number(b.lat))*111320;
      const dx=(Number(a.lng)-Number(b.lng))*111320*Math.cos(((Number(a.lat)+Number(b.lat))/2)*Math.PI/180);
      return Math.hypot(dx,dy)<150;
    }
    return false;
  }

  function currentKnownLocation(data){
    if(data.lastEndpoint?.location)return data.lastEndpoint.location;
    const trips=Array.isArray(data.trips)?data.trips:[];
    const latest=[...trips].filter(trip=>trip?.destination).sort((a,b)=>new Date(b.arrivalTime||b.departureTime||0)-new Date(a.arrivalTime||a.departureTime||0))[0];
    return latest?.destination||null;
  }

  function resetRow(row){
    const surface=$('.swipe-surface',row);
    if(surface){
      surface.style.transition='transform .18s cubic-bezier(.2,.8,.2,1)';
      surface.style.transform='translateX(0)';
      delete surface.dataset.swipeOpen;
    }
    row?.classList.remove('swipe-open','delete-armed');
  }

  function ensureLeftGroup(row){
    let group=$('.swipe-actions-left',row);
    if(group)return group;
    group=document.createElement('div');
    group.className='swipe-actions swipe-actions-left';
    row.insertBefore(group,row.firstChild);
    return group;
  }

  function routeCanStart(trip,data,origin){
    if(!trip||!origin||data.activeTrip)return false;
    if(!sameLocation(trip.origin,origin))return false;
    if(!trip.destination?.id)return false;
    return Array.isArray(data.locations)&&data.locations.some(location=>String(location.id)===String(trip.destination.id));
  }

  function decorateTripActions(){
    const data=readData();
    const trips=Array.isArray(data.trips)?data.trips:[];
    const byId=new Map(trips.map(trip=>[String(trip.id),trip]));
    const origin=currentKnownLocation(data);

    for(const row of $$('.swipe-row[data-swipe-kind="trip"]')){
      const id=String(row.dataset.id||'');
      const trip=byId.get(id);
      if(!trip)continue;

      const nativeResume=$('.swipe-actions-left [data-action="reopen-trip"]',row);
      const canResume=!data.activeTrip&&data.lastCompletion?.type==='trip'&&String(data.lastCompletion.tripId)===id;
      if(nativeResume){
        if(nativeResume.textContent!=='Hervatten')nativeResume.textContent='Hervatten';
        nativeResume.setAttribute('aria-label','Rit hervatten');
        nativeResume.title='Hervatten';
      }

      let start=$('[data-log-start-trip]',row);
      const canStart=!canResume&&routeCanStart(trip,data,origin);
      if(!canStart){
        start?.remove();
      }else{
        const group=ensureLeftGroup(row);
        if(!start){
          start=document.createElement('button');
          start.type='button';
          start.className='swipe-action trip-swipe-action swipe-reopen log-quick-start';
          start.dataset.logStartTrip=id;
          start.textContent='Start';
          group.appendChild(start);
        }
        start.setAttribute('aria-label',`Rit naar ${trip.destination?.name||'bestemming'} starten`);
        start.title='Start';
      }

      const group=$('.swipe-actions-left',row);
      if(group&&!group.querySelector('.swipe-action'))group.remove();
    }
  }

  function waitForStartForm(timeout=3500){
    return new Promise(resolve=>{
      const existing=$('#startForm');
      if(existing){resolve(existing);return;}
      const started=Date.now();
      const observer=new MutationObserver(()=>{
        const form=$('#startForm');
        if(form){observer.disconnect();resolve(form);return;}
        if(Date.now()-started>timeout){observer.disconnect();resolve(null);}
      });
      observer.observe(document.body,{childList:true,subtree:true});
      setTimeout(()=>{observer.disconnect();resolve($('#startForm'));},timeout);
    });
  }

  async function startHistoricalTrip(id,button){
    if(busy)return;
    busy=true;
    try{
      const data=readData();
      const trip=(Array.isArray(data.trips)?data.trips:[]).find(item=>String(item.id)===String(id));
      const origin=currentKnownLocation(data);
      if(!routeCanStart(trip,data,origin))return;

      resetRow(button.closest('.swipe-row'));
      const trigger=$('[data-action="start"]');
      if(!trigger)return;
      trigger.click();
      const form=await waitForStartForm();
      if(!form)return;

      const destination=$('#startDestination',form);
      if(!destination||![...destination.options].some(option=>String(option.value)===String(trip.destination.id))){
        $('[data-action="cancel-start"]')?.click();
        return;
      }
      destination.value=String(trip.destination.id);
      destination.dispatchEvent(new Event('change',{bubbles:true}));

      const category=form.querySelector(`[name="category"][value="${CSS.escape(String(trip.category||''))}"]`);
      if(category)category.checked=true;
      if(typeof form.requestSubmit==='function')form.requestSubmit();
      else form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
    }finally{
      setTimeout(()=>{busy=false;},250);
    }
  }

  function scheduleDecorate(){
    if(decorateQueued)return;
    decorateQueued=true;
    requestAnimationFrame(()=>{
      decorateQueued=false;
      decorateTripActions();
    });
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

  function init(){
    updateVersion();
    scheduleDecorate();
    document.addEventListener('click',event=>{
      const button=event.target.closest?.('[data-log-start-trip]');
      if(!button)return;
      event.preventDefault();
      event.stopImmediatePropagation();
      startHistoricalTrip(button.dataset.logStartTrip,button);
    },true);
    const app=$('#app');
    if(app)new MutationObserver(scheduleDecorate).observe(app,{childList:true,subtree:true});
    new MutationObserver(()=>{updateVersion();scheduleDecorate();}).observe(document.body,{attributes:true,attributeFilter:['class']});
    window.addEventListener('log-shell-view-refresh',scheduleDecorate);
    window.addEventListener('storage',event=>{if(event.key===DATA_KEY)scheduleDecorate();});
    window.addEventListener('pageshow',()=>{updateVersion();scheduleDecorate();});
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();

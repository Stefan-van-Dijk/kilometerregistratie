(function(){
  'use strict';

  const BUILD='0.31.10-test.48';
  const FRAME_ID='timeAppFrame';
  const boundDocuments=new WeakMap();
  let frameLoadBound=false;

  const $=(selector,root=document)=>root.querySelector(selector);

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

  function isMainEmbeddedTimeDocument(doc){
    try{
      const url=new URL(doc.defaultView.location.href);
      return url.searchParams.get('embedded')==='1'&&url.searchParams.get('instance')!=='settings';
    }catch(_){
      return false;
    }
  }

  function installSingleScrollStyle(doc){
    let style=doc.getElementById('kmLogSingleScrollStyle');
    if(style)return style;
    style=doc.createElement('style');
    style.id='kmLogSingleScrollStyle';
    style.textContent=`
      html,body{height:auto!important;min-height:0!important;overflow:hidden!important;overscroll-behavior:none!important}
      body{position:static!important}
      .app-shell{min-height:0!important}
    `;
    doc.head.appendChild(style);
    return style;
  }

  function contentHeight(doc){
    const app=doc.getElementById('app');
    const main=doc.getElementById('main');
    return Math.ceil(Math.max(
      app?.scrollHeight||0,
      app?.offsetHeight||0,
      main?.scrollHeight||0,
      doc.body?.scrollHeight||0,
      doc.body?.offsetHeight||0,
      doc.documentElement?.scrollHeight||0
    ));
  }

  function resizeTimeFrame(frame,doc){
    if(!frame||!doc?.body)return;
    const height=Math.max(1,contentHeight(doc));
    const current=parseFloat(frame.style.height)||frame.getBoundingClientRect().height||0;
    if(Math.abs(current-height)>1)frame.style.height=`${height}px`;
  }

  function bindDocument(frame,doc){
    if(!doc?.head||!doc.body||!isMainEmbeddedTimeDocument(doc))return;

    installSingleScrollStyle(doc);
    frame.setAttribute('scrolling','no');
    frame.style.setProperty('display','block');
    frame.style.setProperty('width','100%');
    frame.style.setProperty('max-width','100%');
    frame.style.setProperty('overflow','hidden');
    frame.style.setProperty('border','0');

    const schedule=()=>requestAnimationFrame(()=>resizeTimeFrame(frame,doc));
    const existing=boundDocuments.get(doc);
    if(existing){
      schedule();
      return;
    }

    const resizeObserver=new ResizeObserver(schedule);
    const app=doc.getElementById('app');
    resizeObserver.observe(doc.body);
    if(app)resizeObserver.observe(app);

    const mutationObserver=new MutationObserver(schedule);
    mutationObserver.observe(doc.body,{
      childList:true,
      subtree:true,
      attributes:true,
      characterData:true
    });

    doc.defaultView?.addEventListener('resize',schedule,{passive:true});
    doc.addEventListener('transitionend',schedule,{passive:true});
    doc.addEventListener('animationend',schedule,{passive:true});
    doc.addEventListener('load',schedule,true);

    boundDocuments.set(doc,{resizeObserver,mutationObserver,schedule});
    try{doc.scrollingElement?.scrollTo(0,0);}catch(_){}
    schedule();
    setTimeout(schedule,80);
    setTimeout(schedule,300);
  }

  function bindTimeFrame(){
    const frame=$(`#${FRAME_ID}`);
    if(!frame)return;
    const bind=()=>{
      try{bindDocument(frame,frame.contentDocument);}catch(error){console.warn('Tijdmodule kon niet aan de paginascroll worden gekoppeld.',error);}
    };
    if(!frameLoadBound){
      frameLoadBound=true;
      frame.addEventListener('load',()=>requestAnimationFrame(bind),{passive:true});
    }
    bind();
  }

  function init(){
    updateVersion();
    bindTimeFrame();

    const bodyObserver=new MutationObserver(()=>{
      updateVersion();
      bindTimeFrame();
    });
    bodyObserver.observe(document.body,{attributes:true,attributeFilter:['class'],childList:true,subtree:false});

    window.addEventListener('pageshow',()=>{
      updateVersion();
      bindTimeFrame();
    });
    window.addEventListener('resize',()=>{
      const frame=$(`#${FRAME_ID}`);
      try{
        const doc=frame?.contentDocument;
        if(frame&&doc)boundDocuments.get(doc)?.schedule?.();
      }catch(_){}
    },{passive:true});
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();

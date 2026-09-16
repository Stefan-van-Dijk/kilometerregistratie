(function(){
  'use strict';

  const VERSION='0.31.2';

  function settingsOpen(){
    return document.getElementById('kmShellSettings')?.classList.contains('open');
  }

  function unlockPageScroll(){
    if(settingsOpen()) return;
    document.documentElement.style.overflowY='auto';
    document.documentElement.style.touchAction='pan-y';
    document.body.style.overflow='';
    document.body.style.overflowY='auto';
    document.body.style.touchAction='pan-y';
    document.body.style.webkitOverflowScrolling='touch';
  }

  function installOuterCss(){
    if(document.getElementById('km-scroll-hotfix-style')) return;
    const style=document.createElement('style');
    style.id='km-scroll-hotfix-style';
    style.textContent=`
      html,body{min-height:100%;}
      body:not(.km-shell-settings-open){overflow-y:auto;touch-action:pan-y;-webkit-overflow-scrolling:touch;}
      body.time-mode .time-app-frame{
        height:calc(100dvh - env(safe-area-inset-top))!important;
        min-height:460px!important;
        margin-top:0!important;
        overflow:auto!important;
        touch-action:pan-y!important;
        -webkit-overflow-scrolling:touch!important;
      }
    `;
    document.head.appendChild(style);
  }

  function fixTimeFrame(){
    const frame=document.getElementById('timeAppFrame');
    if(!frame) return;
    frame.setAttribute('scrolling','yes');
    frame.style.overflow='auto';
    frame.style.touchAction='pan-y';
    frame.style.webkitOverflowScrolling='touch';

    const apply=()=>{
      try{
        const doc=frame.contentDocument;
        if(!doc?.head) return;
        let style=doc.getElementById('km-scroll-hotfix-inner');
        if(!style){
          style=doc.createElement('style');
          style.id='km-scroll-hotfix-inner';
          style.textContent=`
            html,body{
              height:auto!important;
              min-height:100%!important;
              overflow-x:hidden!important;
              overflow-y:auto!important;
              touch-action:pan-y!important;
              -webkit-overflow-scrolling:touch!important;
              position:static!important;
            }
            .app-shell{
              min-height:100%!important;
              overflow:visible!important;
              touch-action:pan-y!important;
            }
          `;
          doc.head.appendChild(style);
        }
        doc.documentElement.style.overflowY='auto';
        doc.body.style.overflowY='auto';
        doc.documentElement.style.touchAction='pan-y';
        doc.body.style.touchAction='pan-y';
      }catch(error){
        console.warn('Scrollherstel voor tijdweergave kon niet worden toegepast.',error);
      }
    };

    if(frame.dataset.kmScrollHotfixBound!=='1'){
      frame.dataset.kmScrollHotfixBound='1';
      frame.addEventListener('load',()=>requestAnimationFrame(()=>{apply();setTimeout(apply,100);}),{passive:true});
    }
    apply();
    setTimeout(apply,120);
  }

  function syncSettingsLock(){
    const open=settingsOpen();
    document.body.classList.toggle('km-shell-settings-open',!!open);
    if(!open) unlockPageScroll();
  }

  function updateVersion(){
    const today=document.getElementById('today');
    if(!today) return;
    const text=today.textContent||'';
    today.textContent=text.replace(/0\.31\.1\b/g,VERSION);
  }

  function apply(){
    installOuterCss();
    syncSettingsLock();
    fixTimeFrame();
    updateVersion();
  }

  function init(){
    apply();
    setTimeout(apply,100);
    setTimeout(apply,500);
    document.addEventListener('click',()=>setTimeout(apply,0),{passive:true});
    const settings=document.getElementById('kmShellSettings');
    if(settings){
      new MutationObserver(syncSettingsLock).observe(settings,{attributes:true,attributeFilter:['class']});
    }
    const bodyObserver=new MutationObserver(()=>{
      syncSettingsLock();
      fixTimeFrame();
    });
    bodyObserver.observe(document.body,{attributes:true,attributeFilter:['class']});
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();

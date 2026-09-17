(function () {
  'use strict';

  const BUILD = '0.31.10';
  const DATA_KEY = 'kmreg-test-v4-data';
  const MODE_KEY = 'kmreg-test-active-app-v1';
  const SECTION_KEY = 'kmreg-test-shell-section-v1';
  const DRAWER_KEY = 'kmreg-test-shell-drawer-v1';
  const ROOT_SECTIONS = new Set(['rides', 'time', 'locations']);

  let section = localStorage.getItem(SECTION_KEY);
  if (!ROOT_SECTIONS.has(section)) section = localStorage.getItem(MODE_KEY) === 'time' ? 'time' : 'rides';
  let drawerOpen = false;
  let expandedLocationId = null;
  let pendingParentForNew = null;
  let pendingParentSave = null;
  let pendingHierarchyReload = false;
  let kmSettingsMounted = false;
  let timeFramePlaceholder = null;
  let kmAppPlaceholder = null;
  let lastEditorState = document.body.classList.contains('editor-view');
  let timeFrameOriginalParent = null;
  let timeFrameOriginalNext = null;
  let locationEditorAugmentQueued = false;
  let timeSettingsOpen = false;

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));

  function readData() {
    try {
      const parsed = JSON.parse(localStorage.getItem(DATA_KEY) || '{}');
      return {
        settings: parsed.settings && typeof parsed.settings === 'object' ? parsed.settings : {},
        locations: Array.isArray(parsed.locations) ? parsed.locations : [],
        trips: Array.isArray(parsed.trips) ? parsed.trips : [],
        events: Array.isArray(parsed.events) ? parsed.events : []
      };
    } catch (_) {
      return { settings: {}, locations: [], trips: [], events: [] };
    }
  }

  function locationById(id, snapshot = readData()) {
    return snapshot.locations.find(location => location.id === id) || null;
  }

  function typeLabel(type) {
    return ({ home: 'Thuis', work: 'Werk', business: 'Zakelijk', private: 'Privé', other: 'Overig' })[type] || 'Overig';
  }

  function locationGlyph(type) {
    return ({ home: '⌂', work: '▣', business: '▦', private: '●', other: '⌖' })[type] || '⌖';
  }

  function effectiveLocation(location, snapshot = readData()) {
    const parent = location?.parentId ? locationById(location.parentId, snapshot) : null;
    return {
      address: location?.address || parent?.address || '',
      lat: location?.lat ?? parent?.lat ?? null,
      lng: location?.lng ?? parent?.lng ?? null,
      parent
    };
  }

  function injectStyles() {
    if ($('#kmregShellStyles')) return;
    const style = document.createElement('style');
    style.id = 'kmregShellStyles';
    style.textContent = `
      .km-shell-top{display:grid!important;grid-template-columns:42px minmax(0,1fr) 42px;align-items:center!important;gap:8px;padding:12px 0 14px!important}
      .km-shell-menu-button,.km-shell-top-spacer{width:40px;height:40px}
      .km-shell-menu-button{position:fixed;z-index:92;top:calc(env(safe-area-inset-top) + 10px);left:max(12px,calc((100vw - 760px)/2 + 12px));display:inline-flex;align-items:center;justify-content:center;border:0;border-radius:12px;background:transparent;color:var(--text);font-size:24px;line-height:1;cursor:pointer;touch-action:manipulation}
      .km-shell-menu-button:active{background:var(--card2)}
      .km-shell-top-copy{text-align:center;overflow:hidden}.km-shell-top-copy .eyebrow{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.km-shell-title{margin-top:3px;font-size:20px;font-weight:850;letter-spacing:-.025em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.km-shell-meta{margin-top:3px;color:var(--muted);font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
      .km-shell-legacy{position:absolute!important;width:1px!important;height:1px!important;overflow:hidden!important;clip:rect(0 0 0 0)!important;clip-path:inset(50%)!important;white-space:nowrap!important}
      .km-shell-backdrop{position:fixed;z-index:95;inset:0;background:rgba(0,0,0,.42);opacity:0;pointer-events:none;transition:opacity .22s ease}
      .km-shell-backdrop.open{opacity:1;pointer-events:auto}
      .km-shell-drawer{position:fixed;z-index:100;inset:0 auto 0 0;width:min(82vw,330px);display:flex;flex-direction:column;padding:calc(18px + env(safe-area-inset-top)) 14px calc(12px + env(safe-area-inset-bottom));border-right:1px solid var(--line);background:rgba(17,21,26,.97);box-shadow:18px 0 52px rgba(0,0,0,.34);transform:translateX(-102%);transition:transform .24s cubic-bezier(.2,.8,.2,1);-webkit-backdrop-filter:blur(26px) saturate(165%);backdrop-filter:blur(26px) saturate(165%)}
      .km-shell-drawer.open{transform:translateX(0)}
      .km-shell-drawer-head{padding:4px 8px 17px}.km-shell-drawer-head strong{display:block;font-size:19px;letter-spacing:-.02em}.km-shell-drawer-head small{display:block;margin-top:4px;color:var(--muted);font-size:11px}
      .km-shell-nav{display:grid;gap:4px}.km-shell-nav-button{display:flex;align-items:center;gap:12px;width:100%;min-height:48px;padding:9px 11px;border:0;border-radius:12px;background:transparent;color:var(--text);font-weight:760;text-align:left;cursor:pointer}.km-shell-nav-button .icon{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border:1px solid var(--line);border-radius:9px;color:var(--muted);font-size:15px}.km-shell-nav-button.active{background:var(--card2)}.km-shell-nav-button.active .icon{border-color:rgba(77,163,255,.45);color:var(--accent);background:rgba(77,163,255,.09)}
      .km-shell-drawer-spacer{flex:1}.km-shell-drawer-footer{display:flex;justify-content:flex-end;padding:10px 4px 2px;border-top:1px solid var(--line)}.km-shell-settings-button{display:inline-flex;align-items:center;justify-content:center;width:46px;height:46px;border:0;border-radius:14px;background:transparent;color:var(--text);font-size:23px;cursor:pointer}.km-shell-settings-button:active{background:var(--card2)}
      .km-shell-settings{position:fixed;z-index:120;inset:0;display:flex;align-items:flex-end;justify-content:center;background:rgba(0,0,0,.38);opacity:0;pointer-events:none;transition:opacity .22s ease}.km-shell-settings.open{opacity:1;pointer-events:auto}
      .km-shell-settings-surface{width:100%;height:min(94dvh,900px);display:flex;flex-direction:column;border-radius:24px 24px 0 0;border:1px solid var(--line);border-bottom:0;background:var(--bg);box-shadow:0 -18px 52px rgba(0,0,0,.34);transform:translateY(104%);transition:transform .46s cubic-bezier(.22,1,.36,1);overflow:hidden;will-change:transform}.km-shell-settings.open .km-shell-settings-surface{transform:translateY(0)}
      .km-shell-settings-head{position:relative;display:grid;grid-template-columns:42px 1fr 42px;align-items:center;gap:8px;flex:0 0 auto;padding:calc(10px + env(safe-area-inset-top)) 14px 10px;border-bottom:1px solid var(--line);background:rgba(13,17,23,.92);-webkit-backdrop-filter:blur(22px) saturate(165%);backdrop-filter:blur(22px) saturate(165%)}.km-shell-settings-title{text-align:center;font-size:16px;font-weight:850}.km-shell-settings-close{position:absolute;right:14px;top:calc(10px + env(safe-area-inset-top));display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;border:0;border-radius:50%;background:var(--card2);color:var(--text);font-size:25px;cursor:pointer}.km-shell-settings-content{position:relative;flex:1;min-height:0;overflow:auto;padding:8px 16px calc(24px + env(safe-area-inset-bottom))}.km-shell-settings-content>#app{display:block!important;max-width:760px;margin:0 auto}.km-shell-settings-content .time-app-frame{display:block!important;width:100%;height:100%!important;min-height:0!important;opacity:1!important}
      .km-shell-settings-back{position:absolute;left:14px;top:calc(10px + env(safe-area-inset-top));display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;border:0;border-radius:50%;background:transparent;color:var(--accent);font-size:22px;font-weight:800;cursor:pointer}.km-shell-settings-back[hidden]{display:none!important}.km-shell-settings-back:active{background:var(--card2)}
      .km-shell-general-settings{max-width:760px;margin:0 auto;padding:8px 0 24px}.km-shell-general-intro{padding:8px 1px 16px;border-bottom:1px solid var(--line)}.km-shell-general-intro h2{margin:3px 0 5px;font-size:28px;letter-spacing:-.035em}.km-shell-general-intro p{margin:0;color:var(--muted);font-size:12px;line-height:1.45}
      .km-shell-general-card{padding:17px 1px;border-bottom:1px solid var(--line)}.km-shell-general-card>strong,.km-shell-general-card>small{display:block}.km-shell-general-card>strong{font-size:17px}.km-shell-general-card>small{margin-top:4px;color:var(--muted);font-size:11px;line-height:1.4}.km-shell-general-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:13px}.km-shell-general-actions .btn{width:100%;margin:0;text-align:center}.km-shell-general-nav{display:grid;gap:2px;margin-top:10px}.km-shell-general-nav button{display:flex;align-items:center;justify-content:space-between;width:100%;min-height:48px;padding:10px 1px;border:0;border-bottom:1px solid var(--line);background:transparent;color:var(--text);font-weight:760;text-align:left}.km-shell-general-nav button span:last-child{color:var(--muted);font-size:21px}.km-shell-general-advanced{margin-top:12px}.km-shell-general-advanced summary{color:var(--muted);font-size:12px;font-weight:750;cursor:pointer}.km-shell-general-status{margin-top:8px;color:var(--muted);font-size:11px;line-height:1.4}
      @keyframes kmSettingsForwardIn{from{opacity:.35;transform:translateX(24px)}to{opacity:1;transform:translateX(0)}}@keyframes kmSettingsBackIn{from{opacity:.35;transform:translateX(-24px)}to{opacity:1;transform:translateX(0)}}@keyframes kmPageForwardIn{from{opacity:.72;transform:translateX(22px)}to{opacity:1;transform:translateX(0)}}@keyframes kmPageBackIn{from{opacity:.72;transform:translateX(-22px)}to{opacity:1;transform:translateX(0)}}
      .km-shell-settings-content.km-settings-forward-in>*{animation:kmSettingsForwardIn .24s cubic-bezier(.22,1,.36,1) both}.km-shell-settings-content.km-settings-back-in>*{animation:kmSettingsBackIn .24s cubic-bezier(.22,1,.36,1) both}
      body.km-shell-page-forward .shell{animation:kmPageForwardIn .24s cubic-bezier(.22,1,.36,1) both}body.km-shell-page-back .shell{animation:kmPageBackIn .24s cubic-bezier(.22,1,.36,1) both}
      @media(max-width:480px){.km-shell-general-actions{grid-template-columns:1fr}}
      .shell>#timeAppFrame{position:relative;z-index:0}.km-shell-drawer-open .shell>#timeAppFrame{visibility:hidden!important;pointer-events:none!important}.editor-view>.km-shell-menu-button{display:none!important}
      .km-shell-locations{padding:2px 0 28px}.km-shell-locations-head{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;padding:8px 1px 10px}.km-shell-locations-head h2{margin:2px 0 0;font-size:28px;letter-spacing:-.035em}.km-shell-location-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:5px 0 16px}.km-shell-location-actions button{min-height:44px}
      .km-shell-location-sort{display:grid;grid-template-columns:1fr 1fr;gap:5px;padding:4px;margin-bottom:8px;border:1px solid var(--line);border-radius:12px;background:var(--card)}.km-shell-location-sort button{min-height:34px;border:0;border-radius:8px;background:transparent;color:var(--muted);font-size:11px;font-weight:800}.km-shell-location-sort button.active{background:var(--card2);color:var(--text)}
      .km-shell-location-tree{border-top:1px solid var(--line)}.km-shell-location-node{--depth:0;margin-left:calc(var(--depth) * 20px)}.km-shell-location-row{display:grid;grid-template-columns:28px minmax(0,1fr) auto;align-items:center;gap:9px;min-height:58px;padding:10px 2px;border-bottom:1px solid var(--line)}.km-shell-location-node[data-depth="1"] .km-shell-location-row{position:relative}.km-shell-location-node[data-depth="1"] .km-shell-location-row::before{content:"";position:absolute;left:-12px;top:0;bottom:50%;width:9px;border-left:1px solid var(--line);border-bottom:1px solid var(--line);border-radius:0 0 0 6px}.km-shell-location-icon{display:flex;align-items:center;justify-content:center;width:27px;height:27px;border:1px solid var(--line);border-radius:9px;color:var(--muted);font-size:15px}.km-shell-location-copy{min-width:0}.km-shell-location-copy strong,.km-shell-location-copy small{display:block}.km-shell-location-copy strong{font-size:14px}.km-shell-location-copy small{margin-top:3px;color:var(--muted);font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.km-shell-location-buttons{display:flex;align-items:center;gap:3px}.km-shell-location-buttons button{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;padding:0;border:0;border-radius:9px;background:transparent;color:var(--muted);font-size:19px}.km-shell-location-buttons button:active{background:var(--card2);color:var(--text)}.km-shell-location-chevron{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;color:var(--muted);font-size:19px}.km-shell-location-details{padding:10px 2px 12px 37px;border-bottom:1px solid var(--line);color:var(--muted);font-size:11px;line-height:1.5}.km-shell-location-detail-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.km-shell-location-detail{padding:8px 0}.km-shell-location-detail span,.km-shell-location-detail strong{display:block}.km-shell-location-detail span{font-size:9px;text-transform:uppercase;letter-spacing:.06em}.km-shell-location-detail strong{margin-top:2px;color:var(--text);font-size:11px}.km-shell-child-add{margin-top:7px;padding:4px 0;border:0;background:transparent;color:var(--accent);font-size:11px;font-weight:800}.km-shell-empty{padding:24px 2px;color:var(--muted);font-size:13px}
      .km-shell-parent-section select{width:100%;min-height:38px;padding:6px 0 7px;border:0;border-bottom:1px solid var(--line);border-radius:0;background:transparent;color:var(--text);font-size:15px;outline:none}.km-shell-parent-hint{margin-top:6px;color:var(--muted);font-size:10px;line-height:1.4}
      body.km-shell-locations-mode #app,body.km-shell-locations-mode #timeAppFrame{display:none!important}body.km-shell-locations-mode #kmShellLocationsView{display:block!important}
      body.editor-view #kmShellLocationsView{display:none!important}
      @media(prefers-color-scheme:light){.km-shell-drawer{background:rgba(255,255,255,.97);box-shadow:18px 0 52px rgba(30,45,65,.16)}.km-shell-settings-head{background:rgba(245,245,247,.93)}.km-shell-backdrop{background:rgba(0,0,0,.22)}.km-shell-settings{background:rgba(0,0,0,.22)}}
      @media(max-width:480px){.km-shell-drawer{width:min(86vw,330px)}.km-shell-settings-surface{height:96dvh;border-radius:21px 21px 0 0}.km-shell-settings-content{padding-left:12px;padding-right:12px}.km-shell-location-detail-grid{grid-template-columns:1fr}.km-shell-location-actions{grid-template-columns:1fr 1fr}}
      @media(prefers-reduced-motion:reduce){.km-shell-drawer,.km-shell-backdrop,.km-shell-settings,.km-shell-settings-surface{transition:none!important}.km-shell-settings-content>*,body.km-shell-page-forward .shell,body.km-shell-page-back .shell{animation:none!important}}
    `;
    document.head.appendChild(style);
  }

  function installChrome() {
    const top = $('.top');
    if (!top || $('#kmShellMenuButton')) return;

    const today = $('#today');
    const legacyMode = $('#appModeToggle');
    const legacyAction = $('#topAction');
    const legacyMeta = $('#appModeMeta');

    const menu = document.createElement('button');
    menu.id = 'kmShellMenuButton';
    menu.className = 'km-shell-menu-button';
    menu.type = 'button';
    menu.setAttribute('aria-label', 'Menu openen');
    menu.setAttribute('aria-controls', 'kmShellDrawer');
    menu.setAttribute('aria-expanded', 'false');
    menu.textContent = '☰';

    const copy = document.createElement('div');
    copy.className = 'km-shell-top-copy';
    if (today) copy.appendChild(today);
    const title = document.createElement('div');
    title.id = 'kmShellTitle';
    title.className = 'km-shell-title';
    copy.appendChild(title);
    const meta = document.createElement('div');
    meta.id = 'kmShellMeta';
    meta.className = 'km-shell-meta';
    copy.appendChild(meta);

    const spacer = document.createElement('span');
    spacer.className = 'km-shell-top-spacer';
    const legacy = document.createElement('div');
    legacy.className = 'km-shell-legacy';
    if (legacyMode) legacy.appendChild(legacyMode);
    if (legacyAction) legacy.appendChild(legacyAction);
    if (legacyMeta) legacy.appendChild(legacyMeta);

    const menuSlot = document.createElement('span');
    menuSlot.className = 'km-shell-top-spacer';
    menuSlot.setAttribute('aria-hidden', 'true');
    top.innerHTML = '';
    top.classList.add('km-shell-top');
    top.append(menuSlot, copy, spacer, legacy);
    document.body.appendChild(menu);
    menu.addEventListener('click', () => {
      if (section === 'time' && timeSettingsOpen) closeTimeSettingsPage();
      else openDrawer();
    });

    if (today) {
      today.textContent = new Intl.DateTimeFormat('nl-NL', { weekday: 'long', day: 'numeric', month: 'long' }).format(new Date()) + ' · ' + BUILD;
    }
  }

  function installShellElements() {
    if ($('#kmShellDrawer')) return;

    const backdrop = document.createElement('div');
    backdrop.id = 'kmShellBackdrop';
    backdrop.className = 'km-shell-backdrop';
    backdrop.addEventListener('click', closeDrawer);

    const drawer = document.createElement('aside');
    drawer.id = 'kmShellDrawer';
    drawer.className = 'km-shell-drawer';
    drawer.setAttribute('aria-label', 'Navigatie');
    drawer.innerHTML = `
      <div class="km-shell-drawer-head"><strong>Registratie</strong><small>Ritten, tijd en plaatsen in één app</small></div>
      <nav class="km-shell-nav">
        <button class="km-shell-nav-button" type="button" data-shell-section="rides"><span class="icon">↗</span><span>Ritten</span></button>
        <button class="km-shell-nav-button" type="button" data-shell-section="time"><span class="icon">◷</span><span>Tijd / taken</span></button>
        <button class="km-shell-nav-button" type="button" data-shell-section="locations"><span class="icon">⌖</span><span>Locaties</span></button>
      </nav>
      <div class="km-shell-drawer-spacer"></div>
      <div class="km-shell-drawer-footer"><button id="kmShellSettingsButton" class="km-shell-settings-button" type="button" aria-label="Instellingen">⚙︎</button></div>`;

    drawer.addEventListener('click', event => {
      const button = event.target.closest('[data-shell-section]');
      if (button) selectSection(button.dataset.shellSection);
    });
    $('#kmShellSettingsButton', drawer).addEventListener('click', openSettingsSheet);

    const settings = document.createElement('div');
    settings.id = 'kmShellSettings';
    settings.className = 'km-shell-settings';
    settings.innerHTML = `
      <section class="km-shell-settings-surface" role="dialog" aria-modal="true" aria-labelledby="kmShellSettingsTitle">
        <header class="km-shell-settings-head"><button id="kmShellSettingsBack" class="km-shell-settings-back" type="button" aria-label="Terug naar algemene instellingen" hidden>←</button><div id="kmShellSettingsTitle" class="km-shell-settings-title">Algemene instellingen</div><button id="kmShellSettingsClose" class="km-shell-settings-close" type="button" aria-label="Instellingen sluiten">×</button></header>
        <div id="kmShellSettingsContent" class="km-shell-settings-content"></div>
      </section>`;
    $('#kmShellSettingsClose', settings).addEventListener('click', closeSettingsSheet);
    $('#kmShellSettingsBack', settings).addEventListener('click', () => {
      if ($('#kmShellSettingsContent > #timeAppFrame')) restoreTimeFrame();
      if (kmSettingsMounted) restoreKmApp();
      renderGeneralSettings();
      animateSettingsContent('back');
    });

    const locationsView = document.createElement('main');
    locationsView.id = 'kmShellLocationsView';
    locationsView.className = 'km-shell-locations';
    locationsView.hidden = true;
    const shell = $('.shell');
    if (shell) shell.appendChild(locationsView);

    document.body.append(backdrop, drawer, settings);
  }

  function openDrawer() {
    if ($('#kmShellSettings')?.classList.contains('open')) return;
    drawerOpen = true;
    localStorage.setItem(DRAWER_KEY, '1');
    document.body.classList.add('km-shell-drawer-open');
    $('#kmShellMenuButton')?.setAttribute('aria-expanded', 'true');
    $('#kmShellDrawer')?.classList.add('open');
    $('#kmShellBackdrop')?.classList.add('open');
    syncDrawerSelection();
  }

  function closeDrawer() {
    drawerOpen = false;
    localStorage.removeItem(DRAWER_KEY);
    document.body.classList.remove('km-shell-drawer-open');
    $('#kmShellMenuButton')?.setAttribute('aria-expanded', 'false');
    $('#kmShellDrawer')?.classList.remove('open');
    $('#kmShellBackdrop')?.classList.remove('open');
  }

  function syncDrawerSelection() {
    $$('.km-shell-nav-button').forEach(button => button.classList.toggle('active', button.dataset.shellSection === section));
  }

  function originalIsTimeMode() {
    return document.body.classList.contains('time-mode');
  }

  function ensureOriginalMode(mode) {
    const wantTime = mode === 'time';
    if (originalIsTimeMode() === wantTime) return;
    const toggle = $('#appModeToggle');
    if (toggle) toggle.click();
  }

  function ensureKmView(wanted) {
    const topAction = $('#topAction');
    if (!topAction) return false;
    const current = topAction.dataset.action === 'home' ? 'settings' : 'ride';
    if (current !== wanted) topAction.click();
    return (topAction.dataset.action === 'home' ? 'settings' : 'ride') === wanted;
  }

  function selectSection(next) {
    if (!ROOT_SECTIONS.has(next)) return;
    section = next;
    localStorage.setItem(SECTION_KEY, section);
    localStorage.setItem(MODE_KEY, section === 'time' ? 'time' : 'kilometers');
    if (section === 'time') ensureOriginalMode('time');
    else {
      ensureOriginalMode('kilometers');
      if (!document.body.classList.contains('editor-view')) ensureKmView('ride');
    }
    closeDrawer();
    showSection();
  }

  function showSection() {
    if (document.body.classList.contains('editor-view')) {
      document.body.classList.remove('km-shell-locations-mode');
      const locations = $('#kmShellLocationsView');
      if (locations) locations.hidden = true;
      syncChrome();
      return;
    }

    if (section === 'locations') {
      ensureOriginalMode('kilometers');
      ensureKmView('ride');
      document.body.classList.add('km-shell-locations-mode');
      const locations = $('#kmShellLocationsView');
      if (locations) locations.hidden = false;
      renderLocations();
    } else {
      document.body.classList.remove('km-shell-locations-mode');
      const locations = $('#kmShellLocationsView');
      if (locations) locations.hidden = true;
      ensureOriginalMode(section === 'time' ? 'time' : 'kilometers');
      if (section === 'rides') ensureKmView('ride');
    }
    syncChrome();
  }

  function syncChrome() {
    const title = $('#kmShellTitle');
    const meta = $('#kmShellMeta');
    const menu = $('#kmShellMenuButton');
    const labels = { rides: 'Ritten', time: 'Tijd / taken', locations: 'Locaties' };
    const wantedTitle = section === 'time' && timeSettingsOpen ? 'Instellingen' : (labels[section] || 'Registratie');
    if (title && title.textContent !== wantedTitle) title.textContent = wantedTitle;
    if (menu) {
      const isBack = section === 'time' && timeSettingsOpen;
      const wantedIcon = isBack ? '←' : '☰';
      const wantedLabel = isBack ? 'Terug naar tijd / taken' : 'Menu openen';
      const wantedExpanded = isBack ? 'false' : String(drawerOpen);
      if (menu.textContent !== wantedIcon) menu.textContent = wantedIcon;
      if (menu.getAttribute('aria-label') !== wantedLabel) menu.setAttribute('aria-label', wantedLabel);
      if (menu.getAttribute('aria-expanded') !== wantedExpanded) menu.setAttribute('aria-expanded', wantedExpanded);
    }
    if (meta) {
      let wantedMeta = '';
      if (section === 'rides') {
        const data = readData();
        wantedMeta = `${data.trips.length} ${data.trips.length === 1 ? 'rit' : 'ritten'} geregistreerd`;
      } else if (section === 'locations') {
        const data = readData();
        const childCount = data.locations.filter(location => location.parentId).length;
        wantedMeta = `${data.locations.length} locaties${childCount ? ` · ${childCount} sublocaties` : ''}`;
      } else {
        try {
          const time = JSON.parse(localStorage.getItem('urenregistratie.test.pwa.v1') || '{}');
          const entries = Array.isArray(time.entries) ? time.entries.filter(entry => entry.activityType !== 'interruption') : [];
          wantedMeta = `${entries.length} ${entries.length === 1 ? 'taak' : 'taken'} geregistreerd${time.timer?.status === 'active' ? ' · timer actief' : ''}`;
        } catch (_) {
          wantedMeta = 'Tijdsregistratie';
        }
      }
      if (meta.textContent !== wantedMeta) meta.textContent = wantedMeta;
    }
    syncDrawerSelection();
  }

  function filterTripLocationSelects() {
    const snapshot = readData();
    const childToParent = new Map(snapshot.locations.filter(location => location.parentId).map(location => [String(location.id), String(location.parentId)]));
    if (!childToParent.size) return;
    const selectors = [
      '#startDestination',
      '#arrivalDestination',
      '#manualForm select[name="originId"]',
      '#manualForm select[name="destinationId"]',
      '#tripEditForm select[name="originId"]',
      '#tripEditForm select[name="destinationId"]'
    ];
    for (const select of $$(selectors.join(','))) {
      const isArrival = select.id === 'arrivalDestination';
      const isEditor = Boolean(select.closest('#tripEditForm'));
      const selectedBefore = select.value;
      const selectedId = isArrival && selectedBefore.startsWith('known:') ? selectedBefore.slice(6) : selectedBefore;
      const parentId = childToParent.get(selectedId);
      if (parentId && !isEditor) {
        const parentValue = isArrival ? `known:${parentId}` : parentId;
        if ([...select.options].some(option => option.value === parentValue)) select.value = parentValue;
      }
      for (const option of [...select.options]) {
        const optionId = isArrival && option.value.startsWith('known:') ? option.value.slice(6) : option.value;
        if (!childToParent.has(optionId)) continue;
        if (isEditor && option.value === selectedBefore) continue;
        option.remove();
      }
    }
  }

  function locationTripCount(location, snapshot) {
    const seen = new Set();
    for (const trip of snapshot.trips) {
      if (trip.origin?.id === location.id || trip.destination?.id === location.id) seen.add(trip.id);
    }
    for (const event of snapshot.events) {
      if (event.tripId && event.location?.id === location.id) seen.add(event.tripId);
    }
    return seen.size;
  }

  function orderedRoots(snapshot) {
    const roots = snapshot.locations.filter(location => !location.parentId || !snapshot.locations.some(candidate => candidate.id === location.parentId));
    const smart = snapshot.settings.locationSortMode !== 'alpha';
    return roots.sort((a, b) => smart
      ? locationTripCount(b, snapshot) - locationTripCount(a, snapshot) || String(a.name).localeCompare(String(b.name), 'nl', { sensitivity: 'base' })
      : String(a.name).localeCompare(String(b.name), 'nl', { sensitivity: 'base' }));
  }

  function locationNodeHtml(location, depth, snapshot) {
    const effective = effectiveLocation(location, snapshot);
    const children = snapshot.locations
      .filter(candidate => candidate.parentId === location.id)
      .sort((a, b) => String(a.name).localeCompare(String(b.name), 'nl', { sensitivity: 'base' }));
    const expanded = expandedLocationId === location.id;
    const subtitle = depth
      ? (location.address || (effective.parent ? `Onder ${effective.parent.name}` : '') || 'Sublocatie')
      : (location.address || (effective.lat != null && effective.lng != null ? `${Number(effective.lat).toFixed(5)}, ${Number(effective.lng).toFixed(5)}` : 'Geen adres/GPS'));
    const gps = effective.lat != null && effective.lng != null ? `${Number(effective.lat).toFixed(5)}, ${Number(effective.lng).toFixed(5)}` : 'Niet vastgelegd';
    const inherited = depth && (!location.address || location.lat == null || location.lng == null) && effective.parent;
    const count = locationTripCount(location, snapshot);
    return `
      <div class="km-shell-location-node" data-shell-location-node="${esc(location.id)}" data-depth="${depth}" style="--depth:${depth}">
        <div class="km-shell-location-row" data-shell-location-toggle="${esc(location.id)}">
          <span class="km-shell-location-icon">${locationGlyph(location.type)}</span>
          <div class="km-shell-location-copy"><strong>${esc(location.name || 'Locatie')}</strong><small>${esc(subtitle)}</small></div>
          <div class="km-shell-location-buttons">
            <button type="button" data-shell-edit-location="${esc(location.id)}" aria-label="${esc(location.name)} bewerken">•••</button>
            <span class="km-shell-location-chevron" aria-hidden="true">${expanded ? '⌄' : '›'}</span>
          </div>
        </div>
        ${expanded ? `<div class="km-shell-location-details"><div class="km-shell-location-detail-grid"><div class="km-shell-location-detail"><span>Type</span><strong>${esc(typeLabel(location.type))}</strong></div><div class="km-shell-location-detail"><span>Ritten</span><strong>${count}</strong></div><div class="km-shell-location-detail"><span>GPS</span><strong>${esc(gps)}${inherited ? ' · geërfd' : ''}</strong></div><div class="km-shell-location-detail"><span>Niveau</span><strong>${depth ? 'Sublocatie' : 'Hoofdlocatie'}</strong></div></div>${depth === 0 ? `<button type="button" class="km-shell-child-add" data-shell-add-child="${esc(location.id)}">+ Sublocatie toevoegen</button>` : ''}</div>` : ''}
      </div>
      ${children.map(child => locationNodeHtml(child, Math.min(depth + 1, 1), snapshot)).join('')}`;
  }

  function renderLocations() {
    const root = $('#kmShellLocationsView');
    if (!root || section !== 'locations' || document.body.classList.contains('editor-view')) return;
    const snapshot = readData();
    const sortMode = snapshot.settings.locationSortMode === 'alpha' ? 'alpha' : 'smart';
    const roots = orderedRoots(snapshot);
    root.innerHTML = `
      <div class="km-shell-locations-head"><div><div class="kicker">Gedeeld</div><h2>Locaties</h2></div><span class="muted">${snapshot.locations.length}</span></div>
      <div class="km-shell-location-actions"><button type="button" class="btn secondary" data-shell-current-location>Huidige locatie +</button><button type="button" class="btn secondary" data-shell-add-location>Nieuwe locatie +</button></div>
      <div class="km-shell-location-sort" aria-label="Locaties sorteren"><button type="button" class="${sortMode === 'smart' ? 'active' : ''}" data-action="location-sort" data-mode="smart">◎ Logisch</button><button type="button" class="${sortMode === 'alpha' ? 'active' : ''}" data-action="location-sort" data-mode="alpha">A–Z Naam</button></div>
      ${roots.length ? `<div class="km-shell-location-tree">${roots.map(location => locationNodeHtml(location, 0, snapshot)).join('')}</div>` : '<div class="km-shell-empty">Nog geen locaties opgeslagen.</div>'}`;
  }

  function dispatchOriginalAction(action, extra = {}) {
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.action = action;
    Object.entries(extra).forEach(([key, value]) => { button.dataset[key] = value; });
    button.className = 'km-shell-legacy';
    document.body.appendChild(button);
    button.click();
    button.remove();
  }

  function openLocationEditor(id = null, parentId = null, current = false) {
    pendingParentForNew = id ? null : parentId;
    ensureOriginalMode('kilometers');
    ensureKmView('ride');
    document.body.classList.remove('km-shell-locations-mode');
    $('#kmShellLocationsView').hidden = true;
    if (current) {
      dispatchOriginalAction('current-location');
    } else if (id) {
      const wrapper = document.createElement('div');
      wrapper.dataset.id = id;
      wrapper.className = 'km-shell-legacy';
      const button = document.createElement('button');
      button.type = 'button';
      button.dataset.action = 'edit-location';
      wrapper.appendChild(button);
      document.body.appendChild(wrapper);
      button.click();
      wrapper.remove();
    } else {
      dispatchOriginalAction('add-location');
    }
    queueLocationEditorAugment();
  }

  function parentOptions(currentId, selectedParentId, snapshot) {
    const roots = snapshot.locations
      .filter(location => location.id !== currentId && !location.parentId)
      .sort((a, b) => String(a.name).localeCompare(String(b.name), 'nl', { sensitivity: 'base' }));
    return `<option value="">Geen · hoofdlocatie</option>${roots.map(location => `<option value="${esc(location.id)}" ${location.id === selectedParentId ? 'selected' : ''}>${esc(location.name)}</option>`).join('')}`;
  }

  function augmentLocationEditor() {
    const form = $('#locationForm');
    if (!form || $('#kmShellLocationParentSection', form)) return;
    const snapshot = readData();
    const id = form.elements.id?.value || '';
    const stored = id ? locationById(id, snapshot) : null;
    const selectedParent = stored?.parentId || pendingParentForNew || '';
    const basisSection = form.querySelector('.edit-section');
    const sectionEl = document.createElement('section');
    sectionEl.id = 'kmShellLocationParentSection';
    sectionEl.className = 'edit-section km-shell-parent-section';
    sectionEl.innerHTML = `<div class="edit-section-head"><strong>Onder locatie</strong><small>Hoofdlocatie of sublocatie</small></div><div class="form-group"><label>Onder locatie</label><select id="kmShellParentId">${parentOptions(id, selectedParent, snapshot)}</select><div id="kmShellParentHint" class="km-shell-parent-hint"></div></div>`;
    if (basisSection?.nextSibling) form.insertBefore(sectionEl, basisSection.nextSibling);
    else form.prepend(sectionEl);

    const select = $('#kmShellParentId', form);
    const hint = $('#kmShellParentHint', form);
    const updateHint = () => {
      const parent = select.value ? locationById(select.value, readData()) : null;
      if (!hint) return;
      hint.textContent = parent
        ? `Sublocatie van ${parent.name}. Leeg adres of GPS kan in het locatieoverzicht van de hoofdlocatie worden overgenomen.`
        : 'Als hoofdlocatie kan deze plek zelf sublocaties bevatten.';
    };
    select?.addEventListener('change', updateHint);
    updateHint();
  }

  function queueLocationEditorAugment() {
    if (locationEditorAugmentQueued) return;
    locationEditorAugmentQueued = true;
    requestAnimationFrame(() => {
      locationEditorAugmentQueued = false;
      augmentLocationEditor();
    });
  }

  function installStorageHierarchyPatch() {
    if (Storage.prototype.__kmShellParentPatch) return;
    const nativeSetItem = Storage.prototype.setItem;
    Object.defineProperty(Storage.prototype, '__kmShellParentPatch', { value: true, configurable: false });
    Storage.prototype.setItem = function (key, value) {
      if (this === localStorage && key === DATA_KEY && pendingParentSave) {
        try {
          const payload = JSON.parse(String(value));
          if (Array.isArray(payload.locations)) {
            let target = pendingParentSave.id ? payload.locations.find(location => location.id === pendingParentSave.id) : null;
            if (!target) target = payload.locations.find(location => location.id && !pendingParentSave.beforeIds.has(location.id));
            if (target) {
              if (pendingParentSave.parentId) target.parentId = pendingParentSave.parentId;
              else delete target.parentId;
              const previous = pendingParentSave.previousParentId || '';
              if (previous !== (pendingParentSave.parentId || '')) pendingHierarchyReload = true;
              value = JSON.stringify(payload);
            }
          }
        } catch (error) {
          console.warn('Sublocatie kon niet in opslag worden aangevuld.', error);
        }
      }
      return nativeSetItem.call(this, key, value);
    };
  }

  function captureParentBeforeSave() {
    const form = $('#locationForm');
    const select = $('#kmShellParentId', form);
    if (!form || !select) return;
    const snapshot = readData();
    const id = form.elements.id?.value || '';
    const stored = id ? locationById(id, snapshot) : null;
    pendingParentSave = {
      id,
      parentId: select.value || '',
      previousParentId: stored?.parentId || '',
      beforeIds: new Set(snapshot.locations.map(location => location.id))
    };
    setTimeout(() => { pendingParentSave = null; }, 2500);
  }

  function generalBackupStatus() {
    const last = readData().settings.lastBackupAt;
    if (!last) return 'Nog geen complete back-up gemaakt.';
    const date = new Date(last);
    if (Number.isNaN(date.getTime())) return 'Laatste complete back-up is vastgelegd.';
    return 'Laatste complete back-up: ' + new Intl.DateTimeFormat('nl-NL', { dateStyle: 'medium', timeStyle: 'short' }).format(date);
  }

  function setSettingsBackVisible(visible) {
    const back = $('#kmShellSettingsBack');
    if (back) back.hidden = !visible;
  }

  function animateSettingsContent(direction) {
    const content = $('#kmShellSettingsContent');
    if (!content) return;
    content.classList.remove('km-settings-forward-in', 'km-settings-back-in');
    void content.offsetWidth;
    content.classList.add(direction === 'back' ? 'km-settings-back-in' : 'km-settings-forward-in');
    setTimeout(() => content.classList.remove('km-settings-forward-in', 'km-settings-back-in'), 280);
  }

  function renderGeneralSettings() {
    const content = $('#kmShellSettingsContent');
    if (!content) return false;
    content.dataset.mode = 'general';
    const title = $('#kmShellSettingsTitle');
    if (title) title.textContent = 'Algemene instellingen';
    setSettingsBackVisible(false);
    content.innerHTML = `
      <section class="km-shell-general-settings">
        <div class="km-shell-general-intro"><div class="kicker">Log</div><h2>Algemene instellingen</h2><p>Deze instellingen gelden voor de volledige app: ritten, tijd, taken en locaties.</p></div>
        <div class="km-shell-general-card">
          <strong>Data & back-up</strong>
          <small>Maak of herstel één complete back-up van de volledige Log-app.</small>
          <div class="km-shell-general-status" id="kmShellBackupStatus">${esc(generalBackupStatus())}</div>
          <div class="km-shell-general-actions">
            <button type="button" class="btn" data-general-action="backup-export">Complete back-up maken</button>
            <label class="btn" style="text-align:center">Back-up herstellen<input id="kmShellBackupImport" type="file" accept="application/json,.json" hidden></label>
          </div>
          <details class="km-shell-general-advanced">
            <summary>Geavanceerd gegevensbeheer</summary>
            <div class="km-shell-general-actions">
              <label class="btn secondary" style="text-align:center">Kilometergegevens toevoegen<input id="kmShellMergeImport" type="file" accept="application/json,.json" hidden></label>
              <button type="button" class="btn secondary" data-general-action="id-converter">ID-converter</button>
            </div>
          </details>
        </div>
        <div class="km-shell-general-card">
          <strong>Instellingen per onderdeel</strong>
          <small>Open alleen de instellingen die bij dat onderdeel horen.</small>
          <div class="km-shell-general-nav">
            <button type="button" data-settings-target="rides"><span>Ritten</span><span>›</span></button>
            <button type="button" data-settings-target="locations"><span>Locaties</span><span>›</span></button>
            <button type="button" data-settings-target="time"><span>Tijd / taken</span><span>›</span></button>
          </div>
        </div>
      </section>`;
    content.querySelector('[data-general-action="backup-export"]')?.addEventListener('click', () => {
      const status = $('#kmShellBackupStatus');
      if (status) status.textContent = 'Back-up wordt voorbereid…';
      window.dispatchEvent(new CustomEvent('log-general-backup-export'));
    });
    content.querySelector('#kmShellBackupImport')?.addEventListener('change', event => {
      const file = event.target.files?.[0];
      event.target.value = '';
      if (file) window.dispatchEvent(new CustomEvent('log-general-backup-import', { detail: { file } }));
    });
    content.querySelector('#kmShellMergeImport')?.addEventListener('change', event => {
      const file = event.target.files?.[0];
      event.target.value = '';
      if (file) window.dispatchEvent(new CustomEvent('log-general-merge-import', { detail: { file } }));
    });
    content.querySelector('[data-general-action="id-converter"]')?.addEventListener('click', () => {
      window.dispatchEvent(new CustomEvent('log-general-id-converter'));
    });
    content.querySelectorAll('[data-settings-target]').forEach(button => button.addEventListener('click', () => openSubSettings(button.dataset.settingsTarget)));
    return true;
  }

  function openSubSettings(target) {
    if (!ROOT_SECTIONS.has(target)) return;
    selectSection(target);
    const content = $('#kmShellSettingsContent');
    if (content) {
      content.innerHTML = '';
      content.dataset.mode = 'sub';
    }
    const mounted = target === 'time' ? mountTimeSettings() : mountKmSettings();
    if (!mounted) {
      renderGeneralSettings();
      return;
    }
    setSettingsBackVisible(true);
    animateSettingsContent('forward');
  }

  function mountKmSettings() {
    const content = $('#kmShellSettingsContent');
    const app = $('#app');
    const topAction = $('#topAction');
    if (!content || !app || !topAction) return false;

    kmAppPlaceholder = document.createComment('km-app-placeholder');
    app.parentNode?.insertBefore(kmAppPlaceholder, app);
    if (!ensureKmView('settings')) {
      kmAppPlaceholder.remove();
      kmAppPlaceholder = null;
      return false;
    }
    content.innerHTML = '';
    content.dataset.mode = 'sub';
    content.appendChild(app);
    app.hidden = false;
    kmSettingsMounted = true;

    requestAnimationFrame(() => filterKmSettings());
    return true;
  }

  function filterKmSettings() {
    const app = $('#kmShellSettingsContent > #app');
    if (!app) return;
    const details = [...app.querySelectorAll('details.accordion')];
    for (const detail of details) {
      const label = detail.querySelector('summary strong')?.textContent?.trim() || '';
      if (label === 'Locaties') detail.style.display = 'none';
      if (section === 'locations' && label !== 'Algemeen') detail.style.display = 'none';
    }
    const title = $('#kmShellSettingsTitle');
    if (title) title.textContent = section === 'locations' ? 'Instellingen locaties' : 'Instellingen ritten';
  }

  function mountTimeSettings() {
    const content = $('#kmShellSettingsContent');
    const frame = $('#timeAppFrame');
    if (!content || !frame) return false;
    timeFrameOriginalParent = frame.parentNode;
    timeFrameOriginalNext = frame.nextSibling;
    timeFramePlaceholder = document.createComment('time-frame-placeholder');
    timeFrameOriginalParent?.insertBefore(timeFramePlaceholder, frame);
    content.innerHTML = '';
    content.dataset.mode = 'sub';
    content.appendChild(frame);
    frame.hidden = false;
    const title = $('#kmShellSettingsTitle');
    if (title) title.textContent = 'Instellingen tijd / taken';
    const open = () => {
      try {
        if (timeFrameView() !== 'settings') {
          const direct = frame.contentWindow?.openSettings;
          if (typeof direct === 'function') direct.call(frame.contentWindow);
          else frame.contentDocument?.getElementById('openSettings')?.click();
        }
        setTimeSettingsOpen(timeFrameView() === 'settings');
      } catch (error) {
        console.warn('Tijdinstellingen konden niet worden geopend.', error);
      }
    };
    const openRepeatedly = () => {
      open();
      setTimeout(open, 80);
      setTimeout(open, 220);
    };
    if (frame.contentDocument?.readyState === 'complete') requestAnimationFrame(openRepeatedly);
    else frame.addEventListener('load', () => requestAnimationFrame(openRepeatedly), { once: true });
    return true;
  }

  function timeFrameView() {
    const frame = $('#timeAppFrame');
    try {
      return frame?.contentDocument?.getElementById('appTaskCount')?.dataset.navigationView === 'settings' ? 'settings' : 'home';
    } catch (_) {
      return 'home';
    }
  }

  function setTimeSettingsOpen(open) {
    timeSettingsOpen = Boolean(open);
    document.body.classList.toggle('km-shell-time-settings-open', timeSettingsOpen);
    syncChrome();
  }

  function clickTimeSettingsToggle(wantedView) {
    const frame = $('#timeAppFrame');
    if (!frame) return false;
    try {
      const current = timeFrameView();
      if (current === wantedView) {
        setTimeSettingsOpen(wantedView === 'settings');
        return true;
      }
      const button = frame.contentDocument?.getElementById('openSettings');
      if (!button) return false;
      button.click();
      requestAnimationFrame(() => setTimeSettingsOpen(timeFrameView() === 'settings'));
      return true;
    } catch (error) {
      console.warn('Tijdinstellingen konden niet worden geopend.', error);
      return false;
    }
  }

  function openTimeSettingsPage() {
    closeDrawer();
    if (clickTimeSettingsToggle('settings')) return;
    const frame = $('#timeAppFrame');
    frame?.addEventListener('load', () => clickTimeSettingsToggle('settings'), { once: true });
  }

  function closeTimeSettingsPage() {
    if (!clickTimeSettingsToggle('home')) setTimeSettingsOpen(false);
  }

  function openSettingsSheet() {
    const settings = $('#kmShellSettings');
    if (!settings || settings.classList.contains('open')) return;
    if (timeSettingsOpen) closeTimeSettingsPage();
    if (!renderGeneralSettings()) return;
    settings.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function restoreKmApp() {
    if (!kmSettingsMounted) return;
    const app = $('#kmShellSettingsContent > #app');
    if (app && kmAppPlaceholder?.parentNode) {
      kmAppPlaceholder.parentNode.insertBefore(app, kmAppPlaceholder);
      kmAppPlaceholder.remove();
    }
    kmAppPlaceholder = null;
    kmSettingsMounted = false;
    ensureKmView('ride');
  }

  function restoreTimeFrame() {
    const frame = $('#kmShellSettingsContent > #timeAppFrame');
    if (!frame) return;
    if (timeFramePlaceholder?.parentNode) {
      timeFramePlaceholder.parentNode.insertBefore(frame, timeFramePlaceholder);
      timeFramePlaceholder.remove();
    } else if (timeFrameOriginalParent) {
      timeFrameOriginalParent.insertBefore(frame, timeFrameOriginalNext || null);
    }
    timeFramePlaceholder = null;
    timeFrameOriginalParent = null;
    timeFrameOriginalNext = null;
    // Settings autosave in de tijd-app. Reload returns the embedded app to its home screen.
    try {
      const src = frame.src;
      if (src) frame.src = src;
    } catch (_) {}
  }

  function closeSettingsSheet() {
    const settings = $('#kmShellSettings');
    if (!settings?.classList.contains('open')) return;
    if ($('#kmShellSettingsContent > #timeAppFrame')) restoreTimeFrame();
    if (kmSettingsMounted) restoreKmApp();
    settings.classList.remove('open');
    document.body.style.overflow = '';
    // Het zijpaneel blijft bewust open staan achter de sheet.
    drawerOpen = true;
    document.body.classList.add('km-shell-drawer-open');
    $('#kmShellMenuButton')?.setAttribute('aria-expanded', 'true');
    $('#kmShellDrawer')?.classList.add('open');
    $('#kmShellBackdrop')?.classList.add('open');
    localStorage.setItem(DRAWER_KEY, '1');
    showSection();
  }

  const SWIPE_SECTIONS = ['rides', 'time', 'locations'];
  const swipeDocuments = new WeakSet();
  let pageSwipe = null;

  function pageSwipeBlocked() {
    return drawerOpen || $('#kmShellSettings')?.classList.contains('open') || !$('#modal')?.hidden || document.body.classList.contains('editor-view');
  }

  function pageSwipeInteractive(target) {
    return Boolean(target?.closest?.('button,input,select,textarea,a,label,summary,[contenteditable="true"],.swipe-row,.trip-swipe-row,.entry'));
  }

  function pageSwipeStart(event) {
    if (event.touches?.length !== 1 || pageSwipeBlocked()) return;
    const touch = event.touches[0];
    const edge = touch.clientX <= 30 || touch.clientX >= window.innerWidth - 30;
    if (!edge && pageSwipeInteractive(event.target)) return;
    pageSwipe = { x: touch.clientX, y: touch.clientY, dx: 0, dy: 0, horizontal: false };
  }

  function pageSwipeMove(event) {
    if (!pageSwipe || event.touches?.length !== 1) return;
    const touch = event.touches[0];
    pageSwipe.dx = touch.clientX - pageSwipe.x;
    pageSwipe.dy = touch.clientY - pageSwipe.y;
    if (!pageSwipe.horizontal) {
      if (Math.abs(pageSwipe.dy) > 12 && Math.abs(pageSwipe.dy) > Math.abs(pageSwipe.dx)) {
        pageSwipe = null;
        return;
      }
      if (Math.abs(pageSwipe.dx) > 12 && Math.abs(pageSwipe.dx) > Math.abs(pageSwipe.dy) * 1.25) pageSwipe.horizontal = true;
    }
    if (pageSwipe?.horizontal && event.cancelable) event.preventDefault();
  }

  function pageSwipeEnd() {
    const gesture = pageSwipe;
    pageSwipe = null;
    if (!gesture?.horizontal || Math.abs(gesture.dx) < 72 || Math.abs(gesture.dx) < Math.abs(gesture.dy) * 1.3) return;
    navigateByPageSwipe(gesture.dx < 0 ? 1 : -1);
  }

  function navigateByPageSwipe(direction) {
    const index = SWIPE_SECTIONS.indexOf(section);
    const nextIndex = index + direction;
    if (index < 0 || nextIndex < 0 || nextIndex >= SWIPE_SECTIONS.length) return;
    const animationClass = direction > 0 ? 'km-shell-page-forward' : 'km-shell-page-back';
    document.body.classList.remove('km-shell-page-forward', 'km-shell-page-back');
    void document.body.offsetWidth;
    document.body.classList.add(animationClass);
    selectSection(SWIPE_SECTIONS[nextIndex]);
    setTimeout(() => document.body.classList.remove(animationClass), 280);
  }

  function bindSwipeDocument(doc) {
    if (!doc || swipeDocuments.has(doc)) return;
    swipeDocuments.add(doc);
    doc.addEventListener('touchstart', pageSwipeStart, { passive: true });
    doc.addEventListener('touchmove', pageSwipeMove, { passive: false });
    doc.addEventListener('touchend', pageSwipeEnd, { passive: true });
    doc.addEventListener('touchcancel', () => { pageSwipe = null; }, { passive: true });
  }

  function bindTimeFrameSwipe() {
    const frame = $('#timeAppFrame');
    try { bindSwipeDocument(frame?.contentDocument); } catch (_) {}
  }

  function bindPageSwipes() {
    bindSwipeDocument(document);
    const frame = $('#timeAppFrame');
    frame?.addEventListener('load', () => requestAnimationFrame(bindTimeFrameSwipe), { passive: true });
    bindTimeFrameSwipe();
  }

  function bindGlobalEvents() {
    window.addEventListener('kmreg-test-shell-select-section', event => selectSection(event.detail?.section));
    window.addEventListener('kmreg-test-shell-open-settings', () => openSettingsSheet());
    window.addEventListener('log-backup-updated', () => {
      const content = $('#kmShellSettingsContent');
      if (content?.dataset.mode === 'general') renderGeneralSettings();
    });
    window.addEventListener('message', event => {
      const frame = $('#timeAppFrame');
      if (event.origin !== window.location.origin || event.source !== frame?.contentWindow || event.data?.type !== 'urenregistratie-view') return;
      setTimeSettingsOpen(event.data.view === 'settings');
    });

    document.addEventListener('click', event => {
      const edit = event.target.closest('[data-shell-edit-location]');
      if (edit) {
        event.preventDefault();
        event.stopPropagation();
        openLocationEditor(edit.dataset.shellEditLocation);
        return;
      }
      const add = event.target.closest('[data-shell-add-location]');
      if (add) {
        event.preventDefault();
        openLocationEditor(null, null, false);
        return;
      }
      const current = event.target.closest('[data-shell-current-location]');
      if (current) {
        event.preventDefault();
        openLocationEditor(null, null, true);
        return;
      }
      const child = event.target.closest('[data-shell-add-child]');
      if (child) {
        event.preventDefault();
        event.stopPropagation();
        openLocationEditor(null, child.dataset.shellAddChild, false);
        return;
      }
      const toggle = event.target.closest('[data-shell-location-toggle]');
      if (toggle && !event.target.closest('button')) {
        expandedLocationId = expandedLocationId === toggle.dataset.shellLocationToggle ? null : toggle.dataset.shellLocationToggle;
        renderLocations();
        return;
      }
      if (event.target.closest('[data-action="save-location"]')) captureParentBeforeSave();
      if (event.target.closest('[data-action="location-sort"]') && section === 'locations') setTimeout(renderLocations, 0);
    }, false);

    const observer = new MutationObserver(() => {
      if ($('#locationForm')) queueLocationEditorAugment();
      filterTripLocationSelects();
      const editor = document.body.classList.contains('editor-view');
      const editorClosed = lastEditorState && !editor;
      lastEditorState = editor;
      if (editorClosed && section === 'locations' && !$('#kmShellSettings')?.classList.contains('open')) {
        document.body.classList.add('km-shell-locations-mode');
        renderLocations();
      }
      if (!editor && pendingHierarchyReload) {
        pendingHierarchyReload = false;
        localStorage.setItem(SECTION_KEY, 'locations');
        setTimeout(() => location.reload(), 60);
      }
      syncChrome();
    });
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });

    window.addEventListener('storage', event => {
      if ([DATA_KEY, 'urenregistratie.test.pwa.v1'].includes(event.key)) {
        renderLocations();
        syncChrome();
      }
    });
  }

  function init() {
    injectStyles();
    installStorageHierarchyPatch();
    installChrome();
    installShellElements();
    bindGlobalEvents();
    bindPageSwipes();
    showSection();
    filterTripLocationSelects();
    // Na sluiten van Instellingen moet het paneel zichtbaar blijven; normale herlaad start rustig gesloten.
    closeDrawer();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();

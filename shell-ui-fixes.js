(function () {
  'use strict';

  const BUILD = '0.31.1';
  const DATA_KEY = 'kmreg-v4-data';
  const SECTION_KEY = 'kmreg-shell-section-v1';
  const TIME_KEY = 'urenregistratie.pwa.v1';
  let gpsState = { status: 'idle', lat: null, lng: null, accuracy: null, matchedId: null, matchedRootId: null, distance: null, nearestId: null, nearestDistance: null, error: '', updatedAt: 0 };
  let gpsPending = false;
  let decorateQueued = false;
  let decorating = false;

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

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

  function currentSection() {
    const value = localStorage.getItem(SECTION_KEY);
    return ['rides', 'time', 'locations'].includes(value) ? value : (document.body.classList.contains('time-mode') ? 'time' : 'rides');
  }

  function injectStyle() {
    if ($('#kmShellFixes0311')) return;
    const style = document.createElement('style');
    style.id = 'kmShellFixes0311';
    style.textContent = `
      .km-shell-top{position:relative!important;top:auto!important;z-index:1!important;background:transparent!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
      .km-shell-top-copy{padding-left:44px;padding-right:44px}
      .km-shell-menu-button{position:fixed!important;z-index:92!important;top:calc(env(safe-area-inset-top) + 10px);left:max(12px,calc((100vw - 760px)/2 + 12px));width:42px!important;height:42px!important;border:1px solid color-mix(in srgb,var(--line) 82%,transparent)!important;border-radius:50%!important;background:color-mix(in srgb,var(--bg) 80%,transparent)!important;box-shadow:0 7px 24px rgba(0,0,0,.18);-webkit-backdrop-filter:blur(18px) saturate(165%);backdrop-filter:blur(18px) saturate(165%)}
      body.time-mode .km-shell-top{position:static!important;height:0!important;min-height:0!important;margin:0!important;padding:0!important}
      body.time-mode .km-shell-top-copy,body.time-mode .km-shell-top-spacer{display:none!important}
      body.time-mode .time-app-frame{height:100dvh!important;min-height:100dvh!important;margin-top:calc(-1 * env(safe-area-inset-top))}
      .editor-nav{position:relative!important;top:auto!important;z-index:1!important;background:transparent!important;border-bottom:0!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
      .editor-back{position:fixed!important;z-index:92!important;top:calc(env(safe-area-inset-top) + 10px);left:max(12px,calc((100vw - 820px)/2 + 12px))}
      .editor-nav-actions{position:fixed!important;z-index:92!important;top:calc(env(safe-area-inset-top) + 10px);right:max(12px,calc((100vw - 820px)/2 + 12px));margin:0!important}
      .editor-nav-title{position:static!important;left:auto!important;transform:none!important;margin:0 auto}
      .km-shell-current-location-status{margin:0 0 12px;padding:9px 1px 11px;border-bottom:1px solid var(--line);color:var(--muted);font-size:11px;line-height:1.4}
      .km-shell-current-location-status strong{color:var(--text)}
      .km-shell-current-location-status.good{color:var(--good)}
      .km-shell-current-location-status.warn{color:var(--warn)}
      .km-shell-location-node.km-current-location>.km-shell-location-row{background:color-mix(in srgb,var(--accent) 8%,transparent)}
      .km-shell-location-node.km-current-location>.km-shell-location-row .km-shell-location-icon{border-color:color-mix(in srgb,var(--accent) 55%,var(--line));color:var(--accent)}
      .km-shell-location-node.km-current-location>.km-shell-location-row .km-shell-location-copy strong::after{content:' · hier';color:var(--accent);font-size:10px;font-weight:800}
      @media(prefers-color-scheme:light){.km-shell-menu-button{background:rgba(255,255,255,.76)!important;box-shadow:0 6px 20px rgba(30,45,65,.12)}}
    `;
    document.head.appendChild(style);
  }

  function updateVersionLabel() {
    const today = $('#today');
    if (!today) return;
    today.textContent = new Intl.DateTimeFormat('nl-NL', { weekday: 'long', day: 'numeric', month: 'long' }).format(new Date()) + ' · ' + BUILD;
  }

  function prepareTimeFrame() {
    const frame = $('#timeAppFrame');
    if (!frame) return;
    const apply = () => {
      try {
        const doc = frame.contentDocument;
        if (!doc?.head) return;
        let style = doc.getElementById('km-shell-time-scroll-fix');
        if (!style) {
          style = doc.createElement('style');
          style.id = 'km-shell-time-scroll-fix';
          style.textContent = `
            html,body{background:transparent!important}
            .app-shell{max-width:none!important;padding-top:0!important}
            html body .topbar{display:flex!important;position:static!important;top:auto!important;z-index:auto!important;padding:14px 48px 16px!important;background:transparent!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
            html body #openSettings{display:none!important}
            @media(max-width:520px){html body .topbar{padding-left:50px!important;padding-right:12px!important}}
          `;
          doc.head.appendChild(style);
        }
      } catch (error) {
        console.warn('Scrollende tijdkop kon niet worden ingesteld.', error);
      }
    };
    if (frame.dataset.kmShellScrollFixBound !== '1') {
      frame.dataset.kmShellScrollFixBound = '1';
      frame.addEventListener('load', () => requestAnimationFrame(() => { apply(); setTimeout(apply, 80); }), { passive: true });
    }
    apply();
    setTimeout(apply, 160);
  }

  function distanceMeters(a, b) {
    const R = 6371000;
    const rad = value => value * Math.PI / 180;
    const dLat = rad(Number(b.lat) - Number(a.lat));
    const dLng = rad(Number(b.lng) - Number(a.lng));
    const lat1 = rad(Number(a.lat));
    const lat2 = rad(Number(b.lat));
    const h = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(h));
  }

  function locationById(id, snapshot) {
    return snapshot.locations.find(location => String(location.id) === String(id)) || null;
  }

  function rootFor(location, snapshot) {
    let current = location;
    const seen = new Set();
    while (current?.parentId && !seen.has(current.id)) {
      seen.add(current.id);
      const parent = locationById(current.parentId, snapshot);
      if (!parent) break;
      current = parent;
    }
    return current || location;
  }

  function effectiveCoords(location, snapshot) {
    let current = location;
    const seen = new Set();
    while (current && !seen.has(current.id)) {
      seen.add(current.id);
      const lat = Number(current.lat), lng = Number(current.lng);
      if (Number.isFinite(lat) && Number.isFinite(lng)) return { lat, lng, inherited: current.id !== location.id };
      current = current.parentId ? locationById(current.parentId, snapshot) : null;
    }
    return null;
  }

  function formatDistance(meters) {
    if (!Number.isFinite(meters)) return '';
    if (meters < 1000) return `${Math.round(meters)} m`;
    return `${new Intl.NumberFormat('nl-NL', { maximumFractionDigits: 1 }).format(meters / 1000)} km`;
  }

  function locationPath(location, snapshot) {
    if (!location) return '';
    const parent = location.parentId ? locationById(location.parentId, snapshot) : null;
    return parent ? `${parent.name} › ${location.name}` : (location.name || 'Locatie');
  }

  function recognitionRadius(snapshot) {
    return Math.max(25, Number(snapshot.settings.recognitionRadius) || 500);
  }

  function analyzePosition(lat, lng, accuracy) {
    const snapshot = readData();
    const point = { lat, lng };
    const candidates = snapshot.locations.map(location => {
      const coords = effectiveCoords(location, snapshot);
      if (!coords) return null;
      return { location, root: rootFor(location, snapshot), distance: distanceMeters(point, coords), ownCoords: !coords.inherited };
    }).filter(Boolean).sort((a, b) => a.distance - b.distance || Number(b.ownCoords) - Number(a.ownCoords));
    const nearest = candidates[0] || null;
    const radius = recognitionRadius(snapshot);
    const matched = nearest && nearest.distance <= radius ? nearest : null;
    gpsState = {
      status: 'ready', lat, lng, accuracy: Number(accuracy) || null,
      matchedId: matched?.location?.id || null,
      matchedRootId: matched?.root?.id || null,
      distance: matched?.distance ?? null,
      nearestId: nearest?.location?.id || null,
      nearestDistance: nearest?.distance ?? null,
      error: '', updatedAt: Date.now()
    };
    scheduleDecorate();
  }

  function requestCurrentLocation(force = false) {
    if (currentSection() !== 'locations' || !document.body.classList.contains('km-shell-locations-mode')) return;
    if (gpsPending) return;
    if (!force && gpsState.updatedAt && Date.now() - gpsState.updatedAt < 60000) {
      scheduleDecorate();
      return;
    }
    if (!navigator.geolocation) {
      gpsState = { ...gpsState, status: 'error', error: 'GPS is niet beschikbaar op dit apparaat.', updatedAt: Date.now() };
      scheduleDecorate();
      return;
    }
    gpsPending = true;
    gpsState = { ...gpsState, status: 'loading', error: '' };
    scheduleDecorate();
    navigator.geolocation.getCurrentPosition(
      position => {
        gpsPending = false;
        analyzePosition(position.coords.latitude, position.coords.longitude, position.coords.accuracy);
      },
      error => {
        gpsPending = false;
        const message = error.code === 1 ? 'Geen locatietoestemming. De slimme volgorde gebruikt nu alleen je registratiehistorie.' : error.code === 3 ? 'GPS ophalen duurde te lang. De slimme volgorde gebruikt nu alleen je registratiehistorie.' : 'Huidige locatie kon niet worden bepaald.';
        gpsState = { ...gpsState, status: 'error', error: message, updatedAt: Date.now() };
        scheduleDecorate();
      },
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 30000 }
    );
  }

  function tripCount(location, snapshot) {
    const seen = new Set();
    for (const trip of snapshot.trips) {
      if (trip.origin?.id === location.id || trip.destination?.id === location.id) seen.add(trip.id);
    }
    for (const event of snapshot.events) {
      if (event.tripId && event.location?.id === location.id) seen.add(event.tripId);
    }
    return seen.size;
  }

  function rootDistance(root, snapshot) {
    if (!Number.isFinite(gpsState.lat) || !Number.isFinite(gpsState.lng)) return Infinity;
    const coords = effectiveCoords(root, snapshot);
    return coords ? distanceMeters(gpsState, coords) : Infinity;
  }

  function reorderSmartLocationGroups(snapshot) {
    const tree = $('.km-shell-location-tree');
    const smart = $('.km-shell-location-sort button[data-mode="smart"]')?.classList.contains('active');
    if (!tree || !smart) return;
    const children = [...tree.children].filter(node => node.matches?.('.km-shell-location-node'));
    if (!children.length) return;
    const groups = [];
    let current = null;
    for (const node of children) {
      if (node.dataset.depth === '0' || !current) {
        current = { nodes: [node], id: node.dataset.shellLocationNode };
        groups.push(current);
      } else current.nodes.push(node);
    }
    const nearWindow = Math.max(2000, recognitionRadius(snapshot) * 4);
    groups.sort((a, b) => {
      const aLoc = locationById(a.id, snapshot), bLoc = locationById(b.id, snapshot);
      if (!aLoc || !bLoc) return 0;
      const aCurrent = String(a.id) === String(gpsState.matchedRootId), bCurrent = String(b.id) === String(gpsState.matchedRootId);
      if (aCurrent !== bCurrent) return aCurrent ? -1 : 1;
      const aDistance = rootDistance(aLoc, snapshot), bDistance = rootDistance(bLoc, snapshot);
      const aNear = aDistance <= nearWindow, bNear = bDistance <= nearWindow;
      if (aNear !== bNear) return aNear ? -1 : 1;
      if (aNear && bNear && Math.abs(aDistance - bDistance) > 25) return aDistance - bDistance;
      const countDiff = tripCount(bLoc, snapshot) - tripCount(aLoc, snapshot);
      if (countDiff) return countDiff;
      return String(aLoc.name || '').localeCompare(String(bLoc.name || ''), 'nl', { sensitivity: 'base' });
    });
    const currentRootOrder = children.filter(node => node.dataset.depth === '0').map(node => node.dataset.shellLocationNode);
    const desiredRootOrder = groups.map(group => group.id);
    if (currentRootOrder.join('|') === desiredRootOrder.join('|')) return;
    const fragment = document.createDocumentFragment();
    for (const group of groups) for (const node of group.nodes) fragment.appendChild(node);
    tree.appendChild(fragment);
  }

  function decorateCurrentLocation(snapshot) {
    const view = $('#kmShellLocationsView');
    if (!view || view.hidden || currentSection() !== 'locations') return;
    let status = $('#kmShellCurrentLocationStatus', view);
    if (!status) {
      status = document.createElement('div');
      status.id = 'kmShellCurrentLocationStatus';
      status.className = 'km-shell-current-location-status';
      const actions = $('.km-shell-location-actions', view);
      actions?.insertAdjacentElement('afterend', status);
    }
    status.className = 'km-shell-current-location-status';
    const button = $('[data-shell-current-location]', view);
    if (button) delete button.dataset.currentLocationId;

    if (gpsState.status === 'loading' || gpsState.status === 'idle') {
      status.textContent = 'Huidige locatie wordt bepaald…';
    } else if (gpsState.status === 'error') {
      status.classList.add('warn');
      status.textContent = gpsState.error;
    } else {
      const radius = recognitionRadius(snapshot);
      const matched = gpsState.matchedId ? locationById(gpsState.matchedId, snapshot) : null;
      const nearest = gpsState.nearestId ? locationById(gpsState.nearestId, snapshot) : null;
      if (matched) {
        status.classList.add('good');
        status.innerHTML = `<strong>Huidige locatie: ${locationPath(matched, snapshot)}</strong> · ${formatDistance(gpsState.distance)}${gpsState.accuracy ? ` · GPS ±${Math.round(gpsState.accuracy)} m` : ''}`;
        if (button) {
          button.textContent = `✓ ${matched.name}`;
          button.dataset.currentLocationId = matched.id;
        }
      } else if (nearest) {
        status.innerHTML = `Geen opgeslagen locatie binnen <strong>${Math.round(radius)} m</strong>. Dichtstbij: ${locationPath(nearest, snapshot)} · ${formatDistance(gpsState.nearestDistance)}.`;
        if (button) button.textContent = 'Huidige locatie +';
      } else {
        status.textContent = 'Er zijn nog geen locaties met GPS om de huidige locatie mee te vergelijken.';
        if (button) button.textContent = 'Huidige locatie +';
      }
    }

    $$('.km-shell-location-node', view).forEach(node => node.classList.toggle('km-current-location', String(node.dataset.shellLocationNode) === String(gpsState.matchedId)));
  }

  function decorateLocations() {
    if (decorating) return;
    decorating = true;
    try {
      const snapshot = readData();
      decorateCurrentLocation(snapshot);
      reorderSmartLocationGroups(snapshot);
    } finally {
      decorating = false;
    }
  }

  function scheduleDecorate() {
    if (decorateQueued) return;
    decorateQueued = true;
    requestAnimationFrame(() => {
      decorateQueued = false;
      decorateLocations();
    });
  }

  function bindEvents() {
    document.addEventListener('click', event => {
      const currentButton = event.target.closest?.('[data-shell-current-location]');
      if (currentButton?.dataset.currentLocationId) {
        event.preventDefault();
        event.stopImmediatePropagation();
        const id = currentButton.dataset.currentLocationId;
        setTimeout(() => {
          const edit = $(`[data-shell-edit-location="${CSS.escape(id)}"]`);
          if (edit) edit.click();
        }, 0);
        return;
      }
      const locationNav = event.target.closest?.('[data-shell-section="locations"]');
      if (locationNav) setTimeout(() => requestCurrentLocation(true), 60);
      const sort = event.target.closest?.('[data-action="location-sort"]');
      if (sort) setTimeout(scheduleDecorate, 30);
    }, true);

    window.addEventListener('storage', event => {
      if ([DATA_KEY, TIME_KEY].includes(event.key)) scheduleDecorate();
    });

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && currentSection() === 'locations') requestCurrentLocation(true);
    });

    const observer = new MutationObserver(mutations => {
      if (mutations.length && mutations.every(mutation => mutation.target.closest?.('#kmShellCurrentLocationStatus'))) return;
      updateVersionLabel();
      prepareTimeFrame();
      if (document.body.classList.contains('km-shell-locations-mode') && currentSection() === 'locations') {
        requestCurrentLocation(false);
        scheduleDecorate();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  function init() {
    injectStyle();
    updateVersionLabel();
    prepareTimeFrame();
    bindEvents();
    if (document.body.classList.contains('km-shell-locations-mode') || currentSection() === 'locations') requestCurrentLocation(true);
    scheduleDecorate();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();

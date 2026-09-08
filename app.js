const DB_NAME = 'kmreg-db';
const DB_VERSION = 1;
const STORES = ['settings', 'locations', 'trips', 'events', 'trackPoints', 'appState'];

const DEFAULT_SETTINGS = {
  id: 'main',
  name: '',
  vehicleBrand: '',
  vehicleModel: '',
  plate: '',
  initialOdometer: '',
  registrationStart: new Date().toISOString().slice(0, 10),
  reportEmail: '',
  recognitionRadius: 500,
  googleApiKey: '',
  defaultReportPeriod: 'week'
};

let db;
let state = {
  view: 'home',
  settings: { ...DEFAULT_SETTINGS },
  locations: [],
  trips: [],
  events: [],
  activeTrip: null,
  selectedWeekStart: startOfISOWeek(new Date()),
  reportRange: null,
  gps: { watchId: null, intervalId: null, latest: null }
};

const app = document.getElementById('app');
const modal = document.getElementById('modal');
const modalContent = document.getElementById('modalContent');
const toastEl = document.getElementById('toast');

document.getElementById('todayLabel').textContent = new Intl.DateTimeFormat('nl-NL', {
  weekday: 'long', day: 'numeric', month: 'long'
}).format(new Date());

init();

async function init() {
  db = await openDb();
  state.settings = { ...DEFAULT_SETTINGS, ...(await idbGet('settings', 'main') || {}) };
  if (!(await idbGet('settings', 'main'))) await idbPut('settings', state.settings);
  await refreshData();
  bindGlobalEvents();
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js').catch(() => {});
  if (state.activeTrip) startGpsTracking(state.activeTrip.id).catch(() => {});
  render();
}

function openDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = () => {
      const d = req.result;
      for (const store of STORES) {
        if (!d.objectStoreNames.contains(store)) d.createObjectStore(store, { keyPath: 'id' });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function tx(store, mode = 'readonly') { return db.transaction(store, mode).objectStore(store); }
function idbGet(store, id) { return new Promise((res, rej) => { const r = tx(store).get(id); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); }); }
function idbGetAll(store) { return new Promise((res, rej) => { const r = tx(store).getAll(); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); }); }
function idbPut(store, value) { return new Promise((res, rej) => { const r = tx(store, 'readwrite').put(value); r.onsuccess = () => res(value); r.onerror = () => rej(r.error); }); }
function idbDelete(store, id) { return new Promise((res, rej) => { const r = tx(store, 'readwrite').delete(id); r.onsuccess = () => res(); r.onerror = () => rej(r.error); }); }
function idbClear(store) { return new Promise((res, rej) => { const r = tx(store, 'readwrite').clear(); r.onsuccess = () => res(); r.onerror = () => rej(r.error); }); }

async function refreshData() {
  [state.locations, state.trips, state.events] = await Promise.all([
    idbGetAll('locations'), idbGetAll('trips'), idbGetAll('events')
  ]);
  state.trips.sort((a, b) => new Date(b.departureTime) - new Date(a.departureTime));
  state.events.sort((a, b) => new Date(b.time) - new Date(a.time));
  state.activeTrip = await idbGet('appState', 'activeTrip') || null;
}

function bindGlobalEvents() {
  document.addEventListener('click', async (e) => {
    const viewBtn = e.target.closest('[data-view]');
    if (viewBtn) {
      state.view = viewBtn.dataset.view;
      render();
      return;
    }
    const action = e.target.closest('[data-action]')?.dataset.action;
    if (!action) return;
    try {
      if (action === 'go-settings') { state.view = 'settings'; render(); }
      if (action === 'start-trip') await openStartTrip();
      if (action === 'arrive-trip') await openArrival();
      if (action === 'tank') await openTank();
      if (action === 'add-trip') await openManualTrip();
      if (action === 'private-km') await openPrivateKm();
      if (action === 'close-modal') closeModal();
      if (action === 'week-prev') { state.selectedWeekStart = addDays(state.selectedWeekStart, -7); render(); }
      if (action === 'week-next') { state.selectedWeekStart = addDays(state.selectedWeekStart, 7); render(); }
      if (action === 'week-now') { state.selectedWeekStart = startOfISOWeek(new Date()); render(); }
      if (action === 'add-location') await openLocationEditor();
      if (action === 'add-current-location') await openLocationEditor(null, true);
      if (action === 'edit-location') await openLocationEditor(e.target.closest('[data-id]').dataset.id);
      if (action === 'delete-location') await deleteLocation(e.target.closest('[data-id]').dataset.id);
      if (action === 'edit-trip') await openTripEditor(e.target.closest('[data-id]').dataset.id);
      if (action === 'delete-trip') await deleteTrip(e.target.closest('[data-id]').dataset.id);
      if (action === 'report-email') sendReportEmail();
      if (action === 'report-csv') downloadReportCsv();
      if (action === 'report-print') window.print();
      if (action === 'report-share') await shareReport();
      if (action === 'export-data') await exportData();
      if (action === 'import-data') document.getElementById('importFile')?.click();
      if (action === 'clear-data') await clearAllData();
    } catch (err) {
      console.error(err);
      toast(err.message || 'Er ging iets mis');
    }
  });

  document.addEventListener('submit', async (e) => {
    const form = e.target;
    if (!(form instanceof HTMLFormElement)) return;
    e.preventDefault();
    try {
      if (form.id === 'settingsForm') await saveSettings(new FormData(form));
      if (form.id === 'locationForm') await saveLocation(new FormData(form));
      if (form.id === 'startTripForm') await saveStartTrip(new FormData(form));
      if (form.id === 'arrivalForm') await saveArrival(new FormData(form));
      if (form.id === 'tankForm') await saveTank(new FormData(form));
      if (form.id === 'manualTripForm') await saveManualTrip(new FormData(form));
      if (form.id === 'privateKmForm') await savePrivateKm(new FormData(form));
      if (form.id === 'tripEditForm') await saveTripEdit(new FormData(form));
      if (form.id === 'reportForm') { state.reportRange = rangeFromReportForm(new FormData(form)); render(); }
    } catch (err) {
      console.error(err);
      toast(err.message || 'Opslaan mislukt');
    }
  });

  document.addEventListener('change', (e) => {
    if (e.target.id === 'reportPeriod') updateReportFormFields();
    if (e.target.id === 'arrivalCategory') updateArrivalPrivateUi();
  });
  document.addEventListener('input', (e) => {
    if (e.target.id === 'arrivalEndOdo') updateArrivalDistancePreview();
    if (e.target.id === 'manualEndOdo' || e.target.id === 'manualStartOdo') updateManualDistancePreview();
  });

  document.addEventListener('change', async (e) => {
    if (e.target.id === 'importFile' && e.target.files?.[0]) await importData(e.target.files[0]);
  });
}

function render() {
  document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.toggle('is-active', btn.dataset.view === state.view));
  if (state.view === 'home') renderHome();
  if (state.view === 'week') renderWeek();
  if (state.view === 'locations') renderLocations();
  if (state.view === 'reports') renderReports();
  if (state.view === 'settings') renderSettings();
}

function renderHome() {
  const last = getLastEndpointSync();
  const weekTrips = tripsInRange(startOfISOWeek(new Date()), addDays(startOfISOWeek(new Date()), 7));
  const total = sum(weekTrips, 'actualKm');
  const active = state.activeTrip;
  app.innerHTML = `
    <section class="hero">
      <div class="kicker">${active ? 'Actieve rit' : 'Gereed voor vertrek'}</div>
      ${active ? `
        <h2>${esc(active.origin?.name || active.origin?.address || 'Vertrek')} → ${esc(active.expectedDestination?.name || active.expectedDestination?.address || 'bestemming')}</h2>
        <p>Start ${fmtOdo(active.startOdometer)} km · voorstel ${fmtKm(active.proposedRouteKm)} km · GPS ${active.gpsTracking ? 'actief' : 'gereed'}</p>
        <div class="status-row"><span class="pill"><span class="dot"></span>Rit gestart ${formatTime(active.departureTime)}</span></div>
      ` : `
        <h2>${last ? `${fmtOdo(last.odometer)} km` : 'Stel eerst je auto in'}</h2>
        <p>${last ? `Laatste locatie: ${esc(last.location?.name || last.location?.address || 'onbekend')}` : 'Voer in Instellingen de auto en beginstand in.'}</p>
      `}
    </section>

    <div class="grid-2">
      <button class="action-card" data-action="start-trip" ${active ? 'disabled' : ''}><div class="ico">↗</div><strong>Vertrek</strong><small>Startpunt, bestemming, routevoorstel en GPS.</small></button>
      <button class="action-card" data-action="arrive-trip" ${active ? '' : 'disabled'}><div class="ico">◎</div><strong>Aankomst</strong><small>Locatie herkennen, eindstand en ritverdeling.</small></button>
      <button class="action-card" data-action="add-trip"><div class="ico">＋</div><strong>Rit toevoegen</strong><small>Een rit handmatig of achteraf registreren.</small></button>
      <button class="action-card" data-action="tank"><div class="ico">⛽︎</div><strong>Tanken</strong><small>Meetpunt met kilometerstand en locatie; geen ritonderbreking.</small></button>
      <button class="action-card" data-action="private-km"><div class="ico">⌁</div><strong>Privé kilometers</strong><small>Ken een privédeel toe aan een bestaande rit.</small></button>
      <button class="action-card" data-view="week"><div class="ico">◫</div><strong>Deze week</strong><small>${fmtKm(total)} km verdeeld over ${weekTrips.length} ritten.</small></button>
    </div>

    <div class="section"><div class="section-title"><h2>Laatste ritten</h2></div>
      ${renderTripList(state.trips.slice(0, 4))}
    </div>
  `;
}

function renderWeek() {
  const start = state.selectedWeekStart;
  const end = addDays(start, 7);
  const trips = tripsInRange(start, end);
  const tanks = state.events.filter(x => x.type === 'tank' && inRange(new Date(x.time), start, end));
  const totals = tripTotals(trips);
  app.innerHTML = `
    <div class="week-nav">
      <button class="mini-btn" data-action="week-prev">‹</button>
      <div class="center"><h2>Week ${isoWeek(start)} · ${start.getFullYear()}</h2><small>${formatDate(start)} – ${formatDate(addDays(end,-1))}</small></div>
      <button class="mini-btn" data-action="week-next">›</button>
    </div>
    <div class="button-row no-print"><button class="btn ghost" data-action="week-now">Huidige week</button><button class="btn secondary" data-view="reports">Rapport van deze week</button></div>
    <div class="section">
      <div class="grid-2">
        ${metric('Totaal auto', `${fmtKm(totals.total)} km`)}
        ${metric('Zakelijk', `${fmtKm(totals.business)} km`)}
        ${metric('Woon-werk', `${fmtKm(totals.commute)} km`)}
        ${metric('Privé', `${fmtKm(totals.private)} km`)}
      </div>
    </div>
    <div class="section"><div class="section-title"><h2>Ritten</h2><span class="muted">${trips.length}</span></div>${renderTripList(trips)}</div>
    <div class="section"><div class="section-title"><h2>Tankmomenten</h2><span class="muted">${tanks.length}</span></div>
      ${tanks.length ? `<div class="list">${tanks.map(t => `<div class="list-item"><div class="list-main"><strong>${esc(t.location?.name || t.location?.address || 'Tanklocatie')}</strong><small>${formatDateTime(t.time)}</small></div><div class="nowrap">${fmtOdo(t.odometer)} km</div></div>`).join('')}</div>` : '<div class="empty">Geen tankregistraties in deze week.</div>'}
    </div>
  `;
}

function renderLocations() {
  const sorted = [...state.locations].sort((a,b) => (b.useCount||0)-(a.useCount||0) || a.name.localeCompare(b.name));
  app.innerHTML = `
    <div class="section-title"><div><div class="kicker">Herkenning binnen ${state.settings.recognitionRadius || 500} m</div><h2>Bekende locaties</h2></div></div>
    <div class="button-row"><button class="btn" data-action="add-current-location">Gebruik huidige locatie</button><button class="btn secondary" data-action="add-location">Handmatig toevoegen</button></div>
    <div class="section">
      ${sorted.length ? `<div class="list">${sorted.map(l => `
        <div class="list-item" data-id="${l.id}"><div class="list-main"><strong>${esc(l.name)}</strong><small>${esc(l.address || `${l.lat?.toFixed(5)}, ${l.lng?.toFixed(5)}`)}</small><small>${esc(typeLabel(l.type))} · ${l.useCount || 0}× gebruikt</small></div><div class="list-actions"><button class="mini-btn" data-action="edit-location">Wijzig</button><button class="mini-btn" data-action="delete-location">×</button></div></div>
      `).join('')}</div>` : '<div class="empty">Nog geen bekende locaties. Voeg thuis, werk en veelbezochte locaties toe.</div>'}
    </div>
  `;
}

function renderReports() {
  if (!state.reportRange) state.reportRange = defaultReportRange();
  const { start, end, label } = state.reportRange;
  const trips = tripsInRange(start, end);
  const totals = tripTotals(trips);
  app.innerHTML = `
    <div class="no-print">
      <div class="section-title"><div><div class="kicker">Verslag</div><h2>${esc(label)}</h2></div></div>
      <form id="reportForm" class="card">
        <div class="form-group"><label>Periode</label><select name="period" id="reportPeriod">
          <option value="week" ${state.settings.defaultReportPeriod==='week'?'selected':''}>Week</option>
          <option value="month" ${state.settings.defaultReportPeriod==='month'?'selected':''}>Maand</option>
          <option value="custom">Zelf kiezen</option>
        </select></div>
        <div id="reportDynamicFields">${reportFormFields(state.settings.defaultReportPeriod)}</div>
        <button class="btn full" type="submit">Toon verslag</button>
      </form>
      <div class="grid-2">
        ${metric('Totaal', `${fmtKm(totals.total)} km`)}${metric('Ritten', String(trips.length))}${metric('Zakelijk', `${fmtKm(totals.business)} km`)}${metric('Privé', `${fmtKm(totals.private)} km`)}
      </div>
      <div class="section"><div class="button-row">
        <button class="btn" data-action="report-email">E-mail openen</button>
        <button class="btn secondary" data-action="report-share">Deel CSV</button>
        <button class="btn secondary" data-action="report-csv">Download CSV</button>
        <button class="btn secondary" data-action="report-print">Print / PDF</button>
      </div></div>
      <div class="notice">De statische GitHub Pages-versie kan een e-mail voorbereiden of een rapport delen. Volledig automatische verzending op een vast tijdstip vraagt later om een kleine backend/serverless functie.</div>
      <div class="section"><div class="section-title"><h2>Ritten in verslag</h2></div>${renderTripList(trips)}</div>
    </div>
    ${renderPrintableReport(trips, totals, label)}
  `;
}

function renderSettings() {
  const s = state.settings;
  app.innerHTML = `
    <form id="settingsForm">
      <div class="section-title"><div><div class="kicker">Basisgegevens</div><h2>Instellingen</h2></div></div>
      <div class="card">
        <h3>Bestuurder & auto</h3>
        ${field('Naam', 'name', s.name, 'text', 'Voor op het rapport')}
        <div class="grid-2">${field('Automerk', 'vehicleBrand', s.vehicleBrand)}${field('Model / type', 'vehicleModel', s.vehicleModel)}</div>
        <div class="grid-2">${field('Kenteken', 'plate', s.plate)}${field('Beginstand km', 'initialOdometer', s.initialOdometer, 'number')}</div>
        ${field('Start registratie', 'registrationStart', s.registrationStart, 'date')}
      </div>
      <div class="card">
        <h3>Locatie & route</h3>
        ${field('Herkenningsstraal (meter)', 'recognitionRadius', s.recognitionRadius, 'number')}
        ${field('Google Maps API-key', 'googleApiKey', s.googleApiKey, 'password', 'Voor verkeersafhankelijke routevoorstellen en adresherkenning. Beperk deze sleutel in Google Cloud op jouw GitHub Pages-domein.')}
        <div class="notice warning">Zonder Google-key blijft de registratie werken. Het routevoorstel gebruikt dan eerdere A→B-ritten; als die ontbreken volgt alleen een grove afstandsschatting.</div>
      </div>
      <div class="card">
        <h3>Rapportage</h3>
        ${field('E-mailadres', 'reportEmail', s.reportEmail, 'email')}
        <div class="form-group"><label>Standaardperiode</label><select name="defaultReportPeriod"><option value="week" ${s.defaultReportPeriod==='week'?'selected':''}>Week</option><option value="month" ${s.defaultReportPeriod==='month'?'selected':''}>Maand</option></select></div>
      </div>
      <button class="btn full" type="submit">Instellingen opslaan</button>
    </form>
    <div class="section"><div class="section-title"><h2>Data</h2></div><div class="button-row"><button class="btn secondary" data-action="export-data">Backup exporteren</button><button class="btn secondary" data-action="import-data">Backup importeren</button></div><input id="importFile" type="file" accept="application/json" hidden><div style="height:10px"></div><button class="btn danger full" data-action="clear-data">Alle ritdata wissen</button></div>
  `;
}

function field(label, name, value='', type='text', hint='') {
  return `<div class="form-group"><label>${esc(label)}</label><input type="${type}" name="${name}" value="${esc(value ?? '')}">${hint?`<div class="hint">${esc(hint)}</div>`:''}</div>`;
}
function metric(label, value) { return `<div class="metric"><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`; }

function renderTripList(trips) {
  if (!trips.length) return '<div class="empty">Nog geen ritten in deze selectie.</div>';
  return `<div class="list">${trips.map(t => `
    <div class="list-item trip-row" data-id="${t.id}">
      <div class="trip-date">${new Intl.DateTimeFormat('nl-NL',{weekday:'short',day:'2-digit',month:'2-digit'}).format(new Date(t.departureTime))}<br>${formatTime(t.departureTime)}</div>
      <div class="trip-path"><strong>${esc(t.origin?.name || t.origin?.address || 'Onbekend')} → ${esc(t.destination?.name || t.destination?.address || 'Onbekend')}</strong><small>${esc(categoryLabel(t.category))}${t.reason ? ` · ${esc(t.reason)}` : ''}</small><small>${fmtOdo(t.startOdometer)} → ${fmtOdo(t.endOdometer)} km${t.privateKm ? ` · ${fmtKm(t.privateKm)} km privé` : ''}</small></div>
      <div><div class="trip-km">${fmtKm(t.actualKm)} km</div><button class="mini-btn" data-action="edit-trip">Wijzig</button></div>
    </div>`).join('')}</div>`;
}

async function openStartTrip() {
  if (state.activeTrip) return toast('Er is al een actieve rit.');
  const base = await getLastEndpoint();
  let gps = null, address = '';
  try { gps = await getCurrentPosition(); address = await reverseGeocode(gps.lat, gps.lng); } catch {}
  const suggestions = gps ? matchKnownLocations(gps) : [];
  let origin = base?.location || (suggestions[0]?.location ?? (gps ? currentLocationObject(gps, address) : null));
  const startOdo = base?.odometer ?? Number(state.settings.initialOdometer || 0);
  if (!origin && !state.locations.length) return toast('Voeg eerst een locatie toe of geef locatietoegang.');

  openModal(`
    <div class="modal-head"><h2>Vertrek</h2><button class="close" data-action="close-modal">×</button></div>
    <form id="startTripForm">
      <input type="hidden" name="originJson" value='${attr(JSON.stringify(origin))}'>
      <div class="card"><div class="kicker">Beginpunt uit vorige rit</div><h3>${esc(origin?.name || origin?.address || 'Onbekend')}</h3><p>${esc(origin?.address || '')}</p></div>
      ${gps && base?.location && distanceMeters(gps, base.location) > (state.settings.recognitionRadius||500) ? `<div class="notice warning">Je GPS staat meer dan ${state.settings.recognitionRadius||500} meter van het laatste bestemmingspunt. Controleer of er een rit ontbreekt.</div>` : ''}
      <div class="form-group"><label>Startkilometerstand</label><input name="startOdometer" type="number" step="1" required value="${startOdo || ''}"><div class="hint">Automatisch de eindstand van de vorige rit. Aanpasbaar voor correcties.</div></div>
      <div class="form-group"><label>Verwachte bestemming</label><select name="destinationId" required><option value="">Kies locatie…</option>${locationOptions()}</select></div>
      <div class="form-group"><label>Vertrektijd</label><input name="departureTime" type="datetime-local" value="${toLocalInput(new Date())}" required></div>
      <div class="notice">Bij opslaan berekenen we de actuele verkeersafhankelijke route als een Google Maps API-key is ingesteld. De GPS-track slaat tijdens de actieve rit maximaal één punt per minuut op zolang de browser dit op iOS toelaat.</div>
      <button class="btn full" type="submit">Rit starten</button>
    </form>`);
}

async function saveStartTrip(fd) {
  const origin = JSON.parse(fd.get('originJson'));
  const destination = state.locations.find(l => l.id === fd.get('destinationId'));
  if (!destination) throw new Error('Kies een bestemming.');
  const startOdometer = Number(fd.get('startOdometer'));
  if (!Number.isFinite(startOdometer)) throw new Error('Vul een geldige kilometerstand in.');
  const departureTime = new Date(fd.get('departureTime')).toISOString();
  const route = await getRouteProposal(origin, destination, departureTime);
  const active = {
    id: 'activeTrip', tripId: crypto.randomUUID(),
    origin: snapshotLocation(origin), expectedDestination: snapshotLocation(destination),
    startOdometer, departureTime,
    proposedRouteKm: route.km, routeProvider: route.provider, routeDurationMin: route.durationMin,
    gpsTracking: true, startGps: route.startGps || (origin.lat != null ? {lat:origin.lat,lng:origin.lng}:null),
    createdAt: new Date().toISOString()
  };
  await idbPut('appState', active);
  state.activeTrip = active;
  incrementLocationUse(origin.id);
  await startGpsTracking(active.tripId);
  closeModal();
  render();
  toast(`Rit gestart · voorstel ${fmtKm(route.km)} km (${route.providerLabel})`);
}

async function openArrival() {
  const active = state.activeTrip;
  if (!active) return toast('Er is geen actieve rit.');
  let gps = null, address = '';
  try { gps = await getCurrentPosition(); address = await reverseGeocode(gps.lat, gps.lng); } catch {}
  const matches = gps ? matchKnownLocations(gps) : [];
  let defaultId = '';
  const expected = state.locations.find(l => l.id === active.expectedDestination?.id);
  if (expected && gps && distanceMeters(gps, expected) <= (state.settings.recognitionRadius || 500)) defaultId = expected.id;
  else if (matches[0]) defaultId = matches[0].location.id;
  const current = gps ? currentLocationObject(gps, address) : null;
  const suggestedEnd = Math.round(Number(active.startOdometer) + Number(active.proposedRouteKm || 0));
  openModal(`
    <div class="modal-head"><h2>Aankomst</h2><button class="close" data-action="close-modal">×</button></div>
    <form id="arrivalForm">
      ${gps ? `<div class="notice ${defaultId ? 'success':''}">${matches.length ? `Locatieherkenning: ${matches.map(m=>`${esc(m.location.name)} (${Math.round(m.distance)} m)`).join(', ')}` : `Geen bekende locatie binnen ${state.settings.recognitionRadius||500} m. Huidige GPS-locatie wordt voorgesteld.`}</div>` : '<div class="notice warning">GPS kon niet worden opgehaald. Kies een bekende locatie.</div>'}
      <div class="form-group"><label>Bestemmingslocatie</label><select name="destinationId" id="arrivalDestination"><option value="">Kies locatie…</option>${locationOptions(defaultId)}${current ? `<option value="__current__" ${!defaultId?'selected':''}>Huidige locatie · ${esc(current.address)}</option>`:''}</select></div>
      <input type="hidden" name="currentJson" value='${attr(JSON.stringify(current))}'>
      <div class="grid-2"><div class="metric"><span>Startstand</span><strong>${fmtOdo(active.startOdometer)}</strong></div><div class="metric"><span>Routevoorstel</span><strong>${fmtKm(active.proposedRouteKm)} km</strong></div></div>
      <div class="form-group" style="margin-top:15px"><label>Eindkilometerstand</label><input id="arrivalEndOdo" name="endOdometer" type="number" step="1" required value="${suggestedEnd}"><div id="arrivalDistancePreview" class="hint">Werkelijk gereden: ${fmtKm(suggestedEnd-active.startOdometer)} km</div></div>
      <div class="form-group"><label>Type rit</label><select name="category" id="arrivalCategory"><option value="commute">Woon-werk</option><option value="business">Zakelijk</option><option value="private">Privé</option></select></div>
      <div class="form-group"><label>Reden / omschrijving</label><input name="reason" placeholder="Bijv. overleg, projectbezoek of afspraak"></div>
      <div class="form-group" id="privateKmGroup"><label>Privékilometers binnen deze rit</label><input name="privateKm" type="number" min="0" step="1" value="0"><div class="hint">De resterende kilometers worden toegekend aan woon-werk of zakelijk.</div></div>
      <div class="form-group"><label>Aankomsttijd</label><input name="arrivalTime" type="datetime-local" value="${toLocalInput(new Date())}" required></div>
      <button class="btn full" type="submit">Rit afronden</button>
    </form>`);
}

function updateArrivalDistancePreview() {
  const el = document.getElementById('arrivalEndOdo');
  const out = document.getElementById('arrivalDistancePreview');
  if (!el || !out || !state.activeTrip) return;
  const km = Number(el.value) - Number(state.activeTrip.startOdometer);
  out.textContent = Number.isFinite(km) ? `Werkelijk gereden: ${fmtKm(km)} km` : '';
}
function updateArrivalPrivateUi() {
  const sel = document.getElementById('arrivalCategory'); const group = document.getElementById('privateKmGroup');
  if (!sel || !group) return; group.style.display = sel.value === 'private' ? 'none' : '';
}

async function saveArrival(fd) {
  const active = state.activeTrip;
  if (!active) throw new Error('Geen actieve rit gevonden.');
  let destination = fd.get('destinationId') === '__current__' ? JSON.parse(fd.get('currentJson')) : state.locations.find(l => l.id === fd.get('destinationId'));
  if (!destination) throw new Error('Kies een bestemmingslocatie.');
  const endOdometer = Number(fd.get('endOdometer'));
  const actualKm = endOdometer - Number(active.startOdometer);
  if (!Number.isFinite(actualKm) || actualKm < 0) throw new Error('De eindstand moet gelijk of hoger zijn dan de startstand.');
  const category = fd.get('category');
  const requestedPrivate = category === 'private' ? actualKm : Number(fd.get('privateKm') || 0);
  if (requestedPrivate < 0 || requestedPrivate > actualKm) throw new Error('Privékilometers kunnen niet hoger zijn dan het totaal.');
  const split = splitKilometers(actualKm, category, requestedPrivate);
  const trip = {
    id: active.tripId,
    departureTime: active.departureTime,
    arrivalTime: new Date(fd.get('arrivalTime')).toISOString(),
    origin: active.origin,
    destination: snapshotLocation(destination),
    startOdometer: Number(active.startOdometer), endOdometer, actualKm,
    proposedRouteKm: Number(active.proposedRouteKm || 0), routeProvider: active.routeProvider,
    category, reason: String(fd.get('reason') || '').trim(),
    privateKm: split.private, businessKm: split.business, commuteKm: split.commute,
    createdAt: active.createdAt, completedAt: new Date().toISOString()
  };
  await idbPut('trips', trip);
  await idbPut('appState', { id:'lastEndpoint', location: trip.destination, odometer:endOdometer, time:trip.arrivalTime });
  await idbDelete('appState', 'activeTrip');
  incrementLocationUse(destination.id);
  stopGpsTracking();
  await refreshData();
  closeModal(); render(); toast(`Rit opgeslagen: ${fmtKm(actualKm)} km`);
}

async function openTank() {
  const base = await getLastEndpoint();
  let gps=null,address=''; try { gps=await getCurrentPosition(); address=await reverseGeocode(gps.lat,gps.lng); } catch {}
  const matches = gps ? matchKnownLocations(gps) : [];
  const current = gps ? currentLocationObject(gps,address) : null;
  openModal(`
    <div class="modal-head"><h2>Tanken</h2><button class="close" data-action="close-modal">×</button></div>
    <form id="tankForm">
      <div class="notice">Dit is alleen een kilometerteller-meetpunt. Het verandert nooit het vertrek- of bestemmingspunt van een actieve of volgende A→B-rit.</div>
      <div class="form-group"><label>Kilometerstand auto</label><input name="odometer" type="number" step="1" required value="${base?.odometer || state.activeTrip?.startOdometer || ''}"></div>
      <div class="form-group"><label>Tanklocatie</label><select name="locationId"><option value="">Kies locatie…</option>${locationOptions(matches[0]?.location.id || '')}${current?`<option value="__current__" ${matches.length?'':'selected'}>Huidige locatie · ${esc(current.address)}</option>`:''}</select></div>
      <input type="hidden" name="currentJson" value='${attr(JSON.stringify(current))}'>
      <div class="grid-2">${field('Liters (optioneel)','liters','','number')}${field('Bedrag € (optioneel)','amount','','number')}</div>
      <div class="form-group"><label>Tijd</label><input name="time" type="datetime-local" value="${toLocalInput(new Date())}" required></div>
      <button class="btn full" type="submit">Tankmoment opslaan</button>
    </form>`);
}

async function saveTank(fd) {
  const location = fd.get('locationId') === '__current__' ? JSON.parse(fd.get('currentJson')) : state.locations.find(l=>l.id===fd.get('locationId'));
  if (!location) throw new Error('Kies een tanklocatie.');
  const event = { id:crypto.randomUUID(), type:'tank', time:new Date(fd.get('time')).toISOString(), odometer:Number(fd.get('odometer')), location:snapshotLocation(location), liters:numOrNull(fd.get('liters')), amount:numOrNull(fd.get('amount')) };
  await idbPut('events', event); incrementLocationUse(location.id); await refreshData(); closeModal(); render(); toast('Tankmoment opgeslagen zonder de ritketen te wijzigen.');
}

async function openManualTrip() {
  const base = await getLastEndpoint();
  openModal(`
    <div class="modal-head"><h2>Rit toevoegen</h2><button class="close" data-action="close-modal">×</button></div>
    <form id="manualTripForm">
      <div class="grid-2"><div class="form-group"><label>Vertrek</label><select name="originId" required><option value="">Kies…</option>${locationOptions(base?.location?.id||'')}</select></div><div class="form-group"><label>Aankomst</label><select name="destinationId" required><option value="">Kies…</option>${locationOptions()}</select></div></div>
      <div class="grid-2"><div class="form-group"><label>Vertrektijd</label><input name="departureTime" type="datetime-local" value="${toLocalInput(new Date())}" required></div><div class="form-group"><label>Aankomsttijd</label><input name="arrivalTime" type="datetime-local" value="${toLocalInput(new Date())}" required></div></div>
      <div class="grid-2"><div class="form-group"><label>Startstand</label><input id="manualStartOdo" name="startOdometer" type="number" value="${base?.odometer||''}" required></div><div class="form-group"><label>Eindstand</label><input id="manualEndOdo" name="endOdometer" type="number" required></div></div>
      <div id="manualDistancePreview" class="notice">Werkelijk gereden wordt berekend uit de kilometerstanden.</div>
      <div class="form-group"><label>Type</label><select name="category"><option value="commute">Woon-werk</option><option value="business">Zakelijk</option><option value="private">Privé</option></select></div>
      ${field('Reden / omschrijving','reason')}${field('Privédeel km','privateKm','0','number')}
      <button class="btn full" type="submit">Rit opslaan</button>
    </form>`);
}
function updateManualDistancePreview(){const a=Number(document.getElementById('manualStartOdo')?.value),b=Number(document.getElementById('manualEndOdo')?.value),o=document.getElementById('manualDistancePreview');if(o&&Number.isFinite(a)&&Number.isFinite(b))o.textContent=`Werkelijk gereden: ${fmtKm(b-a)} km`;}
async function saveManualTrip(fd) {
  const origin=state.locations.find(l=>l.id===fd.get('originId')), destination=state.locations.find(l=>l.id===fd.get('destinationId'));
  if(!origin||!destination) throw new Error('Kies vertrek en aankomst.');
  const start=Number(fd.get('startOdometer')), end=Number(fd.get('endOdometer')), actual=end-start;
  if(actual<0) throw new Error('Eindstand moet hoger zijn dan startstand.');
  const category=fd.get('category'), requested=category==='private'?actual:Number(fd.get('privateKm')||0); if(requested>actual) throw new Error('Privédeel is hoger dan totaal.');
  const split=splitKilometers(actual,category,requested);
  const trip={id:crypto.randomUUID(),departureTime:new Date(fd.get('departureTime')).toISOString(),arrivalTime:new Date(fd.get('arrivalTime')).toISOString(),origin:snapshotLocation(origin),destination:snapshotLocation(destination),startOdometer:start,endOdometer:end,actualKm:actual,proposedRouteKm:null,routeProvider:'manual',category,reason:String(fd.get('reason')||''),privateKm:split.private,businessKm:split.business,commuteKm:split.commute,createdAt:new Date().toISOString(),completedAt:new Date().toISOString()};
  await idbPut('trips',trip); incrementLocationUse(origin.id); incrementLocationUse(destination.id);
  const last=await getLastEndpoint(); if(!last?.time || new Date(trip.arrivalTime)>=new Date(last.time)) await idbPut('appState',{id:'lastEndpoint',location:trip.destination,odometer:end,time:trip.arrivalTime});
  await refreshData(); closeModal(); render(); toast('Rit toegevoegd.');
}

async function openPrivateKm() {
  if (!state.trips.length) return toast('Er zijn nog geen ritten.');
  openModal(`<div class="modal-head"><h2>Privékilometers toekennen</h2><button class="close" data-action="close-modal">×</button></div><form id="privateKmForm"><div class="form-group"><label>Rit</label><select name="tripId">${state.trips.slice(0,30).map(t=>`<option value="${t.id}">${formatDateTime(t.departureTime)} · ${esc(t.origin?.name||'')} → ${esc(t.destination?.name||'')} · ${fmtKm(t.actualKm)} km</option>`).join('')}</select></div>${field('Privékilometers binnen rit','privateKm','0','number')}<button class="btn full">Opslaan</button></form>`);
}
async function savePrivateKm(fd) {
  const trip=state.trips.find(t=>t.id===fd.get('tripId')); if(!trip) throw new Error('Rit niet gevonden.');
  const p=Number(fd.get('privateKm')||0); if(p<0||p>trip.actualKm) throw new Error('Privédeel moet tussen 0 en het totaal liggen.');
  const split=splitKilometers(trip.actualKm,trip.category,p); Object.assign(trip,{privateKm:split.private,businessKm:split.business,commuteKm:split.commute});
  await idbPut('trips',trip); await refreshData(); closeModal(); render(); toast('Privéverdeling bijgewerkt.');
}

async function openTripEditor(id) {
  const t=state.trips.find(x=>x.id===id); if(!t)return;
  openModal(`<div class="modal-head"><h2>Rit wijzigen</h2><button class="close" data-action="close-modal">×</button></div><form id="tripEditForm"><input type="hidden" name="id" value="${t.id}"><div class="card"><strong>${esc(t.origin?.name||t.origin?.address||'')} → ${esc(t.destination?.name||t.destination?.address||'')}</strong><p>${formatDateTime(t.departureTime)}</p></div><div class="grid-2">${field('Startstand','startOdometer',t.startOdometer,'number')}${field('Eindstand','endOdometer',t.endOdometer,'number')}</div><div class="form-group"><label>Type</label><select name="category"><option value="commute" ${t.category==='commute'?'selected':''}>Woon-werk</option><option value="business" ${t.category==='business'?'selected':''}>Zakelijk</option><option value="private" ${t.category==='private'?'selected':''}>Privé</option></select></div>${field('Reden','reason',t.reason||'')}${field('Privédeel km','privateKm',t.privateKm||0,'number')}<button class="btn full">Wijzigingen opslaan</button><div style="height:10px"></div><button class="btn danger full" type="button" data-action="delete-trip" data-id="${t.id}">Rit verwijderen</button></form>`);
}
async function saveTripEdit(fd){const t=state.trips.find(x=>x.id===fd.get('id'));if(!t)throw new Error('Rit niet gevonden.');const start=Number(fd.get('startOdometer')),end=Number(fd.get('endOdometer')),actual=end-start,cat=fd.get('category'),p=cat==='private'?actual:Number(fd.get('privateKm')||0);if(actual<0||p<0||p>actual)throw new Error('Controleer kilometerstanden en privédeel.');const split=splitKilometers(actual,cat,p);Object.assign(t,{startOdometer:start,endOdometer:end,actualKm:actual,category:cat,reason:String(fd.get('reason')||''),privateKm:split.private,businessKm:split.business,commuteKm:split.commute});await idbPut('trips',t);await refreshData();closeModal();render();toast('Rit bijgewerkt.');}
async function deleteTrip(id){if(!confirm('Deze rit verwijderen?'))return;await idbDelete('trips',id);await rebuildLastEndpoint();await refreshData();closeModal();render();toast('Rit verwijderd.');}

async function openLocationEditor(id=null,useCurrent=false) {
  const existing=id?state.locations.find(x=>x.id===id):null; let gps=null,address='';
  if(useCurrent){try{gps=await getCurrentPosition();address=await reverseGeocode(gps.lat,gps.lng);}catch{toast('Huidige locatie kon niet worden opgehaald.');}}
  openModal(`<div class="modal-head"><h2>${existing?'Locatie wijzigen':'Locatie toevoegen'}</h2><button class="close" data-action="close-modal">×</button></div><form id="locationForm"><input type="hidden" name="id" value="${existing?.id||''}">${field('Naam','name',existing?.name||'')}${field('Adres','address',existing?.address||address)}<div class="grid-2">${field('Latitude','lat',existing?.lat??gps?.lat??'','number')}${field('Longitude','lng',existing?.lng??gps?.lng??'','number')}</div><div class="form-group"><label>Type</label><select name="type"><option value="home" ${existing?.type==='home'?'selected':''}>Thuis</option><option value="work" ${existing?.type==='work'?'selected':''}>Werk</option><option value="business" ${existing?.type==='business'?'selected':''}>Zakelijk</option><option value="private" ${existing?.type==='private'?'selected':''}>Privé</option><option value="other" ${!existing||existing?.type==='other'?'selected':''}>Overig</option></select></div><button class="btn full">Opslaan</button></form>`);
}
async function saveLocation(fd){const id=fd.get('id')||crypto.randomUUID();const old=state.locations.find(x=>x.id===id);const loc={id,name:String(fd.get('name')||'').trim(),address:String(fd.get('address')||'').trim(),lat:Number(fd.get('lat')),lng:Number(fd.get('lng')),type:fd.get('type'),useCount:old?.useCount||0,createdAt:old?.createdAt||new Date().toISOString(),updatedAt:new Date().toISOString()};if(!loc.name)throw new Error('Geef de locatie een naam.');if(!Number.isFinite(loc.lat)||!Number.isFinite(loc.lng))throw new Error('Latitude en longitude zijn nodig voor herkenning.');await idbPut('locations',loc);await refreshData();closeModal();render();toast('Locatie opgeslagen.');}
async function deleteLocation(id){if(!confirm('Locatie verwijderen? Bestaande ritten behouden hun opgeslagen locatiegegevens.'))return;await idbDelete('locations',id);await refreshData();render();}

async function saveSettings(fd) {
  state.settings={...state.settings,id:'main',name:String(fd.get('name')||''),vehicleBrand:String(fd.get('vehicleBrand')||''),vehicleModel:String(fd.get('vehicleModel')||''),plate:String(fd.get('plate')||''),initialOdometer:String(fd.get('initialOdometer')||''),registrationStart:String(fd.get('registrationStart')||''),reportEmail:String(fd.get('reportEmail')||''),recognitionRadius:Number(fd.get('recognitionRadius')||500),googleApiKey:String(fd.get('googleApiKey')||'').trim(),defaultReportPeriod:String(fd.get('defaultReportPeriod')||'week')};
  await idbPut('settings',state.settings); state.reportRange=null; render(); toast('Instellingen opgeslagen.');
}

function openModal(html){modalContent.innerHTML=html;modal.showModal();}
function closeModal(){if(modal.open)modal.close();modalContent.innerHTML='';}
function toast(msg){toastEl.textContent=msg;toastEl.classList.add('show');clearTimeout(toastEl._t);toastEl._t=setTimeout(()=>toastEl.classList.remove('show'),2600);}

async function getLastEndpoint(){return await idbGet('appState','lastEndpoint') || getLastEndpointSync();}
function getLastEndpointSync(){const x=state._lastEndpoint;if(x)return x;const latest=state.trips[0];if(latest)return {id:'lastEndpoint',location:latest.destination,odometer:latest.endOdometer,time:latest.arrivalTime};if(state.settings.initialOdometer)return {location:null,odometer:Number(state.settings.initialOdometer),time:state.settings.registrationStart};return null;}
async function rebuildLastEndpoint(){const trips=await idbGetAll('trips');trips.sort((a,b)=>new Date(b.arrivalTime)-new Date(a.arrivalTime));if(trips[0])await idbPut('appState',{id:'lastEndpoint',location:trips[0].destination,odometer:trips[0].endOdometer,time:trips[0].arrivalTime});else await idbDelete('appState','lastEndpoint');}

function locationOptions(selected=''){return [...state.locations].sort((a,b)=>(b.useCount||0)-(a.useCount||0)||a.name.localeCompare(b.name)).map(l=>`<option value="${l.id}" ${l.id===selected?'selected':''}>${esc(l.name)}${l.address?` · ${esc(l.address)}`:''}</option>`).join('');}
function matchKnownLocations(pos){const radius=Number(state.settings.recognitionRadius||500);return state.locations.map(location=>({location,distance:distanceMeters(pos,location)})).filter(x=>Number.isFinite(x.distance)&&x.distance<=radius).sort((a,b)=>a.distance-b.distance);}
function currentLocationObject(pos,address){return {id:null,name:'Huidige locatie',address:address||`GPS ${pos.lat.toFixed(5)}, ${pos.lng.toFixed(5)}`,lat:pos.lat,lng:pos.lng,type:'other'};}
function snapshotLocation(l){return l?{id:l.id||null,name:l.name||'',address:l.address||'',lat:numOrNull(l.lat),lng:numOrNull(l.lng),type:l.type||'other'}:null;}
async function incrementLocationUse(id){if(!id)return;const loc=await idbGet('locations',id);if(loc){loc.useCount=(loc.useCount||0)+1;loc.lastUsedAt=new Date().toISOString();await idbPut('locations',loc);state.locations=await idbGetAll('locations');}}

function getCurrentPosition(){return new Promise((resolve,reject)=>{if(!navigator.geolocation)return reject(new Error('Geolocatie wordt niet ondersteund.'));navigator.geolocation.getCurrentPosition(p=>resolve({lat:p.coords.latitude,lng:p.coords.longitude,accuracy:p.coords.accuracy,timestamp:p.timestamp}),err=>reject(new Error(locationErrorMessage(err))),{enableHighAccuracy:true,timeout:12000,maximumAge:15000});});}
function locationErrorMessage(err){if(err?.code===1)return 'Geen toestemming voor locatie. Controleer de locatie-instellingen van Safari.';if(err?.code===2)return 'Locatie tijdelijk niet beschikbaar.';if(err?.code===3)return 'Locatie ophalen duurde te lang.';return 'Locatie kon niet worden opgehaald.';}

async function startGpsTracking(tripId){
  if(!navigator.geolocation||state.gps.watchId!=null)return;
  state.gps.watchId=navigator.geolocation.watchPosition(p=>{state.gps.latest={lat:p.coords.latitude,lng:p.coords.longitude,accuracy:p.coords.accuracy,timestamp:p.timestamp};},err=>console.warn('GPS watch',err),{enableHighAccuracy:true,maximumAge:15000,timeout:20000});
  try{state.gps.latest=await getCurrentPosition();await persistTrackPoint(tripId,state.gps.latest);}catch{}
  state.gps.intervalId=setInterval(async()=>{if(state.gps.latest)await persistTrackPoint(tripId,state.gps.latest);},60000);
}
function stopGpsTracking(){if(state.gps.watchId!=null)navigator.geolocation.clearWatch(state.gps.watchId);if(state.gps.intervalId)clearInterval(state.gps.intervalId);state.gps={watchId:null,intervalId:null,latest:null};}
async function persistTrackPoint(tripId,pos){const id=`${tripId}_${new Date().toISOString().slice(0,16)}`;await idbPut('trackPoints',{id,tripId,time:new Date().toISOString(),lat:pos.lat,lng:pos.lng,accuracy:pos.accuracy??null});}

let googleLoadPromise=null;
function loadGoogleMaps(){
  if(window.google?.maps?.importLibrary)return Promise.resolve();
  const key=state.settings.googleApiKey;if(!key)return Promise.reject(new Error('Geen Google Maps API-key ingesteld.'));
  if(googleLoadPromise)return googleLoadPromise;
  googleLoadPromise=new Promise((resolve,reject)=>{const cb='__kmGoogleReady';window[cb]=()=>{delete window[cb];resolve();};const s=document.createElement('script');s.async=true;s.src=`https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(key)}&loading=async&v=weekly&libraries=routes,geocoding&language=nl&region=NL&callback=${cb}`;s.onerror=()=>reject(new Error('Google Maps kon niet worden geladen.'));document.head.appendChild(s);});
  return googleLoadPromise;
}
async function reverseGeocode(lat,lng){if(!state.settings.googleApiKey)return '';try{await loadGoogleMaps();const {Geocoder}=await google.maps.importLibrary('geocoding');const g=new Geocoder();const {results}=await g.geocode({location:{lat,lng}});return results?.[0]?.formatted_address||'';}catch{return '';}}

async function getRouteProposal(origin,destination,departureTime){
  if(state.settings.googleApiKey){
    try{
      await loadGoogleMaps(); const {Route}=await google.maps.importLibrary('routes');
      const request={origin:routePoint(origin),destination:routePoint(destination),travelMode:'DRIVING',routingPreference:'TRAFFIC_AWARE_OPTIMAL',departureTime:new Date(departureTime),fields:['distanceMeters','durationMillis']};
      const {routes}=await Route.computeRoutes(request); if(routes?.[0]?.distanceMeters!=null){return{km:routes[0].distanceMeters/1000,durationMin:routes[0].durationMillis?routes[0].durationMillis/60000:null,provider:'google_traffic',providerLabel:'Google verkeer'}};
    }catch(err){console.warn('Route API fallback',err);}
  }
  const hist=historicalRouteKm(origin,destination);if(hist!=null)return{km:hist,durationMin:null,provider:'history',providerLabel:'eerdere ritten'};
  if(origin?.lat!=null&&destination?.lat!=null){return{km:(distanceMeters(origin,destination)/1000)*1.25,durationMin:null,provider:'estimate',providerLabel:'grove schatting'};}
  throw new Error('Route kon niet worden berekend.');
}
function routePoint(l){if(l?.lat!=null&&l?.lng!=null)return{lat:Number(l.lat),lng:Number(l.lng)};if(l?.address)return l.address;return l?.name||'';}
function historicalRouteKm(origin,dest){const values=state.trips.filter(t=>sameLocation(t.origin,origin)&&sameLocation(t.destination,dest)&&Number.isFinite(Number(t.actualKm))).slice(0,8).map(t=>Number(t.actualKm)).sort((a,b)=>a-b);if(!values.length)return null;const mid=Math.floor(values.length/2);return values.length%2?values[mid]:(values[mid-1]+values[mid])/2;}
function sameLocation(a,b){if(!a||!b)return false;if(a.id&&b.id)return a.id===b.id;if(a.lat!=null&&b.lat!=null)return distanceMeters(a,b)<150;return (a.address&&b.address&&a.address===b.address);}

function splitKilometers(total,category,privateKm){const p=category==='private'?total:privateKm;return{private:p,business:category==='business'?total-p:0,commute:category==='commute'?total-p:0};}
function tripsInRange(start,end){return state.trips.filter(t=>inRange(new Date(t.departureTime),start,end)).sort((a,b)=>new Date(a.departureTime)-new Date(b.departureTime));}
function inRange(d,start,end){return d>=start&&d<end;}
function tripTotals(trips){return{total:sum(trips,'actualKm'),business:sum(trips,'businessKm'),commute:sum(trips,'commuteKm'),private:sum(trips,'privateKm')};}
function sum(arr,key){return arr.reduce((n,x)=>n+Number(x[key]||0),0);}

function defaultReportRange(){const now=new Date();if(state.settings.defaultReportPeriod==='month'){const s=new Date(now.getFullYear(),now.getMonth(),1);return{start:s,end:new Date(now.getFullYear(),now.getMonth()+1,1),label:new Intl.DateTimeFormat('nl-NL',{month:'long',year:'numeric'}).format(s)}}const s=startOfISOWeek(now);return{start:s,end:addDays(s,7),label:`Week ${isoWeek(s)} ${s.getFullYear()}`};}
function reportFormFields(period){const now=new Date();if(period==='month')return `<div class="form-group"><label>Maand</label><input name="month" type="month" value="${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}"></div>`;if(period==='custom')return `<div class="grid-2"><div class="form-group"><label>Van</label><input name="from" type="date" value="${toDateInput(startOfISOWeek(now))}"></div><div class="form-group"><label>Tot en met</label><input name="to" type="date" value="${toDateInput(now)}"></div></div>`;return `<div class="form-group"><label>Datum in week</label><input name="weekDate" type="date" value="${toDateInput(now)}"></div>`;}
function updateReportFormFields(){const p=document.getElementById('reportPeriod')?.value,o=document.getElementById('reportDynamicFields');if(o)o.innerHTML=reportFormFields(p);}
function rangeFromReportForm(fd){const p=fd.get('period');if(p==='month'){const [y,m]=String(fd.get('month')).split('-').map(Number);const s=new Date(y,m-1,1);return{start:s,end:new Date(y,m,1),label:new Intl.DateTimeFormat('nl-NL',{month:'long',year:'numeric'}).format(s)}}if(p==='custom'){const s=new Date(`${fd.get('from')}T00:00:00`),e=addDays(new Date(`${fd.get('to')}T00:00:00`),1);return{start:s,end:e,label:`${formatDate(s)} – ${formatDate(addDays(e,-1))}`}}const d=new Date(`${fd.get('weekDate')}T12:00:00`),s=startOfISOWeek(d);return{start:s,end:addDays(s,7),label:`Week ${isoWeek(s)} ${s.getFullYear()}`};}

function currentReportData(){const r=state.reportRange||defaultReportRange();const trips=tripsInRange(r.start,r.end);return{range:r,trips,totals:tripTotals(trips)};}
function reportText(){const{range,trips,totals}=currentReportData();const s=state.settings;const lines=[`Kilometerregistratie: ${range.label}`,`Naam: ${s.name||'-'}`,`Auto: ${[s.vehicleBrand,s.vehicleModel].filter(Boolean).join(' ')||'-'}`,`Kenteken: ${s.plate||'-'}`,'',`Totaal: ${fmtKm(totals.total)} km`,`Zakelijk: ${fmtKm(totals.business)} km`,`Woon-werk: ${fmtKm(totals.commute)} km`,`Privé: ${fmtKm(totals.private)} km`,''];trips.forEach((t,i)=>{lines.push(`Rit ${i+1}: ${formatDateTime(t.departureTime)}`,`${t.origin?.address||t.origin?.name||'-'} (${fmtOdo(t.startOdometer)}) → ${t.destination?.address||t.destination?.name||'-'} (${fmtOdo(t.endOdometer)})`,`Afstand: ${fmtKm(t.actualKm)} km · ${categoryLabel(t.category)}${t.privateKm?` · privé ${fmtKm(t.privateKm)} km`:''}${t.reason?` · ${t.reason}`:''}`,'');});return lines.join('\n');}
function sendReportEmail(){const email=state.settings.reportEmail;if(!email)return toast('Vul eerst een rapport-e-mailadres in bij Instellingen.');const {range}=currentReportData();location.href=`mailto:${encodeURIComponent(email)}?subject=${encodeURIComponent(`Kilometerregistratie ${range.label}`)}&body=${encodeURIComponent(reportText())}`;}
function reportCsv(){const{trips}=currentReportData();const rows=[['Datum vertrek','Tijd vertrek','Vertrek','Start km','Aankomst','Eind km','Ritafstand','Type','Reden','Zakelijk km','Woon-werk km','Privé km','Routevoorstel km','Routebron']];for(const t of trips)rows.push([toDateInput(new Date(t.departureTime)),formatTime(t.departureTime),t.origin?.address||t.origin?.name||'',t.startOdometer,t.destination?.address||t.destination?.name||'',t.endOdometer,t.actualKm,categoryLabel(t.category),t.reason||'',t.businessKm||0,t.commuteKm||0,t.privateKm||0,t.proposedRouteKm??'',t.routeProvider||'']);return '\ufeff'+rows.map(r=>r.map(csvCell).join(';')).join('\n');}
function csvCell(v){const s=String(v??'').replace(/"/g,'""');return /[;"\n]/.test(s)?`"${s}"`:s;}
function downloadReportCsv(){const{range}=currentReportData();downloadBlob(new Blob([reportCsv()],{type:'text/csv;charset=utf-8'}),`kilometerregistratie-${slug(range.label)}.csv`);}
async function shareReport(){const{range}=currentReportData();const file=new File([reportCsv()],`kilometerregistratie-${slug(range.label)}.csv`,{type:'text/csv'});if(navigator.canShare?.({files:[file]})){await navigator.share({title:`Kilometerregistratie ${range.label}`,text:`Rapport ${range.label}`,files:[file]});}else{downloadReportCsv();toast('Delen met bestand wordt hier niet ondersteund; CSV is gedownload.');}}
function renderPrintableReport(trips,totals,label){const s=state.settings;return `<section class="report-print"><h1>Kilometerregistratie: ${esc(label)}</h1><p>Naam: ${esc(s.name||'-')}<br>Automerk: ${esc([s.vehicleBrand,s.vehicleModel].filter(Boolean).join(' ')||'-')}<br>Kenteken: ${esc(s.plate||'-')}</p><div class="summary"><div>Totaal<br><strong>${fmtKm(totals.total)} km</strong></div><div>Zakelijk<br><strong>${fmtKm(totals.business)} km</strong></div><div>Woon-werk<br><strong>${fmtKm(totals.commute)} km</strong></div><div>Privé<br><strong>${fmtKm(totals.private)} km</strong></div></div><table><thead><tr><th>Datum</th><th>Vertrek</th><th>Aankomst</th><th>Type</th><th>Km</th></tr></thead><tbody>${trips.map(t=>`<tr><td>${formatDateTime(t.departureTime)}</td><td>${esc(t.origin?.address||t.origin?.name||'')}<br>${fmtOdo(t.startOdometer)}</td><td>${esc(t.destination?.address||t.destination?.name||'')}<br>${fmtOdo(t.endOdometer)}</td><td>${esc(categoryLabel(t.category))}${t.privateKm?`<br>Privédeel ${fmtKm(t.privateKm)} km`:''}</td><td>${fmtKm(t.actualKm)}</td></tr>`).join('')}</tbody></table></section>`;}

async function exportData(){const payload={version:1,exportedAt:new Date().toISOString(),settings:state.settings,locations:await idbGetAll('locations'),trips:await idbGetAll('trips'),events:await idbGetAll('events'),trackPoints:await idbGetAll('trackPoints'),appState:await idbGetAll('appState')};downloadBlob(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}),`kilometerregistratie-backup-${toDateInput(new Date())}.json`);}
async function importData(file){const data=JSON.parse(await file.text());if(!confirm('Import vervangt de huidige lokale data. Doorgaan?'))return;for(const s of STORES)await idbClear(s);if(data.settings)await idbPut('settings',{...DEFAULT_SETTINGS,...data.settings,id:'main'});for(const s of ['locations','trips','events','trackPoints','appState'])for(const item of (data[s]||[]))await idbPut(s,item);state.settings={...DEFAULT_SETTINGS,...(await idbGet('settings','main')||{})};await refreshData();render();toast('Backup geïmporteerd.');}
async function clearAllData(){if(!confirm('Alle ritten, locaties, GPS-punten en instellingen wissen? Dit kan niet ongedaan worden gemaakt zonder backup.'))return;stopGpsTracking();for(const s of STORES)await idbClear(s);state.settings={...DEFAULT_SETTINGS};await idbPut('settings',state.settings);await refreshData();render();toast('Alle lokale data is gewist.');}
function downloadBlob(blob,name){const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}

function startOfISOWeek(d){const x=new Date(d);x.setHours(0,0,0,0);const day=x.getDay()||7;x.setDate(x.getDate()-day+1);return x;}
function isoWeek(d){const date=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));const day=date.getUTCDay()||7;date.setUTCDate(date.getUTCDate()+4-day);const yearStart=new Date(Date.UTC(date.getUTCFullYear(),0,1));return Math.ceil((((date-yearStart)/86400000)+1)/7);}
function addDays(d,n){const x=new Date(d);x.setDate(x.getDate()+n);return x;}
function toDateInput(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
function toLocalInput(d){const x=new Date(d.getTime()-d.getTimezoneOffset()*60000);return x.toISOString().slice(0,16);}
function formatDate(d){return new Intl.DateTimeFormat('nl-NL',{day:'2-digit',month:'2-digit',year:'numeric'}).format(new Date(d));}
function formatTime(d){return new Intl.DateTimeFormat('nl-NL',{hour:'2-digit',minute:'2-digit'}).format(new Date(d));}
function formatDateTime(d){return new Intl.DateTimeFormat('nl-NL',{weekday:'short',day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'}).format(new Date(d));}
function fmtKm(v){const n=Number(v||0);return new Intl.NumberFormat('nl-NL',{maximumFractionDigits:1}).format(n);}
function fmtOdo(v){return new Intl.NumberFormat('nl-NL',{maximumFractionDigits:0}).format(Number(v||0));}
function categoryLabel(v){return ({commute:'Woon-werk',business:'Zakelijk',private:'Privé'})[v]||v||'-';}
function typeLabel(v){return ({home:'Thuis',work:'Werk',business:'Zakelijk',private:'Privé',other:'Overig'})[v]||'Overig';}
function distanceMeters(a,b){if(a?.lat==null||a?.lng==null||b?.lat==null||b?.lng==null)return Infinity;const R=6371000,p1=a.lat*Math.PI/180,p2=b.lat*Math.PI/180,dp=(b.lat-a.lat)*Math.PI/180,dl=(b.lng-a.lng)*Math.PI/180;const h=Math.sin(dp/2)**2+Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2;return 2*R*Math.atan2(Math.sqrt(h),Math.sqrt(1-h));}
function numOrNull(v){const n=Number(v);return v===''||v==null||!Number.isFinite(n)?null:n;}
function esc(v){return String(v??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}
function attr(v){return esc(v).replace(/`/g,'&#96;');}
function slug(v){return String(v).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');}

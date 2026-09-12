# v19 — configureerbare navigatie

Dit voorstel bouwt voort op de huidige `index.html` op `main` (v18) en laat de bestaande opslag onder `kmreg-v4-data` intact.

## Doel

De huidige knop **Apple Kaarten** wordt vervangen door één algemene knop **Start navigatie**. De gebruiker kiest zelf hoe navigatie moet worden geopend. Een webapp probeert niet te detecteren welke navigatie-apps geïnstalleerd zijn, omdat dat vanuit de browser niet betrouwbaar kan.

## Instelling

Nieuwe instelling `settings.navigationMode`, standaard `system`.

Mogelijke waarden:

- `system` — **Systeemstandaard**; gebruikt waar ondersteund de navigatie-app die op de telefoon als standaard is ingesteld.
- `apple` — **Apple Kaarten**.
- `google` — **Google Maps**.
- `ask` — **Telkens vragen**; toont bij de actieve rit een keuze tussen systeemstandaard, Apple Kaarten en Google Maps.
- `off` — **Uit**; de navigatieknop wordt niet getoond.

De instelling komt als een eigen, standaard ingeklapte sectie **Navigatie** onder **Ritvoorstellen**.

## Gedrag actieve rit

Als een actieve rit een bekende bestemming heeft en navigatie niet op `off` staat:

```html
<button class="btn secondary" data-action="navigate-active">Start navigatie</button>
```

Als de bestemming nog onbekend is, wordt geen navigatieknop getoond.

## Links per navigatiemodus

### Google Maps

Google krijgt alleen de bestemming mee, zodat de actuele apparaatlocatie als vertrekpunt kan worden gebruikt. `dir_action=navigate` vraagt Google Maps om waar mogelijk direct turn-by-turn navigatie te starten.

```js
location.href = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(target)}&travelmode=driving&dir_action=navigate`;
```

### Apple Kaarten

Bij Apple wordt het vaste vertrekpunt uit de kilometerregistratie niet meer meegestuurd. Apple Kaarten kan daardoor zelf de actuele locatie als vertrekpunt gebruiken.

```js
location.href = `https://maps.apple.com/?daddr=${encodeURIComponent(target)}&dirflg=d`;
```

Apple biedt via een gewone web-link geen betrouwbare manier om actieve turn-by-turn navigatie zonder extra tik te garanderen. Dit wordt ook zo in de instellingen vermeld.

### Systeemstandaard

Voor ondersteunde iOS-versies in de EU gebruikt het voorstel Apple's standaard-navigatieschema:

```js
location.href = `geo-navigation://directions?destination=${encodeURIComponent(target)}`;
```

Daarmee bepaalt het besturingssysteem welke als standaard ingestelde navigatie-app wordt geopend.

## Voorgestelde helpers

```js
function navigationTarget(d){
  return d?.lat!=null&&d?.lng!=null
    ? `${d.lat},${d.lng}`
    : d?.address||d?.name||'';
}

function navigationModeLabel(mode){
  return mode==='apple'?'Apple Kaarten'
    :mode==='google'?'Google Maps'
    :mode==='ask'?'Telkens vragen'
    :mode==='off'?'Uit'
    :'Systeemstandaard';
}

function startNavigation(d){
  if(!d) throw new Error('Er is nog geen bestemming gekozen.');
  const mode=data.settings.navigationMode||'system';
  if(mode==='off') return;
  if(mode==='ask'){
    openNavigationChooser(d);
    return;
  }
  openNavigation(d,mode);
}

function openNavigation(d,mode){
  const target=navigationTarget(d);
  if(!target) throw new Error('Voor navigatie is een adres of GPS-locatie nodig.');
  closeModal();

  if(mode==='google'){
    location.href=`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(target)}&travelmode=driving&dir_action=navigate`;
    return;
  }

  if(mode==='apple'){
    location.href=`https://maps.apple.com/?daddr=${encodeURIComponent(target)}&dirflg=d`;
    return;
  }

  location.href=`geo-navigation://directions?destination=${encodeURIComponent(target)}`;
}
```

## Backwards compatibility

`navigationMode:'system'` wordt alleen aan `DEFAULT.settings` toegevoegd. De bestaande `normalize()` merge zorgt ervoor dat bestaande gebruikersdata automatisch deze standaardwaarde krijgt. De storage key blijft:

```js
const KEY='kmreg-v4-data';
```

Er is dus geen datamigratie nodig.

## Testpunten voor iPhone

1. **Systeemstandaard** met Apple Kaarten als standaard navigatie-app.
2. **Systeemstandaard** met Google Maps als standaard navigatie-app, indien op het toestel ondersteund/geconfigureerd.
3. **Apple Kaarten** — route opent met huidige locatie als vertrekpunt; controleren hoeveel tikken nog nodig zijn om turn-by-turn te starten.
4. **Google Maps** — controleren of `dir_action=navigate` direct navigatie start.
5. **Telkens vragen** — keuzevenster werkt en keuze wordt alleen voor die navigatieactie gebruikt.
6. **Uit** — navigatieknop verdwijnt volledig van de actieve rit.
7. Bestaande v18-data blijft zichtbaar en ongewijzigd.

## Status

Voorstel voor v19; nog niet bedoeld om `main` te wijzigen voordat het gedrag op iPhone is getest.
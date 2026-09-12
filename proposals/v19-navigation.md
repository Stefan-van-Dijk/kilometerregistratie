# v19 — systeemnavigatie

Dit voorstel bouwt voort op de huidige `index.html` op `main` (v18) en laat de bestaande opslag onder `kmreg-v4-data` intact.

## Doel

De huidige knop **Apple Kaarten** wordt vervangen door één algemene knop **Start navigatie**. De kilometerregistratie kiest niet zelf tussen Apple Kaarten, Google Maps of een andere navigatie-app. Dat laat de app over aan de systeeminstelling van de telefoon.

## Instelling

Nieuwe instelling `settings.navigationMode`, standaard `system`.

Er zijn bewust maar twee waarden:

- `system` — **Systeemstandaard**; opent de navigatie-app die door het besturingssysteem als standaard wordt afgehandeld.
- `off` — **Uit**; navigatie vanuit de kilometerregistratie is volledig uitgeschakeld.

De instelling komt als een eigen, standaard ingeklapte sectie **Navigatie** onder **Ritvoorstellen**.

## Gedrag actieve rit

Als een actieve rit een bekende bestemming heeft en navigatie op `system` staat:

```html
<button class="btn secondary" data-action="navigate-active">Start navigatie</button>
```

Als de bestemming nog onbekend is, wordt geen navigatieknop getoond. Als navigatie op `off` staat, wordt de knop eveneens niet getoond.

## Systeemstandaard

De webapp probeert niet te detecteren welke navigatie-app is geïnstalleerd of ingesteld. Dat is vanuit een browser niet betrouwbaar en is bovendien niet nodig wanneer het besturingssysteem zelf de standaardkeuze beheert.

Voor ondersteunde iOS-versies in de EU gebruikt v19 het systeemnavigatieschema:

```js
location.href = `geo-navigation://directions?destination=${encodeURIComponent(target)}`;
```

Daarmee wordt alleen de bestemming aangeboden. De navigatie-app gebruikt vervolgens de actuele apparaatlocatie als vertrekpunt.

## Voorgestelde helpers

```js
function navigationTarget(d){
  return d?.lat!=null&&d?.lng!=null
    ? `${d.lat},${d.lng}`
    : d?.address||d?.name||'';
}

function startNavigation(d){
  if(!d) throw new Error('Er is nog geen bestemming gekozen.');
  if((data.settings.navigationMode||'system')==='off') return;

  const target=navigationTarget(d);
  if(!target) throw new Error('Voor navigatie is een adres of GPS-locatie nodig.');

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

1. **Systeemstandaard** opent de op het toestel ingestelde navigatie-app.
2. De actuele apparaatlocatie wordt door de navigatie-app als vertrekpunt gebruikt.
3. De bekende bestemming uit de actieve rit wordt correct doorgegeven.
4. **Uit** verbergt de navigatieknop volledig.
5. Een rit zonder bekende bestemming toont geen navigatieknop.
6. Bestaande v18-data blijft zichtbaar en ongewijzigd.

## Status

Voorstel voor v19; `main` blijft op v18 totdat dit gedrag op iPhone is getest.

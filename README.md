# Kilometerregistratie

Een lokale, mobiele webapp/PWA voor kilometerregistratie. De app is bewust geschikt gemaakt voor hosting op **GitHub Pages** en gebruikt standaard geen eigen backend.

## Wat zit in deze eerste versie?

- Vertrek en aankomst als doorlopende kilometertellerketen.
- Het beginadres en de startkilometerstand komen automatisch van de laatste bestemming/eindstand.
- Bekende locaties met herkenningsstraal (standaard 500 meter).
- GPS-locatie bij vertrek/aankomst en tijdens een actieve rit maximaal één opgeslagen trackpunt per minuut.
- Actuele Google-route als kilometer-voorstel wanneer een Google Maps API-key is ingesteld.
- Routevoorstel met verkeersinformatie via de huidige `Route.computeRoutes()`-interface en `TRAFFIC_AWARE_OPTIMAL`.
- Fallback op eerdere A→B-ritten wanneer Google niet beschikbaar is.
- Kilometerstand blijft de administratieve werkelijkheid: `eindstand - startstand = gereden km`.
- Verdeling in **woon-werk**, **zakelijk** en **privé**.
- Een privédeel kan binnen een woon-werk- of zakelijke rit worden toegekend.
- Tankmoment registreert locatie + kilometerstand maar verandert **niet** de A→B-ritketen.
- Weekoverzicht (ISO-week, maandag t/m zondag).
- Rapport over week, maand of vrije periode.
- Rapport als CSV, delen via iOS Share Sheet, e-mailtekst en print/PDF.
- Lokale JSON-backup/import.
- PWA/offline-cache.

## GitHub Pages publiceren

1. Maak een nieuwe GitHub repository, bijvoorbeeld `kilometerregistratie`.
2. Upload alle bestanden uit deze map naar de root van de repository.
3. Open **Settings → Pages** in de repository.
4. Kies bij *Build and deployment* voor **Deploy from a branch**.
5. Selecteer `main` en `/ (root)` en sla op.
6. Open daarna de GitHub Pages-URL op je iPhone in Safari.
7. Kies **Deel → Zet op beginscherm** om de app als PWA te gebruiken.

HTTPS is noodzakelijk voor geolocatie. GitHub Pages levert HTTPS.

## Google Maps / verkeersafhankelijke routevoorstellen

De app werkt zonder Google, maar voor een verkeersafhankelijk routevoorstel heb je een Google Maps Platform API-key nodig.

Zet in Google Cloud de benodigde Maps JavaScript/Routes-functionaliteit aan en plaats de API-key via **Instellingen** in de app. Beperk een browser-key altijd op HTTP referrers, bijvoorbeeld alleen:

`https://jouwgebruikersnaam.github.io/*`

Beperk de key daarnaast tot de APIs die de app daadwerkelijk gebruikt. De key staat bij een statische webapp altijd aan de browserkant en is dus zichtbaar; domein- en API-restricties zijn daarom belangrijk.

Na het wijzigen van de API-key is het verstandig de PWA eenmaal volledig te herladen.

## Belangrijk: GPS in de achtergrond op iPhone

De app gebruikt `watchPosition()` en bewaart tijdens een actieve rit maximaal één laatst bekende GPS-positie per minuut. In een normale webapp/PWA kan iOS Safari achtergrondprocessen echter pauzeren zodra de app langere tijd niet actief is of de telefoon wordt vergrendeld. Daardoor is een exact punt **iedere minuut niet gegarandeerd**.

De database bewaart de GPS-punten wel als losse brondata (`trackPoints`). Daardoor kan later een SVG-path of native iOS-wrapper worden toegevoegd zonder de bestaande ritdata te veranderen.

## E-mailrapporten

Omdat GitHub Pages statisch is, kan de browser niet zelfstandig op een vast tijdstip een e-mail verzenden wanneer de app gesloten is. Deze versie ondersteunt daarom:

- een e-mailconcept naar het ingestelde adres;
- CSV downloaden;
- CSV via de iOS Share Sheet delen;
- printen / als PDF bewaren.

Voor volledig automatische week- of maandmail kan later een kleine serverless backend worden toegevoegd, bijvoorbeeld met Supabase, Cloudflare Workers of een andere mailfunctie. De huidige datastructuur is hierop voorbereid, maar de lokale gegevens moeten dan ook veilig naar die backend worden gesynchroniseerd.

## Privacy en opslag

Alle ritten, locaties, instellingen en GPS-trackpunten worden in deze versie lokaal in IndexedDB van de browser bewaard. Publiceer dus nooit een export/backupbestand in de openbare GitHub repository.

Maak regelmatig een backup via **Instellingen → Backup exporteren**. Browserdata kan verdwijnen wanneer websitegegevens worden gewist of een apparaat wordt vervangen.

## Bestanden

- `index.html` — app-shell
- `styles.css` — mobiele interface
- `app.js` — registratie-, GPS-, route-, rapport- en opslaglogica
- `manifest.webmanifest` — PWA-configuratie
- `sw.js` — offline-cache
- `icons/icon.svg` — app-icoon

## Logische vervolgstappen

1. SVG-path genereren uit GPS-trackpunten/delta's.
2. Kaartweergave van gereden en voorgestelde route.
3. Native iOS-wrapper voor betrouwbaardere achtergrondlocatie.
4. Automatische rapportmail via serverless backend.
5. Synchronisatie tussen meerdere apparaten.
6. Detectie van ontbrekende ritten wanneer huidige GPS niet aansluit op de laatst bekende bestemming.

# Log JSON v2

## Doel

`log.v2` is één logisch gegevensmodel voor kilometerregistratie, tijdregistratie en taken. De structuur scheidt inhoudelijke gegevens van schermweergave en bevat daarnaast een herstelgedeelte voor een exacte back-up.

## Hoofdstructuur

```json
{
  "$schema": "https://stefan-van-dijk.github.io/log/schemas/log-v2.schema.json",
  "schema": "log.v2",
  "schema_version": 2,
  "export_kind": "complete_backup",
  "generated_at": "2026-09-17T18:00:00.000Z",
  "app": { "name": "Log", "build": "0.31.10" },
  "counts": {},
  "data": {
    "settings": {},
    "catalog": {
      "locations": [],
      "tasks": [],
      "people": [],
      "departments": []
    },
    "activities": [],
    "relationships": [],
    "track_points": [],
    "state": { "active_activity_ids": [] }
  },
  "recovery": {
    "format": "log.internal.v1",
    "sources": {}
  }
}
```

## Afspraken voor lege waarden

- De hoofdcollecties zijn altijd aanwezig, ook wanneer ze leeg zijn.
- `id`, `type` en het onderscheidende typeveld zijn verplicht.
- Een veld wordt weggelaten als het niet van toepassing is.
- `null` betekent dat het veld wel van toepassing is, maar de waarde onbekend is.
- Lege teksten worden niet geëxporteerd.
- Een numerieke waarde van `0` en de waarde `false` blijven behouden omdat ze betekenis kunnen hebben.

## Catalogus

- `locations`: gedeelde locaties voor ritten en tijdregistraties.
- `tasks`: thema's en subthema's; `task_type` bepaalt het niveau.
- `people`: collega's die aan tijdregistraties kunnen worden toegerekend.
- `departments`: beheerde of gebruikte afdelingen.

## Activiteiten

Alle registraties staan in één lijst. `activity_type` bepaalt welke velden relevant zijn:

- `trip`: rit, route, kilometerstand en kilometerverdeling.
- `trip_event`: tankmoment, omrijpunt of ander moment binnen een rit.
- `time`: stopwatch- of handmatige tijdregistratie.

Voorbeeld van een rit:

```json
{
  "id": "registration:km:abc123",
  "type": "activity",
  "activity_type": "trip",
  "status": "completed",
  "started_at": "2026-09-17T06:45:00.000Z",
  "ended_at": "2026-09-17T07:20:00.000Z",
  "route": {
    "origin_id": "location:km:home",
    "destination_id": "location:km:office"
  },
  "odometer": {
    "start_km": 125430,
    "end_km": 125468
  },
  "distance": {
    "total_km": 38,
    "business_km": 0,
    "commute_km": 38,
    "private_km": 0
  }
}
```

Voorbeeld van tijdregistratie zonder niet-toepasselijke ritvelden:

```json
{
  "id": "registration:time:def456",
  "type": "activity",
  "activity_type": "time",
  "status": "completed",
  "started_at": "2026-09-17T08:00:00.000Z",
  "ended_at": "2026-09-17T09:15:00.000Z",
  "task_id": "task:time:kip",
  "duration": {
    "actual_minutes": 75,
    "rounded_minutes": 75,
    "own_minutes": 75,
    "total_minutes": 75
  }
}
```

## Relaties

Relaties staan los van de objecten en gebruiken `from_id`, `relationship_type` en `to_id`. Hierdoor kan dezelfde locatie, taak of registratie vanuit meerdere onderdelen worden gebruikt zonder gegevens te dupliceren.

## Herstel en compatibiliteit

`data` is de voorkeursstructuur voor analyse en toekomstige koppelingen. `recovery` bevat tijdelijk de interne opslagvorm, zodat een export exact kan worden hersteld zonder gegevensverlies. De testversie kan zowel bestaande `registratie-model.v1`-exports als nieuwe `log.v2`-exports herstellen.

## Versiebeheer

Wijzigingen die bestaande lezers kunnen breken verhogen `schema_version`. Nieuwe optionele velden binnen versie 2 mogen worden toegevoegd zolang de betekenis van bestaande velden gelijk blijft.

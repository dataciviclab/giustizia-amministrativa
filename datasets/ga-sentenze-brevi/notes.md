# ga-sentenze-brevi — Note tecniche

## Architettura

31 source CKAN native, una per sede. `download_all: true` scarica tutte le
risorse CSV (`2017-2024` bulk + `2025` + `2026`); il RAW produce un CSV per sede.

## Tipo di dato

Tabella **aggregata** (non record-level): ogni riga è un conteggio
`(anno, mese, sede, classificazione, tipo_sentenza) -> numero_sentenze`.

I mart fanno `SUM(numero_sentenze)`, non `COUNT(*)`.

## Vocabolario `tipo_sentenza`

- `SENTENZA` — sentenza piena
- `SENTENZA BREVE` — sentenza breve (rito snellito / materia standardizzata)

Altri valori potrebbero comparire in futuro: non hardcodare filtri stretti.

## Join utili

- `classificazione_ricorso` ↔ `ga_ricorsi_definiti` (stessa tassonomia materia)
- `codice_sede` ↔ tutti i dataset GA
- Complementare a `ga_ricorsi_definiti` (esito) e `ga_ricorsi_tipo_decisione`
  (meccanismo di definizione)

## Cautele

- La risorsa multi-anno `2017-2024` è bulk: non deduplicare per file anno
- `NUMERO_SENTENZE` è un conteggio già aggregato — mai contare le righe raw
- Config runna `years: [2026]` ma il clean contiene la serie completa
  (pattern `download_all` del repo)

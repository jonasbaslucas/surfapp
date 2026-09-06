# SurfKompas lab preview

Deze versie staat op de aparte branch `codex/surfkompas-lab` en wordt niet door de bestaande Cloudflare-deploy opgepakt.

## Lokaal openen

Dubbelklik op `start_surfkompas_lab.bat`. Daarna opent de preview op:

`http://127.0.0.1:8788`

De server blijft in het geopende PowerShell-venster draaien. Sluit dat venster om de labversie te stoppen.

## Wat zit erin?

- Consensusforecast uit ECMWF, ICON en GFS via Open-Meteo.
- Een nu- en komende-4-uur-blok met modelspreiding als stabiliteitsindicator.
- Een adapter voor actuele Rijkswaterstaat-windmetingen wanneer een passend station en actuele meting beschikbaar zijn.
- Spotgerichte scoring en spottekst voor golfsurfen, kitesurfen en windsurfen.
- Hamburger-menu met Surfadvies, Over SurfKompas en Feedback.
- Lokale feedbackcorrecties per sport en spot. Dit is bewust lokaal in de browser; gedeelde correcties voor alle gebruikers vragen later een kleine backend/database.

De productiebranch `main` en de live Cloudflare-site zijn door deze labbranch niet gewijzigd.

# Wintersportkalender – geprüfter Stand 05.11.2026

Aktuell: **414 Einträge**. Alle 412 zuvor veröffentlichten UIDs erhalten; 402 bestehende VEVENT-Blöcke unverändert, 10 gezielt aktualisiert, 2 ergänzt. Abo-URL unverändert.

## Prüfung 05.11.2026

- Aktuelle offizielle FIS-ICS-Dateien für AL/WC, AL/WSC, JP/WC und JP/WSC vollständig abgerufen und gegen die vorhandenen Termine nach Datum, Geschlecht und Disziplin abgeglichen. IBU-Events und Competitions für alle 11 Blöcke erneut abgerufen: alle 70 Renntermine/Startzeiten stimmen mit dem Kalender überein. Keine neue belegte Absage festgestellt.
- Zwei zuvor fehlende Damenrennen ergänzt: Kvitfjell 12.03.2027 Abfahrt und 13.03.2027 Super-G, beide 11:00 MEZ laut FIS-Datenbank. Ersatz für Narvik, bestätigt durch FIS-Datenbank und FISI-Mitteilung vom 29.10.2026. IDs fis-AL131683@julian-wintersport und fis-AL131684@julian-wintersport; keine geschätzten Endzeiten.
- Vier alpine WM-Qualifikationen behalten ihre IDs und haben jetzt die in der aktuellen FIS-Datenbank publizierte Startzeit 09:00 MEZ: Damen-GS 10.02., Herren-GS 11.02., Damen-SL 12.02., Herren-SL 13.02.2027. IDs fis-AL131852/55/56/59@julian-wintersport.
- Vier Lillehammer-Qualifikationen mit Veranstalterstartzeiten versehen: 20.11. Damen 10:30, Herren 14:00; 22.11. Damen 10:30, Herren 14:30. FIS bestätigt Datum/Geschlecht. UIDs fis-JP7798/7796/8011/8010@julian-wintersport erhalten.
- Beaver Creek Damen-Abfahrt 12.12.2026: 19:00 MEZ jetzt konsistent zwischen FIS-Datenbank (LAST-MODIFIED 02.11.2026) und Infosheet. Konfliktmarkierung entfernt, Status CONFIRMED.
- Die drei Konflikte Val d’Isère 12./13.12.2026 und Åre 13.03.2027 bleiben vorläufig, da bisheriger Infosheet-Stand und aktuelle FIS-Datenbank abweichen.
- Lillehammer Damen 21.11.2026 14:35 als vorläufigen Quellenkonflikt markiert: FIS nennt diesen Tag Damen-Einzelweltcup, Veranstalter nennt den Programmpunkt um 14:35 Qualifikation. Vorhandene Planzeit/UID erhalten; keine zusätzliche unbestätigte Qualifikation erzeugt.
- Unbekannte zweite Durchgangszeiten weiterhin transparent ganztägig. Keine geschätzten Start-/Endzeiten ergänzt.
- Generator wegen der unten beschriebenen sekundären Quellenprobleme nicht blind ausgeführt/veröffentlicht. Neue Einträge werden unabhängig von Quell-UID-Dubletten gegen die aktuelle Live-Datei geprüft.

Zusätzliche Quellen:
- https://www.wclhmr.no/en/program
- https://www.fisi.org/coppa-del-mondo-femminile-kvitfjell-prende-il-posto-di-narvik-per-le-gare-veloci-di-marzo/
- https://www.fis-ski.com/DB/general/results.html?sectorcode=AL&raceid=131683
- https://www.fis-ski.com/DB/general/results.html?sectorcode=AL&raceid=131684
- https://www.fis-ski.com/DB/general/results.html?sectorcode=AL&raceid=131602

---

# Wintersportkalender – geprüfter Stand 29.10.2026

Die maßgebliche veröffentlichte Datei ist `wintersport.ics`. Abo-Adresse beibehalten. Alle bisherigen 408 UIDs wurden erhalten; vier bestätigte alpine WM-Qualifikationen wurden hinzugefügt (insgesamt 412 Einträge einschließlich separater zweiter Durchgänge).

## Bestätigte Korrekturen (Europe/Vienna)

- 04.12.2026 Beaver Creek Abfahrt Herren: 19:00 statt 19:15.
- 05.12.2026 Beaver Creek Super-G Herren: 18:30 statt 19:15.

Beide Änderungen stimmen zwischen FIS-Datenbank-ICS und FIS-Infosheet überein. Keine bestätigten Endzeiten aus vermuteter Dauer ableiten.

## Widersprüchliche offizielle Startzeiten

Die bisherigen Planzeiten wurden beibehalten, aber mit STATUS:TENTATIVE und X-JULIAN-TIME-STATUS:SOURCE-CONFLICT versehen:

- 12.12.2026 Beaver Creek Abfahrt Damen: FIS-Datenbank 18:00, FIS-Infosheet 19:00.
- 12.12.2026 Val d’Isère Riesenslalom Herren: FIS-Datenbank 10:00, FIS-Infosheet 09:30.
- 13.12.2026 Val d’Isère Slalom Herren: FIS-Datenbank 10:00, FIS-Infosheet 09:30.
- 13.03.2027 Åre Riesenslalom Herren: FIS-Datenbank 09:30, FIS-Infosheet 10:00.

Vor endgültiger Zeitänderung Veranstalter oder aktualisierten FIS-Rennzeitplan prüfen.

## Neue bestätigte WM-Qualifikationstage

Crans-Montana: Damen-Riesenslalom 10.02.; Herren-Riesenslalom 11.02.; Damen-Slalom 12.02.; Herren-Slalom 13.02.2027. Startzeiten offen; transparente ganztägige Marker, keine erfundenen Uhrzeiten. Neue IDs fis-AL131852, fis-AL131855, fis-AL131856, fis-AL131859 jeweils mit @julian-wintersport.

## Quellen und Prüfumfang

- FIS Alpine WC: https://www.fis-ski.com/DB/services/public/icalendar-feed-fis-events.html?seasoncode=2027&sectorcode=AL&categorycode=WC (81 Wettbewerbe).
- FIS Alpine WM: gleicher Dienst mit categorycode=WSC (11 Medaillenbewerbe und 4 Qualifikationen).
- FIS Skispringen: gleicher Dienst mit sectorcode=JP&categorycode=WC (110 Datenbankeinträge einschließlich 41 Qualifikationen; Tourneegesamtwertungen sind keine zusätzlichen Springen).
- FIS-Infosheet: https://assets.fis-ski.com/f/252177/x/8399f37ec9/complett_finaldoc_26_27_v1_21-10-2026.pdf (Beaver Creek S.12, Val d’Isère S.16, Åre S.64; Seitenindex nullbasiert).
- WM Veranstalter: https://www.cransmontana2027.ch/de/wettkaempfe/rennprogramm/
- Falun: https://falun2027.com/en/here-is-the-competition-schedule-for-falun-2027-2/
- IBU: https://biathlonresults.com/modules/sportapi/api/Events?SeasonId=2627&Level=1 und Competitions?EventId=... für alle elf Veranstaltungsblöcke. Alle 70 Wettkampftermine und Startzeiten stimmten mit dem bestehenden Kalender überein. API-UTC-Zeiten nach Europe/Vienna umrechnen.

## Wichtig für weitere Aktualisierungen

Die sekundären calovo-Exporte enthielten am 29.10.2026 semantische Dubletten mit verschiedenen Quell-UIDs sowie wiederverwendete UIDs für andere Rennen. Ein blinder Lauf von update_wintersport.py erzeugte deshalb fälschlich 519 statt der 408 live vorhandenen Einträge. Dieses temporäre Ergebnis wurde NICHT veröffentlicht. Das Skript nicht ungeprüft veröffentlichen; Änderungen zuerst gegen die aktuelle GitHub-Datei nach Datum, Bewerb, Geschlecht und Ort abgleichen. Quellen-UID allein ist keine zuverlässige Identität. Vorhandene eigene UIDs und bestätigte zweite Durchgänge erhalten. Weder Dubletten hinzufügen noch Quellenwidersprüche stillschweigend als bestätigt behandeln. Eine fehlende Quellzeile ist kein Beleg für eine Absage.

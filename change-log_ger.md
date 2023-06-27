# Änderungsprotokoll:

## Allgemeine Änderungen und Notizen:
- Update auf Python 3 des gesamten Codes
- Damit die Funktionen des Bots angefangen mit download-metadata funktionierten mussten wir zuerst die Test Dateien dummy.py und pmc_doi anpassen

#### dummy.py 
- Für dummy.py probierten wir verschieden Download Dateien und reparierten kleiner Fehler
- Fügten die links als Variable der Funktion hinzu, ergänzen den Code so das er tatsächlich die files runterlädt statt sie nur zu "yielden", dies Funktionierte vielleicht in Python 2

#### pmc_doi.py
- Viele kleine Anpassungen der Relationen der Funktionen der Dateien untereinander, Hinzufügen von Argumenten, oft ausblenden von optinoalen Parametern und Argumenten
- Anpassen der Download Struktur selbes Problem wie bei dummy.py mit dem "yielden" von Inhalten
- Hinzufügen von Download statements mit Hilfe von Carlin (externer Programmieren von WikiData)
- Oft wurde nur der Inhalt geprinted statt gespeichert


### Datei: oa-cache
  
#### 1. Art der Änderung: Import-Anweisungen entfernt

Was?

- Folgende Module wurden entfernt: gobject, pygst, gst
- Funktionen und Klassen, die nicht mehr verwendet werden, wurden entfernt: setup_all, create_all


#### 2. Art der Änderung: Import-Anweisungen aktualisiert / Hinzugefügt

Was?

- make_datestring aus helpers wurde importiert anstatt das gesamte Modul helpers zu importieren - Funktionen und Klassen wurden aktualisiert, um aus den entsprechenden Modulen zu importieren.
- sqlalchemy wurde hinzugefügt um die Datenbank mit sqllite zu erstellen und zu verknüpfen

  

#### 3. Art der Änderung: prints

Was?

- stderr.write wurde mit print ersetzt

#### 4. Art der Änderung: 'convert-media'

Was?

- materials wurde geändert (keine filter --> Alles)
- path wurde entfernt (an manchen Stellen os.path hinzugefügt)
- relative Pfade hinzugefügt
- Zeilen 167 - 186 wurden neu hinzugefügt, um die Konvertierung der Dateien statt mit gobject nun mit ffmpeg zu machen
- ffmpeg Konvertierung zu .ogg Format mit vorherigem Code verknüpfen

#### 5. Art der Änderung: 'find-media'

Was?

- Erster Teil des Codes wurde Auskommentiert, da das Tool Elixir auf Python 3 nicht mehr funktioniert und somit mussten alle Variablen mit Beziehungen zu diesen Funktionen erstmal deaktiviert werden
- skip wurde auskommentiert, diese Funktion funktionierte mit dem vorhanden Code nicht mehr, dies hatte einen Python 3 oder Elixir Grund
- journal und artical.get_by wurde entfernt, contrib_authors wurde als eigene variable hinzugefügt
- get_by ist eine Elixir Variable und somit depreciated
- der Code für category wurde zunächst entfernt, weil dies in der Pipeline der find-media Funktion für Probleme mit Abhängigkeiten gesorgt hat, dafür werden die Ergebnise geprintet

### Datei: oa-get

#### 1. Art der Änderung: Import-Anweisungen hinzugefügt / geändert

Was?

- sqlalchemy, model, urllib3, filetype, importlib, requests

#### 2. Art der Änderung: Hinzufügen von einer database engine und einer session

Was?

- eine database engine und eine Session wurde hinzugefügt, sowie Database tabellen
- hierzu wird sqllite über sqlalchemy verwendet um nach dem Format in der dummy Datei Metadaten zu speichern

#### 3. Art der Änderung: Path der source wurde hinzugefügt / try-except geändert

Was?

- Relative Pfade die temporär in absolute Pfade geändert wurden als jeder einzelnd versuchte Probleme der Dateien zu lösen

#### 4. Art der Änderung: Aktualisieren einer Funktion check_mime_types

Was?

- Umschreiben der FUnktion um Probleme in der Pipeline zu beheben

#### 5. Art der Änderung: 'update-mimetypes'

Was?

- Beginn der if-else-Anweisung loops wurde gelöscht
- .all() wurde in die Klammer gesetzt
- hinzufügen eines for-loops, um den file-path zu kontrollieren

#### 6. Art der Änderung: 'download-media'

Was?

- materials wurde session hinzugefügt und dann geprintet, soll überprüfen ob Inhalte hinzugefügt werden
- Funktion download-media funktioniert wenn eine PMC DOI in der Datei pmc_doi.py hinzugefügt wird, klappt auch mit einer Liste

  

### Datei: model.py

#### 1. Art der Änderung: Import-Anweisungen hinzugefügt / geändert

Was?

- sqlalchemy, importlib, sys

#### 2. Art der Änderung: Neu definieren der Funktion 'set_source'

Was?

- anstatt sqllite nutzen von importlib, um das source_module zu definieren.

#### 3. Art der Änderung: Definieren neuer Variablen

Was?
- engine --> zum deklarieren der SQL-Umgebung
- Session --> zum definieren einer Session im Botablauf


#### 4. Art der Änderung: Änderung in der Klasse 'Journal'

Was?

- anderes Objekt, anstatt Entity nun Base, weil Probleme mit dem Aufruf der Variable entstanden sind vor der Änderung
- hinzufügen von 'tablename', weil Daten vorher nicht im richtigen Format gespeichert wurdem im sqllite Server
- deswegen müssen nun auch die Variablen in der Klasse geändert werden, einmal wird bei titel nicht mehr Field() genutzt sondern Column() als Update aus Python 2
- bei articels wurden relationen der Felder und Keys vergeben

#### 5. Art der Änderung: Hinzufügen der Variable 'article_category'

Was?

- Hier wird nun eine Assoziationstabelle definiert mit dem Namen 'article_category'
- dadurch können Artikel und Kategorien über die Verknüpfungstabelle miteinander verbunden werden.
- eine Funktion in oa-get oder oa-cache fragte hier nach dieser Tabelle obwohl diese vorher nicht existierte, beim Wechsel zu Python 3 müssen an einigen Stelle Variablen verloren gegangen sein die dann später durch Trial and Error der Fehler Meldungen für die Funktionen, Download-media, Download-metadata, find-media und convert-media manuell hinzugefügt werden mussten

#### 6. Art der Änderung: Änderung in der Klasse 'Category', 'Article' & 'SupplementaryMaterial'

Was?

- Wieder anstatt Entity Base, als Anpassung an einen neuen Import 

### Datei: config.py

Update auf Python 3

#### 1. Art der Änderung: Path Änderung

Was?

- Ursprünglicher Pfad hat auf den eigenen Laptops nicht funktioniert, jeder musste diesen manuell ändern
- Später eine Änderung mit Relativen Pfad hinzugefügt
- Anpassung der User Config und erweiterung um spezifische lokale Variablen

#### 2. Art der Änderung: Hinzufügen bei der Funktion 'database_path'

Was?

- sqlite wird beim 'database_path' benötigt, damit der jeweilige Befehl die einzelnen Databases anlegen kann.



## Allgemeine Änderungen und Notizen:
- Damit die Funktionen des Bots angefangen mit download-metadata funktionierten mussten wir zuerst die Test Dateien dummy.py und pmc_doi anpassen

#### dummy.py 
- Für dummy.py probierten wir verschieden Download Dateien und reparierten kleiner Fehler
- Fügten die links als Variable der Funktion hinzu, ergänzen den Code so das er tatsächlich die files runterlädt statt sie nur zu "yielden", dies Funktionierte vielleicht in Python 2

#### pmc_doi.py
- Viele kleine Anpassungen der Relationen der Funktionen der Dateien untereinander, Hinzufügen von Argumenten, oft ausblenden von optinoalen Parametern und Argumenten
- Anpassen der Download Struktur selbes Problem wie bei dummy.py mit dem "yielden" von Inhalten
- Hinzufügen von Download statements mit Hilfe von Carlin (externer Programmieren von WikiData)
- Oft wurde nur der Inhalt geprinted statt gespeichert

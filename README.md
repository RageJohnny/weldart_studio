# WELDART Studio

<p align="center">
  <img src="icons/logo.png" alt="WELDART Studio Logo" width="300" />
</p>

## Übersicht

WELDART Studio ist eine vielseitige Anwendung, die es Ihnen ermöglicht, mithilfe eines Grafiktabletts Zeichnungen und Unterschriften zu erstellen. Diese Zeichnungen können Sie anschließend als STL-Dateien speichern, die für Schweißarbeiten verwendet werden können. Das Programm bietet eine breite Palette an Werkzeugen und Funktionen, mit denen Sie Ihre Zeichnungen nicht nur erstellen, sondern auch bearbeiten und speichern können. Egal, ob Sie einfache Skizzen oder komplexe Designs erstellen möchten – WELDART Studio unterstützt Sie dabei mit leistungsstarken und benutzerfreundlichen Tools.


## Installation

1. Klone das Repository oder lade den Code als ZIP-Datei herunter und entpacke sie.
2. Stelle sicher, dass Python 3.x auf deinem System installiert ist.
3. Installiere die notwendigen Abhängigkeiten mit folgendem Befehl:

   ```bash
   pip install -r requirements.txt
   ```

## Verwendung

Starte das Programm mit folgendem Befehl:

```bash
python main.py
```
Die Hauptoberfläche von WELDART Studio wird geöffnet. Von hier aus kannst du deine Zeichnungen erstellen und bearbeiten.

## Funktionen

### Werkzeugleiste

Die Werkzeugleiste befindet sich auf der linken Seite des Fensters und enthält folgende Werkzeuge:

- **Select Tool**: Auswahlwerkzeug
- **Draw Rectangle**: Rechteck zeichnen
- **Draw Circle**: Kreis zeichnen
- **Draw Line**: Linie zeichnen
- **Free Draw**: Freihandzeichnung
- **Erase**: Radiergummi für Freihandlinien
- **Move**: Objekte bewegen
- **Resize**: Objekte skalieren
- **Reset Canvas**: Zeichenfläche zurücksetzen

### Einstellungen

Die Einstellungen befinden sich auf der rechten Seite des Fensters und umfassen:

- **Line Thickness**: Setzt die Linienstärke für das Freihandzeichenwerkzeug in mm.
- **Fill Objects**: Aktiviert oder deaktiviert die Füllung von Objekten.
- **Eraser Radius**: Setzt den Radius des Radiergummis in Pixel.

### Lineale

Es gibt horizontale und vertikale Lineale, die die aktuellen Abmessungen anzeigen und als Referenzpunkte dienen.

### Zoom und Pan

- **Zoom**: Verwende das Mausrad, um in die Zeichenfläche hinein- und herauszuzoomen.
- **Pan**: Halte die mittlere Maustaste gedrückt und bewege die Maus, um die Zeichenfläche zu verschieben.

### Shortcuts

- **Strg+Z**: Rückgängig
- **Strg+Y**: Wiederholen
- **Strg+S**: Speichern als SVG

## Speichern als SVG

Um die Zeichnung als SVG-Datei zu speichern, wähle im Menü "File" die Option "Save as SVG". Du wirst aufgefordert, einen Speicherort und einen Dateinamen anzugeben.

## Undo und Redo

- **Undo**: Macht die letzte Aktion rückgängig.
- **Redo**: Wiederholt die letzte rückgängig gemachte Aktion.

## Über

Im Menü "About" findest du Informationen über das Programm und den Urheber.

## Autoren

- **Johannes Georg Larcher**: Entwicklung und Design.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Informationen findest du in der Datei `LICENSE`.

## Abhängigkeiten

- `tkinter`: GUI-Bibliothek für Python.
- `xml.etree.ElementTree`: Modul zum Erstellen und Parsen von XML.
- `tooltip`: Modul zur Erstellung von Tooltips.

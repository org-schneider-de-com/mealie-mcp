# BLS-Nährwerte bei Rezeptanlage und auf Nachfrage berechnen

WSJF 2,00, Issue #28. Der lokale BLS-4.0-Auszug stammt vom Max Rubner-Institut
(2025), DOI 10.25826/Data20251217-134202-0, CC BY 4.0.

- Einmalige optionale Rechnung bei Rezeptanlage; bestehende explizite Werte bleiben erhalten.
- `find_bls_food` meldet eindeutige, mehrdeutige und fehlende Namen samt Codes.
- `calculate_recipe_nutrition` liefert Vorschau, Vollständigkeit, Grundportionen,
  angenommene Grammgewichte und Quelle; schreibt nur bei `save=true` und vollständiger Summe.
- Stück/Volumen werden nur mit ausdrücklich übergebenem Gesamtgewicht gerechnet.
- Bereits gespeicherte Nährwerte verlangen `replace_existing=true`.
- BLS-Lesefehler bei Neuanlage lassen die Rezeptanlage zu und werden gemeldet.

Keine laufende Synchronisierung: Mealie speichert Nährwerte statisch. Die
Berechnung beruht auf BLS-Werten je 100 g und der expliziten Zutatengrundmenge.

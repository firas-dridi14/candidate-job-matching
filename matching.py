"""
Werkia-Matching: findet fuer jede Stelle die 3 besten Kandidaten.
Nur Testdaten (keine echten Personen) - DSGVO-konform.
"""
import csv

# So viele Punkte gibt es fuer jedes Kriterium (zusammen 100)
PUNKTE_STADT = 20
PUNKTE_FAEHIGKEITEN = 20
PUNKTE_ERFAHRUNG = 10
PUNKTE_BERUF = 50


def lese_csv(dateiname):
    """Liest eine CSV-Datei und gibt eine Liste von Zeilen zurueck."""
    with open(dateiname, encoding="utf-8") as datei:
        return list(csv.DictReader(datei))


def liste_aus_text(text):
    """'KNX;Smart Home' -> {'knx', 'smart home'}"""
    return {teil.strip().lower() for teil in text.split(";") if teil.strip()}


def berechne_score(kandidat, stelle):
    """Gibt einen Score von 0 bis 100 zurueck (0 = passt gar nicht)."""
    # Der Beruf muss passen, sonst ist es kein Match
    if kandidat["beruf"] != stelle["beruf"]:
        return 0

    score = PUNKTE_BERUF

    # Gleiche Stadt
    if kandidat["stadt"] == stelle["stadt"]:
        score += PUNKTE_STADT

    # Gemeinsame Faehigkeiten (Anteil der geforderten, die der Kandidat hat)
    gefordert = liste_aus_text(stelle["faehigkeiten"])
    vorhanden = liste_aus_text(kandidat["faehigkeiten"])
    if gefordert:
        anteil = len(gefordert & vorhanden) / len(gefordert)
        score += round(PUNKTE_FAEHIGKEITEN * anteil)

    # Genug Erfahrung
    if int(kandidat["erfahrung_jahre"]) >= int(stelle["min_erfahrung"]):
        score += PUNKTE_ERFAHRUNG

    return score


def beste_kandidaten(stelle, kandidaten, anzahl=3):
    """Gibt die besten Kandidaten fuer eine Stelle zurueck."""
    bewertet = []
    for kandidat in kandidaten:
        score = berechne_score(kandidat, stelle)
        if score > 0:
            bewertet.append((score, kandidat))
    bewertet.sort(key=lambda paar: paar[0], reverse=True)
    return bewertet[:anzahl]


def main():
    kandidaten = lese_csv("kandidaten.csv")
    stellen = lese_csv("stellen.csv")
    ergebnisse = []

    for stelle in stellen:
        print(f"\nStelle {stelle['id']}: {stelle['beruf']} bei {stelle['firma']} ({stelle['stadt']})")
        top = beste_kandidaten(stelle, kandidaten)
        for platz, (score, k) in enumerate(top, start=1):
            print(f"  {platz}. {k['name']:<16} Score {score:>3}  ({k['stadt']}, {k['erfahrung_jahre']} Jahre)")
            ergebnisse.append({
                "stelle_id": stelle["id"],
                "firma": stelle["firma"],
                "platz": platz,
                "kandidat": k["name"],
                "score": score,
            })

    # Ergebnis als CSV speichern (utf-8-sig, damit Excel Umlaute richtig zeigt)
    with open("ergebnis.csv", "w", newline="", encoding="utf-8-sig") as datei:
        schreiber = csv.DictWriter(datei, fieldnames=["stelle_id", "firma", "platz", "kandidat", "score"])
        schreiber.writeheader()
        schreiber.writerows(ergebnisse)
    print("\nFertig! Ergebnis gespeichert in ergebnis.csv")


if __name__ == "__main__":
    main()
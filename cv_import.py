"""
CV-Import: wandelt einen Lebenslauf (PDF oder Text) in eine Tabellenzeile um,
die zu kandidaten.csv passt. Nur Testdaten (DSGVO).

Benutzung:
    python cv_import.py mein_cv.pdf          -> zeigt die Zeile an
    python cv_import.py mein_cv.pdf --speichern   -> haengt sie an kandidaten.csv an
"""
import csv
import re
import sys

# Bekannte Werte (so wie sie in kandidaten.csv / stellen.csv stehen)
BEKANNTE_BERUFE = ["Elektriker", "Anlagenmechaniker SHK"]
BEKANNTE_STAEDTE = ["Berlin", "Brandenburg", "Hamburg", "Potsdam"]
BEKANNTE_FAEHIGKEITEN = [
    "Elektroinstallation", "Photovoltaik", "KNX", "Smart Home",
    "Schaltschrankbau", "E-Mobilitaet", "Pruefung DGUV V3",
    "Waermepumpe", "Klimatechnik", "Rohrinstallation", "Sanitaer",
    "Gasinstallation", "Heizungsbau", "Lueftung",
]
# Zusaetzliche Schreibweisen -> Beruf
BERUF_SYNONYME = {"anlagenmechaniker": "Anlagenmechaniker SHK"}


def pdf_zu_text(pfad):
    """Liest alle Seiten einer PDF-Datei und gibt den Text zurueck."""
    from pypdf import PdfReader
    leser = PdfReader(pfad)
    return "\n".join((seite.extract_text() or "") for seite in leser.pages)


def normalisiere(text):
    """Kleinbuchstaben, Umlaute -> ae/oe/ue/ss, damit Vergleiche klappen."""
    text = text.lower()
    for alt, neu in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(alt, neu)
    return text


def cv_zu_zeile(text):
    """Macht aus dem CV-Text eine Zeile (Dictionary) fuer kandidaten.csv."""
    sauber = normalisiere(text)

    # Name: erste nicht leere Zeile des CVs
    zeilen = [z.strip() for z in text.splitlines() if z.strip()]
    name = zeilen[0] if zeilen else ""

    # Beruf: erster bekannter Beruf, der im Text vorkommt
    beruf = ""
    for kandidat in BEKANNTE_BERUFE:
        if normalisiere(kandidat) in sauber:
            beruf = kandidat
            break
    if not beruf:
        for stichwort, wert in BERUF_SYNONYME.items():
            if stichwort in sauber:
                beruf = wert
                break

    # Stadt: erste bekannte Stadt im Text
    stadt = next((s for s in BEKANNTE_STAEDTE if normalisiere(s) in sauber), "")

    # Faehigkeiten: alle bekannten, die im Text vorkommen
    faehigkeiten = [f for f in BEKANNTE_FAEHIGKEITEN if normalisiere(f) in sauber]

    # Erfahrung: groesste Zahl vor "Jahre"/"Jahr"/"years"
    zahlen = re.findall(r"(\d+)\s*(?:\+\s*)?(?:jahre|jahr|years|year)", sauber)
    erfahrung = max((int(z) for z in zahlen), default=0)

    return {
        "name": name,
        "beruf": beruf,
        "stadt": stadt,
        "faehigkeiten": ";".join(faehigkeiten),
        "erfahrung_jahre": erfahrung,
    }


def zeile_speichern(zeile, dateiname="kandidaten.csv"):
    """Haengt die Zeile mit der naechsten freien id an die CSV an."""
    with open(dateiname, encoding="utf-8") as datei:
        vorhandene = list(csv.DictReader(datei))
    neue_id = max((int(k["id"]) for k in vorhandene), default=0) + 1
    zeile = {"id": neue_id, **zeile}
    with open(dateiname, "a", newline="", encoding="utf-8") as datei:
        schreiber = csv.DictWriter(datei, fieldnames=[
            "id", "name", "beruf", "stadt", "faehigkeiten", "erfahrung_jahre"])
        schreiber.writerow(zeile)
    return neue_id


def main():
    if len(sys.argv) < 2:
        print("Benutzung: python cv_import.py cv.pdf [--speichern]")
        return
    pfad = sys.argv[1]
    text = pdf_zu_text(pfad) if pfad.lower().endswith(".pdf") else open(pfad, encoding="utf-8").read()
    zeile = cv_zu_zeile(text)
    print("Gefundene Daten:")
    for schluessel, wert in zeile.items():
        print(f"  {schluessel:<16} {wert}")
    if not zeile["beruf"]:
        print("Hinweis: Kein bekannter Beruf gefunden - bitte pruefen!")
    if "--speichern" in sys.argv:
        print(f"Gespeichert in kandidaten.csv mit id {zeile_speichern(zeile)}")


if __name__ == "__main__":
    main()

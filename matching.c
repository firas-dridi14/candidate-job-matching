/*
 * Werkia-Matching in C: findet fuer jede Stelle die 3 besten Kandidaten.
 * Nur Testdaten (keine echten Personen) - DSGVO-konform.
 *
 * Kompilieren:  gcc -Wall -o matching matching.c
 * Starten:      ./matching        (Windows: matching.exe)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ZEILEN 100
#define FELD 80
#define TOP 3

/* So viele Punkte gibt es fuer jedes Kriterium (zusammen 100) */
#define PUNKTE_BERUF 50
#define PUNKTE_STADT 20
#define PUNKTE_FAEHIGKEITEN 20
#define PUNKTE_ERFAHRUNG 10

typedef struct {
    int id;
    char name[FELD];
    char beruf[FELD];
    char stadt[FELD];
    char faehigkeiten[FELD * 2];
    int erfahrung;
} Kandidat;

typedef struct {
    int id;
    char firma[FELD];
    char beruf[FELD];
    char stadt[FELD];
    char faehigkeiten[FELD * 2];
    int min_erfahrung;
} Stelle;

/* Teilt eine Zeile an den Kommas in 6 Felder (fuer unsere CSV-Dateien). */
static int teile_zeile(char *zeile, char *felder[], int max) {
    int n = 0;
    zeile[strcspn(zeile, "\r\n")] = '\0';   /* Zeilenende entfernen */
    char *start = zeile;
    while (n < max) {
        felder[n++] = start;
        char *komma = strchr(start, ',');
        if (!komma) break;
        *komma = '\0';
        start = komma + 1;
    }
    return n;
}

static int lese_kandidaten(const char *datei, Kandidat k[]) {
    FILE *f = fopen(datei, "r");
    if (!f) { printf("Datei %s nicht gefunden!\n", datei); return 0; }
    char zeile[512];
    int n = 0;
    fgets(zeile, sizeof zeile, f);           /* Kopfzeile ueberspringen */
    while (n < MAX_ZEILEN && fgets(zeile, sizeof zeile, f)) {
        char *fd[6];
        if (teile_zeile(zeile, fd, 6) < 6) continue;
        k[n].id = atoi(fd[0]);
        snprintf(k[n].name, FELD, "%s", fd[1]);
        snprintf(k[n].beruf, FELD, "%s", fd[2]);
        snprintf(k[n].stadt, FELD, "%s", fd[3]);
        snprintf(k[n].faehigkeiten, FELD * 2, "%s", fd[4]);
        k[n].erfahrung = atoi(fd[5]);
        n++;
    }
    fclose(f);
    return n;
}

static int lese_stellen(const char *datei, Stelle s[]) {
    FILE *f = fopen(datei, "r");
    if (!f) { printf("Datei %s nicht gefunden!\n", datei); return 0; }
    char zeile[512];
    int n = 0;
    fgets(zeile, sizeof zeile, f);
    while (n < MAX_ZEILEN && fgets(zeile, sizeof zeile, f)) {
        char *fd[6];
        if (teile_zeile(zeile, fd, 6) < 6) continue;
        s[n].id = atoi(fd[0]);
        snprintf(s[n].firma, FELD, "%s", fd[1]);
        snprintf(s[n].beruf, FELD, "%s", fd[2]);
        snprintf(s[n].stadt, FELD, "%s", fd[3]);
        snprintf(s[n].faehigkeiten, FELD * 2, "%s", fd[4]);
        s[n].min_erfahrung = atoi(fd[5]);
        n++;
    }
    fclose(f);
    return n;
}

/* Holt das naechste Stueck aus einer Liste "A;B;C" (bei jedem Aufruf das naechste).
 * Gibt 0 zurueck, wenn die Liste zu Ende ist. */
static int naechstes_teil(const char **pos, char *teil, size_t max) {
    if (**pos == '\0') return 0;
    const char *ende = strchr(*pos, ';');
    size_t laenge = ende ? (size_t)(ende - *pos) : strlen(*pos);
    if (laenge >= max) laenge = max - 1;
    memcpy(teil, *pos, laenge);
    teil[laenge] = '\0';
    *pos = ende ? ende + 1 : *pos + strlen(*pos);
    return 1;
}

/* Prueft, ob 'gesucht' in der Liste "A;B;C" vorkommt. */
static int hat_faehigkeit(const char *liste, const char *gesucht) {
    char teil[FELD];
    const char *pos = liste;
    while (naechstes_teil(&pos, teil, sizeof teil))
        if (strcmp(teil, gesucht) == 0) return 1;
    return 0;
}

/* Gibt einen Score von 0 bis 100 zurueck (0 = passt gar nicht). */
static int berechne_score(const Kandidat *k, const Stelle *s) {
    if (strcmp(k->beruf, s->beruf) != 0) return 0;   /* Beruf muss passen */

    int score = PUNKTE_BERUF;
    if (strcmp(k->stadt, s->stadt) == 0) score += PUNKTE_STADT;

    /* Anteil der geforderten Faehigkeiten, die der Kandidat hat */
    char teil[FELD];
    const char *pos = s->faehigkeiten;
    int gefordert = 0, vorhanden = 0;
    while (naechstes_teil(&pos, teil, sizeof teil)) {
        gefordert++;
        if (hat_faehigkeit(k->faehigkeiten, teil)) vorhanden++;
    }
    if (gefordert > 0)
        score += (PUNKTE_FAEHIGKEITEN * vorhanden + gefordert / 2) / gefordert;

    if (k->erfahrung >= s->min_erfahrung) score += PUNKTE_ERFAHRUNG;
    return score;
}

int main(void) {
    static Kandidat kandidaten[MAX_ZEILEN];
    static Stelle stellen[MAX_ZEILEN];
    int nk = lese_kandidaten("kandidaten.csv", kandidaten);
    int ns = lese_stellen("stellen.csv", stellen);
    if (nk == 0 || ns == 0) return 1;

    FILE *out = fopen("ergebnis.csv", "w");
    if (!out) { printf("Kann ergebnis.csv nicht schreiben!\n"); return 1; }
    fprintf(out, "stelle_id,firma,platz,kandidat,score\n");

    for (int i = 0; i < ns; i++) {
        printf("\nStelle %d: %s bei %s (%s)\n", stellen[i].id,
               stellen[i].beruf, stellen[i].firma, stellen[i].stadt);

        int scores[MAX_ZEILEN];
        for (int j = 0; j < nk; j++)
            scores[j] = berechne_score(&kandidaten[j], &stellen[i]);

        /* Die 3 besten finden: 3x den hoechsten Score suchen */
        for (int platz = 1; platz <= TOP; platz++) {
            int best = -1;
            for (int j = 0; j < nk; j++)
                if (scores[j] > 0 && (best == -1 || scores[j] > scores[best]))
                    best = j;
            if (best == -1) break;               /* keine Kandidaten mehr */

            printf("  %d. %-16s Score %3d  (%s, %d Jahre)\n", platz,
                   kandidaten[best].name, scores[best],
                   kandidaten[best].stadt, kandidaten[best].erfahrung);
            fprintf(out, "%d,%s,%d,%s,%d\n", stellen[i].id, stellen[i].firma,
                    platz, kandidaten[best].name, scores[best]);
            scores[best] = 0;                    /* nicht nochmal waehlen */
        }
    }
    fclose(out);
    printf("\nFertig! Ergebnis gespeichert in ergebnis.csv\n");
    return 0;
}

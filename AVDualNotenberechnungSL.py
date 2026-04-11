import math
import textwrap
from typing import Literal
import streamlit as st

# !streamlit run AVDualNotenberechnungSL.py --server.headless true

st.subheader("Notenberechnung AVDual")
st.markdown("<p style='font-size:10px; color:green;'>Version 5 - Frank Bader</p>", unsafe_allow_html=True)
st.markdown("""<style>
    div[data-testid="stTextInput"] input {
        /* 1. Horizontal zentrieren */
        text-align: center !important;

        /* 2. Vertikale Zentrierung erzwingen */
        height: 40px !important;       /* Eine feste Höhe für das Feld */
        line-height: 40px !important;  /* Gleicher Wert wie height zentriert den Text vertikal */
        padding: 0px !important;       /* Verhindert, dass Padding den Text wegdrückt */
        
        /* 3. Optik */
        font-size: 14px !important;
    }</style>""", unsafe_allow_html=True)

st.markdown("""<style>
    /* Alle durch st.write oder st.markdown erzeugten Standard-Texte ansprechen */
    .stApp p {
        font-size: 12px !important;    /* Schriftgröße verkleinern */
        margin-bottom: 0px !important; /* Abstand zur nächsten Zeile verringern */
        line-height: 1.0 !important;   /* Zeilenhöhe innerhalb des Textes verkleinern */
    }</style>""", unsafe_allow_html=True)

status = 0

col1_1, col1_2, col1_3 = st.columns([2, 1, 4])
with col1_1: st.markdown(""" <p style='margin:10; font-size:6px;'>Anmeldenote</p>
                             <p style='margin:10; font-size:10px;'>(ganze Note)</p>
                         """, unsafe_allow_html=True)

with col1_2: eingabe1 = st.text_input("eingabe1", label_visibility="collapsed")
error1 = col1_3.empty()   # Platz für Fehlermeldung

col2_1, col2_2, col2_3 = st.columns([2, 1, 4])
with col2_1: st.markdown(""" <p style='margin:0; font-size:12px;'>Kommunikationsprüfung</p>
                             <p style='margin:0; font-size:10px;'>(ganze oder halbe Note,</p>
                             <p style='margin:0; font-size:10px;'>leer, falls keine KP)</p>
                         """, unsafe_allow_html=True)

with col2_2: eingabe2 = st.text_input("eingabe2", label_visibility="collapsed")
error2 = col2_3.empty()

col3_1, col3_2, col3_3 = st.columns([2, 1, 4])
with col3_1: st.markdown(""" <p style='margin:0; font-size:12px;'>Schriftliche Prüfungsnote</p>
                             <p style='margin:0; font-size:10px;'>(ganze oder halbe Note)</p>
                         """, unsafe_allow_html=True)

with col3_2: eingabe3 = st.text_input("eingabe3", label_visibility="collapsed")
error3 = col3_3.empty()

# OK‑Button erscheint NUR hier rechts
ok = st.button("Berechne Zeugnisnote")

def round_0(x: float) -> float:
    """ Runden auf die nächste ganze Zahl.
        round(): Achtung: das Rundungsverfahren „Bankers Rounding“ (Tie-to-even).
    """
    return math.floor(x + 0.5)

def round_1(x: float) -> float:
    """ Rundet eine Kommazahl zuerst auf 1 Dezimalstellen ab (floor),
        und rundet das Ergebnis anschließend auf das nächste Vielfache von 0.5
    """
    x2 = math.floor(x * 10) / 10.0    # Schritt 1: auf 1 Dezimalstellen ABRUNDEN
    return round_0(x2 * 2) / 2.0      # Schritt 2: auf das nächste halbe Vielfache runden

def round_2(x: float) -> float:
    """ Rundet eine Kommazahl zuerst auf 1 Dezimalstellen ab (floor),
        und rundet das Ergebnis anschließend auf die nächste ganze Zahl
    """
    x2 = math.floor(x * 10) / 10.0    # Schritt 1: auf 1 Dezimalstellen ABRUNDEN
    return round_0(x2)                # Schritt 2: auf das nächste ganze Zahl runden

# --------------------------------------------------------
# Prüfung nach Button
# --------------------------------------------------------

def check_number(value, error_placeholder, art: Literal["ganz", "halb"]="ganz", muss: Literal["ja", "nein"]="ja") -> float:
    global status
    status += 1
    eingabe = value.strip()
    if eingabe == "" and muss == "ja":
        error_placeholder.error("Es muss eine Note eingegeben werden!")
        return None
    if eingabe == "":
        status -= 1
        return 0

    eingabe = eingabe.replace(",",".")
    try:
        zahl = float(eingabe)
    except ValueError:
        error_placeholder.error("Das ist keine gültige Dezimalzahl!")
        return None
    
    if zahl < 1 or zahl > 6:
        error_placeholder.error("Die Note muss zwischen 1 und 6 liegen!")
        return None

    if zahl != int(zahl) and art == "ganz":
        error_placeholder.error("Es muss eine ganze Note sein!")
        return None
    if zahl != round_1(zahl) and art == "halb":
        error_placeholder.error("Es muss eine ganze oder halbe Note sein!")
        return None
    status -= 1
    return zahl

if ok: # Button wurde gedrückt
    bem = ""
    status = 0
    AN  = check_number(eingabe1, error1, art="ganz", muss="ja")
    KP  = check_number(eingabe2, error2, art="halb", muss="nein")
    sPN = check_number(eingabe3, error3, art="halb", muss="ja")

    if status==0:
        if KP == 0:
            PEu = sPN
            PEg = sPN
        else:
            PEu = (2*sPN+KP)/3.0
            PEg = round_1(PEu)
        ZNu = (AN+PEg)/2.0
        ZNg = round_2(ZNu)

        # Ausgabe Notenübersicht
        st.subheader("Notenübersicht")
        col1_1, col1_2, col1_3 = st.columns([3, 1, 2])
        with col1_1: st.write("Anmeldenote:")
        with col1_2: st.write(AN)

        col1_1, col1_2, col1_3 = st.columns([3, 1, 2])
        with col1_1: st.write("Kommunikationsprüfung:")
        if KP == 0:
            with col1_2: st.write("keine")
            bem = "(= schriftliche Prüfung):"
        else:    
            with col1_2: st.write(KP)
            bem = "(mit Kommunikationsprüfung):"

        col1_1, col1_2, col1_3 = st.columns([3, 1, 2])
        with col1_1: st.write("Schriftliche Prüfung:")
        with col1_2: st.write(sPN)

        col1_1, col1_2, col1_3 = st.columns([3, 1, 2])
        with col1_1: st.write("Prüfungsergebnis "+bem)
        with col1_2: st.write(PEg)
        with col1_3: st.write("nicht gerundet: ", round(PEu,4))
        
        col1_1, col1_2, col1_3 = st.columns([3, 1, 2])
        with col1_1: st.write("Zeugnisnote (ohne mündliche Prüfung):")
        with col1_2: st.write(ZNg)
        with col1_3: st.write("nicht gerundet: ",round(ZNu,4))
        
        st.subheader("Zeugnisnote mit mündlicher Prüfung")

        # 1. Daten in der Schleife sammeln (NUR die <tr> Zeilen!)
        mPN = 1.0
        rows_html = ""

        while mPN <= 6.0:
            ZNu = (round_1((PEg + mPN) / 2.0) + AN)/2.0
            ZNg = round_2(ZNu)
            
            # WICHTIG: Hier nur die Zeilen bauen, KEIN </tbody> am Ende hinzufügen!
            rows_html += f"<tr><td>{mPN:.1f}</td><td>{ZNg}</td><td>{ZNu:.4f}</td></tr>"
            mPN += 0.5

        # 2. Das Template bauen
        tabelle_html = textwrap.dedent(f"""
            <style>
                .noten-tabelle {{
                    border-collapse: collapse;
                    width: auto;
                    font-family: sans-serif;
                    font-size: 10px;
                }}
                .noten-tabelle th, .noten-tabelle td {{
                    border: 1px solid #ddd;
                    padding: 1px 10px;
                    text-align: center;
                }}
                .noten-tabelle th {{
                    background-color: #f8f9fa;
                }}
            </style>
            <table class="noten-tabelle">
                <thead>
                    <tr>
                        <th>Mündliche Note</th>
                        <th>Zeugnisnote</th>
                        <th>nicht gerundet</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        """)

        # Jetzt ausgeben
        st.markdown(tabelle_html, unsafe_allow_html=True)
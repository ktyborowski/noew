import streamlit as st
import sqlite3
import pandas as pd
import json
from config import settings
def get_data(format):
    query = "SELECT * FROM results"
    con = sqlite3.connect(settings["database"])

    if format in ["csv", "tsv"]:
        df = pd.read_sql(query, con)

    if format == "csv":
        data = df.to_csv(index=False).encode("utf-8")
    elif format == "tsv":
        data = df.to_csv(index=False, sep="\t").encode("utf-8")
    elif format == "jsonl":
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()

        json_lines = [json.dumps(dict(row)) for row in rows]

        data = "\n".join(json_lines)
    else:
        raise ValueError(f"Uknown format: {format}")

    con.close()
    return data
def validate_data(df):
    columns = set(df.columns.values.tolist())
    required = {"text", "source", "category"}

    missing = required - columns
    if missing:
        return False, missing
    else:
        return True, {}


def write():
    st.write("# Dane")


    st.write("## Dane wejściowe")

    st.write(
        "Akcpetowanym formatem danych wejściowych w **NOEW** jest plik w fromacie CSV."
    )

    with st.expander("Struktura danych wejściowych"):
        st.write(
            """
            | Atrybut  | Opis                                          | Typ        | Opcjonalny |
            |----------|-----------------------------------------------|------------|------------|
            | text     | Tekst zdania.                                 | str        | Nie        |
            | source   | Źródło tekstu. Np. Twitter.                   | str        | Tak        |
            | category | Kategoria tekstu. Np. Recenzja, Komentarz etc.| str        | Tak        |
        """
        )
        st.write("")
    file = st.file_uploader("Wybierz plik CSV", key="files", type="csv")

    if file:


        conn = sqlite3.connect(settings["database"])
        cur = conn.cursor()

        cur.execute(
            """CREATE TABLE IF NOT EXISTS input (id INTEGER PRIMARY KEY ASC, text TEXT, source TEXT, category TEXT)"""
        )

        data = pd.read_csv(file)


        is_valid, missing = validate_data(data)

        if is_valid:
            data.to_sql("input", conn, if_exists="append", index=False)
            st.success(f"Pomyślnie załadowano dane z pliku: {file.name}.")
        else:
            message = "Załączony plik ma brakujące kolumny: {}.".format(", ".join(missing))
            st.error(message)

        conn.commit()
        cur.close()
        conn.close()


    st.write("## Dane wyjściowe")
    st.write("**NOEW** umożliwia ekport danych w formacie CSV lub Json Lines.")

    with st.expander("Struktura danych wyjściowych"):
        st.write(
            """
            | Atrybut   | Opis                                            | Typ        | Opcjonalny |
            |-----------|-------------------------------------------------|------------|------------|
            | text      | Tekst zdania.                                   | str        | Nie        |
            | source    | Źródło tekstu. Np. Twitter.                     | str        | Tak        |
            | category  | Kategoria tekstu. Np. Recenzja, Komentarz etc.  | str        | Tak        |
            | sentiment | Ogólny sentyment tekstu.                        | int        | Nie        |
            | happiness | Emocja rozpoznawalna w tekście - radość         | int        | Nie        |
            | sadness   | Emocja rozpoznawalna w tekście - smutek         | int        | Nie        |
            | fear      | Emocja rozpoznawalna w tekście - strach         | int        | Nie        |
            | disgust   | Emocja rozpoznawalna w tekście - wstręt         | int        | Nie        |
            | anger     | Emocja rozpoznawalna w tekście - złość          | int        | Nie        |
            | surprise  | Emocja rozpoznawalna w tekście - zaskoczenie    | int        | Nie        |
        """
        )
        st.write("")

        st.write("""
        Sentyment jest reprezentowany przez wartość numeryczną gdzie:  
        0 - Negatywny,  
        1 - Neutralny,  
        2 - Pozytywny.
    
        Emocje są reprezentowane przez wartość numeryczną zero-jedynkową.
        """)
    formats = {"CSV": "csv", "TSV": "tsv", "JSON Lines": "jsonl"}

    format_choice = st.selectbox("Wybierz format pliku", options=formats.keys())
    format = formats.get(format_choice)

    st.download_button("Pobierz dane", get_data(format), f"noew_data.{format}")

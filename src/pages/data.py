import streamlit as st
import sqlite3
import pandas as pd
import json
from config import settings


def get_data(format):
    query = "SELECT * FROM results"
    con = sqlite3.connect(settings["database"])

    if format == "csv":
        df = pd.read_sql(query, con)
    elif format == "jsonl":
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()

        json_lines = [json.dumps(dict(row)) for row in rows]

        return "\n".join(json_lines)
    else:
        raise ValueError(f"Uknown format: {format}")

    con.close()
    return df.to_csv(index=False).encode("utf-8")


def write():
    st.write("# Dane")

    st.write("## Dane wejściowe")

    st.write(
        "Akcpetowanym formatem danych wejściowych w **NOEW** jest plik w fromacie CSV."
    )

    st.write(
        """
        Struktura danych wejściowych:
        | Atrybut  | Opis                                           | Opcjonalny |
        |----------|------------------------------------------------|------------|
        | text     | Tekst zdania.                                  | Nie        |
        | source   | Źródło tekstu. Np. Twitter.                    | Tak        |
        | category | Kategoria tekstu. Np. Recenzja, Komentarz etc. | Tak        |
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
        data.to_sql("input", conn, if_exists="append", index=False)

        conn.commit()
        cur.close()
        conn.close()

        st.success(f"Pomyślnie załadowano dane z pliku: {file.name}.")

    st.write("## Dane wyjściowe")
    st.write("**NOEW** umożliwia ekport danych w formacie CSV lub Json Lines.")

    st.write(
        """
        Struktura danych wyjściowych:
        | Atrybut  | Opis                                           | Opcjonalny |
        |----------|------------------------------------------------|------------|
        | text     | Tekst zdania.                                  | Nie        |
        | source   | Źródło tekstu. Np. Twitter.                    | Tak        |
        | category | Kategoria tekstu. Np. Recenzja, Komentarz etc. | Tak        |
    """
    )
    st.write("")

    formats = {"CSV": "csv", "JSON Lines": "jsonl"}

    format_choice = st.selectbox("Wybierz format pliku", options=["CSV", "JSON Lines"])
    format = formats.get(format_choice)

    st.download_button("Pobierz dane", get_data(format), "noew_data.txt")

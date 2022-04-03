import zipfile
from io import BytesIO
import json
import sqlite3

import pandas as pd
import streamlit as st

from config import settings



def get_data(table, format):
    query = f"SELECT * FROM {table}"
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

def generate_zip(files):
    mem_zip = BytesIO()

    with zipfile.ZipFile(mem_zip, mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.writestr(f[0], f[1])

    return mem_zip.getvalue()

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
        con = sqlite3.connect(settings["database"])
        cur = con.cursor()

        data = pd.read_csv(file)

        is_valid, missing = validate_data(data)

        if is_valid:
            data.to_sql("input", con, if_exists="append", index=False)
            st.success(f"Pomyślnie załadowano dane z pliku: {file.name}.")
        else:
            message = "Załączony plik ma brakujące kolumny: {}.".format(
                ", ".join(missing)
            )
            st.error(message)

        con.commit()
        cur.close()
        con.close()

    st.write("## Dane wyjściowe")
    st.write(
        "**NOEW** umożliwia ekport oznaczonych danych w formacie CSV lub Json Lines."
    )

    with st.expander("Struktura danych wyjściowych"):
        st.write("##### Oznaczone:")
        st.write(
            """
            | Atrybut   | Opis                                            | Typ        | Opcjonalny |
            |-----------|-------------------------------------------------|------------|------------|
            | text      | Tekst zdania.                                   | str        | Nie        |
            | timestamp | Czas oznaczenia.                                | str        | Nie        |
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

        st.write(
            """
        Sentyment jest reprezentowany przez wartość numeryczną gdzie:  
        0 - Negatywny,  
        1 - Neutralny,  
        2 - Pozytywny.
    
        Emocje są reprezentowane przez wartość numeryczną zero-jedynkową.
        """
        )
        
        st.write("##### Pominięte:")
        st.write("Dane pominięte mają tę samą strukturę co dane wejściowe.")

    formats = {"CSV": "csv", "TSV": "tsv", "JSON Lines": "jsonl"}

    exports = {"Oznaczone": "labeled", "Pominięte": "skipped"}

   # export_choice = st.selectbox("Wybierz co eksportować", options=exports.keys())
    export_selection = st.multiselect("Wybierz co eksportować", options=exports.keys(), default=["Oznaczone"])

    if export_selection:
        disable_export = False
    else:
        disable_export = True


    format_choice = st.selectbox("Wybierz format pliku", options=formats.keys(), disabled=disable_export)
    export_format = formats.get(format_choice)

    file_format = ""
    file = ""
    if len(export_selection) > 1:
        files = []
        for selection in export_selection:
            table = exports.get(selection)
            data = get_data(table, export_format)
            file_name = f"{table}_noew_data.{export_format}"
            files.append((file_name, data))

        file = generate_zip(files)
        file_format = "zip"
    elif len(export_selection) == 1:
        table = exports.get(export_selection.pop())
        file = get_data(table, export_format)
        file_format = export_format



    st.download_button(
        "Pobierz dane", file, f"noew_data.{file_format}",
        disabled=disable_export
    )

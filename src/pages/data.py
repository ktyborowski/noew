import zipfile
from io import BytesIO
from datetime import datetime
import pandas as pd
import streamlit as st
from src import db


conn = db.init_connection()


def get_data(format):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
            annotation.created_at,
            input.text,
            score,
            magnitude,
            happiness,
            sadness,
            fear,
            disgust,
            anger,
            surprise FROM annotation
            LEFT JOIN input ON annotation.input_id = input.id;
        """)
        rows = cur.fetchall()

    df = pd.DataFrame(rows)

    if format == "csv":
        data = df.to_csv(index=False)
    elif format == "tsv":
        data = df.to_csv(index=False, sep="\t")
    elif format == "json":
        data = df.to_json(orient="records")
    else:
        raise ValueError(f"Uknown format: {format}")

    return data.encode("utf-8")


def generate_zip(files):
    mem_zip = BytesIO()

    with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.writestr(f[0], f[1])

    return mem_zip.getvalue()


def validate_data(df):
    columns = set(df.columns.values.tolist())
    required = {"text"}

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
        df = pd.read_csv(file)

        is_valid, missing = validate_data(df)

        if is_valid:
            df = df[["text"]]
            df["created_at"] = datetime.now()


            records = df.to_numpy().tolist()
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO input (text, created_at) VALUES (%s, %s)", records
                )
            # data.to_sql("input", conn, if_exists="append", index=False)
            st.success(f"Pomyślnie załadowano dane z pliku: {file.name}.")
        else:
            message = "Załączony plik ma brakujące kolumny: {}.".format(
                ", ".join(missing)
            )
            st.error(message)

    st.write("## Dane wyjściowe")
    st.write(
        "**NOEW** umożliwia ekport oznaczonych danych w formacie CSV, TSV lub Json Lines."
    )

    with st.expander("Struktura danych wyjściowych"):
        st.write("##### Oznaczone:")
        st.write(
            """
            | Atrybut    | Opis                                            | Typ        | Opcjonalny |
            |------------|-------------------------------------------------|------------|------------|
            | text       | Tekst zdania.                                   | str        | Nie        |
            | created_at | Czas oznaczenia.                                | str        | Nie        |
            | source     | Źródło tekstu. Np. Twitter.                     | str        | Tak        |
            | category   | Kategoria tekstu. Np. Recenzja, Komentarz etc.  | str        | Tak        |
            | score      | Ogólny sentyment tekstu.                        | int        | Nie        |
            | magnitude  | Natężenie emocji tekstu.                        | int        | Nie        |
            | happiness  | Emocja rozpoznawalna w tekście - radość         | int        | Nie        |
            | sadness    | Emocja rozpoznawalna w tekście - smutek         | int        | Nie        |
            | fear       | Emocja rozpoznawalna w tekście - strach         | int        | Nie        |
            | disgust    | Emocja rozpoznawalna w tekście - wstręt         | int        | Nie        |
            | anger      | Emocja rozpoznawalna w tekście - złość          | int        | Nie        |
            | surprise   | Emocja rozpoznawalna w tekście - zaskoczenie    | int        | Nie        |
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

    formats = {"CSV": "csv", "TSV": "tsv", "JSON": "json"}

    format_choice = st.selectbox("Wybierz format pliku", options=formats.keys())
    export_format = formats.get(format_choice)

    file_format = ""
    file = ""

    file = get_data(export_format)
    file_format = export_format

    st.download_button("Pobierz dane", file, f"noew_data.{file_format}")

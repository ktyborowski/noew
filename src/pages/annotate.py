import sqlite3
from datetime import datetime

import streamlit as st

from config import settings


def initalize_state():
    if "sentiment" not in st.session_state:
        st.session_state["sentiment"] = "Neutralny"

    if "data" not in st.session_state:
        st.session_state["submit"] = False

    if "text" not in st.session_state:
        st.session_state["text"] = None

    if "text_id" not in st.session_state:
        st.session_state["text_id"] = None


def reset_state():
    st.session_state["happiness"] = False
    st.session_state["sadness"] = False
    st.session_state["fear"] = False
    st.session_state["disgust"] = False
    st.session_state["anger"] = False
    st.session_state["surprise"] = False

    st.session_state["sentiment"] = "Neutralny"
    st.session_state["text"] = None


def insert_skip():
    conn = sqlite3.connect(settings["database"])
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO skipped(text, source, category) VALUES (?, ?, ?)",
        # FIXME: Add real category and source
        (st.session_state["text"], "", ""),
    )

    conn.commit()
    cur.close()
    conn.close()


def insert_annotation():
    conn = sqlite3.connect(settings["database"])
    cur = conn.cursor()
    sentiment_map = {"Negatywny": 0, "Neutralny": 1, "Pozytywny": 2}
    cur.execute(
        "INSERT INTO labeled VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            st.session_state["text"],
            datetime.now(),
            sentiment_map[st.session_state["sentiment"]],
            st.session_state["happiness"],
            st.session_state["sadness"],
            st.session_state["fear"],
            st.session_state["disgust"],
            st.session_state["anger"],
            st.session_state["surprise"],
        ),
    )

    conn.commit()
    cur.close()
    conn.close()


def delete_row(row_id):
    con = sqlite3.connect(settings["database"])
    cur = con.cursor()
    cur.execute("""DELETE FROM input WHERE id = ?""", (row_id,))
    con.commit()
    cur.close()
    con.close()


def on_submit(text_id):
    insert_annotation()
    reset_state()
    delete_row(text_id)


def on_skip(text_id):
    insert_skip()
    reset_state()
    delete_row(text_id)


def write():
    initalize_state()

    st.write(
        """
    # NOEW
    ## Narzędzie Oznaczania Emocji i Wydźwięku
    """
    )

    with st.expander("Jak korzystać?"):
        skip_message = ""
        if not settings["unskippable"]:
            skip_message = "*Jeśli nie wiesz jak oznaczyć zdanie, możesz je pominąć.*"
        st.write(
            f"""
             Oznaczanie danych za pomocą **NOEW**:

             1. Poczekaj do momentu załadowania kolejnego zdania.
             2. Przeczytaj zdanie. 
             3. Wybierz najbardziej odpowiadające emocje, kategorię oraz wydźwięk.
             4. Zatwierdź oznaczenia. {skip_message}
             5. Powtórz powyższe kroki na kolejnym zdaniu. 😉
         """
        )

    st.write("---")

    st.write("<p style='font-size:14px'>Tekst</p>", unsafe_allow_html=True)

    if not st.session_state["text"]:
        con = sqlite3.connect(settings["database"])

        cur = con.cursor()

        cur.execute("""SELECT * FROM input LIMIT 1""")
        row = cur.fetchone()

        if row:
            st.session_state["text"] = row[1]
            st.session_state["text_id"] = row[0]
        else:
            st.session_state["text"] = None

        con.commit()
        cur.close()
        con.close()

    if st.session_state["text"]:
        st.code(st.session_state["text"])
        form_col1, form_col2 = st.columns(2)
        form_col1.write("<p style='font-size:14px'>Emocje</p>", unsafe_allow_html=True)

        form_col1.checkbox(
            "😄 Radość",
            key="happiness",
            help="Stan emocjonalny, który wyraża w świadomości uczucie całkowitego spełnienia.",
        )
        form_col1.checkbox(
            "😞 Smutek",
            key="sadness",
            help="Stan emocjonalny powiązany z uczuciem niekorzystnej sytuacji, stratą, rozpaczą, żałobą, żalem, bezradnością oraz rozczarowaniem.",
        )
        form_col1.checkbox(
            "😱 Strach",
            key="fear",
            help="Niepokój wywołany przez grożące niebezpieczeństwo lub przez rzecz nieznaną, która wydaje się groźna.",
        )
        form_col1.checkbox(
            "🤢 Wstręt",
            key="disgust",
            help="Stan emocjonalny wyrażający odrazę do czegoś, kogoś lub sytuacji.",
        )
        form_col1.checkbox(
            "😡 Gniew",
            key="anger",
            help="Gwałtowna reakcja na jakiś przykry bodziec zewnętrzny wyrażająca się niezadowoleniem i agresją.",
        )
        form_col1.checkbox(
            "😮 Zaskoczenie",
            key="surprise",
            help="Stan emocjonalny wywołany doświadczeniem czegoś niespodziewanego.",
        )

        form_col2.select_slider(
            "Wydźwięk",
            key="sentiment",
            help="Ogólne nastawienie emocjonalne zdania.",
            options=["Negatywny", "Neutralny", "Pozytywny"],
        )
        st.write("---")

        buttons_col1, buttons_col2, _ = st.columns([1, 1, 3])
        submitted = buttons_col1.button(
            "✔️ Zatwierdź", on_click=on_submit, args=(st.session_state["text_id"],)
        )
        skipped = buttons_col2.button(
            "▶️ Pomiń",
            on_click=on_skip,
            disabled=settings["unskippable"],
            args=(st.session_state["text_id"],),
        )

        if submitted:
            st.success("Zdanie oznaczono pomyślnie. Dzięki!")
        if skipped:
            st.info("Pominięto zdanie.")
    else:
        st.warning("😕 Brak danych. Spróbuj ponownie później.")

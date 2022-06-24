from datetime import datetime
import streamlit as st
from src import db

ACCEPTED_TERMS_KEY = "accepted_terms"

conn = db.init_connection()

class AnnotationService:
    def __init__(self, conn) -> None:
        self.conn = conn

    score_map = {"Negatywny": 0, "Neutralny": 1, "Pozytywny": 2}
    magnitude_map = {
        "Znikome": 0,
        "Niskie": 1,
        "Umiarkowane": 2,
        "Wysokie": 3,
        "Bardzo Wysokie": 4,
    }

    def create_annotation(self):

        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO annotation (input_id, created_at, score, magnitude, happiness, sadness, fear, disgust, anger, surprise) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    st.session_state["text_id"],
                    datetime.now(),
                    self.score_map[st.session_state["score"]],
                    self.magnitude_map[st.session_state["magnitude"]],
                    st.session_state["happiness"],
                    st.session_state["sadness"],
                    st.session_state["fear"],
                    st.session_state["disgust"],
                    st.session_state["anger"],
                    st.session_state["surprise"],
                ),
            )
            self.conn.commit()


annotation_service = AnnotationService(conn)


def execute_query(connection, query: str, args=None) -> list:
    """Given sqlite3.Connection and a string query (and optionally necessary query args as a dict),
    Attempt to execute query with cursor, commit transaction, and return fetched rows"""
    with conn.cursor() as cur:
        if args is not None:
            cur.execute(query, args)
        else:
            cur.execute(query)
        connection.commit()
        results = cur.fetchall()
    return results


def initalize_state():
    if ACCEPTED_TERMS_KEY not in st.session_state:
        st.session_state[ACCEPTED_TERMS_KEY] = False

    if "score" not in st.session_state:
        st.session_state["score"] = "Neutralny"

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

    st.session_state["score"] = "Neutralny"
    st.session_state["magnitude"] = "Znikome"
    st.session_state["text"] = None


def delete_row(row_id):
    with conn.cursor() as cur:
        cur.execute("UPDATE input SET annotated = true WHERE id = %s", (row_id,))
        conn.commit()


def on_submit(text_id):
    annotation_service.create_annotation()

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
    with st.expander("Zanim zaczniesz..."):
        st.write("#### Jak korzystać?")
        st.write(
            """
             1. Poczekaj na załadowania zdania.
             2. Przeczytaj zdanie. 
             3. Wybierz najbardziej odpowiadające emocje oraz ustal parametry wydźwięku.
             4. Zatwierdź oznaczenia.
             5. Powtórz powyższe kroki na kolejnym zdaniu. 😉
         """
        )

        st.write("#### Jak interpretować parametry wydźwięku?")
        st.write(
            """
            | Wydźwięk           | Przykład                                         | Znak                | Natężenie                |
            |--------------------|--------------------------------------------------|---------------------|--------------------------|
            | Neutralny          | Mieszko I był władcą Polski.                     | Neutralny           | Znikome                  |
            | Mieszany           | Długi czas dostawy, ale produkty dobrej jakości. | Neutralny           | Słabe - Umiarkowane      |
            | Wyraźnie negatywny | Absolutnie nie polecam, strata czasu...          | Negatywny           | Wysokie - Bardzo wysokie |
            | Wyraźnie pozytywny | Praca z Tobą to wielka przyjemność!              | Pozytywny           | Wysokie - Bardzo wysokie |
            | Pozytywny          | Było całkiem ok.                                 | Pozytywny           | Słabe - Umiarkowane      |
        """
        )

    with st.expander("Warunki udziału"):
        st.write("#### Warunki")

    st.checkbox("Przeczytałem/am i akceptuję warunki udziału.", key=ACCEPTED_TERMS_KEY)
    if not st.session_state[ACCEPTED_TERMS_KEY]:
        st.warning("Musisz zaakceptować warunki udziału, aby móc oznaczać dane.")

    st.write("---")

    if not st.session_state["text"]:

        with conn.cursor() as cur:
            cur.execute(
                """SELECT * FROM input WHERE fetched = false AND annotated = false LIMIT 1"""
            )
            row = cur.fetchone()

            if row:
                id = row.get("id")

                st.session_state["text"] = row.get("text")
                st.session_state["text_id"] = id

                cur.execute("UPDATE input SET fetched = true WHERE id = %s", (id,))
                conn.commit()
            else:
                st.session_state["text"] = None

    if st.session_state["text"]:

        st.write("###### Tekst")
        st.code(st.session_state["text"])
        st.write("")

        form_col1, form_col2 = st.columns(2)
        form_col1.write("###### Emocje")

        form_col1.checkbox(
            "😄 Radość",
            key="happiness",
            help="Stan emocjonalny, który wyraża w świadomości uczucie całkowitego spełnienia.",
            disabled=not st.session_state[ACCEPTED_TERMS_KEY],
        )
        form_col1.checkbox(
            "😞 Smutek",
            key="sadness",
            help="Stan emocjonalny powiązany z uczuciem niekorzystnej sytuacji, stratą, rozpaczą, żałobą, żalem, bezradnością oraz rozczarowaniem.",
            disabled=not st.session_state[ACCEPTED_TERMS_KEY],
        )
        form_col1.checkbox(
            "😱 Strach",
            key="fear",
            help="Niepokój wywołany przez grożące niebezpieczeństwo lub przez rzecz nieznaną, która wydaje się groźna.",
            disabled=not st.session_state[ACCEPTED_TERMS_KEY],
        )
        form_col1.checkbox(
            "🤢 Wstręt",
            key="disgust",
            help="Stan emocjonalny wyrażający odrazę do czegoś, kogoś lub sytuacji.",
            disabled=not st.session_state[ACCEPTED_TERMS_KEY],
        )
        form_col1.checkbox(
            "😡 Złość",
            key="anger",
            help="Gwałtowna reakcja na jakiś przykry bodziec zewnętrzny wyrażająca się niezadowoleniem i agresją.",
            disabled=not st.session_state[ACCEPTED_TERMS_KEY],
        )
        form_col1.checkbox(
            "😮 Zaskoczenie",
            key="surprise",
            help="Stan emocjonalny wywołany doświadczeniem czegoś niespodziewanego.",
            disabled=not st.session_state[ACCEPTED_TERMS_KEY],
        )

        form_col2.write("###### Wydźwięk")
        form_col2.select_slider(
            "Znak",
            key="score",
            help="Ogólne nastawienie emocjonalne zdania.",
            options=["Negatywny", "Neutralny", "Pozytywny"],
            disabled=not st.session_state[ACCEPTED_TERMS_KEY],
        )

        form_col2.write("")
        form_col2.write("")
        form_col2.select_slider(
            "Natężenie",
            key="magnitude",
            help="Ogólne nastawienie emocjonalne zdania.",
            options=["Znikome", "Niskie", "Umiarkowane", "Wysokie", "Bardzo Wysokie"],
            disabled=not st.session_state[ACCEPTED_TERMS_KEY],
        )

        submitted = st.button(
            "Zatwierdź",
            on_click=on_submit,
            args=(st.session_state["text_id"],),
            disabled=not st.session_state[ACCEPTED_TERMS_KEY],
        )

        if submitted:
            st.success("Zdanie oznaczono pomyślnie. Dzięki!")

    else:
        st.warning("😕 Brak danych. Spróbuj ponownie później.")

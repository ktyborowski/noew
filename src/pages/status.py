import streamlit as st
import sqlite3
from config import settings
import time

def get_count(table):
    conn = sqlite3.connect(settings["database"])
    cur = conn.cursor()

    cur.execute(f"SELECT count(*) FROM {table}")
    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return count


def write():
    st.write("# Status")
    st.write("Ta strona przedstawia aktualne statystyki oznaczeń.")
    st.write("*Dane aktualizują się przy zmianie strony lub odświeżeniu przeglądarki.*")
    st.write("---")


    with st.spinner("Ładowanie..."):
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Oznaczono ✔️", value=get_count("results"))
        col2.metric(label="Pominięto ❌", value=10)
        col3.metric(label="Oczekujących ⏳", value=get_count("input"))



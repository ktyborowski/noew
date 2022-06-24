import streamlit as st
import psycopg

from psycopg.rows import dict_row

@st.experimental_singleton
def init_connection():
    conn = None
    try:
        conn = psycopg.connect(**st.secrets["postgres"], row_factory=dict_row)
    except:
        pass

    return conn
 
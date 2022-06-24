import streamlit as st

from src.db import init_connection

conn = init_connection()


def get_last_24h():
    with conn.cursor() as cur:
        cur.execute("""
            SELECT  COUNT(*)
            FROM    annotation
            WHERE   created_at >= NOW() - '1 day'::INTERVAL
        """)
    
        count = cur.fetchone().get("count")
    return count

def get_last_week():
    with conn.cursor() as cur:
        cur.execute("""
            SELECT  COUNT(*)
            FROM    annotation
            WHERE   created_at >= NOW() - '1 week'::INTERVAL
        """)
    
        count = cur.fetchone().get("count")
    return count



def get_annotated():
    with conn.cursor() as cur:
        cur.execute("""
            SELECT  COUNT(*)
            FROM    annotation
        """)
    
        count = cur.fetchone().get("count")
    return count

def get_all():
    with conn.cursor() as cur:
        cur.execute("""
            SELECT  COUNT(*)
            FROM    input
        """)
    
        count = cur.fetchone().get("count")
    return count

def write():
    st.write("# Status")
    st.write("Ta strona przedstawia aktualne statystyki oznaczeń.")
    st.caption("Dane aktualizują się przy zmianie strony lub odświeżeniu przeglądarki.")

    with st.spinner("Ładowanie..."):
        st.write("###### Ogółem")
        
        progress = (get_annotated()/get_all())
        st.progress(progress)
        col1, col2, col3 = st.columns(3)

        col1.metric(label="Ostatnie 24h", value=get_last_24h())
        col2.metric(label="Ostatni tydzień", value=get_last_week())
        col3.metric(label="Wszystkie", value=f"{get_annotated()}/{get_all()}")



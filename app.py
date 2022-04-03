"""Main module for the streamlit app"""
import logging
import sqlite3

import streamlit as st

import src.pages.data
import src.pages.annotate
import src.pages.status
from config import settings
from src.auth import check_password

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
log = logging.getLogger(__name__)


PAGES = {
    "Oznaczanie": src.pages.annotate,
    "Dane": src.pages.data,
    "Status": src.pages.status
}


def initialize_db():
    log.debug("Initializing database.")
    con = sqlite3.connect(settings["database"])
    con.execute('pragma journal_mode=wal')
    
    cur = con.cursor()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS input (id INTEGER PRIMARY KEY ASC, text TEXT, source TEXT, category TEXT)"""
    )

    cur.execute(
        """CREATE TABLE IF NOT EXISTS skipped (id INTEGER PRIMARY KEY ASC, text TEXT, source TEXT, category TEXT)"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS labeled
                       (text text,
                       timestamp text,
                       sentiment integer,
                       happiness integer,
                       sadness integer,
                       fear integer,
                       disgust integer,
                       anger integer,
                       surprise integer)"""
    )
    con.commit()
    cur.close()
    con.close()


def write_page(page):
    """Writes the specified page/module
    Our multipage app is structured into sub-files with a `def write()` function
    Arguments:
        page {module} -- A module with a 'def write():' function
    """

    page.write()


def main():
    st.set_page_config(
        page_title="NOEW: Narzędzie Oznaczania Emocji i Wydźwięku",
        page_icon="📝",
        layout="centered",
    )
    initialize_db()

    sidebar = st.sidebar
    sidebar.title("Nawigacja")
    selection = sidebar.radio("Idź do", list(PAGES.keys()))

    page = PAGES[selection]

    if selection in settings["auth"]:
        if check_password():
            write_page(page)
    else:
        write_page(page)


if __name__ == "__main__":
    main()

"""Main module for the streamlit app"""
import logging
from src import db

import streamlit as st
st.set_page_config(
    page_title="NOEW: Narzędzie Oznaczania Emocji i Wydźwięku",
    page_icon="📝",
    layout="centered",
)


conn = db.init_connection()
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


def write_page(page):
    """Writes the specified page/module
    Our multipage app is structured into sub-files with a `def write()` function
    Arguments:
        page {module} -- A module with a 'def write():' function
    """

    page.write()



def main():


    if conn:
        sidebar = st.sidebar
        sidebar.title("Nawigacja")
        selection = sidebar.radio("Idź do", list(PAGES.keys()))

        page = PAGES[selection]

        if selection in settings["auth"]:
            if check_password():
                write_page(page)
        else:
            write_page(page)
    else:
        st.error("Nie udało się połączyć z bazą danych. Spróbuj ponownie później.")


if __name__ == "__main__":
    main()

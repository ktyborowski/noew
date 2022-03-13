"""Main module for the streamlit app"""
import streamlit as st
import src.pages.home
import src.pages.data
import src.pages.options
import src.pages.about
from src.auth import check_password


PAGES = {
    "Home": src.pages.home,
    "Dane": src.pages.data,
    #"Konfiguracja": src.pages.options,
    #"Opis": src.pages.about,
}




def write_page(page):  # pylint: disable=redefined-outer-name
    """Writes the specified page/module
    Our multipage app is structured into sub-files with a `def write()` function
    Arguments:
        page {module} -- A module with a 'def write():' function
    """

    page.write()


def main():
    st.set_page_config(
        page_title="NOEW: Narzędzie Oznaczania Emocji i Wydźwięku",
        page_icon="🧊",
        layout="centered",
    )
    sidebar = st.sidebar
    sidebar.title("Nawigacja")
    selection = sidebar.radio("Go to", list(PAGES.keys()))

    page = PAGES[selection]

    if selection == "Dane":
        if check_password():
            write_page(page)
    else:
        write_page(page)


if __name__ == "__main__":
    main()

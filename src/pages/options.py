import streamlit as st


def write():
    st.write("# Konfiguracja")

    st.write("## Oznaczanie")

    st.checkbox("Zezwalaj na pomijanie.")
    st.checkbox(
        "Wyświetlaj źródło tekstu.",
    )
    st.checkbox(
        'Zezwalaj na "neutralne" oznaczenia emocji.',
        help='"Neutralne" - bez zaznaczonych emocji.',
    )

    st.write("## Dane")

    st.radio("Kto może pobierać dane?", options=["Wszyscy", "Administrator"])

    st.write("## Uwierzytelnianie")
    
    auth = st.checkbox("Uwierzytelnianie użytkowników")
    if auth:
        st.multiselect("Które strony wymagają uwierzytelniania?", options=["Home", "Dane", "Konfiguracja", "Opis"], default=["Konfiguracja"])
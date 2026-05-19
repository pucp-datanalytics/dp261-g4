from __future__ import annotations

import streamlit as st


def explain_metric(label: str, explanation: str) -> None:
    st.caption(f"{label}: {explanation}")


def status_box(status: str, message: str) -> None:
    if status == "Verde":
        st.success(f"Semáforo verde: {message}")
    elif status == "Rojo":
        st.warning(f"Semáforo rojo: {message}")
    else:
        st.info(f"Semáforo amarillo: {message}")


def business_note(text: str) -> None:
    st.info(f"Lectura de negocio: {text}")


def missing_warning(name: str) -> None:
    st.warning(f"No se encontró {name}. El dashboard continúa con la información disponible.")

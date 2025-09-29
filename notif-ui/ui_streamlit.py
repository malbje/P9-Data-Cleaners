# Frontend knapper i Streamlit - KUN UI. Ingen databasekode her.
# For at køre: streamlit run ui_streamlit.py

import streamlit as st
from datetime import date, datetime
import pandas as pd

DEMO_MODE = True

if DEMO_MODE:
    # Mock af "service-lag" så UI kan demonstreres uden backend
    class ValidationError(Exception):
        pass
    if "rows" not in st.session_state:
        st.session_state.rows = [] # en lille fake DB i lokalhukommelsen

        def find_index_by_email(email):
            for i, r in enumerate(st.session_state.rows):
                if r["email"].lower().strip() == email.lower().strip():
                    return i
            return -1
        
        def create_customer_logic(name: str, email: str, adress, str, cleaning_date_str: str):
            name = (name or "").strip()
            email = (email or "").strip()
            adress = (adress or "").strip()
            dstr = (cleaning_date_str or "").strip()

            if not name: raise ValidationError("Navn er påkrævet.")
            if "@" not in email: raise ValidationError("Ikke en rigtig email adresse.")
            if not  adress: raise ValidationError("Adresse er påkrævet.")
            try:
                d = datetime.strptime(dstr, "%Y-%m-%d").date()
            except Exception:
                raise ValidationError("Dato SKAL være i formatet YYYY-MM-DD.")
            if d < date.today():
                raise ValidationError("Rengøringsdato må ikke ligge i fortiden.")
            if find_index_by_email(email) != -1:
                raise ValidationError("Der findes allerede en kunde med denne email.")
            
            st.session_state.rows.append({
                "name": name, "email": email, "adress": adress, "cleaning_date": dstr
            })
            return {"status": "ok"}
        
        def update_date_logic(email: str, new_date_str: str):
            email = (email or "").strip()
            dstr = (new_date_str or "").strip()
            try:
                d = datetime.strptime(dstr, "%Y-%m-%d").date()
            except Exception:
                raise ValidationError("Ny dato skal være i formatet YYYY-MM-DD.")
            if d < date.today():
                raise ValidationError("Ny dato må ikke ligge i fortiden.")
            idx = _find_index_by_email(email)
            if idx == -1:
                raise ValidationError("Ingen kunde fundet med den email.")
            st.session_state.rows[idx]["cleaning_date"] = dstr
            return {"status": "ok"}
        
        def delete_customer_logic(email: str):
            email = (email or "").strip()
            idx = _find_index_by_email(email)
            if idx == -1:
                raise ValidationError("Ingen kunde fundet med denne email.")
            st.session_state.rows.pop(idx)
            return{"status": "ok"}
        
    else:
        # Rigtig backend: disse funktioner skal evt. laves i en fil ved navn "app.service"
        from app.service import (
            create_customer_logic,
            update_date_logic,
            delete_customer_logic,
            ValidationError,
        )

        
        # ========== Streamlit UI (knapper) ==========

        st.set_page_config(page_title="Rengøringsplan - Admin", page_icon="🧹", layout="centered")
        st.title("🧹 Rengøringsplan - Admin")
        st.caption("Frontend (knapper) til at oprette, opdatere og slette kunder.")

        # Overblikstabel - KUN for at se effekt i DEMO_MODE
        if DEMO_MODE:
            with st.expander("📋 Aktuelle kunder (demo)", expanded=True):
                df = pd.DataFrame(st.session_state.rows)
                if df.empty:
                    st.info("Ingen kunder endnu.")
                else:
                    df_show = df.rename(columns={
                        "name": "Navn", "email": "Email", "adress": "Adresse", "cleaning_date": "Rengøringsdato" 
                    })
                    st.dataframe(df_show, use_container_width=True, hide_index=True)

        st.divider()


        # ---------- Opret kunde ----------
        st.subheader("➕ Opret kunde")
        with st.form("form_create", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Navn")
            email = c2.text_input("Email")
            adress = st.text_input("Adresse")
            # data_input er mere brugervenligt - konverter til YYYY-MM-DD
            d = st.date_input("Rengøringsdato", value=date.today())
            created_clicked = st.form_submit_button("Opret kunde")
            if create_clicked:
                try:
                    res = create_customer_logic(name, email, adress, d.isformat())
                    st.success("Kunde oprettet.")
                    if DEMO_MODE: st.experimental_rerun()
                except ValidationError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Uventet fejl: {e}")

        st.divider()

        # ---------- Opdater dato ----------
        st.subheader("✏️ Opdater rengøringsdato")
        with st.form("form_update"):
            u1, u2 = st.columns(2)
            email:u = u1.text_input("Kunden email")
            d_new = u2.date_input("Ny dato", value=date.today())
            update_clicked = st.form_submit_button("Opdatér dato")
            if update_clicked:
                try:
                    update_date_logic(email_u, d_new.isformat())
                    st.success("Dato opdateret")
                    if DEMO_MODE: st.experimental_rerun()
                except ValidationError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Uventet fejl: {e}")

        st.divider()

        # ---------- Slet kunde ----------
        st.subheader("🗑️ Slet kunde")
        with st.form("form_delete"):
            email_d = st.text_input("Kundens email")
            delete_clicked = st.form_submit_button("Slet kunde", type="primary")
            if delete_clicked:
                # Enkel bekræftelse for at slette kunde
                confirm = st.checkbox("Ja, jeg er sikker")
                if confirm:
                    try:
                        delete_customer_logic(email_d)
                        st.success("Kunde slettet")
                        if DEMO_MODE: st.experimental_rerun()
                    except ValidationError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error (f"Uventet fejl: {e}")

                    else:
                        st.info("Sæt flueben for at bekræfte sletning")
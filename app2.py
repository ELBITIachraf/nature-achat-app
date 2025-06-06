import streamlit as st
import pandas as pd
from io import BytesIO

# -------- PAGE CONFIG --------
st.set_page_config(page_title="Valeo - Traitement Données Finance", page_icon="💼", layout="wide")

# -------- HEADER DESIGN --------
col_logo, col_title = st.columns([3, 9])
with col_logo:
    st.image("https://raw.githubusercontent.com/ELBITIachraf/nature-achat-app/main/Valeo_Logo.svg.png", width=100)


# -------- PAGE CONFIG --------

if "mode" not in st.session_state:
    st.session_state.mode = None
# -------- HEADER DESIGN --------
col_logo, col_title = st.columns([3, 9])


with col_title:
    st.markdown("""
        <div style='display: flex; flex-direction: column; justify-content: center; height: 100%; margin-top: 20px;'>
            <h1 style='font-size: 32px; margin-bottom: 10px;'>📊 Outil Finance - Traitement des Données</h1>
            <p style='font-size: 18px; color: grey; margin-top: 0;margin-left: 7%;'>Détermination automatique de la nature d’achat & génération de clé</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

if st.session_state.mode is None:
    st.markdown("### Que souhaitez-vous faire ?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧠 Déterminer la Nature d'achat"):
            st.session_state.mode = "nature"
    with col2:
        if st.button("🔐 Générer la Clé"):
            st.session_state.mode = "cle"

# -------- MODE : NATURE D'ACHAT --------
elif st.session_state.mode == "nature":
    st.markdown("### 🧠 Détermination automatique de la nature d'achat")
    uploaded_file = st.file_uploader("📂 Importer un fichier Excel (.xlsx)", type=["xlsx"], key="nature_file")

    if uploaded_file:
        with st.spinner("Chargement du fichier..."):
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()

        df["Nature d'achat finale"] = df.apply(lambda row: str(row.get("Nature d'achat unique ou spécifique", "") or "").strip()
            if str(row.get("Nature d'achat unique ou spécifique", "") or "").strip().lower() not in ["", "vide", "nan"]
            else (str(row.get("Nature achat commandes fermées", "") or "").strip()
            if str(row.get("Nature achat commandes fermées", "") or "").strip().lower() not in ["", "vide", "nan"]
            else str(row.get("Nature d'achat du compte", "") or "").strip()), axis=1)

        st.success("✅ Colonne 'Nature d'achat finale' ajoutée.")
        st.dataframe(df.head(10))

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Résultat")
        output.seek(0)

        st.download_button("📥 Télécharger le résultat", output, file_name="Valeo_Nature_Achat.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.button("⬅️ Retour", on_click=lambda: st.session_state.update({"mode": None}))

# -------- MODE : CLÉ --------
elif st.session_state.mode == "cle":
    st.markdown("### 🔐 Génération de la Clé d'achat")
    uploaded_file = st.file_uploader("📂 Importer un fichier Excel (.xlsx)", type=["xlsx"], key="cle_file")

    if uploaded_file:
        with st.spinner("Chargement du fichier..."):
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()

        def safe(row, col):
            return str(row.get(col, "") or "").strip()

        def generer_cle(row):
            nature_piece = safe(row, "Nature pièce").lower()
            tv = safe(row, "TV")
            zone_geo = safe(row, "Zone géographique")
            nature_achat = safe(row, "Nature d'achat finale")
            option_debit = safe(row, "Option débit")

            if nature_piece in ["paiement", "provision", "lettrage", "od"]:
                return f"{safe(row, 'Nature pièce')}_{tv}"
            elif nature_piece == "ndf":
                return f"{safe(row, 'Nature pièce')}_{zone_geo}_{tv}"
            else:
                return f"{zone_geo}_{safe(row, 'Nature pièce')}_{nature_achat}_{tv}_{option_debit}"

        df["Clé"] = df.apply(generer_cle, axis=1)
        st.success("✅ Colonne 'Clé' générée avec succès.")
        st.dataframe(df.head(10))

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Résultat")
        output.seek(0)

        st.download_button("📥 Télécharger le résultat", output, file_name="Valeo_Cle_Achat.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.button("⬅️ Retour", on_click=lambda: st.session_state.update({"mode": None}))

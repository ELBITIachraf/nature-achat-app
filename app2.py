import streamlit as st
import pandas as pd
from io import BytesIO

# -------- PAGE CONFIG --------
st.set_page_config(page_title="Valeo - Traitement Données Finance", page_icon="💼", layout="wide")

# -------- HEADER DESIGN --------
col_logo, col_title = st.columns([3, 9])
with col_logo:
    st.image("https://raw.githubusercontent.com/ELBITIachraf/nature-achat-app/main/Valeo_Logo.svg.png", width=100)

with col_title:
    st.markdown("""
        <div style='display: flex; flex-direction: column; justify-content: center; height: 100%; margin-top: 20px;'>
            <h1 style='font-size: 32px; margin-bottom: 10px;'>📊 Outil Finance - Traitement des Données</h1>
            <p style='font-size: 18px; color: grey; margin-top: 0;margin-left: 7%;'>Détermination automatique de la nature d’achat & génération de clé</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -------- FONCTIONS MÉTIERS --------
def determiner_nature_achat(row):
    val1 = str(row.get("Nature achat commandes fermées", "") or "").strip()
    val2 = str(row.get("Nature d'achat unique ou spécifique", "") or "").strip()
    val3 = str(row.get("Nature d'achat du compte", "") or "").strip()
    if val2.lower() not in ["", "vide", "nan"]:
        return val2
    elif val1.lower() not in ["", "vide", "nan"]:
        return val1
    else:
        return val3

def generer_cle(row):
    def safe(col_name):
        return str(row.get(col_name, "") or "").strip()
    nature_piece = safe("Nature pièce").lower()
    tv = safe("TV")
    zone_geo = safe("Zone géographique")
    nature_achat = safe("Nature d'achat finale")
    option_debit = safe("Option débit")

    if nature_piece in ["paiement", "provision", "lettrage", "od"]:
        return f"{safe('Nature pièce')}_{tv}"
    elif nature_piece == "ndf":
        return f"{safe('Nature pièce')}_{zone_geo}_{tv}"
    else:
        return f"{zone_geo}_{safe('Nature pièce')}_{nature_achat}_{tv}_{option_debit}"

# -------- UPLOAD & TRAITEMENT --------
st.subheader("📂 Importer un fichier Excel (.xlsx)")

uploaded_file = st.file_uploader("Déposez ou sélectionnez un fichier", type=["xlsx"])

if uploaded_file:
    with st.spinner("📊 Chargement et analyse du fichier..."):
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()
            st.success("✅ Fichier chargé avec succès.")
            st.dataframe(df.head(30))

            col1, col2 = st.columns(2)

            with col1:
               if st.button("🧠 Déterminer la Nature d'achat finale"):
                 with st.spinner("⏳ Détermination en cours..."):
                   
                   df["Nature d'achat finale"] = df.apply(determiner_nature_achat, axis=1)
                 st.success("✅ Colonne 'Nature d'achat finale' ajoutée.")

            with col2:
                if st.button("🔐 Générer la Clé"):
                    if "Nature d'achat finale" not in df.columns:
                        st.warning("⚠️ Veuillez d'abord calculer 'Nature d'achat finale'.")
                    else:
                        df["Clé"] = df.apply(generer_cle, axis=1)
                        st.success("✅ Colonne 'Clé' générée avec succès.")
                        st.dataframe(df[["Clé"]].head(5))

            st.markdown("---")
            st.subheader("📥 Exporter les résultats")
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Résultat")
            output.seek(0)

            st.download_button(
                label="📁 Télécharger le fichier final (.xlsx)",
                data=output,
                file_name="Valeo_Traitement_Donnees.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Erreur : {e}")

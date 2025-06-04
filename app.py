import streamlit as st
import pandas as pd

st.title("🚦 Détermination de la Nature d'Achat")

def determiner_nature_achat(row):
    val1 = str(row.get("Nature achat commandes fermées", "")).strip()
    val2 = str(row.get("Nature d'achat unique ou spécifique", "")).strip()
    val3 = str(row.get("Nature d'achat du compte", "")).strip()

    if val2.lower() not in ["", "vide", "nan"]:
        return val2
    elif val1.lower() not in ["", "vide", "nan"]:
        return val1
    else:
        return val3

uploaded_file = st.file_uploader("📂 Importez votre fichier Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        if "Nature d'achat finale" in df.columns:
            df.drop(columns=["Nature d'achat finale"], inplace=True)

        df["Nature achat finale"] = df.apply(determiner_nature_achat, axis=1)

        st.success("✅ Traitement terminé avec succès.")
        st.dataframe(df)

        # Télécharger
        output = "Resultat_Nature_Achat_FINAL.xlsx"
        df.to_excel(output, index=False)

        with open(output, "rb") as f:
            st.download_button("📥 Télécharger le fichier final", f, file_name=output)

    except Exception as e:
        st.error(f"❌ Erreur lors du traitement : {e}")

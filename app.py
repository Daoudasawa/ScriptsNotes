import streamlit as st
import pandas as pd
import io

# Configuration de la page
st.set_page_config(
    page_title="Notes - Gestionnaire de Notes",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Style personnalisé pour un look "Premium"
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: white;
    }
    
    .stApp {
        background: transparent;
    }
    
    .title-container {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    h1 {
        background: linear-gradient(90deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem !important;
    }
    
    .upload-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .upload-card:hover {
        border-color: #818cf8;
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.05);
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #6366f1, #a855f7);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
    }
    
    .success-box {
        background: rgba(34, 197, 94, 0.1);
        color: #4ade80;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(34, 197, 94, 0.2);
        margin: 1rem 0;
    }
    
    .stSelectbox label, .stFileUploader label {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# En-tête
st.markdown('<div class="title-container"><h1>Gestionnaire de Notes Étudiants</h1><p style="color: #94a3b8;">Fusion intelligente et tri par INE pour vos délibérations</p></div>', unsafe_allow_html=True)

# Layout principal en deux colonnes pour les uploads
col1, col2 = st.columns(2)

df_pv = None
df_examen = None

with col1:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.subheader(" Fichier PV")
    uploaded_pv = st.file_uploader("Déposez le PV de délibération", type=['xlsx', 'xls', 'csv'], key="pv")
    if uploaded_pv:
        try:
            if uploaded_pv.name.endswith('.csv'):
                df_pv = pd.read_csv(uploaded_pv, sep=None, engine='python')
            else:
                df_pv = pd.read_excel(uploaded_pv)
            st.success(f"PV chargé : {len(df_pv)} lignes")
        except Exception as e:
            st.error(f"Erreur lors de la lecture du PV : {e}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.subheader(" Fichier Examen")
    uploaded_examen = st.file_uploader("Déposez le fichier du module d'examen", type=['xlsx', 'xls', 'csv'], key="examen")
    if uploaded_examen:
        try:
            if uploaded_examen.name.endswith('.csv'):
                df_examen = pd.read_csv(uploaded_examen, sep=None, engine='python')
            else:
                df_examen = pd.read_excel(uploaded_examen)
            st.success(f"Fichier Examen chargé : {len(df_examen)} lignes")
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier examen : {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# Configuration du traitement si les deux fichiers sont chargés
if df_pv is not None and df_examen is not None:
    st.markdown('<hr style="border-color: rgba(255,255,255,0.1); margin: 2rem 0;">', unsafe_allow_html=True)
    
    st.subheader(" Configuration des colonnes")
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        ine_pv_col = st.selectbox("Colonne INE (dans le PV)", options=df_pv.columns)
    
    with c2:
        module_col = st.selectbox("Colonne du Module (dans le PV)", options=df_pv.columns)
        
    with c3:
        ine_exam_col = st.selectbox("Colonne INE (dans l'Examen)", options=df_examen.columns)
        
    with c4:
        target_note_col = st.selectbox("Colonne Note Destination", options=df_examen.columns)

    if st.button(" Lancer le Traitement"):
        with st.spinner("Traitement en cours..."):
            try:
                # 1. Préparation des données PV
                # On ne garde que INE et la colonne du module
                pv_notes = df_pv[[ine_pv_col, module_col]].copy()
                
                # 2. Nettoyage : s'assurer que l'INE est traité comme une chaîne pour la fusion
                pv_notes[ine_pv_col] = pv_notes[ine_pv_col].astype(str).str.strip()
                df_examen[ine_exam_col] = df_examen[ine_exam_col].astype(str).str.strip()
                
                # Renommer pour la fusion
                pv_notes = pv_notes.rename(columns={module_col: 'note_source'})
                
                # 3. Fusion (Left join pour garder tous les étudiants de l'examen)
                # On supprime d'abord l'ancienne colonne de note si elle existe ou on va la mettre à jour
                df_result = df_examen.copy()
                
                # Fusionner avec les notes du PV
                df_result = df_result.merge(pv_notes, left_on=ine_exam_col, right_on=ine_pv_col, how='left')
                
                # 4. Appliquer les notes
                # Si note_source est absent (NaN), mettre 0
                df_result['note_source'] = df_result['note_source'].fillna(0)
                
                # Mettre à jour la colonne cible
                df_result[target_note_col] = df_result['note_source']
                
                # Supprimer les colonnes temporaires de fusion
                cols_to_drop = ['note_source']
                if ine_pv_col != ine_exam_col: # Ne pas supprimer si c'est la même colonne
                    cols_to_drop.append(ine_pv_col)
                df_result = df_result.drop(columns=[c for c in cols_to_drop if c in df_result.columns])
                
                # 5. Trier par INE
                df_result = df_result.sort_values(by=ine_exam_col)
                
                st.markdown('<div class="success-box">Traitement terminé avec succès !</div>', unsafe_allow_html=True)
                
                # Préparation du téléchargement (Toujours en Excel pour éviter les erreurs de formatage)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_result.to_excel(writer, index=False)
                processed_data = output.getvalue()
                
                # S'assurer que l'extension est .xlsx
                new_filename = uploaded_examen.name
                if new_filename.lower().endswith('.csv'):
                    new_filename = new_filename[:-4] + ".xlsx"
                elif not new_filename.lower().endswith('.xlsx'):
                    new_filename = new_filename + ".xlsx"

                st.download_button(
                    label=" Télécharger le fichier mis à jour",
                    data=processed_data,
                    file_name=new_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Aperçu
                st.subheader(" Aperçu du résultat")
                st.dataframe(df_result.head(10), use_container_width=True)
                
            except Exception as e:
                st.error(f"Une erreur est survenue lors du traitement : {e}")

else:
    st.info(" Veuillez charger les deux fichiers Excel pour commencer la configuration.")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 5rem; color: #4b5563; font-size: 0.8rem;">
    DSI 
</div>
""", unsafe_allow_html=True)
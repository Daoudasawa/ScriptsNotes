import streamlit as st
import pandas as pd
import io
import logging
from typing import Tuple, Optional, Dict, List
import numpy as np
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

# ============ FONCTIONS UTILITAIRES ============

def load_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Charge un fichier CSV ou Excel de manière sécurisée.
    NB: Pas de @st.cache_data car les fichiers uploadés changent
    
    Args:
        uploaded_file: Fichier uploadé via Streamlit
        
    Returns:
        DataFrame ou None en cas d'erreur
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            return pd.read_excel(uploaded_file)
    except Exception as e:
        logger.error(f"Erreur lors du chargement du fichier {uploaded_file.name}: {e}")
        raise


def validate_dataframe(df: pd.DataFrame, file_type: str = "fichier") -> Dict[str, any]:
    """
    Valide la qualité des données d'un DataFrame.
    
    Args:
        df: DataFrame à valider
        file_type: Type de fichier pour les messages
        
    Returns:
        Dict avec les résultats de validation
    """
    issues = []
    warnings = []
    
    # Vérifier les lignes vides
    empty_rows = df.index[df.isna().all(axis=1)].tolist()
    if empty_rows:
        warnings.append(f"⚠️ {len(empty_rows)} lignes complètement vides")
    
    # Vérifier les doublons
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        warnings.append(f"⚠️ {duplicates} lignes dupliquées détectées")
    
    # Vérifier les colonnes vides
    empty_cols = [col for col in df.columns if df[col].isna().all()]
    if empty_cols:
        issues.append(f"❌ Colonnes complètement vides : {', '.join(empty_cols)}")
    
    # Vérifier les types de données
    for col in df.columns:
        null_count = df[col].isna().sum()
        null_pct = (null_count / len(df)) * 100
        if null_pct > 50:
            warnings.append(f"⚠️ Colonne '{col}' : {null_pct:.1f}% de valeurs vides")
    
    return {
        "issues": issues,
        "warnings": warnings,
        "empty_rows": empty_rows,
        "duplicates": duplicates,
        "empty_cols": empty_cols
    }


def normalize_grades(series: pd.Series, column_name: str = "note") -> Tuple[pd.Series, List[str]]:
    """
    Normalise les notes : conversion en nombres, gestion virgule/point, validation plage.
    
    Args:
        series: Série pandas avec les notes
        column_name: Nom de la colonne pour les messages
        
    Returns:
        Tuple (série normalisée, liste des problèmes)
    """
    issues = []
    normalized = series.copy()
    
    # Étape 1 : Convertir en string pour nettoyer
    normalized = normalized.astype(str).str.strip()
    
    # Étape 2 : Remplacer virgule par point (normalisation français/international)
    normalized = normalized.str.replace(',', '.', regex=False)
    
    # Étape 3 : Supprimer les caractères non numériques (sauf . et -)
    normalized = normalized.str.replace(r'[^\d.\-]', '', regex=True)
    
    # Étape 4 : Convertir en float
    normalized = pd.to_numeric(normalized, errors='coerce')
    
    # Étape 5 : Valider la plage (notes généralement 0-20)
    invalid_range = normalized[(normalized < 0) | (normalized > 20)].index.tolist()
    if invalid_range:
        issues.append(f"⚠️ {column_name} : {len(invalid_range)} valeurs hors plage 0-20")
    
    # Étape 6 : Vérifier les NaN créées par conversion
    nan_count = normalized.isna().sum()
    if nan_count > 0:
        original_nan = series.isna().sum()
        new_nan = nan_count - original_nan
        if new_nan > 0:
            issues.append(f"⚠️ {column_name} : {new_nan} valeurs non numériques converties en NaN")
    
    return normalized, issues


def validate_columns(df: pd.DataFrame, required_columns: list) -> bool:
    """
    Valide que les colonnes requises existent dans le DataFrame.
    
    Args:
        df: DataFrame à valider
        required_columns: Liste des colonnes requises
        
    Returns:
        True si toutes les colonnes existent
    """
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"❌ Colonnes manquantes : {', '.join(missing_cols)}")
        return False
    return True


def check_ine_matches(pv_df: pd.DataFrame, exam_df: pd.DataFrame, 
                     ine_pv_col: str, ine_exam_col: str) -> Dict[str, any]:
    """
    Vérifie la correspondance des INE entre les deux fichiers.
    
    Args:
        pv_df: DataFrame du PV
        exam_df: DataFrame de l'examen
        ine_pv_col: Colonne INE du PV
        ine_exam_col: Colonne INE de l'examen
        
    Returns:
        Dict avec les statistiques de correspondance
    """
    pv_ine = set(pv_df[ine_pv_col].astype(str).str.strip())
    exam_ine = set(exam_df[ine_exam_col].astype(str).str.strip())
    
    missing_in_pv = exam_ine - pv_ine  # Étudiants sans notes
    extra_in_pv = pv_ine - exam_ine    # Étudiants dans PV mais pas exam
    matches = pv_ine & exam_ine
    
    return {
        "total_exam": len(exam_ine),
        "total_pv": len(pv_ine),
        "matched": len(matches),
        "missing_in_pv": len(missing_in_pv),
        "extra_in_pv": len(extra_in_pv),
        "pct_match": (len(matches) / len(exam_ine) * 100) if exam_ine else 0
    }


def merge_grades(pv_df: pd.DataFrame, exam_df: pd.DataFrame, 
                 ine_pv_col: str, module_col: str, 
                 ine_exam_col: str, target_note_col: str,
                 missing_value_strategy: str = "zero",
                 normalize_notes: bool = True) -> Tuple[pd.DataFrame, Dict]:
    """
    Fusionne les notes du PV avec le fichier examen avec normalisation.
    
    Args:
        pv_df: DataFrame du PV
        exam_df: DataFrame de l'examen
        ine_pv_col: Colonne INE du PV
        module_col: Colonne des notes du module
        ine_exam_col: Colonne INE de l'examen
        target_note_col: Colonne cible pour les notes
        missing_value_strategy: Stratégie pour les valeurs manquantes
        normalize_notes: Si True, normalise les notes (virgule→point, validation)
        
    Returns:
        Tuple (DataFrame fusionné et trié, dict with stats)
    """
    # Initialiser les stats
    stats = {"normalization_issues": []}
    
    # Préparation des données
    pv_notes = pv_df[[ine_pv_col, module_col]].copy()
    
    # NORMALISATION DES NOTES IMPORTANT!
    if normalize_notes:
        normalized, issues = normalize_grades(pv_notes[module_col], module_col)
        pv_notes[module_col] = normalized
        stats["normalization_issues"].extend(issues)
    
    # Nettoyage des INE
    pv_notes[ine_pv_col] = pv_notes[ine_pv_col].astype(str).str.strip()
    exam_df = exam_df.copy()
    exam_df[ine_exam_col] = exam_df[ine_exam_col].astype(str).str.strip()
    
    # Renommage pour la fusion
    pv_notes = pv_notes.rename(columns={module_col: 'note_source'})
    
    # Fusion
    result = exam_df.merge(pv_notes, left_on=ine_exam_col, right_on=ine_pv_col, how='left')
    
    # Gestion des valeurs manquantes
    if missing_value_strategy == "zero":
        result['note_source'] = result['note_source'].fillna(0)
    elif missing_value_strategy == "drop":
        result = result.dropna(subset=['note_source'])
    
    # Application des notes
    result[target_note_col] = result['note_source']
    
    # Nettoyage des colonnes temporaires
    cols_to_drop = ['note_source']
    if ine_pv_col != ine_exam_col:
        cols_to_drop.append(ine_pv_col)
    result = result.drop(columns=[c for c in cols_to_drop if c in result.columns])
    
    # Tri par INE
    result = result.sort_values(by=ine_exam_col).reset_index(drop=True)
    
    stats["rows_processed"] = len(result)
    logger.info(f"Fusion complétée : {len(result)} lignes")
    return result, stats


def export_to_excel(df: pd.DataFrame, original_filename: str) -> bytes:
    """
    Exporte un DataFrame en fichier Excel.
    
    Args:
        df: DataFrame à exporter
        original_filename: Nom du fichier original pour génération du nom
        
    Returns:
        Bytes du fichier Excel
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Notes')
    
    return output.getvalue()


def prepare_download_file(df: pd.DataFrame, original_filename: str) -> Tuple[bytes, str, str]:
    """
    Prepare le fichier a telecharger en Excel pour eviter les problemes
    d'affichage lies aux formats CSV ou aux anciens fichiers .xls.
    """
    base_filename = re.sub(r"\.(csv|xls|xlsx)$", "", original_filename, flags=re.IGNORECASE)
    download_filename = f"{base_filename}.xlsx"

    data = export_to_excel(df, original_filename)
    return data, download_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# En-tête
st.markdown('<div class="title-container"><h1>Gestionnaire de Notes Étudiants</h1><p style="color: #94a3b8;">Fusion intelligente et tri par INE pour vos délibérations</p></div>', unsafe_allow_html=True)

# ============ INTERFACE PRINCIPALE ============

# Layout principal pour les uploads
col1, col2 = st.columns(2)

df_pv = None
exam_files_dict = {}  # Support multi-modules
uploaded_pv = None

with col1:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.subheader(" Fichier PV")
    uploaded_pv = st.file_uploader("Déposez le PV de délibération", type=['xlsx', 'xls', 'csv'], key="pv", disabled=False)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.subheader(" Fichiers Examen (Multi-modules)")
    uploaded_exams = st.file_uploader(
        "Déposez le(s) fichier(s) du module d'examen", 
        type=['xlsx', 'xls', 'csv'], 
        key="examen",
        accept_multiple_files=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ============ CHARGEMENT ET VALIDATION DU PV ============
if uploaded_pv:
    try:
        df_pv = load_file(uploaded_pv)
        st.success(f"✅ PV chargé : {len(df_pv)} lignes")
        
        # Validation immédiate du PV
        pv_validation = validate_dataframe(df_pv, "PV")
        
        # Afficher les problèmes
        if pv_validation["issues"]:
            for issue in pv_validation["issues"]:
                st.error(issue)
        
        if pv_validation["warnings"]:
            with st.expander("⚠️ Avertissements du PV"):
                for warning in pv_validation["warnings"]:
                    st.warning(warning)
        
        # Aperçu immédiat du PV
        with st.expander("👁️ Aperçu du PV", expanded=False):
            col_preview1, col_preview2 = st.columns(2)
            with col_preview1:
                st.caption(f"Dimensions : {df_pv.shape[0]} lignes × {df_pv.shape[1]} colonnes")
                st.caption(f"Colonnes : {', '.join(df_pv.columns[:5])}...")
            with col_preview2:
                st.caption(f"Types : {df_pv.dtypes.value_counts().to_dict()}")
            
            st.dataframe(df_pv.head(10), use_container_width=True, height=300)
    
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du PV : {e}")
        df_pv = None

# ============ CHARGEMENT ET VALIDATION DES FICHIERS EXAMEN ============
if uploaded_exams:
    for uploaded_exam in uploaded_exams:
        try:
            df_exam = load_file(uploaded_exam)
            exam_files_dict[uploaded_exam.name] = df_exam
            st.success(f"✅ {uploaded_exam.name} : {len(df_exam)} lignes")
            
            # Validation immédiate
            exam_validation = validate_dataframe(df_exam, uploaded_exam.name)
            
            # Afficher les problèmes
            if exam_validation["issues"]:
                for issue in exam_validation["issues"]:
                    st.error(issue)
            
            if exam_validation["warnings"]:
                with st.expander(f"⚠️ Avertissements - {uploaded_exam.name}"):
                    for warning in exam_validation["warnings"]:
                        st.warning(warning)
            
            # Aperçu immédiat
            with st.expander(f"👁️ Aperçu - {uploaded_exam.name}", expanded=False):
                col_preview1, col_preview2 = st.columns(2)
                with col_preview1:
                    st.caption(f"Dimensions : {df_exam.shape[0]} lignes × {df_exam.shape[1]} colonnes")
                with col_preview2:
                    st.caption(f"Colonnes : {', '.join(df_exam.columns[:5])}...")
                
                st.dataframe(df_exam.head(10), use_container_width=True, height=300)
        
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture de {uploaded_exam.name} : {e}")

# ============ CONFIGURATION DU TRAITEMENT ============
if df_pv is not None and exam_files_dict:
    st.markdown('<hr style="border-color: rgba(255,255,255,0.1); margin: 2rem 0;">', unsafe_allow_html=True)
    
    st.subheader(" Configuration des colonnes")
    
    # Sélectionner le fichier examen à traiter
    selected_exam_file = st.selectbox(
        "Fichier examen à traiter",
        list(exam_files_dict.keys()),
        help="Sélectionnez quel fichier examen traiter"
    )
    
    df_examen = exam_files_dict[selected_exam_file]
    
    # Section pour afficher les infos des fichiers
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.caption(f"📊 PV : {len(df_pv)} lignes, {len(df_pv.columns)} colonnes")
    with col_info2:
        st.caption(f"📋 {selected_exam_file} : {len(df_examen)} lignes, {len(df_examen.columns)} colonnes")
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        ine_pv_col = st.selectbox("Colonne INE (PV)", options=df_pv.columns)
    
    with c2:
        module_col = st.selectbox("Colonne Notes (PV)", options=df_pv.columns)
        
    with c3:
        ine_exam_col = st.selectbox("Colonne INE (Exam)", options=df_examen.columns)
        
    with c4:
        target_note_col = st.selectbox("Colonne Notes (Exam)", options=df_examen.columns)

    # Vérification préalable des INE
    if st.checkbox("🔍 Vérifier la correspondance des INE", value=True):
        ine_check = check_ine_matches(df_pv, df_examen, ine_pv_col, ine_exam_col)
        
        col_ine1, col_ine2, col_ine3 = st.columns(3)
        with col_ine1:
            st.metric("INE correspondances", f"{ine_check['matched']}/{ine_check['total_exam']}")
        with col_ine2:
            st.metric("% Correspondance", f"{ine_check['pct_match']:.1f}%")
        with col_ine3:
            st.metric("Sans notes dans PV", ine_check['missing_in_pv'])
        
        if ine_check['pct_match'] < 100:
            st.warning(f"⚠️ Attention : {ine_check['missing_in_pv']} étudiants n'ont pas de notes dans le PV")

    # Configuration pour les valeurs manquantes
    st.markdown("---")
    st.subheader(" Options avancées")
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    
    with col_opt1:
        missing_strategy = st.radio(
            "Traitement des étudiants sans note :",
            ["Remplacer par 0", "Laisser vide (NaN)", "Exclure les étudiants"],
            help="Définit comment gérer les étudiants qui n'ont pas de note dans le PV"
        )
        strategy_map = {
            "Remplacer par 0": "zero",
            "Laisser vide (NaN)": "nan",
            "Exclure les étudiants": "drop"
        }
        missing_value_strategy = strategy_map[missing_strategy]
    
    with col_opt2:
        normalize_notes_flag = st.checkbox("✨ Normaliser les notes", value=True, help="Convertir virgules en points, valider plages 0-20")
    
    with col_opt3:
        st.info("💡 **Conseil** : Vérifiez les correspondances INE")

    if st.button(" Lancer le Traitement", use_container_width=True):
        with st.spinner("Traitement en cours..."):
            try:
                # Validation des colonnes
                if not validate_columns(df_pv, [ine_pv_col, module_col]):
                    st.stop()
                
                if not validate_columns(df_examen, [ine_exam_col, target_note_col]):
                    st.stop()
                
                # Fusion des notes avec normalisation
                df_result, merge_stats = merge_grades(
                    df_pv, df_examen, 
                    ine_pv_col, module_col,
                    ine_exam_col, target_note_col,
                    missing_value_strategy,
                    normalize_notes=normalize_notes_flag
                )
                
                # Afficher les avertissements de normalisation
                if merge_stats["normalization_issues"]:
                    with st.expander("📝 Détails de la normalisation"):
                        for issue in merge_stats["normalization_issues"]:
                            st.warning(issue)
                
                st.markdown('<div class="success-box">✅ Traitement terminé avec succès !</div>', unsafe_allow_html=True)
                
                # Statistiques du résultat
                col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
                with col_stats1:
                    st.metric("Lignes traitées", len(df_result))
                with col_stats2:
                    notes_non_vides = df_result[target_note_col].notna().sum()
                    st.metric("Notes attribuées", notes_non_vides)
                with col_stats3:
                    notes_vides = df_result[target_note_col].isna().sum()
                    st.metric("Valeurs manquantes", notes_vides)
                with col_stats4:
                    try:
                        note_mean = pd.to_numeric(df_result[target_note_col], errors='coerce').mean()
                        st.metric("Moyenne notes", f"{note_mean:.2f}")
                    except:
                        st.metric("Moyenne notes", "N/A")
                
                # Préparation du téléchargement
                processed_data, download_filename, download_mime = prepare_download_file(df_result, selected_exam_file)
                
                # Génération du nom du fichier
                st.download_button(
                    label="⬇️ Télécharger le fichier mis à jour",
                    data=processed_data,
                    file_name=download_filename,
                    mime=download_mime,
                    use_container_width=True
                )
                
                # Aperçu
                st.subheader(" Aperçu du résultat")
                st.dataframe(df_result.head(20), use_container_width=True, height=450)
                
                # Afficher un résumé des changements
                with st.expander("📊 Rapport de fusion détaillé"):
                    col_rapport1, col_rapport2 = st.columns(2)
                    
                    with col_rapport1:
                        st.write("**Configuration appliquée :**")
                        st.write(f"- INE (PV) : `{ine_pv_col}`")
                        st.write(f"- Notes source : `{module_col}`")
                        st.write(f"- INE (Exam) : `{ine_exam_col}`")
                        st.write(f"- Notes cible : `{target_note_col}`")
                        st.write(f"- Stratégie manquantes : {missing_strategy}")
                        st.write(f"- Normalisation : {'Oui ✓' if normalize_notes_flag else 'Non'}")
                    
                    with col_rapport2:
                        st.write("**Résultats du traitement :**")
                        st.write(f"- Total lignes : {len(df_result)}")
                        st.write(f"- Notes attribuées : {notes_non_vides}")
                        st.write(f"- Valeurs manquantes : {notes_vides}")
                        try:
                            note_min = pd.to_numeric(df_result[target_note_col], errors='coerce').min()
                            note_max = pd.to_numeric(df_result[target_note_col], errors='coerce').max()
                            st.write(f"- Plage notes : {note_min:.1f} à {note_max:.1f}")
                        except:
                            st.write(f"- Plage notes : Non calculable")
                    
                    # Statistiques détaillées sur les notes
                    st.subheader("📈 Statistiques des notes")
                    try:
                        note_series = pd.to_numeric(df_result[target_note_col], errors='coerce')
                        note_stats = note_series.describe()
                        st.dataframe(note_stats)
                    except:
                        st.info("Impossible de calculer les statistiques (colonnes non numériques)")
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement : {e}")
                st.error(f"❌ Une erreur est survenue lors du traitement : {e}")
                st.error(f"Détails : {str(e)}")

else:
    st.info("ℹ️ Chargez le PV et au moins un fichier examen pour commencer.")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 5rem; color: #4b5563; font-size: 0.8rem; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">
    <p><strong>Gestionnaire de Notes v2.5 - Amélioré</strong></p>
    <p>✨ Normalisation de notes | 🔍 Validation complète | 📦 Multi-modules | 🐛 Bugs corrigés</p>
    <p>🔒 Vos données restent locales | 📊 Traitement sécurisé et vérifié</p>
    <p>DSI © 2026</p>
</div>
""", unsafe_allow_html=True)

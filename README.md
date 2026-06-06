# 🎓 Gestionnaire de Notes Étudiants v2.5

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

Application moderne pour **automatiser la fusion des notes d'examen** à partir des PV de délibération globaux.

---

## ✨ Nouvelles Fonctionnalités v2.5

### 🔧 Normalisation des Notes
- ✅ Conversion virgules → points (français/international)
- ✅ Suppression des caractères parasites
- ✅ Validation des plages (0-20)
- ✅ Rapport des anomalies détecté

### 📊 Validation Complète des Données
- ✅ Détection des lignes vides
- ✅ Détection des colonnes vides/incomplètes
- ✅ Repérage des doublons
- ✅ Analyse du taux de remplissage

### 👁️ Aperçu Immédiat
- ✅ Preview des fichiers après upload
- ✅ Dimensions et types de données
- ✅ Détection immédiate des problèmes

### 📦 Support Multi-Modules
- ✅ Upload multiple fichiers examen à la fois
- ✅ Traitement séquentiel des modules
- ✅ Sélecteur pour choisir le module

### 🔍 Vérification INE
- ✅ Correspondance INE entre PV et exam
- ✅ Statistiques de matching (%)
- ✅ Identification des étudiants sans notes

---

## 🛠️ Technologies

| Tech | Version | Usage |
|------|---------|-------|
| **Python** | 3.8+ | Langage principal |
| **Streamlit** | 1.28+ | Interface web |
| **Pandas** | 2.0+ | Manipulation données |
| **Openpyxl** | 3.10+ | Gestion Excel |
| **NumPy** | 1.24+ | Opérations numériques |

---

## 📥 Installation Locale

### Prérequis
- Python 3.8+
- Git
- pip

### Étapes

```bash
# 1. Cloner le repo
git clone https://github.com/Daoudasawa/ScriptsNotes.git
cd ScriptsNotes

# 2. Créer un environnement virtuel (optionnel mais recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'app
streamlit run app.py
```

L'app s'ouvrira à `http://localhost:8501`

---

## 🚀 Déploiement sur Streamlit Cloud

### Option 1 : Déploiement Automatique (Recommandé)

1. **Prérequis** : 
   - Compte Streamlit Cloud
   - Repo GitHub (déjà fait ✓)

2. **Accéder au Cloud** :
   - Allez sur [share.streamlit.io](https://share.streamlit.io)
   - Connectez-vous avec GitHub

3. **Déployer l'App** :
   - Cliquez **"New app"**
   - Sélectionnez :
     - Repository: `Daoudasawa/ScriptsNotes`
     - Branch: `master`
     - Main file: `app.py`
   - Cliquez **"Deploy"** 🎉

4. **Mise à Jour Automatique** :
   - Chaque `git push` déclenche un redéploiement automatique
   - Pas besoin de faire quoi que ce soit!

### Option 2 : Déploiement Manuel (si besoin)

```bash
# Depuis le dashboard Streamlit Cloud
# → Manage app → Reboot app
```

---

## 📖 Mode d'emploi

### Étape 1 : Charger les fichiers
```
┌─ Fichier PV ─────────────────┐  ┌─ Fichiers Examen ──────┐
│ Déposer le PV                │  │ Déposer 1+ fichiers     │
│ (xlsx, xls, csv)             │  │ (xlsx, xls, csv)        │
└──────────────────────────────┘  └─────────────────────────┘
```

### Étape 2 : Vérification Automatique
- ✅ Validation des données
- ✅ Aperçu des contenus
- ⚠️ Avertissements affichés

### Étape 3 : Configuration
```
Colonne INE (PV)      → Sélectionner
Colonne Notes (PV)    → Sélectionner
Colonne INE (Exam)    → Sélectionner
Colonne Notes (Exam)  → Sélectionner
```

### Étape 4 : Traitement
- Vérifier la correspondance INE (%)
- Choisir stratégie manquantes (0, NaN, ou exclure)
- ✓ Cocher "Normaliser les notes"
- Cliquer **"Lancer le Traitement"**

### Étape 5 : Résultats
- ✅ Statistiques complètes
- 📊 Rapport de fusion détaillé
- ⬇️ Télécharger le fichier Excel
- 👁️ Aperçu des 20 premières lignes

---

## ⚙️ Configuration

### Fichier `.streamlit/config.toml`
Personnalise le comportement de l'app :

```toml
[theme]
primaryColor = "#6366f1"          # Couleur principale (violet)
backgroundColor = "#0f172a"        # Fond sombre
textColor = "#ffffff"              # Texte blanc

[server]
maxUploadSize = 200                # Limite upload en MB
headless = true                    # Mode sans navigateur
```

### Secrets (si besoin)
Fichier `.streamlit/secrets.toml` (git-ignored) :

```toml
# À configurer dans Streamlit Cloud Dashboard
api_key = "xxx"
database_url = "xxx"
```

---

## 📋 Format des Fichiers

### Fichier PV
```
INE           | Module_Français | Module_Math | ...
111222333     | 15.5            | 18          |
444555666     | 12              | 14.5        |
```

### Fichier Examen
```
INE           | Nom       | Prenom  | Note_Module_Français | ...
111222333     | DUPONT    | Jean    | 0                    |
444555666     | MARTIN    | Marie   | 0                    |
777888999     | BERNARD   | Pierre  | 0                    |
```

**Le résultat** : `Note_Module_Français` est remplie depuis le PV via l'INE ✓

---

## 🐛 Résolution de Problèmes

### ❌ Erreur "Colonnes manquantes"
→ Vérifiez que les colonnes sélectionnées existent réellement dans vos fichiers

### ⚠️ Faible % Correspondance INE
→ Vérifiez :
- ✓ Format des INE identique
- ✓ Pas d'espaces parasites
- ✓ Même type de données (numérique vs texte)

### 📛 Valeurs NaN dans les résultats
→ L'étudiant n'existe que dans le fichier exam
- Choisir stratégie : Remplacer par 0, ou laisser vide

### 🔄 Normalisation échoue
→ Vérifiez que la colonne contient réellement des notes
- Pas de texte, de formules, ou d'autres types

---

## 📊 Logs & Débogage

Logs sauvegardés dans `.streamlit/`:

```bash
# Voir les logs locaux
tail -f ~/.streamlit/logs/streamlit.log

# Sur Streamlit Cloud → Manage app → Logs
```

---

## 🤝 Contribution

Pour contribuer :

```bash
# 1. Fork le repo
# 2. Créer une branche
git checkout -b feature/my-feature

# 3. Committer
git commit -m "feat: Ajouter ma feature"

# 4. Pousser
git push origin feature/my-feature

# 5. Créer une Pull Request
```

---

## 📝 Changelog

### v2.5 (2026-06-06)
- ✨ Normalisation des notes (virgule→point)
- ✨ Validation complète des données
- ✨ Aperçu immédiat des fichiers
- ✨ Support multi-modules (upload multiple)
- ✨ Vérification correspondance INE
- 🐛 Fix: Cache bug sur uploads
- 🐛 Fix: Normalisation des INE dans fusion
- 📈 Meilleure UX avec statistiques détaillées

### v2.0 (Précédent)
- Initial release avec fusion basique

---

## ⚖️ Licence

MIT © 2026 - DSI (Direction des Systèmes d'Information)

---

## 📞 Support

Pour les problèmes ou suggestions :
- 📧 Email: `support@example.com`
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Développé avec ❤️ par la DSI**

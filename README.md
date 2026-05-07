# Gestionnaire de Notes Étudiants 

Une application moderne pour automatiser la fusion des notes d'examen à partir des PV de délibération globaux.

## Technologies Utilisées
- **Python 3.14+** : Langage de programmation principal.
- **Streamlit** : Framework de création d'interfaces web pour la science des données.
- **Pandas** : Bibliothèque leader pour la manipulation de données (Jointures, tris, filtres).
- **Openpyxl** : Moteur de gestion des fichiers Microsoft Excel.

## Installation et Lancement
1. Ouvrez un terminal dans le dossier du projet.
2. Installez les dépendances :
   ```powershell
   pip install -r requirements.txt
   ```
3. Lancez l'application :
   ```powershell
   python -m streamlit run app.py
   ```

##  Fonctionnalités
- **Support Multi-formats** : Accepte les fichiers `.xlsx`, `.xls` et `.csv`.
- **Détection Automatique** : Identifie les séparateurs de CSV (virgule, point-virgule).
- **Fidélité des données** : 
    - Fusion précise via le numéro **INE**.
    - Gestion des absences : Si un étudiant est présent dans le fichier d'examen mais absent du PV, sa note est automatiquement fixée à **0**.
    - **Tri intelligent** : Le fichier final est systématiquement trié par INE pour faciliter le contrôle.
- **Export Sécurisé** : La sortie est toujours au format Excel (.xlsx) pour garantir une mise en forme parfaite.

##  Mode d'emploi
1. **Dépôt des fichiers** : Glissez le PV et le fichier d'examen dans leurs zones respectives.
2. **Choix des colonnes** : Sélectionnez les colonnes correspondantes via les menus déroulants qui s'affichent automatiquement.
3. **Traitement** : Cliquez sur le bouton de lancement.
4. **Récupération** : Téléchargez le résultat via le bouton dédié.

---
© 2026 - Direction des Systèmes d'Information (DSI)

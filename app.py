import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Organisation Événement", page_icon="🥂", layout="wide")

# --- GESTION DE LA MÉMOIRE (SAUVEGARDE AUTOMATIQUE) ---
FICHIER_DONNEES = "annonces.json"

def charger_donnees():
    if os.path.exists(FICHIER_DONNEES):
        with open(FICHIER_DONNEES, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"Personne": "Exemple : Mamie", "Jour": "Samedi Midi", "Commentaires": "Lui dire de vive voix en premier", "Fait": False}
    ]

def sauvegarder_donnees(donnees):
    with open(FICHIER_DONNEES, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=4)

# Initialisation
if "liste_annonces" not in st.session_state:
    st.session_state.liste_annonces = charger_donnees()

st.title("🥂 App big day")

# Création des deux onglets demandés aujourd'hui
onglet_annonces, onglet_evolution = st.tabs(["Liste des Annonces", "Évolution"])

# --- ONGLET 1 : LES ANNONCES ---
with onglet_annonces:
    st.header("Suivi des annonces ")
    
    # 1. Petit formulaire masqué pour ajouter une personne sans encombrer l'écran
    with st.expander("➕ Ajouter une nouvelle personne à la liste", expanded=False):
        with st.form("form_ajout"):
            nouvelle_personne = st.text_input("Nom de la personne / Groupe")
            jour_annonce = st.text_input("Jour")
            commentaires = st.text_area("Commentaires (Comment lui annoncer ?)")
            bouton_ajouter = st.form_submit_button("Ajouter à la liste")
            
            if bouton_ajouter and nouvelle_personne:
                nouvelle_ligne = {
                    "Personne": nouvelle_personne,
                    "Jour": jour_annonce,
                    "Commentaires": commentaires,
                    "Fait": False
                }
                st.session_state.liste_annonces.append(nouvelle_ligne)
                sauvegarder_donnees(st.session_state.liste_annonces)
                st.success(f"✅ {nouvelle_personne} a été ajouté(e) !")
                st.rerun()

    # 2. Le tableau interactif et modifiable
    if st.session_state.liste_annonces:
        df = pd.DataFrame(st.session_state.liste_annonces)
        
        st.write("💡 *Astuces : Cliquez sur le nom d'une colonne pour trier. Double-cliquez sur une case pour modifier le texte directement !*")
        
        # Ce composant magique permet de modifier les lignes en direct
        df_modifie = st.data_editor(
            df,
            column_config={
                "Fait": st.column_config.CheckboxColumn("Fait ?", default=False),
                "Personne": st.column_config.TextColumn("Qui ?", required=True),
                "Jour": st.column_config.TextColumn("Quand ?"),
                "Commentaires": st.column_config.TextColumn("Commentaires / Méthode"),
            },
            use_container_width=True,
            num_rows="dynamic" # Permet aussi de supprimer des lignes si besoin
        )
        
        # Sauvegarde automatique si un changement est détecté
        if not df.equals(df_modifie):
            st.session_state.liste_annonces = df_modifie.to_dict(orient="records")
            sauvegarder_donnees(st.session_state.liste_annonces)
            st.rerun()
    else:
        st.info("La liste est vide pour le moment.")

# --- ONGLET 2 : L'ÉVOLUTION ---
with onglet_evolution:
    st.header("Progression")
    if st.session_state.liste_annonces:
        total = len(st.session_state.liste_annonces)
        faits = sum(1 for x in st.session_state.liste_annonces if x.get("Fait") == True)
        pourcentage = int((faits / total) * 100) if total > 0 else 0
        
        # Bel affichage visuel
        st.metric(label="Annonces complétées", value=f"{faits} / {total}", delta=f"{pourcentage}% effectué")
        st.progress(pourcentage / 100)
    else:
        st.write("Ajoutez des personnes pour voir les statistiques d'évolution.")

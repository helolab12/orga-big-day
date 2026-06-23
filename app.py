import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Organisation Big Day", page_icon="🥂", layout="wide")

# ==============================================================================
# GESTION DES BASES DE DONNÉES (MÉMOIRE)
# ==============================================================================
FICHIER_ANNONCES = "annonces.json"
FICHIER_FRISE = "frise.json"
FICHIER_DISCUSSION = "discussion.json"

def charger_donnees(fichier, par_defaut):
    if os.path.exists(fichier):
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    return par_defaut

def sauvegarder_donnees(fichier, donnees):
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=4)

# Initialisation des mémoires
if "liste_annonces" not in st.session_state:
    st.session_state.liste_annonces = charger_donnees(FICHIER_ANNONCES, [])
if "liste_frise" not in st.session_state:
    # Événements par défaut pour démarrer la frise aux bonnes dates
    defaut_frise = [
        {"Événement": "Début des préparatifs ", "Date": "2026-06-14"},
        {"Événement": "🥂", "Date": "2028-08-30"}
    ]
    st.session_state.liste_frise = charger_donnees(FICHIER_FRISE, defaut_frise)
if "liste_discussion" not in st.session_state:
    defaut_comm = [
        {
            "Auteur": "Hélo", 
            "Message": "Bienvenue sur l'espace discussion ! @Raph j'espère que tu vas bien.", 
            "Tag": "Raph", 
            "Type": "Urgent",
            "Date": "23 Juin 2026"
        }
    ]
    st.session_state.liste_discussion = charger_donnees(FICHIER_DISCUSSION, defaut_comm)

st.title("🥂 Organisation Big Day")

# ==============================================================================
# LES GRANDS ONGLETS PRINCIPAUX
# ==============================================================================
grand_onglet_global, grand_onglet_annonces, grand_onglet_discussion= st.tabs([
    "Organisation Globale", 
    "Annonces",
    "Discussion"
])

# ==============================================================================
# 1. GRAND ONGLET : ORGANISATION GLOBALE & FRISE
# ==============================================================================
with grand_onglet_global:
    st.header("⏳ Apperçu Chronologique")
    st.write("💡 *Utilisez les options en haut à droite pour naviguer sur la frise*")
    
    # Affichage de la frise
    if st.session_state.liste_frise:
        df_frise = pd.DataFrame(st.session_state.liste_frise)
        df_frise["Date"] = pd.to_datetime(df_frise["Date"])
        
        # Répartition verticale pour éviter la superposition des textes
        df_frise["Position_Verticale"] = [i % 4 for i in range(len(df_frise))]
        
        # Création du graphique Plotly avec une largeur immense de 3000px
        fig = px.scatter(
            df_frise, 
            x="Date", 
            y="Position_Verticale", 
            text="Événement",
            range_x=["2026-05-01", "2028-09-30"],
            width=3000, 
            height=380
        )
        
        fig.update_traces(
            marker=dict(size=14, color="#3182ce", symbol="diamond"),
            textposition="top center",
            hovertemplate="<b>%{text}</b><br>Date : %{x|%d %B %Y}<extra></extra>"
        )
        
        fig.update_layout(
            plot_bgcolor="rgba(235, 248, 255, 0.4)", # Fond bleu dragée pastel
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(visible=False, range=[-1, 4]), # Masque l'axe vertical
            xaxis=dict(
                title="", 
                type="date",
                showgrid=True,          # Active les lignes de séparation verticales
                gridcolor="#cbd5e0",    # Couleur gris bien visible pour séparer les mois/jours
                gridwidth=1.5,          # Épaisseur des lignes de séparation
                showspikes=True,        # Active la ligne guide au survol du point
                spikecolor="#3182ce",
                spikethickness=1,
                tickangle=0
            ),
            margin=dict(l=50, r=50, t=10, b=10)
        )
        
        # ACTION : On force Streamlit à créer une zone de défilement horizontal unique pour la frise
        with st.container(border=True):
            st.markdown(
                '<div style="overflow-x: auto; overflow-y: hidden; width: 100%;">', 
                unsafe_allow_html=True
            )
            # Une seule et unique frise affichée ici
            st.plotly_chart(fig, use_container_width=False, key="frise_mariage_unique")
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Formulaire d'ajout pour la frise
    # Formulaire d'ajout pour la frise
    with st.expander("➕ Ajouter un élément à la frise", expanded=False):
        with st.form("form_frise"):
            nom_evenement = st.text_input("Nom de l'événement (ex: Réception de la Robe)")
            date_evenement = st.date_input("Sélectionnez la date exacte", value=datetime(2026, 6, 14))
            bouton_frise = st.form_submit_button("Ajouter à la frise")
            
            if bouton_frise and nom_evenement:
                nouvel_ev = {
                    "Événement": nom_evenement,
                    "Date": str(date_evenement)
                }
                st.session_state.liste_frise.append(nouvel_ev)
                sauvegarder_donnees(FICHIER_FRISE, st.session_state.liste_frise)
                st.success(f"✅ '{nom_evenement}' ajouté au calendrier !")
                st.rerun()

# Formulaire de suppression pour la frise
    with st.expander("🗑️ Supprimer un élément de la frise", expanded=False):
        if len(st.session_state.liste_frise) > 0:
            # On crée une liste des noms d'événements pour la sélection
            evenements_dispo = [ev["Événement"] for ev in st.session_state.liste_frise]
            evenement_a_supprimer = st.selectbox("Sélectionnez l'élément à retirer :", evenements_dispo)
            bouton_supprimer = st.button("Supprimer définitivement")
            
            if bouton_supprimer:
                # On filtre la liste pour enlever l'élément sélectionné
                st.session_state.liste_frise = [ev for ev in st.session_state.liste_frise if ev["Événement"] != evenement_a_supprimer]
                sauvegarder_donnees(FICHIER_FRISE, st.session_state.liste_frise)
                st.success(f"❌ '{evenement_a_supprimer}' a été supprimé.")
                st.rerun()
        else:
            st.write("Il n'y a aucun élément à supprimer.")

    # Résumé des progressions en dessous
    st.subheader("📈 Résumé de nos progressions")
    if st.session_state.liste_annonces:
        total = len(st.session_state.liste_annonces)
        faits = sum(1 for x in st.session_state.liste_annonces if x.get("Fait") == True)
        pourcentage = int((faits / total) * 100) if total > 0 else 0
        st.write(f"**Avancement des Annonces :** {faits} sur {total} faites ({pourcentage}%)")
        st.progress(pourcentage / 100)
    else:
        st.info("Aucune statistique d'avancement disponible pour le moment.")

# ==============================================================================
# 2. GRAND ONGLET : GESTION DES ANNONCES
# ==============================================================================
with grand_onglet_annonces:
    sous_onglet_liste, sous_onglet_statistiques = st.tabs(["📋 La Liste modifiable", "📈 Statistiques de cet onglet"])
    
    with sous_onglet_liste:
        st.subheader("Qui devons-nous prévenir ?")
        with st.expander("➕ Ajouter une nouvelle personne à la liste", expanded=False):
            with st.form("form_ajout"):
                nouvelle_personne = st.text_input("Nom de la personne / Groupe")
                jour_annonce = st.text_input("Jour prévu pour l'annonce")
                commentaires = st.text_area("Commentaires")
                bouton_ajouter = st.form_submit_button("Ajouter")
                
                if bouton_ajouter and nouvelle_personne:
                    st.session_state.liste_annonces.append({
                        "Personne": nouvelle_personne, "Jour": jour_annonce, "Commentaires": commentaires, "Fait": False
                    })
                    sauvegarder_donnees(FICHIER_ANNONCES, st.session_state.liste_annonces)
                    st.rerun()

        if st.session_state.liste_annonces:
            df = pd.DataFrame(st.session_state.liste_annonces)
            df_modifie = st.data_editor(
                df,
                column_config={
                    "Fait": st.column_config.CheckboxColumn("Fait ?", default=False),
                    "Personne": st.column_config.TextColumn("Qui ?", required=True),
                    "Jour": st.column_config.TextColumn("Quand ?"),
                    "Commentaires": st.column_config.TextColumn("Commentaires"),
                },
                use_container_width=True,
                num_rows="dynamic"
            )
            if not df.equals(df_modifie):
                st.session_state.liste_annonces = df_modifie.to_dict(orient="records")
                sauvegarder_donnees(FICHIER_ANNONCES, st.session_state.liste_annonces)
                st.rerun()

    with sous_onglet_statistiques:
        if st.session_state.liste_annonces:
            total = len(st.session_state.liste_annonces)
            faits = sum(1 for x in st.session_state.liste_annonces if x.get("Fait") == True)
            st.metric(label="Annonces complétées", value=f"{faits} / {total}")
# ==============================================================================
# 3. GRAND ONGLET : ESPACE DISCUSSION
# ==============================================================================
with grand_onglet_discussion:
    st.subheader("💬 Discussion pour les préparatifs")
    st.write("Partagez vos idées, posez vos questions et taguez les bonnes personnes !")
    
    # 1. Formulaire pour publier
    with st.form("form_commentaires"):
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # LE NOUVEAU SYSTÈME DROPDOWN + TEXTE LIBRE
            choix_prenom = st.selectbox(
                "Votre Prénom / Rôle", 
                ["Raph", "Hélo", "Hedwige", "Guillemette", "Matthieu", "Louis", "➕ Autre..."]
            )
            if choix_prenom == "➕ Autre...":
                auteur = st.text_input("Tapez votre prénom / rôle :", placeholder="Ex: Julie (Témoin)")
            else:
                auteur = choix_prenom

        with col2:
            # Système de Tag
            qui_taguer = st.selectbox("Taguer quelqu'un :", ["Tout le monde", "Hélo", "Raph", "Parents Hélo", "Parents Raph"])
            
        with col3:
            # Le Type de message
            type_msg = st.selectbox("Type de message :", ["💬 Discussion", "💡 Idée / Inspiration", "❓ Question", "🚨 Urgent"])
            
        message = st.text_area("Votre message :", placeholder="Écrivez votre texte ici...")
        bouton_publier = st.form_submit_button("🚀 Publier sur le fil")
        
        if bouton_publier and auteur and message:
            import datetime
            nouveau_comm = {
                "Auteur": auteur,
                "Message": message,
                "Tag": qui_taguer,
                "Type": type_msg,
                "Date": datetime.datetime.now().strftime("%d %B %Y à %H:%M")
            }
            # On l'ajoute au DÉBUT de la liste pour que le plus récent soit en haut !
            st.session_state.liste_discussion.insert(0, nouveau_comm)
            sauvegarder_donnees(FICHIER_DISCUSSION, st.session_state.liste_discussion)
            st.success("Message publié !")
            st.rerun()

    st.divider()

    # 2. Affichage du fil de discussion
    for c in st.session_state.liste_discussion:
        # On crée une jolie boîte avec une bordure pour chaque message
        with st.container(border=True):
            # Ligne du haut : Auteur, Date et le Badge du Type
            col_inf1, col_inf2 = st.columns([3, 1])
            with col_inf1:
                st.markdown(f"👤 **{c['Auteur']}** — *le {c['Date']}*")
            with col_inf2:
                st.write(f"**{c['Type']}**")
            
            # Le message
            st.write(c['Message'])
            
            # Le Tag affiché de manière élégante s'il cible quelqu'un
            if c['Tag'] != "Tout le monde":
                st.markdown(f"📌 *Notification envoyée aux : **@{c['Tag']}***")

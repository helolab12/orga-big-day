import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Organisation Big Day", page_icon="🥂", layout="wide")
# ==============================================================================
# FOND D'ÉCRAN PHOTO
# ==============================================================================
import base64

def ajouter_fond_ecran(fichier_image):
    try:
        with open(fichier_image, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        # Le CSS est injecté ici
        st.markdown(
            f"""
            <style>
            /* 1. Configuration du fond d'écran (Voile léger, image peu opaque) */
            .stApp {{
                background-image: linear-gradient(rgba(255, 255, 255, 0.45), rgba(255, 255, 255, 0.45)), 
                                  url("data:image/jpg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}

            /* 2. Titres généraux en Rose Fushia ou Blanc pour contraster */
            h1, h2, h3 {{
                color: #0f0f0f !important; /* Rose Fushia éclatant pour les grands titres */
                
            }}
            
            .stMarkdown, .stText, p, label, .stWidgetLabel {{
                color: #000000 !important; /* Textes par défaut en noir pour le contraste */
            }}

            /* 3. Style des onglets (tabs) */
            .stTabs [data-baseweb="tab"] {{
                background-color: rgba(255, 219, 28, 0.67) !important;
                border-radius: 8px 8px 0 0 !important;
                color: #FFD700 !important; 
                padding: 10px 20px !important;
            }}
            .stTabs [data-baseweb="tab"][aria-selected="true"] {{
                background-color: #e2583ed1 !important; /* Orange-rosé sur l'onglet actif */
                color: #FFFFFF !important;
            }}
            .stTabs [data-baseweb="tab-list"] {{
                background-color: transparent !important;
            }}

            /* 4. DESIGN DES BOÎTES OPAQUES (Orange légèrement rosé) */
            div.stDataEditor, div.stForm, div.stExpander, div.stContainer, .plotly-graph-div, .stPlotlyChart {{
                background-color: #ea6d40 !important; /* Orange corail/rosé 100% opaque */
                border: none !important;
                border-radius: 12px !important;
                padding: 6px !important;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.7) !important;
            }}

            /* Forcer les textes à l'intérieur de cette boîte rose à être très lisibles (Blanc ou Noir selon préférence) */
            div[data-element-to-rasterize="boite_resume_progression"] p,
            div[data-element-to-rasterize="boite_resume_progression"] h3,
            div[data-element-to-rasterize="boite_resume_progression"] span {{
                color: #FFFFFF !important; /* Texte blanc pour un contraste magnifique sur le rose */
                text-shadow: 1px 1px 2px rgba(0,0,0,0.4);
            }}

            /* 5. Textes à l'intérieur des tableaux et entrées de saisie */
            div.stDataEditor [data-baseweb="table"] td, 
            div.stDataEditor [data-baseweb="table"] th {{
                color: #000000 !important; /* Texte noir dans les cellules pour lisibilité */
                background-color: #FFFFFF !important;
            }}
            /* Inputs / Zones de texte */
            .stTextInput input, .stTextArea textarea {{
                background-color: #FFFFFF !important;
                color: #000000 !important;
            }}

            /* 6. BOÎTE DE DISCUSSION */
            div[data-element-to-rasterize="cadre_discussion"] {{
                background-color: #FFA500 !important; /* Jaune orangé complet */
                border-radius: 15px !important;
                padding: 20px !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
                opacity: 1 !important;
                height: auto !important;
            }}

            /* 7. BOITES INDIVIDUELLESDE COMMENTAIRES */
            div[class*="st-emotion-cache-1ne20ew"], 
            .st-emotion-cache-1ne20ew {{
                background-color: #ea6d40 !important; /* Force le fond blanc opaque */
                opacity: 1 !important;                 /* Bloque toute transparence */
                box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            }}
            /* Forcer le texte en noir à l'intérieur de ces commentaires */
            div[class*="st-emotion-cache-1ne20ew"] p,
            div[class*="st-emotion-cache-1ne20ew"] span,
            div[class*="st-emotion-cache-1ne20ew"] strong,
            .st-emotion-cache-1ne20ew p,
            .st-emotion-cache-1ne20ew span,
            .st-emotion-cache-1ne20ew strong {{
                color: #000000 !important;
            }}

            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        pass

# On active le fond avec image locale
ajouter_fond_ecran("fontaine.jpg")

# ==============================================================================
# GESTION DES BASES DE DONNÉES (MÉMOIRE)
# ==============================================================================
FICHIER_ANNONCES = "annonces.json"
FICHIER_FRISE = "frise.json"
FICHIER_DISCUSSION = "discussion.json"
FICHIER_RELIGIEUX_TODO = "religieux_todo.json"
FICHIER_RELIGIEUX_IDEES = "religieux_idees.json"

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
if "religieux_todo" not in st.session_state:
    st.session_state.religieux_todo = charger_donnees(FICHIER_RELIGIEUX_TODO, {
        "Prépa Mariage": [], "Fiançailles": [], "Mariage religieux": [], "Statistiques de progression": []
    })

if "religieux_idees" not in st.session_state:
    st.session_state.religieux_idees = charger_donnees(FICHIER_RELIGIEUX_IDEES, {
        "Prépa Mariage": [], "Fiançailles": [], "Mariage religieux": [], "Statistiques de progression": []
    })

st.title("🥂 Organisation Big Day")

# ==============================================================================
# LES GRANDS ONGLETS PRINCIPAUX
# ==============================================================================
grand_onglet_global, grand_onglet_annonces, grand_onglet_religieux, grand_onglet_discussion= st.tabs([
    "Organisation Globale", 
    "Annonces",
    "Préparation & Célébration Religieuse",
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
            marker=dict(size=14, color="#243ed0", symbol="diamond"),
            textposition="top center",
            hovertemplate="<b>%{text}</b><br>Date : %{x|%d %B %Y}<extra></extra>"
        )
        
        fig.update_layout(
            height=400,               # <-- Fixe la hauteur en pixels pour éviter que ça dépasse en bas
            autosize=True,            # <-- Force la frise à s'adapter automatiquement en largeur au cadre orange
            plot_bgcolor="#F1DFEE",   # <-- Fond bleu dragée pastel
            paper_bgcolor="#F1DFEE",  # <-- Fond externe également bleu dragée pastel
            font=dict(color="#0d1117"), # <-- Rend les textes/dates bien visibles en sombre
            yaxis=dict(visible=False, range=[-1, 4]), # Masque l'axe vertical
            xaxis=dict(
                title="", 
                type="date",
                showgrid=True,          # Active les lignes de séparation verticales
                gridcolor="rgba(255, 255, 255, 0.15)", # <-- Couleur gris/blanc subtile sur fond noir
                gridwidth=1.5,          # Épaisseur des lignes de séparation
                showspikes=True,        # Active la ligne guide au survol du point
                spikecolor="#deff9a",   # <-- Une couleur de guide qui ressort bien sur le sombre
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
    with st.expander("➕ Ajouter un élément à la frise", expanded=False):
        with st.form("form_frise"):
            nom_evenement = st.text_input("Nom de l'événement (ex: Début organisation messe)")
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
    with st.container(border=True):
        st.markdown("### Résumé de nos progressions")
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
        st.subheader("A prévenir")
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
# 3. GRAND ONGLET : PRÉPARATION & CÉLÉBRATION RELIGIEUSE
# ==============================================================================
with grand_onglet_religieux: 
    st.title("Préparation & Célébration Religieuse")
    
    sous_onglets = st.tabs(["Prépa Mariage", "Fiançailles", "Mariage religieux", "Statistiques de progression"])
    noms_sous_onglets = ["Prépa Mariage", "Fiançailles", "Mariage religieux", "Statistiques de progression"]

    for i, sous_onglet in enumerate(sous_onglets):
        nom_categorie = noms_sous_onglets[i]
        
        with sous_onglet:
            # === CAS DES 3 PREMIERS ONGLETS : TO-DO & IDÉES ===
            if nom_categorie != "Statistiques de progression":
                st.subheader(f"Espace {nom_categorie}")
                col_todo, col_idees = st.columns([1, 1.2])
                
                # PARTIE GAUCHE : TO-DO LIST
                with col_todo:
                    st.markdown("### To-Do List")
                    with st.form(key=f"form_todo_{nom_categorie}"):
                        nouvelle_tache = st.text_input("Ajouter une tâche :", placeholder="Ex: Prendre RDV avec le prêtre...", key=f"in_{nom_categorie}")
                        bouton_todo = st.form_submit_button("➕ Ajouter")
                        
                        if bouton_todo and nouvelle_tache:
                            st.session_state.religieux_todo[nom_categorie].append({"texte": nouvelle_tache, "fait": False})
                            sauvegarder_donnees(FICHIER_RELIGIEUX_TODO, st.session_state.religieux_todo)
                            st.rerun()
                    
                    # Affichage des tâches existantes avec option de suppression
                    st.write("")
                    if not st.session_state.religieux_todo[nom_categorie]:
                        st.info("Aucune tâche pour le moment. C'est le moment d'être serein !")
                    else:
                        with st.container(border=True):
                            st.markdown("<p style='color: #FFFFFF !important; font-weight: bold; margin-bottom: 10px;'> Tâches à réaliser :</p>", unsafe_allow_html=True)
                            for idx, tache in enumerate(st.session_state.religieux_todo[nom_categorie]):
                                # Création de deux colonnes : une grande pour la tâche, une petite pour le bouton supprimer
                                col_check, col_del = st.columns([6, 1])
                        
                                with col_check:
                                    # Case à cocher pour le statut (fait / pas fait)
                                    statut = st.checkbox(tache["texte"], value=tache["fait"], key=f"check_{nom_categorie}_{idx}")
                                    if statut != tache["fait"]:
                                        st.session_state.religieux_todo[nom_categorie][idx]["fait"] = statut
                                        sauvegarder_donnees(FICHIER_RELIGIEUX_TODO, st.session_state.religieux_todo)
                                        st.rerun()
                        
                                with col_del:
                                    # Bouton de suppression discret en bout de ligne
                                    if st.button("🗑️", key=f"del_todo_{nom_categorie}_{idx}", help="Supprimer cette tâche"):
                                        # 1. On retire la tâche de la liste
                                        st.session_state.religieux_todo[nom_categorie].pop(idx)
                                        # 2. On sauvegarde dans le fichier JSON
                                        sauvegarder_donnees(FICHIER_RELIGIEUX_TODO, st.session_state.religieux_todo)
                                        # 3. On recharge la page pour mettre à jour l'affichage et les statistiques
                                        st.rerun()

                # PARTIE DROITE : BOÎTE À IDÉES
                with col_idees:
                    st.markdown("### 💡Idées (Texte & Photos)")
                    with st.form(key=f"form_idee_{nom_categorie}"):
                        auteur_idee = st.text_input("Qui dépose l'idée ?", placeholder="Ex: Hélo, Raph...", key=f"aut_{nom_categorie}")
                        texte_idee = st.text_area("Votre idée :", placeholder="Écrivez votre idée ici...", key=f"txt_{nom_categorie}")
                        photo_idee = st.file_uploader("Ajouter une image :", type=["png", "jpg", "jpeg"], key=f"photo_{nom_categorie}")
                        bouton_idee = st.form_submit_button("🚀 Partager l'idée")
                        
                        if bouton_idee and auteur_idee and texte_idee:
                            photo_bytes = None
                            if photo_idee is not None:
                                photo_bytes = base64.b64encode(photo_idee.read()).decode()
                            
                            import datetime
                            nouvel_item_idee = {
                                "Auteur": auteur_idee,
                                "Texte": texte_idee,
                                "Photo": photo_bytes,
                                "Date": datetime.datetime.now().strftime("%d/%m à %H:%M")
                            }
                            st.session_state.religieux_idees[nom_categorie].insert(0, nouvel_item_idee)
                            sauvegarder_donnees(FICHIER_RELIGIEUX_IDEES, st.session_state.religieux_idees)
                            st.success("Idée ajoutée !")
                            st.rerun()

                    st.write("")
                    if not st.session_state.religieux_idees[nom_categorie]:
                        st.info("Aucune idée partagée pour l'instant.")
                    else:
                        # On utilise 'enumerate' pour obtenir l'index (idx) de chaque idée
                        for idx, idee in enumerate(st.session_state.religieux_idees[nom_categorie]):
                        # On crée un container pour chaque idée déposée
                            with st.container(border=True):
                                st.markdown(f"💡 **Idée de {idee['Auteur']}** — *le {idee['Date']}*")
                                st.write(idee["Texte"])
                            
                                if idee["Photo"]:
                                    st.image(f"data:image/jpg;base64,{idee['Photo']}", use_container_width=True)
                            
                                # --- BOUTON DE SUPPRESSION ---
                                # On crée deux petites colonnes pour pousser le bouton à droite
                                col_espace, col_suppr = st.columns([4, 1])
                                with col_suppr:
                                    # Clé unique obligatoire par bouton basée sur la catégorie et l'index
                                    if st.button("🗑️", key=f"suppr_{nom_categorie}_{idx}"):
                                        # 1. On retire l'idée de la liste Python
                                        st.session_state.religieux_idees[nom_categorie].pop(idx)
                                        # 2. On sauvegarde la liste mise à jour dans le fichier JSON
                                        sauvegarder_donnees(FICHIER_RELIGIEUX_IDEES, st.session_state.religieux_idees)
                                        # 3. On recharge la page pour appliquer la suppression visuellement
                                        st.rerun()

            # === CAS DU 4ÈME ONGLET : STATISTIQUES DE PROGRESSION ===
            else:
                st.subheader("Progression")
                
                # 1. Calcul des scores
                total_taches = 0
                taches_faites = 0
                details = {}
                
                for cat in ["Prépa Mariage", "Fiançailles", "Mariage religieux"]:
                    taches_cat = st.session_state.religieux_todo.get(cat, [])
                    tot = len(taches_cat)
                    fait = sum(1 for t in taches_cat if t["fait"])
                    
                    total_taches += tot
                    taches_faites += fait
                    details[cat] = {"total": tot, "fait": fait, "pct": (fait / tot * 100) if tot > 0 else 0}
                
                # Progression Globale
                pct_global = (taches_faites / total_taches * 100) if total_taches > 0 else 0
                
                # 2. Affichage des compteurs visuels (Héritent du style orange de l'app)
                with st.container(border=True):
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric(label="Tâches Complétées", value=f"✅ {taches_faites}")
                    with col_m2:
                        st.metric(label="Tâches Restantes", value=f"⏳ {total_taches - taches_faites}")
                    with col_m3:
                        st.metric(label="Taux d'avancement global", value=f"🎯 {int(pct_global)}%")
                    
                    st.write("")
                    st.markdown("**Progression Générale :**")
                    st.progress(pct_global / 100)
                
                st.write("")
                st.markdown("### Détails par catégorie")
                
                # Affichage des barres par sous-onglet
                for cat, data in details.items():
                    with st.container(border=True):
                        col_txt, col_bar = st.columns([1, 2])
                        with col_txt:
                            st.markdown(f"**{cat}**")
                            st.caption(f"{data['fait']} fait(s) sur {data['total']} tâches")
                        with col_bar:
                            st.write("") # Calage
                            st.progress(data['pct'] / 100)

# ==============================================================================
# 4. GRAND ONGLET : ESPACE DISCUSSION
# ==============================================================================
with grand_onglet_discussion:
    st.subheader("Discussion ")
    
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
            type_msg = st.selectbox("Type de message :", ["💬 Discussion", "💡 Idée / Inspiration", "❓ Question", "🚨 Urgent", "🛠️ Correction du Site"])
            
        message = st.text_area("Votre message :", placeholder="Écrivez votre texte ici...")
        # AJOUT : Uploader de fichier (Accepte les images, PDF, Word, Excel)
        fichier_importe = st.file_uploader("Ajouter une photo ou un document (optionnel) :", type=["png", "jpg", "jpeg", "pdf", "docx", "xlsx"])
        
        bouton_envoi = st.form_submit_button("🚀 Publier")
        
        if bouton_envoi and auteur and (message or fichier_importe):
            import datetime
            import base64
            
            # Gestion du fichier joint s'il existe
            pieces_jointes = None
            if fichier_importe is not None:
                # Lecture et encodage du fichier en Base64
                fichier_bytes = base64.b64encode(fichier_importe.read()).decode()
                pieces_jointes = {
                    "nom": fichier_importe.name,
                    "type": fichier_importe.type,
                    "data": fichier_bytes
                }
            
            nouveau_commentaire = {
                "Auteur": auteur,
                "Tag": qui_taguer,
                "Type": type_msg,
                "Message": message,
                "Date": datetime.datetime.now().strftime("%d/%m à %H:%M"),
                "Fichier": pieces_jointes  # Nouvelle donnée stockée
            }
            
            # Insertion au début de la liste (le plus récent en haut)
            st.session_state.liste_discussion.insert(0, nouveau_commentaire)
            sauvegarder_donnees(FICHIER_DISCUSSION, st.session_state.liste_discussion)
            st.success("Message envoyé !")
            st.rerun()
        
    st.divider()

    # 2. Filtre de discussion
    col_titre_filtre, col_btn_reset = st.columns([4, 1])
    
    with col_titre_filtre:
        st.markdown("### Filtrer la discussion")
        
    with col_btn_reset:
        st.write("") # Petit calage visuel pour aligner le bouton
        # Bouton discret pour tout réinitialiser
        if st.button(" Réinitialiser", key="reset_discussion_filters", help="Effacer tous les filtres"):
            st.session_state.f_auteur = "Tous"
            st.session_state.f_tag = "Tous"
            st.session_state.f_type = "Tous"
            st.rerun()
    col_f1, col_f2, col_f3 = st.columns(3)

    # Récupération dynamique des listes d'auteurs, tags et types présents pour ne pas les écrire en dur
    auteurs_dispos = ["Tous"] + sorted(list(set(c["Auteur"] for c in st.session_state.liste_discussion)))
    tags_dispos = ["Tous"] + sorted(list(set(c["Tag"] for c in st.session_state.liste_discussion)))
    types_dispos = ["Tous"] + sorted(list(set(c["Type"] for c in st.session_state.liste_discussion)))

    with col_f1:
        filtre_auteur = st.selectbox("Par auteur :", auteurs_dispos, key="f_auteur")
    with col_f2:
        filtre_tag = st.selectbox("Par personne taguée :", tags_dispos, key="f_tag")
    with col_f3:
        filtre_type = st.selectbox("Par type de message :", types_dispos, key="f_type")

    # Application des filtres sur une copie de la liste
    discussion_filtree = st.session_state.liste_discussion

    if filtre_auteur != "Tous":
        discussion_filtree = [c for c in discussion_filtree if c["Auteur"] == filtre_auteur]
    
    if filtre_tag != "Tous":
        discussion_filtree = [c for c in discussion_filtree if c["Tag"] == filtre_tag]
        
    if filtre_type != "Tous":
        discussion_filtree = [c for c in discussion_filtree if c["Type"] == filtre_type]

    st.write("") # Petit espace visuel

    # Affichage du fil de discussion
    with st.container(key="cadre_discussion_filtree"):
        if not discussion_filtree:
            st.info("Aucun commentaire ne correspond à vos filtres de recherche.")
        else:
            for idx_filtre, c in enumerate(discussion_filtree):
                with st.container(border=True):
                    col_inf1, col_inf2 = st.columns([3, 1])
                    with col_inf1:
                        st.markdown(f"👤 **{c['Auteur']}** — *le {c['Date']}*")
                    with col_inf2:
                        st.write(f"**{c['Type']}**")
                    
                    if c['Message']:
                        st.write(c['Message'])
                    
                    # --- NOUVEAU : AFFICHAGE DES PIÈCES JOINTES ---
                    if c.get("Fichier") and c["Fichier"] is not None:
                        f_info = c["Fichier"]
                        # Décodage pour utilisation en direct
                        f_data = base64.b64decode(f_info["data"])
                        
                        # CAS 1 : C'est une image -> On l'affiche directement sur l'écran
                        if "image" in f_info["type"]:
                            st.image(f_data, caption=f_info["nom"], use_container_width=True)
                        
                        # CAS 2 : C'est un document (PDF, Excel...) -> On met un bouton de téléchargement
                        else:
                            st.download_button(
                                label=f"📂 Télécharger {f_info['nom']}",
                                data=f_data,
                                file_name=f_info["nom"],
                                mime=f_info["type"],
                                key=f"down_{idx_filtre}_{f_info['nom']}"
                            )
                    
                    if c['Tag'] != "Tout le monde":
                        st.markdown(f"📌 *Message destiné en particulier à **@{c['Tag']}***")
                    
                    # --- BOUTON DE SUPPRESSION ---
                    col_espace, col_suppr = st.columns([5, 1])
                    with col_suppr:
                        if st.button("🗑️ Supprimer", key=f"suppr_disc_{c['Auteur']}_{idx_filtre}"):
                            if c in st.session_state.liste_discussion:
                                st.session_state.liste_discussion.remove(c)
                                sauvegarder_donnees(FICHIER_DISCUSSION, st.session_state.liste_discussion)
                                st.success("Commentaire supprimé !")
                                st.rerun()

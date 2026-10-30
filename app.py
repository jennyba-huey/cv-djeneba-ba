import base64
import json
from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

DOSSIER = Path(__file__).parent
PHOTO = DOSSIER / "assets" / "photo.jpg"
PDF = DOSSIER / "assets" / "CV_Djeneba_Ba.pdf"

st.set_page_config(page_title="Djeneba Ba · CV", page_icon="✨", layout="wide")


FICHIER_CV = DOSSIER / "data" / "cv.json"
NIVEAUX = {1: "Notions", 2: "Bases", 3: "Intermédiaire", 4: "Avancé", 5: "Expert"}


@st.cache_data
def charger_cv(date_modif):
    # date_modif change à chaque enregistrement du JSON : le cache se recharge tout seul
    with open(FICHIER_CV, encoding="utf-8") as f:
        return json.load(f)


def html(code):
    st.markdown(code, unsafe_allow_html=True)


def titre_section(eyebrow, titre, sous_titre=""):
    sous = f'<p class="section-sub">{escape(sous_titre)}</p>' if sous_titre else ""
    html(f'<div class="section-head"><span class="eyebrow">{escape(eyebrow)}</span>'
         f'<h2>{escape(titre)}</h2>{sous}</div>')


def carte_timeline(dates, titre, organisation, description="", tags=()):
    desc = f'<p class="tl-desc">{escape(description)}</p>' if description else ""
    pills = "".join(f'<span class="pill">{escape(t)}</span>' for t in tags)
    pills = f'<div class="tag-wrap">{pills}</div>' if pills else ""
    html(f'<div class="card"><div class="tl-date">{escape(dates)}</div>'
         f'<div class="tl-role">{escape(titre)}</div>'
         f'<div class="tl-org">{escape(organisation)}</div>{desc}{pills}</div>')


COULEURS = {"Formation": "#2F8F6B", "Expérience": "#C8763A"}

FRISE_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
body{margin:0;background:transparent;}
.frise{position:relative;height:620px;margin:6px 8px 0 92px;font-family:Inter,sans-serif;color:#2B2F3A;}
.yr{position:absolute;top:0;bottom:22px;border-left:1px solid #F3EEE8;}
.yr span{position:absolute;bottom:-22px;transform:translateX(-50%);font-family:'IBM Plex Mono',monospace;font-size:12px;color:#9198A4;}
.par{position:absolute;top:232px;height:118px;background:rgba(243,225,205,.75);border-radius:8px;}
.par span{position:absolute;width:100%;text-align:center;top:50px;font-size:11px;color:#8A5A2B;}
.bar{position:absolute;height:16px;border-radius:8px;}
.bar.f{top:246px;}.bar.e{top:320px;}
.prev{background:repeating-linear-gradient(135deg,color-mix(in srgb,var(--c) 30%,transparent) 0 2px,transparent 2px 7px);
 border:1.5px solid var(--c);box-sizing:border-box;}
.lane{position:absolute;left:-92px;font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:500;}
.mini{position:absolute;top:320px;margin-left:6px;font-size:11px;color:#5B6472;line-height:16px;}
.pin{position:absolute;width:0;}
.pin i{position:absolute;transform:translate(-50%,-50%);width:26px;height:26px;border-radius:50%;background:var(--c);
 border:3px solid #fff;box-shadow:0 0 0 1px var(--c);color:#fff;font:500 10px 'IBM Plex Mono',monospace;
 display:flex;align-items:center;justify-content:center;font-style:normal;}
.pin.f{top:254px;}.pin.e{top:328px;}
.pin:before{content:"";position:absolute;border-left:1.5px dotted var(--c);height:62px;}
.pin.f:before{bottom:0;}.pin.e:before{top:0;}
.card{position:absolute;width:172px;margin-left:-14px;background:#fff;border:1px solid #EAE1D8;border-top:3px solid var(--c);
 border-radius:12px;padding:10px 12px;box-sizing:border-box;transition:transform .2s,box-shadow .2s;}
.card:hover{transform:translateY(-2px);box-shadow:0 6px 18px rgba(43,47,58,.08);}
.card.f{bottom:calc(620px - 192px);}.card.e{top:390px;}
.card.now{background:#FFF8F2;}
.an{font-family:'IBM Plex Mono',monospace;font-size:11px;color:#9198A4;}
.t{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:15px;line-height:1.2;margin:2px 0 4px;}
.ds{font-size:12px;color:#5B6472;line-height:1.35;}
.big{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:24px;color:var(--c);line-height:1;margin-top:8px;}
.big sup{font-size:12px;}
.lab{font-size:12px;color:#5B6472;margin-top:2px;}
.today{position:absolute;top:222px;height:140px;border-left:1.5px dashed #2B2F3A;}
.today span{position:absolute;top:142px;transform:translateX(-50%);font-size:11px;white-space:nowrap;}
</style>
"""


def frise_histoire(frise, histoire):
    """Frise chronologique : position = date, longueur = durée, couleur = type."""
    aujourdhui = pd.Timestamp.today().normalize()
    debut_axe, fin_axe = pd.Timestamp("2020-01-01"), pd.Timestamp("2029-01-01")

    def date(d):
        return aujourdhui if d == "aujourdhui" else pd.Timestamp(d)

    def x(d):
        return (date(d) - debut_axe).days / (fin_axe - debut_axe).days * 100

    piste = {"Formation": "f", "Expérience": "e"}
    h = []
    for annee in range(debut_axe.year, fin_axe.year):
        h.append(f'<div class="yr" style="left:{x(f"{annee}-01-01"):.2f}%"><span>{annee}</span></div>')
    for a, b in histoire["zones_paralleles"]:
        h.append(f'<div class="par" style="left:{x(a):.2f}%;width:{x(b) - x(a):.2f}%">'
                 f'<span>études + entreprise</span></div>')
    for e in frise:
        d0, d1 = date(e["debut"]), date(e["fin"])
        mois = max(1, round((d1 - d0).days / 30.44))
        c = COULEURS[e["type"]]
        h.append(f'<div class="bar {piste[e["type"]]}" title="{escape(e["nom"])} : {mois} mois" '
                 f'style="left:{x(e["debut"]):.2f}%;width:{max(x(e["fin"]) - x(e["debut"]), 0.5):.2f}%;background:{c}"></div>')
        if e.get("fin_prevue"):
            h.append(f'<div class="bar {piste[e["type"]]} prev" title="{escape(e["nom"])} : fin prévue en '
                     f'{date(e["fin_prevue"]).year}" style="left:{x(e["fin"]):.2f}%;'
                     f'width:{x(e["fin_prevue"]) - x(e["fin"]):.2f}%;--c:{c}"></div>')
        if mois <= 2 and e["type"] == "Expérience":
            h.append(f'<div class="mini" style="left:{x(e["fin"]):.2f}%">{escape(e["nom"].split()[-1])}</div>')
    for ch in histoire["chapitres"]:
        p = piste[ch["piste"]]
        c = COULEURS[ch.get("couleur", ch["piste"])]
        actuel = " now" if ch.get("actuel") else ""
        h.append(f'<div class="pin {p}" style="left:{x(ch["date"]):.2f}%;--c:{c}"><i>{ch["num"]}</i></div>')
        h.append(f'<div class="card {p}{actuel}" style="left:{x(ch["date"]):.2f}%;--c:{c}">'
                 f'<div class="an">{escape(ch["annee"])}</div><div class="t">{escape(ch["titre"])}</div>'
                 f'<div class="ds">{escape(ch["detail"])}</div><div class="big">{ch["chiffre"]}</div>'
                 f'<div class="lab">{escape(ch["legende"])}</div></div>')
    h.append(f'<div class="today" style="left:{x("aujourdhui"):.2f}%"><span>aujourd\'hui</span></div>')

    return (FRISE_CSS + '<div class="frise">'
            f'<div class="lane" style="top:244px;color:{COULEURS["Formation"]}">Formation</div>'
            f'<div class="lane" style="top:318px;color:{COULEURS["Expérience"]}">Entreprise</div>'
            + "".join(h) + "</div>")


def graphique_radar(radar):
    df = pd.DataFrame(radar)
    df["libelle"] = df["niveau"].apply(lambda n: NIVEAUX[min(5, max(1, round(n)))])
    # on referme la forme en répétant le premier point
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)

    fig = go.Figure(go.Scatterpolar(
        r=df["niveau"], theta=df["outil"], fill="toself",
        fillcolor="rgba(200,118,58,0.18)",
        line=dict(color="#C8763A", width=2),
        marker=dict(size=8, color="#C8763A", line=dict(color="#FFFFFF", width=2)),
        customdata=df[["libelle", "source"]],
        hovertemplate="<b>%{theta}</b><br>Niveau : %{customdata[0]}<br>%{customdata[1]}<extra></extra>",
    ))
    fig.update_layout(
        height=520, margin=dict(l=110, r=110, t=40, b=40), showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13, color="#2B2F3A"),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#EAE1D8",
                        font=dict(color="#2B2F3A", family="Inter")),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 5], tickvals=[1, 2, 3, 4, 5],
                            ticktext=list(NIVEAUX.values()), angle=90, tickangle=90,
                            tickfont=dict(size=10, color="#9198A4"),
                            gridcolor="#EAE1D8", linecolor="#EAE1D8", showline=False),
            angularaxis=dict(tickfont=dict(size=13, color="#2B2F3A"),
                             gridcolor="#EAE1D8", linecolor="#EAE1D8", rotation=90,
                             direction="clockwise"),
        ),
    )
    return fig


cv = charger_cv(FICHIER_CV.stat().st_mtime)
contact = cv["contact"]

html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
:root{--ink:#2B2F3A;--ink-soft:#5B6472;--ink-faint:#9198A4;--peach:#E7B98C;
--sage:#5E8F6E;--sage-soft:#DCEBE1;--line:#EAE1D8;--panel:#FFFFFF;}
html, body, [class*="st-"], p, li{font-family:'Inter',sans-serif;}
h1,h2,h3{font-family:'Space Grotesk',sans-serif !important;letter-spacing:-0.01em;color:var(--ink);}
.block-container{max-width:1080px;padding-top:2.5rem;}
.eyebrow{font-family:'IBM Plex Mono',monospace;font-size:0.74rem;letter-spacing:0.13em;
text-transform:uppercase;color:var(--peach);font-weight:500;}
.hero-title{font-family:'Space Grotesk',sans-serif;font-size:clamp(2rem,4vw,3rem);
font-weight:700;line-height:1.1;color:var(--ink);margin:12px 0 0;}
.hero-title em{font-style:normal;color:var(--peach);}
.lead{margin-top:18px;font-size:1.04rem;color:var(--ink-soft);max-width:44ch;}
.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;
padding:22px 26px;margin-bottom:16px;transition:border-color .2s, transform .2s;}
.card:hover{border-color:var(--peach);}
.fiche .row{display:flex;justify-content:space-between;gap:16px;padding:11px 0;
border-bottom:1px dashed var(--line);font-size:0.9rem;}
.fiche .row:last-child{border-bottom:none;}
.profil{display:flex;align-items:center;gap:18px;padding:4px 0 18px;margin-bottom:6px;border-bottom:1px solid var(--line);}
.avatar{flex-shrink:0;width:96px;height:96px;border-radius:50%;padding:4px;
background:conic-gradient(from 200deg,#E7B98C,#C8763A,#8FB79D,#E7B98C);}
.avatar img{width:100%;height:100%;border-radius:50%;object-fit:cover;object-position:50% 30%;
border:3px solid #fff;box-sizing:border-box;display:block;}
.profil-nom{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.3rem;color:var(--ink);line-height:1.2;}
.profil-role{font-size:0.88rem;color:var(--ink-soft);margin-top:2px;}
.dispo{display:inline-flex;align-items:center;gap:6px;margin-top:8px;font-size:0.75rem;color:#2F6E52;
background:var(--sage-soft);padding:3px 10px;border-radius:999px;white-space:nowrap;}
.dispo i{width:7px;height:7px;border-radius:50%;background:#2F8F6B;display:inline-block;}
.fiche a{color:var(--ink) !important;text-decoration:none;border-bottom:1px solid var(--peach);}
.stButton button[kind="primary"], a[data-testid="stBaseLinkButton-primary"]{color:var(--ink) !important;}
a[data-testid="stBaseLinkButton-primary"] p{color:var(--ink) !important;}
.fiche .row span:first-child{color:var(--ink-soft);}
.fiche .row span:last-child{font-family:'IBM Plex Mono',monospace;font-size:0.82rem;text-align:right;color:var(--ink);}
.section-head{margin:8px 0 26px;}
.section-head h2{font-size:1.9rem;margin:6px 0 0;padding:0;}
.section-sub{color:var(--ink-soft);margin-top:8px;}
.tl-date{font-family:'IBM Plex Mono',monospace;font-size:0.8rem;color:var(--peach);margin-bottom:6px;}
.tl-role{font-family:'Space Grotesk',sans-serif;font-size:1.08rem;font-weight:600;color:var(--ink);}
.tl-org{font-size:0.9rem;color:var(--ink-soft);font-style:italic;margin-top:2px;}
.tl-desc{color:var(--ink-soft);font-size:0.94rem;margin-top:10px;margin-bottom:0;}
.tag-wrap{margin-top:12px;display:flex;flex-wrap:wrap;gap:6px;}
.pill{font-family:'IBM Plex Mono',monospace;font-size:0.72rem;background:var(--sage-soft);
color:var(--sage);padding:4px 10px;border-radius:999px;}
.proj-tag{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;text-transform:uppercase;
letter-spacing:0.05em;color:var(--sage);}
.proj h3{font-size:1.05rem;margin:6px 0 0;padding:0;}
.proj p{color:var(--ink-soft);font-size:0.9rem;margin:8px 0 0;}
.proj a{text-decoration:none;color:var(--ink);font-size:0.85rem;border-bottom:1px solid var(--peach);}
.skill h3{font-family:'IBM Plex Mono',monospace !important;font-size:0.78rem;text-transform:uppercase;
letter-spacing:0.05em;color:var(--ink-faint);font-weight:500;margin:0;padding:0;}
.skill ul{list-style:none;padding:0;margin:12px 0 0;}
.skill li{font-size:0.9rem;display:flex;align-items:center;gap:8px;margin-bottom:6px;color:var(--ink);}
.skill li::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--peach);flex-shrink:0;}
.contact-box{background:var(--ink);border-radius:24px;padding:48px 28px;text-align:center;margin-top:12px;}
.contact-box h2{color:#fff !important;font-size:1.9rem;padding:0;}
.contact-box p{color:#CBD1DA;margin:12px auto 0;max-width:44ch;}
.contact-links{margin-top:26px;display:flex;justify-content:center;gap:12px;flex-wrap:wrap;}
.contact-links a{text-decoration:none !important;padding:11px 20px;border-radius:999px;font-size:0.9rem;
font-weight:500;border:1px solid rgba(255,255,255,0.25);color:#fff !important;transition:border-color .2s;}
.contact-links a:hover{border-color:#fff;}
.contact-links a.main{background:var(--peach);color:var(--ink) !important;border-color:var(--peach);}
.stTabs [data-baseweb="tab"] p{font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:500;}
footer, #MainMenu{visibility:hidden;}
</style>
""")

# En-tête
gauche, droite = st.columns([1.15, 0.85], gap="large")
with gauche:
    html(f'<span class="eyebrow">{escape(cv["eyebrow"])}</span>'
         f'<h1 class="hero-title">{escape(cv["accroche_debut"])}<em>{escape(cv["accroche_fin"])}</em></h1>'
         f'<p class="lead">{escape(cv["presentation"])}</p>')
    b1, b2, _ = st.columns([1, 1, 1.4])
    with b1:
        st.link_button("Me contacter", f"mailto:{contact['email']}", type="primary", use_container_width=True)
    with b2:
        if PDF.exists():
            st.download_button("CV en PDF", PDF.read_bytes(), file_name=PDF.name,
                               mime="application/pdf", use_container_width=True)
        else:
            st.link_button("Mon GitHub", contact["github"], use_container_width=True)

with droite:
    entete = ""
    if PHOTO.exists():
        photo_b64 = base64.b64encode(PHOTO.read_bytes()).decode()
        entete = (f'<div class="profil"><div class="avatar">'
                  f'<img src="data:image/jpeg;base64,{photo_b64}" alt="Photo de {escape(cv["nom"])}"></div>'
                  f'<div><div class="profil-nom">{escape(cv["nom"])}</div>'
                  f'<div class="profil-role">Développeuse RPA et IA</div>'
                  f'<span class="dispo"><i></i>Ouverte aux échanges</span></div></div>')
    lignes = entete + "".join(f'<div class="row"><span>{escape(k)}</span><span>{escape(v)}</span></div>'
                     for k, v in cv["fiche"])
    lignes += (f'<div class="row"><span>GitHub</span><span>'
               f'<a href="{contact["github"]}" target="_blank">{contact["github"].replace("https://", "")}</a>'
               f'</span></div>')
    html(f'<div class="card fiche">{lignes}</div>')

st.write("")

onglets = st.tabs(["Parcours", "Projets", "Compétences", "Formation", "Contact"])

with onglets[0]:
    titre_section("Expérience", "Mon parcours",
                  "Entre transformation digitale terrain et automatisation avancée.")
    with st.container(border=True):
        histoire = cv["histoire"]
        html(f'<span class="eyebrow">Mon histoire</span>'
             f'<h3 style="margin:4px 0 0;padding:0;font-size:1.6rem;">{escape(histoire["titre"])}</h3>'
             f'<p class="section-sub" style="margin:4px 0 0;">{escape(histoire["sous_titre"])}</p>')
        components.html(frise_histoire(cv["frise"], histoire), height=650)
    for exp in cv["experiences"]:
        carte_timeline(exp["dates"], exp["poste"], exp["entreprise"], exp["description"], exp["tags"])

with onglets[1]:
    titre_section("Projets école", "Projets académiques",
                  "Des projets menés dans le cadre de ma formation, en autonomie ou en équipe.")
    technos = sorted({p["techno"] for p in cv["projets"]})
    choix = st.pills("Filtrer par technologie", technos, selection_mode="multi")
    projets = [p for p in cv["projets"] if not choix or p["techno"] in choix]
    colonnes = st.columns(2, gap="medium")
    for i, p in enumerate(projets):
        lien = (f'<p><a href="{p["lien"]}" target="_blank">Voir sur GitHub ↗</a></p>'
                if p["lien"] else "")
        with colonnes[i % 2]:
            html(f'<div class="card proj"><span class="proj-tag">{escape(p["techno"])}</span>'
                 f'<h3>{escape(p["titre"])}</h3><p>{escape(p["description"])}</p>{lien}</div>')

with onglets[2]:
    titre_section("Stack", "Compétences",
                  "Mon niveau sur les outils que j'utilise au quotidien, en entreprise et en projet.")
    with st.container(border=True):
        html('<span class="eyebrow">Mes outils et langages</span>')
        st.plotly_chart(graphique_radar(cv["radar"]), use_container_width=True,
                        config={"displayModeBar": False})
    colonnes = st.columns(len(cv["competences"]), gap="medium")
    for col, (groupe, items) in zip(colonnes, cv["competences"].items()):
        liste = "".join(f"<li>{escape(x)}</li>" for x in items)
        with col:
            html(f'<div class="card skill"><h3>{escape(groupe)}</h3><ul>{liste}</ul></div>')

with onglets[3]:
    titre_section("Formation", "Parcours académique")
    for f in cv["formations"]:
        carte_timeline(f["dates"], f["diplome"], f["ecole"])

with onglets[4]:
    liens = f'<a class="main" href="mailto:{contact["email"]}">{contact["email"]}</a>'
    if contact.get("afficher_telephone"):
        tel = contact["telephone"].replace(" ", "")
        liens += f'<a href="tel:{tel}">{contact["telephone"]}</a>'
    liens += (f'<a href="{contact["github"]}" target="_blank">GitHub ↗</a>'
              f'<a href="{contact["linkedin"]}" target="_blank">LinkedIn ↗</a>')
    html('<div class="contact-box"><h2>Discutons de votre projet</h2>'
         '<p>Disponible pour échanger sur une mission, un stage ou une collaboration.</p>'
         f'<div class="contact-links">{liens}</div></div>')

html(f'<p style="text-align:center;font-size:0.8rem;color:#9198A4;margin-top:40px;">© 2026 {escape(cv["nom"])}</p>')

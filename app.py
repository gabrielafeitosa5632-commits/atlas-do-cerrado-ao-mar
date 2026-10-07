from __future__ import annotations

import base64
import html
import mimetypes
from pathlib import Path

import streamlit as st

from atlas_content import GLOSSARY, REFERENCES, SECTIONS, build_export_markdown, get_section


APP_DIR = Path(__file__).resolve().parent
ASSET_DIR = APP_DIR / "assets"
GALLERY_DIR = ASSET_DIR / "galeria"

st.set_page_config(
    page_title="Atlas Digital · Do Cerrado ao Mar",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def query_section() -> int:
    try:
        return int(st.query_params.get("secao", 0) or 0)
    except (TypeError, ValueError):
        return 0


HERO_URI = image_data_uri(ASSET_DIR / "hero_aquario.png")
HERO_BACKGROUND = (
    f"linear-gradient(90deg, rgba(1,24,41,.98) 0%, rgba(1,36,57,.88) 36%, rgba(1,73,96,.22) 72%), url('{HERO_URI}')"
    if HERO_URI
    else "radial-gradient(circle at 72% 28%, rgba(66,214,235,.56) 0 2%, transparent 3%), linear-gradient(112deg,#00182b 4%,#003b59 48%,#0091b4 100%)"
)


CSS = f"""
<style>
:root {{
  --ink:#062b4a; --deep:#031f35; --ocean:#007eaa; --cyan:#45c7df;
  --foam:#f4fbfd; --sand:#f7f4ec; --line:rgba(5,75,101,.13);
}}
html, body, [class*="css"] {{ font-family:"Segoe UI",Arial,sans-serif; }}
.stApp {{ background:linear-gradient(180deg,#dff5f8 0,#f8fbf8 22rem,#f5f1e8 100%); color:var(--ink); }}
[data-testid="stHeader"] {{ background:transparent; }}
[data-testid="stSidebar"] {{ background:linear-gradient(180deg,#021d32 0%,#063b5a 64%,#075e78 100%); }}
[data-testid="stSidebar"] * {{ color:#f6fbff; }}
[data-testid="stSidebar"] [data-baseweb="select"] * {{ color:#072d49; }}
[data-testid="stSidebar"] input {{ color:#092e49 !important; }}
[data-testid="stSidebar"] button {{ border-color:rgba(255,255,255,.2); }}
[data-testid="stSidebar"] button:hover {{ border-color:#64d5e9; color:#fff; }}
.block-container {{ max-width:1480px; padding-top:1.1rem; padding-bottom:4rem; }}
h1,h2,h3 {{ font-family:"Bahnschrift SemiCondensed","Arial Narrow","Segoe UI",sans-serif; }}

.brand-kicker {{ color:#83dbef; font-weight:800; font-size:.77rem; letter-spacing:.16em; text-transform:uppercase; margin-bottom:.7rem; }}
.sidebar-brand {{ color:white; font-family:"Bahnschrift SemiCondensed","Arial Narrow",sans-serif; font-weight:800; font-size:1.8rem; line-height:.9; letter-spacing:-.04em; margin-bottom:.7rem; }}
.sidebar-caption {{ color:#bfdae7; font-size:.86rem; line-height:1.42; margin-bottom:1.25rem; }}
.sidebar-note {{ padding:.75rem .85rem; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.12); border-radius:12px; color:#cfe6ee; font-size:.76rem; line-height:1.4; }}

.hero {{
  position:relative; overflow:hidden; min-height:340px; border-radius:30px; padding:40px 44px;
  color:white; display:flex; align-items:flex-end; background-image:{HERO_BACKGROUND};
  background-size:cover; background-position:center 43%; box-shadow:0 22px 55px rgba(0,55,83,.24);
}}
.hero::before {{ content:""; position:absolute; width:470px; height:170px; border:2px solid rgba(170,235,246,.48); border-radius:50%; right:-80px; bottom:-125px; transform:rotate(-8deg); box-shadow:0 -20px 0 rgba(170,235,246,.14),0 -42px 0 rgba(170,235,246,.08); }}
.hero-content {{ position:relative; z-index:2; max-width:670px; }}
.eyebrow {{ font-weight:800; font-size:.84rem; letter-spacing:.17em; text-transform:uppercase; color:#91e0f2; margin-bottom:.8rem; }}
.hero h1 {{ font-weight:900; font-size:clamp(3rem,6vw,5.8rem); line-height:.83; letter-spacing:-.065em; margin:0 0 1rem; text-transform:uppercase; }}
.hero h1 span {{ color:#55c8eb; }}
.hero p {{ font-size:1.08rem; line-height:1.5; max-width:580px; color:#e6f5f9; margin:0; }}
.hero-badge {{ display:inline-flex; align-items:center; margin-top:1.3rem; padding:.55rem .82rem; border:1px solid rgba(255,255,255,.22); border-radius:999px; background:rgba(1,29,46,.43); font-size:.82rem; color:#e7f8fb; backdrop-filter:blur(9px); }}
.hero-credit {{ position:absolute; z-index:3; right:18px; bottom:12px; color:rgba(255,255,255,.72); font-size:.7rem; letter-spacing:.02em; }}

.search-label {{ margin:1.8rem 0 .15rem; font-weight:800; color:var(--ink); }}
.section-intro {{ display:flex; justify-content:space-between; gap:1.5rem; align-items:flex-end; margin:1.4rem .15rem 1rem; }}
.section-intro h2 {{ font-weight:900; font-size:clamp(1.65rem,2.4vw,2.25rem); line-height:1.08; margin:0; letter-spacing:-.04em; color:var(--ink); }}
.section-intro p {{ margin:.4rem 0 0; color:#4a6b7c; max-width:730px; }}
.count-pill {{ white-space:nowrap; color:#0b6080; background:#d7f1f4; border:1px solid #b7e4ea; border-radius:999px; padding:.5rem .8rem; font-size:.78rem; font-weight:800; }}
.empty-search {{ padding:2rem; border:1px dashed #7bb8c8; background:rgba(255,255,255,.6); border-radius:18px; color:#365f72; text-align:center; }}

.atlas-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:15px; }}
.atlas-card {{ --accent:#35b5ca; position:relative; min-height:205px; padding:21px 21px 18px; border-radius:20px; overflow:hidden; text-decoration:none !important; color:var(--ink) !important; background:linear-gradient(145deg,#fff 0%,#f6fbfc 70%); border:1px solid var(--line); box-shadow:0 8px 24px rgba(5,59,82,.09); transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease; }}
.atlas-card:hover {{ transform:translateY(-4px); box-shadow:0 16px 35px rgba(5,59,82,.17); border-color:var(--accent); }}
.atlas-card:focus-visible {{ outline:3px solid #f2a900; outline-offset:3px; }}
.atlas-card::after {{ content:""; position:absolute; inset:auto -20% -42% 18%; height:110px; background:var(--accent-soft,rgba(53,181,202,.2)); border-radius:50% 50% 0 0; transform:rotate(-7deg); }}
.card-top {{ display:flex; align-items:flex-start; gap:13px; position:relative; z-index:2; }}
.section-number {{ flex:0 0 auto; display:grid; place-items:center; width:48px; height:48px; border-radius:15px 8px 18px 8px; background:var(--accent); color:white; font-weight:900; font-size:1rem; box-shadow:0 6px 12px rgba(0,74,105,.18); }}
.atlas-card h3 {{ font-weight:900; font-size:1.2rem; line-height:1.05; margin:3px 0 0; letter-spacing:-.035em; }}
.atlas-card p {{ position:relative; z-index:2; color:#385b6f; font-size:.91rem; line-height:1.43; margin:17px 0 10px; max-width:94%; }}
.card-link {{ position:absolute; right:17px; bottom:15px; z-index:3; display:grid; place-items:center; width:36px; height:36px; border-radius:50%; background:#fff; color:#07587b; border:1px solid rgba(5,76,104,.14); font-size:1.4rem; font-weight:800; }}
.tone-0{{--accent:#3aa273;--accent-soft:rgba(58,162,115,.21)}}.tone-1{{--accent:#167dc0;--accent-soft:rgba(22,125,192,.2)}}.tone-2{{--accent:#35b7ca;--accent-soft:rgba(53,183,202,.2)}}.tone-3{{--accent:#84b84b;--accent-soft:rgba(132,184,75,.2)}}.tone-4{{--accent:#0375ad;--accent-soft:rgba(3,117,173,.2)}}.tone-5{{--accent:#22a5c2;--accent-soft:rgba(34,165,194,.2)}}.tone-6{{--accent:#7ab04c;--accent-soft:rgba(122,176,76,.2)}}.tone-7{{--accent:#09688d;--accent-soft:rgba(9,104,141,.2)}}.tone-8{{--accent:#218fa5;--accent-soft:rgba(33,143,165,.2)}}.tone-9{{--accent:#6b4196;--accent-soft:rgba(107,65,150,.2)}}.tone-10{{--accent:#3f71c6;--accent-soft:rgba(63,113,198,.2)}}.tone-11{{--accent:#f2a900;--accent-soft:rgba(242,169,0,.2)}}.tone-12{{--accent:#315b7c;--accent-soft:rgba(49,91,124,.2)}}
.atlas-card.wide {{ grid-column:span 2; }}

.back-link {{ display:inline-flex; align-items:center; min-height:44px; margin:.1rem 0 .5rem; color:#086a8d !important; font-weight:800; text-decoration:none !important; }}
.chapter-hero {{ --accent:#35b7ca; position:relative; overflow:hidden; min-height:270px; border-radius:26px; padding:clamp(1.4rem,4vw,3rem); display:flex; align-items:flex-end; color:white; background:linear-gradient(118deg,#03273f 0%,#075a79 58%,var(--accent) 130%); box-shadow:0 18px 44px rgba(5,59,82,.18); }}
.chapter-hero.has-image {{ background-size:cover; background-position:center; }}
.chapter-hero::after {{ content:""; position:absolute; width:440px; height:150px; right:-80px; bottom:-115px; border:2px solid rgba(255,255,255,.34); border-radius:50%; box-shadow:0 -20px 0 rgba(255,255,255,.11); }}
.chapter-copy {{ position:relative; z-index:2; max-width:900px; }}
.chapter-kicker {{ font-weight:800; font-size:.78rem; letter-spacing:.16em; text-transform:uppercase; color:#a8ebf4; }}
.chapter-hero h1 {{ font-weight:900; font-size:clamp(2.4rem,5vw,4.8rem); line-height:.92; letter-spacing:-.055em; margin:.65rem 0 .8rem; color:white; }}
.chapter-hero p {{ color:#e8f6f8; font-size:1.08rem; line-height:1.58; margin:0; max-width:850px; }}
.stats-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin:1rem 0 1.4rem; }}
.stat {{ background:#fff; border:1px solid var(--line); border-radius:16px; padding:1.05rem 1rem; box-shadow:0 7px 20px rgba(5,59,82,.07); }}
.stat strong {{ display:block; color:#04769a; font-size:1.35rem; line-height:1; margin-bottom:.38rem; }}
.stat span {{ color:#526f7d; font-size:.8rem; }}
.content-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; margin-top:1rem; }}
.content-card {{ background:rgba(255,255,255,.92); border:1px solid var(--line); border-radius:18px; padding:1.35rem 1.4rem; box-shadow:0 9px 26px rgba(5,59,82,.07); }}
.content-card:first-child:nth-last-child(3) {{ grid-column:span 2; }}
.content-card h2 {{ color:var(--ink); font-weight:900; font-size:1.48rem; letter-spacing:-.03em; margin:0 0 .7rem; }}
.content-card p,.content-card li {{ color:#38596b; font-size:.98rem; line-height:1.62; }}
.content-card p {{ margin:0; }}
.content-card ul {{ margin:.2rem 0 0; padding-left:1.2rem; }}
.content-card li+li {{ margin-top:.48rem; }}
.reflection {{ margin:1rem 0; padding:1.2rem 1.35rem; border-radius:18px; background:linear-gradient(120deg,#dff5f6,#eff8ed); border-left:5px solid #36a8b9; }}
.reflection strong {{ display:block; color:#086789; text-transform:uppercase; letter-spacing:.1em; font-size:.76rem; margin-bottom:.35rem; }}
.reflection p {{ margin:0; color:#264f62; line-height:1.55; }}
.source-list a {{ color:#07789e !important; font-weight:700; text-decoration:none; }}
.source-list li {{ margin:.5rem 0; }}
.source-org {{ color:#647d88; font-size:.82rem; }}
.chapter-nav {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:1.3rem; }}
.chapter-nav a {{ display:flex; min-height:60px; align-items:center; padding:.8rem 1rem; background:#fff; border:1px solid var(--line); border-radius:15px; color:#0a6382 !important; text-decoration:none !important; font-weight:800; }}
.chapter-nav a:last-child {{ justify-content:flex-end; text-align:right; }}

.glossary-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; margin:1rem 0; }}
.term-card {{ background:#fff; border:1px solid var(--line); border-radius:16px; padding:1.1rem 1.2rem; }}
.term-card h3 {{ color:#087b9d; font-size:1.08rem; margin:0 0 .45rem; }}
.term-card p {{ color:#496777; line-height:1.5; margin:0; }}
.gallery-empty {{ padding:2.2rem 1.2rem; text-align:center; border:1px dashed #77adbc; border-radius:20px; background:rgba(255,255,255,.6); color:#466978; }}
.atlas-footer {{ margin-top:2.3rem; padding:1.3rem; text-align:center; color:#547382; font-size:.82rem; border-top:1px solid rgba(5,75,101,.12); }}

@media (prefers-reduced-motion:reduce) {{ * {{ scroll-behavior:auto !important; transition:none !important; animation:none !important; }} }}
@media (max-width:1100px) {{ .atlas-grid{{grid-template-columns:repeat(3,minmax(0,1fr))}} .atlas-card.wide{{grid-column:span 1}} }}
@media (max-width:780px) {{ .block-container{{padding-top:.6rem}} .hero{{min-height:350px;padding:30px 24px;border-radius:22px;background-position:64% center}} .hero h1{{font-size:3.35rem}} .atlas-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}} .section-intro{{align-items:flex-start;flex-direction:column}} .count-pill{{display:none}} .content-grid{{grid-template-columns:1fr}} .content-card:first-child:nth-last-child(3){{grid-column:span 1}} .stats-grid{{grid-template-columns:repeat(2,1fr)}} }}
@media (max-width:520px) {{ .atlas-grid,.glossary-grid{{grid-template-columns:1fr}} .atlas-card{{min-height:182px}} .hero h1{{font-size:2.75rem}} .chapter-hero{{min-height:300px}} .chapter-nav{{grid-template-columns:1fr}} .chapter-nav a:last-child{{justify-content:flex-start;text-align:left}} }}
</style>
"""


def go_home() -> None:
    st.query_params.clear()


def go_to(number: int) -> None:
    st.query_params["secao"] = str(number)


def render_sidebar(current: int) -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-kicker">Atlas Digital</div>
            <div class="sidebar-brand">DO CERRADO<br>AO MAR</div>
            <div class="sidebar-caption">A experiência dos estudantes do IFB no AquaRio.</div>
            """,
            unsafe_allow_html=True,
        )
        st.button("⌂  Início", use_container_width=True, on_click=go_home)
        options = [0] + [section["number"] for section in SECTIONS]
        index = options.index(current) if current in options else 0
        selected = st.selectbox(
            "Explorar seção",
            options=options,
            index=index,
            format_func=lambda value: (
                "Escolha uma seção" if value == 0 else f'{value:02d} · {SECTIONS[value - 1]["short_title"]}'
            ),
        )
        if selected != current:
            if selected:
                go_to(selected)
            else:
                go_home()
            st.rerun()

        st.markdown("---")
        st.download_button(
            "↓  Baixar atlas em Markdown",
            data=build_export_markdown().encode("utf-8"),
            file_name="atlas_do_cerrado_ao_mar.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.markdown(
            """
            <div class="sidebar-note">
              <strong>Versão-base editável</strong><br>
              Depoimentos, espécies observadas e fotos da turma devem ser inseridos a partir dos registros reais e das autorizações de uso.
            </div>
            """,
            unsafe_allow_html=True,
        )


def searchable_text(section: dict) -> str:
    parts = [section["title"], section["summary"], section["intro"]]
    for block in section.get("blocks", []):
        parts.extend([block.get("title", ""), block.get("body", ""), " ".join(block.get("bullets", []))])
    if section["number"] == 12:
        parts.extend(f"{term} {definition}" for term, definition in GLOSSARY)
    if section["number"] == 13:
        parts.extend(f'{item["title"]} {item["organization"]} {item["note"]}' for item in REFERENCES.values())
    return " ".join(parts).lower()


def render_home() -> None:
    st.markdown(
        """
        <section class="hero">
          <div class="hero-content">
            <div class="eyebrow">Atlas digital</div>
            <h1>Do Cerrado<br><span>ao Mar</span></h1>
            <p>Uma travessia educativa entre território, água e oceano a partir da experiência dos estudantes do IFB no AquaRio.</p>
            <div class="hero-badge">● &nbsp; 13 percursos de aprendizagem</div>
          </div>
          <span class="hero-credit">Imagem conceitual gerada por IA</span>
        </section>
        <div class="search-label">Buscar no atlas</div>
        """,
        unsafe_allow_html=True,
    )
    search = st.text_input(
        "Buscar no atlas",
        placeholder="Ex.: tubarões, conservação, manguezal…",
        label_visibility="collapsed",
    ).strip().lower()
    shown = [section for section in SECTIONS if not search or search in searchable_text(section)]
    st.markdown(
        f"""
        <div class="section-intro">
          <div><h2>{'Resultados da busca' if search else 'Explore o atlas'}</h2>
          <p>{'Abra uma seção relacionada ao termo pesquisado.' if search else 'Acesse conceitos, registros e propostas de investigação construídos a partir da visita.'}</p></div>
          <div class="count-pill">{len(shown)} {'RESULTADOS' if search else 'SEÇÕES'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not shown:
        st.markdown(
            '<div class="empty-search">Nenhuma seção encontrada. Tente um termo mais amplo, como “água”, “ciência” ou “espécies”.</div>',
            unsafe_allow_html=True,
        )
        return
    cards = []
    for section in shown:
        number = section["number"]
        wide = " wide" if number == 13 and len(shown) > 1 else ""
        cards.append(
            f'<a class="atlas-card tone-{number - 1}{wide}" href="?secao={number}" target="_self" '
            f'aria-label="Abrir seção {number}: {html.escape(section["title"])}">'
            f'<div class="card-top"><span class="section-number">{number:02d}</span><h3>{html.escape(section["title"])}</h3></div>'
            f'<p>{html.escape(section["summary"])}</p><span class="card-link" aria-hidden="true">›</span></a>'
        )
    st.markdown(f'<div class="atlas-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_stats(stats: list[tuple[str, str]]) -> None:
    items = "".join(
        f'<div class="stat"><strong>{html.escape(value)}</strong><span>{html.escape(label)}</span></div>'
        for value, label in stats
    )
    st.markdown(f'<div class="stats-grid">{items}</div>', unsafe_allow_html=True)


def render_blocks(blocks: list[dict]) -> None:
    if not blocks:
        return
    rendered = []
    for block in blocks:
        body = f'<p>{html.escape(block["body"])}</p>' if block.get("body") else ""
        bullets = ""
        if block.get("bullets"):
            bullets = "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in block["bullets"]) + "</ul>"
        rendered.append(
            f'<section class="content-card"><h2>{html.escape(block["title"])}</h2>{body}{bullets}</section>'
        )
    st.markdown(f'<div class="content-grid">{"".join(rendered)}</div>', unsafe_allow_html=True)


def render_sources(source_ids: list[str]) -> None:
    if not source_ids:
        return
    with st.expander("Fontes desta seção"):
        items = []
        for source_id in source_ids:
            source = REFERENCES.get(source_id)
            if not source:
                continue
            items.append(
                f'<li><a href="{html.escape(source["url"])}" target="_blank" rel="noopener noreferrer">'
                f'{html.escape(source["title"])}</a><br><span class="source-org">'
                f'{html.escape(source["organization"])} · {html.escape(source["note"])}</span></li>'
            )
        st.markdown(f'<ul class="source-list">{"".join(items)}</ul>', unsafe_allow_html=True)


def render_observation_log() -> None:
    st.markdown("### Registro da equipe")
    if "observations" not in st.session_state:
        st.session_state.observations = []
    with st.form("observation_form", clear_on_submit=True):
        cols = st.columns([1, 1])
        with cols[0]:
            common_name = st.text_input("Nome informado ou grupo", placeholder="Ex.: raia")
            scientific_name = st.text_input("Nome científico confirmado", placeholder="Opcional")
        with cols[1]:
            location = st.text_input("Recinto ou ponto da visita", placeholder="Ex.: Recinto Oceânico")
            evidence = st.selectbox("Fonte da identificação", ["Fotografia da equipe", "Placa do recinto", "Mediação educativa", "Ainda não confirmada"])
        note = st.text_area("Característica ou comportamento observado", height=90)
        add = st.form_submit_button("Adicionar ao registro")
        if add and common_name.strip():
            st.session_state.observations.append(
                {
                    "Organismo/grupo": common_name.strip(),
                    "Nome científico": scientific_name.strip() or "—",
                    "Local": location.strip() or "—",
                    "Evidência": evidence,
                    "Observação": note.strip() or "—",
                }
            )
    if st.session_state.observations:
        st.dataframe(st.session_state.observations, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum organismo registrado nesta sessão. Comece pelos registros que a equipe consegue comprovar.")


def render_experience_log() -> None:
    st.markdown("### Caderno de memórias")
    st.text_input("Autoria do relato", key="experience_author", placeholder="Nome ou identificação escolhida pela equipe")
    st.text_area(
        "Relato",
        key="experience_report",
        height=160,
        placeholder="O encontro que mais me marcou foi… / Eu pensava que… e depois da visita…",
    )
    st.caption("O texto fica apenas nesta sessão. Confirme autorização antes de publicar autoria, imagem ou informação pessoal.")


def render_gallery() -> None:
    st.warning(
        "Use somente fotografias autorizadas. Imagens com estudantes identificáveis devem respeitar as autorizações da instituição e das pessoas responsáveis."
    )
    uploaded = st.file_uploader(
        "Adicionar fotografias para visualizar nesta sessão",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
    )
    local_files = sorted(
        path for path in GALLERY_DIR.glob("*") if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    pictures: list[tuple[object, str]] = [(path, path.stem.replace("_", " ").title()) for path in local_files]
    pictures.extend((file, file.name.rsplit(".", 1)[0].replace("_", " ").title()) for file in uploaded)
    if not pictures:
        st.markdown(
            '<div class="gallery-empty"><strong>A galeria aguarda o acervo da equipe.</strong><br>Adicione fotos acima para uma prévia ou salve arquivos na pasta <code>assets/galeria</code> para exibição permanente.</div>',
            unsafe_allow_html=True,
        )
        return
    columns = st.columns(3)
    for index, (picture, caption) in enumerate(pictures):
        with columns[index % 3]:
            st.image(picture, caption=caption, use_container_width=True)


def render_glossary() -> None:
    term_search = st.text_input("Buscar termo", placeholder="Ex.: ecossistema").strip().lower()
    terms = [(term, definition) for term, definition in GLOSSARY if not term_search or term_search in f"{term} {definition}".lower()]
    if not terms:
        st.info("Nenhum termo encontrado. Tente outra palavra.")
        return
    cards = "".join(
        f'<article class="term-card"><h3>{html.escape(term)}</h3><p>{html.escape(definition)}</p></article>'
        for term, definition in terms
    )
    st.markdown(f'<div class="glossary-grid">{cards}</div>', unsafe_allow_html=True)


def render_reference_library() -> None:
    st.markdown("### Biblioteca consultada")
    for source in REFERENCES.values():
        st.markdown(
            f'**[{source["title"]}]({source["url"]})**  \n'
            f'{source["organization"]} — {source["note"]}'
        )
    st.caption("Links externos podem ser atualizados pelas instituições responsáveis. Consulta editorial: 6 de outubro de 2026.")


def render_chapter_navigation(number: int) -> None:
    previous = get_section(number - 1)
    following = get_section(number + 1)
    left = (
        f'<a href="?secao={previous["number"]}" target="_self">‹ &nbsp; {html.escape(previous["short_title"])}</a>'
        if previous
        else '<a href="?" target="_self">‹ &nbsp; Início</a>'
    )
    right = (
        f'<a href="?secao={following["number"]}" target="_self">{html.escape(following["short_title"])} &nbsp; ›</a>'
        if following
        else '<a href="?" target="_self">Voltar ao início &nbsp; ›</a>'
    )
    st.markdown(f'<nav class="chapter-nav" aria-label="Navegação entre seções">{left}{right}</nav>', unsafe_allow_html=True)


def render_detail(section_number: int) -> None:
    section = get_section(section_number)
    if section is None:
        st.warning("Seção não encontrada.")
        if st.button("Voltar ao início"):
            go_home()
            st.rerun()
        return
    number = section["number"]
    image_path = ASSET_DIR / section["image"] if section.get("image") else None
    image_uri = image_data_uri(image_path) if image_path else ""
    image_class = " has-image" if image_uri else ""
    background = (
        f' style="background-image:linear-gradient(90deg,rgba(1,27,45,.96) 0%,rgba(2,58,78,.78) 50%,rgba(3,60,77,.2) 100%),url(\'{image_uri}\')"'
        if image_uri
        else ""
    )
    st.markdown('<a class="back-link" href="?" target="_self">← &nbsp; Voltar ao atlas</a>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <header class="chapter-hero tone-{number - 1}{image_class}"{background}>
          <div class="chapter-copy">
            <div class="chapter-kicker">Seção {number:02d}</div>
            <h1>{html.escape(section["title"])}</h1>
            <p>{html.escape(section["intro"])}</p>
          </div>
        </header>
        """,
        unsafe_allow_html=True,
    )
    if image_uri:
        st.caption("Imagem conceitual gerada por IA; não é um registro da visita nem identifica o local retratado.")
    if section.get("stats"):
        render_stats(section["stats"])
    render_blocks(section.get("blocks", []))

    if number == 5:
        render_observation_log()
    elif number == 10:
        render_experience_log()
    elif number == 11:
        render_gallery()
    elif number == 12:
        render_glossary()
    elif number == 13:
        render_reference_library()

    st.markdown(
        f'<aside class="reflection"><strong>Para registrar</strong><p>{html.escape(section["reflection"])}</p></aside>',
        unsafe_allow_html=True,
    )
    if number not in {5, 10, 11}:
        st.text_area("Anotações da equipe", key=f"notes_{number}", placeholder="Escreva aqui as observações desta seção…")
        st.caption("As anotações permanecem apenas durante esta sessão do navegador.")
    render_sources(section.get("sources", []))
    render_chapter_navigation(number)


st.markdown(CSS, unsafe_allow_html=True)
current_section = query_section()
render_sidebar(current_section)
if current_section:
    render_detail(current_section)
else:
    render_home()
st.markdown(
    '<footer class="atlas-footer">Atlas Digital Do Cerrado ao Mar · material educativo editável · IFB / experiência de visita ao AquaRio</footer>',
    unsafe_allow_html=True,
)


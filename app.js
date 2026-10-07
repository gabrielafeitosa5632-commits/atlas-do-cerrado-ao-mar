(() => {
  "use strict";

  const { sections, glossary, references } = window.ATLAS_DATA;
  const app = document.querySelector("#app");
  const select = document.querySelector("#section-select");
  const sidebar = document.querySelector("#sidebar");
  const menuToggle = document.querySelector("#menu-toggle");
  const backdrop = document.querySelector("#backdrop");
  const downloadButton = document.querySelector("#download-atlas");
  const lightbox = document.querySelector("#lightbox");
  const lightboxImage = document.querySelector("#lightbox-image");
  const lightboxCaption = document.querySelector("#lightbox-caption");
  const toast = document.querySelector("#toast");

  const STORAGE = {
    observations: "atlas-observacoes-v1",
    experienceAuthor: "atlas-autoria-v1",
    experienceReport: "atlas-relato-v1",
    notesPrefix: "atlas-notas-v1-"
  };

  let galleryObjectUrls = [];
  let toastTimer;

  const escapeHTML = (value = "") => String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const normalizeText = (value = "") => String(value)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR");

  const readJSON = (key, fallback) => {
    try {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : fallback;
    } catch {
      return fallback;
    }
  };

  const writeJSON = (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch {
      return false;
    }
  };

  const readText = (key) => {
    try {
      return localStorage.getItem(key) || "";
    } catch {
      return "";
    }
  };

  const writeText = (key, value) => {
    try {
      localStorage.setItem(key, value);
      return true;
    } catch {
      return false;
    }
  };

  const removeStored = (key) => {
    try {
      localStorage.removeItem(key);
    } catch {
      // O site continua funcional mesmo quando o navegador bloqueia o armazenamento local.
    }
  };

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("show"), 2600);
  }

  function sectionByNumber(number) {
    return sections.find((section) => section.number === Number(number));
  }

  function sectionSearchText(section) {
    const parts = [section.title, section.summary, section.intro];
    section.blocks.forEach((block) => {
      parts.push(block.title, block.body || "", ...(block.bullets || []));
    });
    if (section.number === 12) {
      glossary.forEach(([term, definition]) => parts.push(term, definition));
    }
    if (section.number === 13) {
      Object.values(references).forEach((source) => parts.push(source.title, source.organization, source.note));
    }
    return normalizeText(parts.join(" "));
  }

  function populateSectionSelect() {
    const options = sections.map((section) => (
      `<option value="${section.number}">${String(section.number).padStart(2, "0")} · ${escapeHTML(section.shortTitle)}</option>`
    ));
    select.insertAdjacentHTML("beforeend", options.join(""));
  }

  function getRoute() {
    const match = window.location.hash.match(/^#secao=(\d{1,2})$/);
    if (!match) return { type: "home" };
    const section = sectionByNumber(match[1]);
    return section ? { type: "section", section } : { type: "home" };
  }

  function updateNavigation(route) {
    document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
    if (route.type === "home") {
      document.querySelector('[data-route="home"].nav-item')?.classList.add("active");
      select.value = "";
    } else {
      document.querySelector(`[data-section-link="${route.section.number}"]`)?.classList.add("active");
      select.value = String(route.section.number);
    }
  }

  function closeMenu() {
    sidebar.classList.remove("open");
    menuToggle.setAttribute("aria-expanded", "false");
    backdrop.hidden = true;
  }

  function renderCards(list, query = "") {
    const region = document.querySelector("#cards-region");
    const title = document.querySelector("#results-title");
    const copy = document.querySelector("#results-copy");
    const count = document.querySelector("#results-count");
    if (!region || !title || !copy || !count) return;

    title.textContent = query ? "Resultados da busca" : "Explore o atlas";
    copy.textContent = query
      ? "Abra uma seção relacionada ao termo pesquisado."
      : "Acesse conceitos, registros e propostas de investigação construídos a partir da visita.";
    count.textContent = `${list.length} ${query ? "RESULTADO" + (list.length === 1 ? "" : "S") : "SEÇÕES"}`;

    if (!list.length) {
      region.innerHTML = '<div class="empty-search">Nenhuma seção encontrada. Tente um termo mais amplo, como “água”, “ciência” ou “espécies”.</div>';
      region.className = "";
      return;
    }

    region.className = "atlas-grid";
    region.innerHTML = list.map((section) => {
      const wide = section.number === 13 && list.length > 1 ? " wide" : "";
      return `
        <a class="atlas-card tone-${section.number - 1}${wide}" href="#secao=${section.number}"
           aria-label="Abrir seção ${section.number}: ${escapeHTML(section.title)}">
          <div class="card-top">
            <span class="section-number">${String(section.number).padStart(2, "0")}</span>
            <h3>${escapeHTML(section.title)}</h3>
          </div>
          <p>${escapeHTML(section.summary)}</p>
          <span class="card-link" aria-hidden="true">›</span>
        </a>`;
    }).join("");
  }

  function renderHome() {
    document.title = "Projeto TAMAR · Do Cerrado ao mar | Atlas Digital";
    app.innerHTML = `
      <section class="hero" aria-labelledby="atlas-title">
        <div class="hero-content">
          <div class="eyebrow">Atlas digital</div>
          <h1 id="atlas-title">Projeto<br><span>TAMAR</span></h1>
          <div class="hero-project">Do Cerrado ao mar</div>
          <p>A experiência dos estudantes do IFB entre ciência, conservação e cultura oceânica.</p>
          <div class="hero-badge">13 percursos de aprendizagem</div>
        </div>
        <span class="hero-credit">Imagem conceitual gerada por IA</span>
      </section>

      <div class="search-wrap">
        <label class="search-label" for="atlas-search">Buscar no atlas</label>
        <input class="search-field" id="atlas-search" type="search" autocomplete="off"
          placeholder="Ex.: tubarões, conservação, manguezal…">
      </div>

      <div class="section-intro">
        <div>
          <h2 id="results-title">Explore o atlas</h2>
          <p id="results-copy">Acesse conceitos, registros e propostas de investigação construídos a partir da visita.</p>
        </div>
        <div class="count-pill" id="results-count">13 SEÇÕES</div>
      </div>
      <div class="atlas-grid" id="cards-region"></div>`;

    renderCards(sections);
    const search = document.querySelector("#atlas-search");
    search.addEventListener("input", () => {
      const query = normalizeText(search.value.trim());
      const results = query ? sections.filter((section) => sectionSearchText(section).includes(query)) : sections;
      renderCards(results, query);
    });
  }

  function renderStats(stats = []) {
    if (!stats.length) return "";
    return `<div class="stats-grid">${stats.map(([value, label]) => `
      <div class="stat"><strong>${escapeHTML(value)}</strong><span>${escapeHTML(label)}</span></div>
    `).join("")}</div>`;
  }

  function renderBlocks(blocks = []) {
    if (!blocks.length) return "";
    return `<div class="content-grid">${blocks.map((block) => {
      const body = block.body ? `<p>${escapeHTML(block.body)}</p>` : "";
      const bullets = block.bullets?.length
        ? `<ul>${block.bullets.map((item) => `<li>${escapeHTML(item)}</li>`).join("")}</ul>`
        : "";
      return `<section class="content-card"><h2>${escapeHTML(block.title)}</h2>${body}${bullets}</section>`;
    }).join("")}</div>`;
  }

  function renderSources(sourceIds = []) {
    if (!sourceIds.length) return "";
    const items = sourceIds.map((id) => references[id]).filter(Boolean).map((source) => `
      <li>
        <a href="${escapeHTML(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(source.title)}</a><br>
        <span class="source-org">${escapeHTML(source.organization)} · ${escapeHTML(source.note)}</span>
      </li>`).join("");
    return `<details class="sources-details"><summary>Fontes desta seção</summary><ul class="source-list">${items}</ul></details>`;
  }

  function renderObservationLog() {
    return `
      <section class="interactive-panel" aria-labelledby="observation-title">
        <h2 id="observation-title">Registro da equipe</h2>
        <form id="observation-form">
          <div class="form-grid">
            <div class="field">
              <label for="common-name">Nome informado ou grupo</label>
              <input id="common-name" name="commonName" required placeholder="Ex.: raia">
            </div>
            <div class="field">
              <label for="scientific-name">Nome científico confirmado</label>
              <input id="scientific-name" name="scientificName" placeholder="Opcional">
            </div>
            <div class="field">
              <label for="location">Espaço ou ponto da visita</label>
              <input id="location" name="location" placeholder="Ex.: área interpretativa">
            </div>
            <div class="field">
              <label for="evidence">Fonte da identificação</label>
              <select id="evidence" name="evidence">
                <option>Fotografia da equipe</option>
                <option>Placa ou painel da unidade</option>
                <option>Mediação educativa</option>
                <option>Ainda não confirmada</option>
              </select>
            </div>
            <div class="field full">
              <label for="observation-note">Característica ou comportamento observado</label>
              <textarea id="observation-note" name="note"></textarea>
            </div>
          </div>
          <div class="button-row">
            <button class="primary-button" type="submit">Adicionar ao registro</button>
            <button class="secondary-button" id="clear-observations" type="button">Limpar registros</button>
          </div>
        </form>
        <p class="helper">Os registros ficam somente neste navegador e não são enviados pela internet.</p>
        <div id="observation-list"></div>
      </section>`;
  }

  function drawObservationList() {
    const container = document.querySelector("#observation-list");
    if (!container) return;
    const observations = readJSON(STORAGE.observations, []);
    if (!observations.length) {
      container.innerHTML = '<div class="empty-note">Nenhum organismo registrado neste navegador. Comece pelos registros que a equipe consegue comprovar.</div>';
      return;
    }
    container.innerHTML = `
      <div class="records-wrap">
        <table class="records-table">
          <thead><tr><th>Organismo/grupo</th><th>Nome científico</th><th>Local</th><th>Evidência</th><th>Observação</th></tr></thead>
          <tbody>${observations.map((item) => `
            <tr>
              <td>${escapeHTML(item.commonName)}</td>
              <td>${escapeHTML(item.scientificName || "—")}</td>
              <td>${escapeHTML(item.location || "—")}</td>
              <td>${escapeHTML(item.evidence)}</td>
              <td>${escapeHTML(item.note || "—")}</td>
            </tr>`).join("")}</tbody>
        </table>
      </div>`;
  }

  function bindObservationLog() {
    const form = document.querySelector("#observation-form");
    const clear = document.querySelector("#clear-observations");
    if (!form || !clear) return;
    drawObservationList();
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const data = new FormData(form);
      const entry = {
        commonName: String(data.get("commonName") || "").trim(),
        scientificName: String(data.get("scientificName") || "").trim(),
        location: String(data.get("location") || "").trim(),
        evidence: String(data.get("evidence") || ""),
        note: String(data.get("note") || "").trim()
      };
      if (!entry.commonName) return;
      const observations = readJSON(STORAGE.observations, []);
      observations.push(entry);
      writeJSON(STORAGE.observations, observations);
      form.reset();
      drawObservationList();
      showToast("Organismo adicionado ao registro local.");
    });
    clear.addEventListener("click", () => {
      removeStored(STORAGE.observations);
      drawObservationList();
      showToast("Registros locais removidos.");
    });
  }

  function renderExperienceLog() {
    return `
      <section class="interactive-panel" aria-labelledby="experience-title">
        <h2 id="experience-title">Caderno de memórias</h2>
        <div class="form-grid">
          <div class="field full">
            <label for="experience-author">Autoria do relato</label>
            <input id="experience-author" placeholder="Nome ou identificação escolhida pela equipe">
          </div>
          <div class="field full">
            <label for="experience-report">Relato</label>
            <textarea id="experience-report" maxlength="600" placeholder="O encontro que mais me marcou foi… / Eu pensava que… e depois da visita…"></textarea>
          </div>
        </div>
        <div class="button-row">
          <button class="primary-button" id="save-experience" type="button">Salvar neste navegador</button>
          <button class="secondary-button" id="clear-experience" type="button">Limpar</button>
        </div>
        <p class="helper">Confirme autorização antes de publicar autoria, imagem ou informação pessoal.</p>
      </section>`;
  }

  function bindExperienceLog() {
    const author = document.querySelector("#experience-author");
    const report = document.querySelector("#experience-report");
    const save = document.querySelector("#save-experience");
    const clear = document.querySelector("#clear-experience");
    if (!author || !report || !save || !clear) return;
    author.value = readText(STORAGE.experienceAuthor);
    report.value = readText(STORAGE.experienceReport);
    save.addEventListener("click", () => {
      writeText(STORAGE.experienceAuthor, author.value.trim());
      writeText(STORAGE.experienceReport, report.value.trim());
      showToast("Memória salva somente neste navegador.");
    });
    clear.addEventListener("click", () => {
      author.value = "";
      report.value = "";
      removeStored(STORAGE.experienceAuthor);
      removeStored(STORAGE.experienceReport);
      showToast("Caderno local limpo.");
    });
  }

  function renderGallery() {
    return `
      <section class="interactive-panel" aria-labelledby="gallery-title">
        <h2 id="gallery-title">Acervo da equipe</h2>
        <div class="notice"><strong>Atenção:</strong> use somente fotografias autorizadas. Imagens com estudantes identificáveis devem respeitar as autorizações da instituição e das pessoas responsáveis.</div>
        <div class="gallery-toolbar">
          <label for="gallery-upload"><strong>Adicionar fotografias para visualizar</strong></label>
          <input id="gallery-upload" type="file" accept="image/png,image/jpeg,image/webp" multiple>
        </div>
        <div id="gallery-content" class="gallery-empty"><strong>A galeria aguarda o acervo da equipe.</strong><br>Escolha imagens acima para montar uma prévia neste navegador.</div>
        <p class="helper">As imagens escolhidas não são enviadas nem permanecem após recarregar a página.</p>
      </section>`;
  }

  function prettyFileName(name) {
    return name.replace(/\.[^.]+$/, "").replaceAll("_", " ").replaceAll("-", " ")
      .replace(/\b\p{L}/gu, (letter) => letter.toLocaleUpperCase("pt-BR"));
  }

  function bindGallery() {
    const input = document.querySelector("#gallery-upload");
    const content = document.querySelector("#gallery-content");
    if (!input || !content) return;
    input.addEventListener("change", () => {
      galleryObjectUrls.forEach((url) => URL.revokeObjectURL(url));
      galleryObjectUrls = [];
      const files = [...input.files].filter((file) => file.type.startsWith("image/"));
      if (!files.length) {
        content.className = "gallery-empty";
        content.innerHTML = "<strong>A galeria aguarda o acervo da equipe.</strong><br>Escolha imagens acima para montar uma prévia neste navegador.";
        return;
      }
      const pictures = files.map((file) => {
        const url = URL.createObjectURL(file);
        galleryObjectUrls.push(url);
        const caption = prettyFileName(file.name);
        return `<figure class="gallery-item">
          <button type="button" class="gallery-open" data-src="${escapeHTML(url)}" data-caption="${escapeHTML(caption)}" aria-label="Ampliar ${escapeHTML(caption)}">
            <img src="${escapeHTML(url)}" alt="${escapeHTML(caption)}">
          </button>
          <figcaption>${escapeHTML(caption)}</figcaption>
        </figure>`;
      }).join("");
      content.className = "gallery-grid";
      content.innerHTML = pictures;
      content.querySelectorAll(".gallery-open").forEach((button) => {
        button.addEventListener("click", () => openLightbox(button.dataset.src, button.dataset.caption));
      });
    });
  }

  function renderGlossary() {
    return `
      <section aria-labelledby="glossary-heading">
        <div class="glossary-tools">
          <label for="glossary-search" id="glossary-heading">Buscar termo</label>
          <input class="glossary-search" id="glossary-search" type="search" autocomplete="off" placeholder="Ex.: ecossistema">
        </div>
        <div class="glossary-grid" id="glossary-grid"></div>
      </section>`;
  }

  function drawGlossary(list) {
    const grid = document.querySelector("#glossary-grid");
    if (!grid) return;
    if (!list.length) {
      grid.innerHTML = '<div class="empty-search">Nenhum termo encontrado. Tente outra palavra.</div>';
      return;
    }
    grid.innerHTML = list.map(([term, definition]) => `
      <article class="term-card"><h2>${escapeHTML(term)}</h2><p>${escapeHTML(definition)}</p></article>
    `).join("");
  }

  function bindGlossary() {
    const input = document.querySelector("#glossary-search");
    if (!input) return;
    drawGlossary(glossary);
    input.addEventListener("input", () => {
      const query = normalizeText(input.value.trim());
      const list = query
        ? glossary.filter(([term, definition]) => normalizeText(`${term} ${definition}`).includes(query))
        : glossary;
      drawGlossary(list);
    });
  }

  function renderReferenceLibrary() {
    return `
      <section aria-labelledby="references-title">
        <div class="section-intro"><div><h2 id="references-title">Biblioteca consultada</h2></div></div>
        <div class="reference-library">${Object.values(references).map((source) => `
          <article class="reference-card">
            <a href="${escapeHTML(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(source.title)}</a>
            <p><strong>${escapeHTML(source.organization)}</strong> — ${escapeHTML(source.note)}</p>
          </article>`).join("")}</div>
        <p class="helper">Links externos podem ser atualizados pelas instituições responsáveis. Consulta editorial: 6 de outubro de 2026.</p>
      </section>`;
  }

  function renderNotes(sectionNumber) {
    const value = readText(`${STORAGE.notesPrefix}${sectionNumber}`);
    return `
      <section class="interactive-panel" aria-labelledby="notes-title">
        <h2 id="notes-title">Anotações da equipe</h2>
        <div class="field">
          <label class="sr-only" for="section-notes">Anotações da seção</label>
          <textarea id="section-notes" placeholder="Escreva aqui as observações desta seção…">${escapeHTML(value)}</textarea>
        </div>
        <div class="button-row">
          <button class="primary-button" id="save-notes" type="button">Salvar neste navegador</button>
          <button class="secondary-button" id="clear-notes" type="button">Limpar</button>
        </div>
        <p class="helper">As anotações ficam apenas neste dispositivo.</p>
      </section>`;
  }

  function bindNotes(sectionNumber) {
    const textarea = document.querySelector("#section-notes");
    const save = document.querySelector("#save-notes");
    const clear = document.querySelector("#clear-notes");
    if (!textarea || !save || !clear) return;
    const key = `${STORAGE.notesPrefix}${sectionNumber}`;
    save.addEventListener("click", () => {
      writeText(key, textarea.value);
      showToast("Anotações salvas somente neste navegador.");
    });
    clear.addEventListener("click", () => {
      textarea.value = "";
      removeStored(key);
      showToast("Anotações locais removidas.");
    });
  }

  function renderChapterNavigation(number) {
    const previous = sectionByNumber(number - 1);
    const next = sectionByNumber(number + 1);
    const left = previous
      ? `<a href="#secao=${previous.number}">‹&nbsp; ${escapeHTML(previous.shortTitle)}</a>`
      : '<a href="#inicio">‹&nbsp; Início</a>';
    const right = next
      ? `<a href="#secao=${next.number}">${escapeHTML(next.shortTitle)} &nbsp;›</a>`
      : '<a href="#inicio">Voltar ao início &nbsp;›</a>';
    return `<nav class="chapter-nav" aria-label="Navegação entre seções">${left}${right}</nav>`;
  }

  function renderDetail(section) {
    document.title = `${String(section.number).padStart(2, "0")} · ${section.title} | Atlas Digital`;
    const imageStyle = section.image
      ? ` style="background-image:linear-gradient(90deg,rgba(1,27,45,.97) 0%,rgba(2,58,78,.78) 50%,rgba(3,60,77,.2) 100%),url('${escapeHTML(section.image)}')"`
      : "";
    const imageClass = section.image ? " has-image" : "";
    const imageCredit = section.image
      ? '<span class="image-credit">Imagem conceitual gerada por IA; não é um registro da visita nem identifica o local retratado.</span>'
      : "";

    let special = "";
    if (section.number === 5) special = renderObservationLog();
    if (section.number === 10) special = renderExperienceLog();
    if (section.number === 11) special = renderGallery();
    if (section.number === 12) special = renderGlossary();
    if (section.number === 13) special = renderReferenceLibrary();
    const notes = [5, 10, 11].includes(section.number) ? "" : renderNotes(section.number);

    app.innerHTML = `
      <a class="back-link" href="#inicio">←&nbsp; Voltar ao atlas</a>
      <header class="chapter-hero tone-${section.number - 1}${imageClass}"${imageStyle}>
        <div class="chapter-copy">
          <div class="chapter-kicker">Seção ${String(section.number).padStart(2, "0")}</div>
          <h1>${escapeHTML(section.title)}</h1>
          <p>${escapeHTML(section.intro)}</p>
        </div>
      </header>
      ${imageCredit}
      ${renderStats(section.stats)}
      ${renderBlocks(section.blocks)}
      ${special}
      <aside class="reflection"><strong>Para registrar</strong><p>${escapeHTML(section.reflection)}</p></aside>
      ${notes}
      ${renderSources(section.sources)}
      ${renderChapterNavigation(section.number)}`;

    if (section.number === 5) bindObservationLog();
    if (section.number === 10) bindExperienceLog();
    if (section.number === 11) bindGallery();
    if (section.number === 12) bindGlossary();
    if (![5, 10, 11].includes(section.number)) bindNotes(section.number);
  }

  function renderRoute({ preserveScroll = false } = {}) {
    galleryObjectUrls.forEach((url) => URL.revokeObjectURL(url));
    galleryObjectUrls = [];
    const route = getRoute();
    updateNavigation(route);
    if (route.type === "section") renderDetail(route.section);
    else renderHome();
    closeMenu();
    if (!preserveScroll) window.scrollTo({ top: 0, behavior: "auto" });
  }

  function openLightbox(src, caption) {
    lightboxImage.src = src;
    lightboxImage.alt = caption;
    lightboxCaption.textContent = caption;
    if (typeof lightbox.showModal === "function") lightbox.showModal();
  }

  function buildMarkdown() {
    const lines = [
      "# PROJETO TAMAR",
      "",
      "Do Cerrado ao mar: a experiência dos estudantes do IFB entre ciência, conservação e cultura oceânica.",
      "",
      "> Versão-base editável. Registros de visita devem ser confirmados pela equipe.",
      ""
    ];
    sections.forEach((section) => {
      lines.push(`## ${section.number}. ${section.title}`, "", section.intro, "");
      section.blocks.forEach((block) => {
        lines.push(`### ${block.title}`, "");
        if (block.body) lines.push(block.body, "");
        (block.bullets || []).forEach((item) => lines.push(`- ${item}`));
        if (block.bullets?.length) lines.push("");
      });
      lines.push("### Para registrar", "", section.reflection, "");
    });
    lines.push("## Glossário", "");
    glossary.forEach(([term, definition]) => lines.push(`- **${term}:** ${definition}`));
    lines.push("", "## Referências", "");
    Object.values(references).forEach((source) => lines.push(`- ${source.organization}. **${source.title}.** ${source.url}`));
    lines.push("");
    return lines.join("\n");
  }

  function downloadAtlas() {
    const blob = new Blob([buildMarkdown()], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "atlas_do_cerrado_ao_mar.md";
    document.body.append(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 500);
    showToast("Download do atlas iniciado.");
  }

  populateSectionSelect();
  renderRoute({ preserveScroll: true });

  select.addEventListener("change", () => {
    window.location.hash = select.value ? `secao=${select.value}` : "inicio";
  });

  window.addEventListener("hashchange", () => renderRoute());

  menuToggle.addEventListener("click", () => {
    const open = !sidebar.classList.contains("open");
    sidebar.classList.toggle("open", open);
    menuToggle.setAttribute("aria-expanded", String(open));
    backdrop.hidden = !open;
  });

  backdrop.addEventListener("click", closeMenu);
  sidebar.addEventListener("click", (event) => {
    if (event.target.closest("a") && window.matchMedia("(max-width: 900px)").matches) closeMenu();
  });

  downloadButton.addEventListener("click", downloadAtlas);

  document.querySelector(".lightbox-close").addEventListener("click", () => lightbox.close());
  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox) lightbox.close();
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
  });
})();

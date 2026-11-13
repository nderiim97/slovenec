/* Slovenec — public page renderers. */
(function () {
  "use strict";

  const P = window.Portal;
  const $ = function (sel, root) {
    return (root || document).querySelector(sel);
  };
  const $$ = function (sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  };

  function cardList(articles, options) {
    return articles.map(function (a) {
      return P.card(a, options);
    }).join("");
  }

  function loading(target) {
    if (target) {
      target.innerHTML = '<div class="empty-state"><strong>Nalaganje …</strong><span>Pripravljamo vsebino.</span></div>';
    }
  }

  function fail(target, err) {
    if (target) {
      target.innerHTML =
        '<div class="empty-state"><strong>Vsebine ni bilo mogoče naložiti</strong>' +
        "<span>" + P.escape(err && err.message ? err.message : "Poskusite znova.") + "</span></div>";
    }
  }

  async function initHome() {
    const hero = $("[data-hero]");
    const latest = $("[data-latest-strip]");
    const main = $("[data-home-sections]");
    const sidebar = $("[data-sidebar]");
    [hero, latest, main, sidebar].forEach(loading);

    let data;
    try {
      data = await P.api("/api/home");
    } catch (err) {
      [hero, latest, main, sidebar].forEach(function (el) { fail(el, err); });
      return;
    }

    P.renderTicker(data.breaking);

    if (data.lead) {
      const lead = data.lead;
      hero.innerHTML =
        '<div class="hero__grid">' +
        '<a class="hero__lead" href="' + P.attr(lead.url) + '">' +
        '<img src="' + P.attr(P.image(lead)) + '" alt="" width="1200" height="675">' +
        '<div class="hero__lead-body">' +
        '<span class="badge">' + P.escape(lead.category_name || "Slovenija") + "</span>" +
        '<h1 class="hero__lead-title">' + P.escape(lead.title) + "</h1>" +
        (lead.deck ? '<p class="hero__lead-deck">' + P.escape(lead.deck) + "</p>" : "") +
        '<div class="hero__lead-meta">' + P.escape(P.dateTime(lead.published_at)) +
        " · " + lead.reading_minutes + " min branja</div>" +
        "</div></a>" +
        '<div class="hero__side">' +
        cardList((data.featured || []).slice(0, 2), { size: "md" }) +
        "</div>" +
        "</div>";
    } else {
      hero.innerHTML = "";
    }

    latest.innerHTML = (data.latest || [])
      .slice(0, 4)
      .map(function (a) {
        return (
          '<a class="latest-strip__item" href="' + P.attr(a.url) + '">' +
          '<span class="latest-strip__time">' + P.escape(P.ago(a.published_at)) + "</span>" +
          P.escape(a.title) +
          "</a>"
        );
      })
      .join("");

    const sections = (data.sections || []).filter(function (s) {
      return s.category.slug !== "mnenja";
    });

    let mainHtml = "";
    if ((data.live || []).length) {
      mainHtml +=
        '<section class="section">' +
        '<div class="section__head"><h2 class="section__title">V živo</h2>' +
        '<a class="section__link" href="/live">Vsi prenosi →</a></div>' +
        '<div class="grid grid--3">' + cardList(data.live, { deck: true }) + "</div>" +
        "</section>";
    }

    mainHtml += sections.map(function (section) {
      return (
        '<section class="section">' +
        '<div class="section__head">' +
        '<h2 class="section__title">' + P.escape(section.category.name) + "</h2>" +
        '<a class="section__link" href="/rubrika/' + P.attr(section.category.slug) + '">Več →</a>' +
        "</div>" +
        '<div class="grid grid--4">' + cardList(section.articles, { size: "sm", deck: true }) + "</div>" +
        "</section>"
      );
    }).join("");
    main.innerHTML = mainHtml;

    const mostRead = (data.most_read || []).map(function (a, index) {
      return (
        "<li>" +
        '<span class="rank-list__num">' + String(index + 1).padStart(2, "0") + "</span>" +
        "<div>" +
        '<a class="rank-list__title" href="' + P.attr(a.url) + '">' + P.escape(a.title) + "</a>" +
        '<span class="rank-list__meta">' + P.escape(a.category_name) + " · " + P.escape(P.ago(a.published_at)) + "</span>" +
        "</div></li>"
      );
    }).join("");

    const opinions = (data.opinions || []).map(function (a) {
      return (
        '<div class="opinion">' +
        '<span class="opinion__avatar">' + P.escape(P.initials(a.author)) + "</span>" +
        "<div>" +
        '<span class="opinion__author">' + P.escape(a.author) + "</span>" +
        '<a class="opinion__title" href="' + P.attr(a.url) + '">' + P.escape(a.title) + "</a>" +
        "</div></div>"
      );
    }).join("");

    sidebar.innerHTML =
      '<div class="side-block">' +
      '<h3 class="side-block__title">Najbolj brano</h3>' +
      '<ol class="rank-list">' + mostRead + "</ol>" +
      "</div>" +
      '<div class="side-block">' +
      '<h3 class="side-block__title">Mnenja</h3>' +
      '<div class="opinion-list">' + opinions + "</div>" +
      "</div>" +
      '<div class="newsletter">' +
      "<h3>Jutranji pregled</h3>" +
      "<p>Najpomembnejše zgodbe dneva v vašem nabiralniku, vsak dan ob 7. uri.</p>" +
      '<form data-newsletter><input type="email" required placeholder="vaš@email.si" aria-label="E-pošta"><button type="submit">Naroči</button></form>' +
      '<p class="newsletter__note">Demo: prijava ni shranjena. Brez sledenja.</p>' +
      "</div>";

    const form = $("[data-newsletter]", sidebar);
    if (form) {
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        form.reset();
        P.toast("Hvala! V demo različici prijava ni shranjena.");
      });
    }
  }

  function categoryFromPath() {
    const match = window.location.pathname.match(/^\/rubrika\/([^/]+)\/?$/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  async function initCategory() {
    const slug = categoryFromPath();
    const grid = $("[data-category-grid]");
    const head = $("[data-category-head]");
    const loadWrap = $("[data-load-more]");
    const countEl = $("[data-category-count]");
    loading(grid);

    const category = (P.categories || []).find(function (c) { return c.slug === slug; });
    if (category) {
      document.title = category.name + " — " + (P.site ? P.site.site_name : "Slovenec");
      $("[data-category-kicker]").textContent = "Rubrika";
      $("[data-category-title]").textContent = category.name;
      $("[data-category-desc]").textContent = category.description || "";
    }

    let offset = 0;
    const limit = 12;
    let total = 0;

    async function load(reset) {
      if (reset) {
        offset = 0;
        grid.innerHTML = "";
      }
      try {
        const data = await P.api(
          "/api/articles?category=" + encodeURIComponent(slug) +
          "&limit=" + limit + "&offset=" + offset
        );
        total = data.total;
        if (!data.articles.length && reset) {
          grid.innerHTML =
            '<div class="empty-state"><strong>Ni objavljenih člankov</strong><span>V tej rubriki še ni vsebine.</span></div>';
        } else {
          grid.insertAdjacentHTML("beforeend", cardList(data.articles, { size: "md", deck: true }));
        }
        offset += data.articles.length;
        if (countEl) countEl.textContent = total + " člankov";
        if (loadWrap) loadWrap.hidden = offset >= total;
      } catch (err) {
        fail(grid, err);
      }
    }

    if (head) head.hidden = false;
    await load(true);
    const more = $("[data-load-more] button");
    if (more) {
      more.addEventListener("click", function () {
        more.disabled = true;
        load(false).finally(function () { more.disabled = false; });
      });
    }
  }

  function articleFromPath() {
    const match = window.location.pathname.match(/^\/clanek\/([^/]+)\/?$/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  function paragraphs(body) {
    return String(body || "")
      .split(/\n\s*\n/)
      .map(function (p) { return p.trim(); })
      .filter(Boolean)
      .map(function (p) { return "<p>" + P.escape(p) + "</p>"; })
      .join("");
  }

  async function initArticle() {
    const slug = articleFromPath();
    const root = $("[data-article]");
    loading(root);

    let data;
    try {
      data = await P.api("/api/articles/" + encodeURIComponent(slug));
    } catch (err) {
      fail(root, err);
      return;
    }

    const a = data.article;
    const articleUrl = window.location.origin + a.url;
    document.title = a.title + " — " + (P.site ? P.site.site_name : "Slovenec");

    root.innerHTML =
      '<nav class="breadcrumbs" aria-label="Pot">' +
      '<a href="/">Domov</a><span>/</span>' +
      '<a href="/rubrika/' + P.attr(a.category_slug) + '">' + P.escape(a.category_name) + "</a>" +
      "</nav>" +
      '<header class="article">' +
      '<a class="article__cat" href="/rubrika/' + P.attr(a.category_slug) + '">' + P.escape(a.category_name) + "</a>" +
      "<h1>" + P.escape(a.title) + "</h1>" +
      (a.deck ? '<p class="article__deck">' + P.escape(a.deck) + "</p>" : "") +
      '<div class="article__meta">' +
      '<span class="article__author">' + P.escape(a.author) + "</span>" +
      "<span>" + P.escape(P.dateTime(a.published_at)) + "</span>" +
      "<span>" + a.reading_minutes + " min branja</span>" +
      '<div class="article__share">' +
      '<button class="share-btn" data-copy title="Kopiraj povezavo">🔗</button>' +
      '<a class="share-btn" target="_blank" rel="noopener" title="Deli na X" href="https://twitter.com/intent/tweet?url=' + encodeURIComponent(articleUrl) + "&text=" + encodeURIComponent(a.title) + '">X</a>' +
      '<a class="share-btn" target="_blank" rel="noopener" title="Deli na Facebooku" href="https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(articleUrl) + '">f</a>' +
      "</div></div></header>" +
      '<figure class="article__figure article">' +
      '<img src="' + P.attr(P.image(a)) + '" alt="" width="1200" height="675">' +
      (a.image_caption ? '<figcaption class="article__caption">' + P.escape(a.image_caption) + "</figcaption>" : "") +
      "</figure>" +
      '<div class="article__body article">' + paragraphs(a.body) + "</div>" +
      (a.tags.length
        ? '<div class="article__tags article">' + a.tags.map(function (t) {
            return '<a class="tag" href="/iskanje?q=' + encodeURIComponent(t) + '">#' + P.escape(t) + "</a>";
          }).join("") + "</div>"
        : "") +
      '<div class="article__authorbox article">' +
      '<span class="opinion__avatar">' + P.escape(P.initials(a.author)) + "</span>" +
      "<div><strong>" + P.escape(a.author) + "</strong>" +
      "<span>Avtor prispevka · " + P.escape(P.site ? P.site.site_name : "Slovenec") + "</span></div>" +
      "</div>";

    const nav = $("[data-article-nav]");
    if (nav) {
      const prev = data.prev
        ? '<a href="' + P.attr(data.prev.url) + '"><small>Prejšnji članek</small><strong>' + P.escape(data.prev.title) + "</strong></a>"
        : "<span></span>";
      const next = data.next
        ? '<a href="' + P.attr(data.next.url) + '"><small>Naslednji članek</small><strong>' + P.escape(data.next.title) + "</strong></a>"
        : "<span></span>";
      nav.innerHTML = prev + next;
    }

    const related = $("[data-related]");
    if (related && data.related.length) {
      related.innerHTML =
        '<div class="section__head"><h2 class="section__title">Sorodni članki</h2></div>' +
        '<div class="grid grid--4">' + cardList(data.related, { size: "sm" }) + "</div>";
    }

    const copy = $("[data-copy]");
    if (copy) {
      copy.addEventListener("click", async function () {
        try {
          await navigator.clipboard.writeText(articleUrl);
          P.toast("Povezava je kopirana.");
        } catch (err) {
          P.toast("Kopiranje ni uspelo.", true);
        }
      });
    }

    P.api("/api/articles/" + encodeURIComponent(a.slug) + "/view", { method: "POST" }).catch(function () {});
  }

  async function initSearch() {
    const params = new URLSearchParams(window.location.search);
    const q = (params.get("q") || "").trim();
    const input = $("[data-search-input]");
    const results = $("[data-search-results]");
    const summary = $("[data-search-summary]");
    if (input) input.value = q;
    if (!q) {
      if (summary) summary.textContent = "Vnesite iskalni niz.";
      if (results) results.innerHTML = "";
      return;
    }
    loading(results);
    try {
      const data = await P.api("/api/articles?q=" + encodeURIComponent(q) + "&limit=30");
      if (summary) {
        summary.textContent = data.total + (data.total === 1 ? " zadetek" : " zadetkov") + ' za »' + q + "«";
      }
      if (!data.articles.length) {
        results.innerHTML =
          '<div class="empty-state"><strong>Ni zadetkov</strong><span>Poskusite z drugim izrazom.</span></div>';
        return;
      }
      results.innerHTML = data.articles.map(function (a) {
        return (
          '<article class="search-result">' +
          '<a class="search-result__media" href="' + P.attr(a.url) + '"><img src="' + P.attr(P.image(a)) + '" alt="" loading="lazy"></a>' +
          "<div>" +
          '<span class="card__cat" style="position:static;display:inline-flex;margin-bottom:6px;background:' + P.attr(a.category_color) + '">' + P.escape(a.category_name) + "</span>" +
          '<h3><a href="' + P.attr(a.url) + '">' + P.escape(a.title) + "</a></h3>" +
          (a.deck ? "<p>" + P.escape(a.deck) + "</p>" : "") +
          '<div class="card__meta"><span>' + P.escape(P.ago(a.published_at)) + "</span><span>" + a.reading_minutes + " min branja</span></div>" +
          "</div></article>"
        );
      }).join("");
    } catch (err) {
      fail(results, err);
    }
  }

  async function initLive() {
    const root = $("[data-live]");
    loading(root);
    try {
      const data = await P.api("/api/live");
      if (!data.articles.length) {
        root.innerHTML =
          '<div class="empty-state"><strong>Trenutno ni prenosov v živo</strong><span>Vrnite se pozneje.</span></div>';
        return;
      }
      root.innerHTML = data.articles.map(function (a) {
        return (
          '<article class="live-entry">' +
          '<div class="live-entry__time">' + P.escape(P.time(a.published_at)) + "</div>" +
          "<div>" +
          '<span class="badge badge--live">V živo</span>' +
          '<h3><a href="' + P.attr(a.url) + '">' + P.escape(a.title) + "</a></h3>" +
          (a.deck ? "<p>" + P.escape(a.deck) + "</p>" : "") +
          '<div class="card__meta"><span>' + P.escape(a.author) + "</span><span>" + P.escape(P.date(a.published_at)) + "</span></div>" +
          "</div></article>"
        );
      }).join("");
    } catch (err) {
      fail(root, err);
    }
  }

  document.addEventListener("DOMContentLoaded", async function () {
    const page = document.body.getAttribute("data-page");
    if (window.Portal && window.Portal.ready) {
      try { await window.Portal.ready; } catch (err) { /* chrome is optional */ }
    }
    if (page === "home") initHome();
    else if (page === "category") initCategory();
    else if (page === "article") initArticle();
    else if (page === "search") initSearch();
    else if (page === "live") initLive();
  });
})();

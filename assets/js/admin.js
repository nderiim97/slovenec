/* Slovenec — admin panel. */
(function () {
  "use strict";

  const $ = function (sel, root) { return (root || document).querySelector(sel); };
  const $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  const state = {
    user: null,
    categories: [],
    articles: [],
    editingId: null,
    editingCategory: null,
    view: "dashboard",
  };

  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  async function api(path, options) {
    const opts = Object.assign({ credentials: "same-origin" }, options || {});
    if (opts.body && typeof opts.body !== "string") {
      opts.body = JSON.stringify(opts.body);
      opts.headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
    }
    const res = await fetch(path, opts);
    let data = null;
    try { data = await res.json(); } catch (err) { data = null; }
    if (!res.ok) {
      if (res.status === 401) {
        showLogin();
      }
      const detail = data && data.detail;
      const error = new Error(typeof detail === "string" ? detail : "Prišlo je do napake.");
      error.status = res.status;
      throw error;
    }
    return data;
  }

  let toastTimer;
  function toast(message, isError) {
    let el = $("[data-toast]");
    if (!el) return;
    el.textContent = message;
    el.classList.toggle("toast--error", !!isError);
    el.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove("is-visible"); }, 3000);
  }

  function showLogin() {
    $("#login-view").hidden = false;
    $("#admin-app").hidden = true;
  }

  function showApp() {
    $("#login-view").hidden = true;
    $("#admin-app").hidden = false;
    $("[data-user-name]").textContent = state.user ? state.user.name + " · " + state.user.email : "";
  }

  function toLocalInput(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return "";
    const pad = function (n) { return String(n).padStart(2, "0"); };
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) +
      "T" + pad(d.getHours()) + ":" + pad(d.getMinutes());
  }

  function fmtDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return "";
    return new Intl.DateTimeFormat("sl-SI", { day: "2-digit", month: "2-digit", year: "numeric" }).format(d);
  }

  // -------------------------------------------------------------------------
  // Navigation
  // -------------------------------------------------------------------------

  const TITLES = {
    dashboard: ["Nadzorna plošča", "Pregled objav in obiska."],
    articles: ["Članki", "Urejanje, objavljanje in brisanje prispevkov."],
    editor: ["Urejanje članka", "Naslov, besedilo, kategorija in oznake."],
    categories: ["Kategorije", "Rubrike, barve in vrstni red v navigaciji."],
    settings: ["Nastavitve", "Osnovni podatki portala."],
  };

  function showView(name) {
    state.view = name;
    $$("[data-panel]").forEach(function (panel) {
      panel.hidden = panel.getAttribute("data-panel") !== name;
    });
    $$("[data-view]").forEach(function (link) {
      link.classList.toggle("is-active", link.getAttribute("data-view") === name);
    });
    const meta = TITLES[name] || TITLES.dashboard;
    $("[data-view-title]").textContent = meta[0];
    $("[data-view-subtitle]").textContent = meta[1];
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // -------------------------------------------------------------------------
  // Dashboard
  // -------------------------------------------------------------------------

  async function loadDashboard() {
    try {
      const data = await api("/api/admin/stats");
      // The recent table is rendered from this data; keep it available for the
      // shared "Uredi" handler so editing works directly from the dashboard.
      state.articles = data.recent || [];
      $("[data-stats]").innerHTML =
        stat("Vsi članki", data.total) +
        stat("Objavljeno", data.published) +
        stat("Osnutki", data.drafts) +
        stat("Skupaj branj", Number(data.views).toLocaleString("sl-SI"));
      $("[data-recent]").innerHTML = articleTable(data.recent, true);
    } catch (err) {
      toast(err.message, true);
    }
  }

  function stat(label, value) {
    return '<div class="stat"><span>' + esc(label) + "</span><strong>" + esc(value) + "</strong></div>";
  }

  // -------------------------------------------------------------------------
  // Articles
  // -------------------------------------------------------------------------

  async function loadArticles() {
    const q = ($("[data-article-search]") || {}).value || "";
    const statusFilter = ($("[data-article-filter]") || {}).value || "";
    const params = new URLSearchParams();
    if (q.trim()) params.set("q", q.trim());
    if (statusFilter) params.set("status_filter", statusFilter);
    try {
      const data = await api("/api/admin/articles?" + params.toString());
      state.articles = data.articles;
      $("[data-articles-table]").innerHTML = articleTable(data.articles, false);
    } catch (err) {
      toast(err.message, true);
    }
  }

  function articleTable(rows, compact) {
    if (!rows || !rows.length) {
      return '<div class="empty-state"><strong>Ni člankov</strong><span>Ustvarite prvi prispevek.</span></div>';
    }
    return (
      '<table class="admin-table"><thead><tr>' +
      "<th>Naslov</th><th>Kategorija</th>" +
      (compact ? "" : '<th class="admin-table__hide-sm">Status</th><th class="admin-table__hide-sm">Branja</th>') +
      '<th class="admin-table__hide-sm">Datum</th><th></th></tr></thead><tbody>' +
      rows.map(function (a) {
        return (
          "<tr>" +
          '<td class="admin-table__title">' + esc(a.title) +
          "<small>/clanek/" + esc(a.slug) + "</small></td>" +
          "<td>" + esc(a.category_name) + "</td>" +
          (compact ? "" :
            '<td class="admin-table__hide-sm"><span class="pill pill--' + esc(a.status) + '">' +
            (a.status === "published" ? "Objavljeno" : "Osnutek") + "</span></td>" +
            '<td class="admin-table__hide-sm">' + Number(a.views).toLocaleString("sl-SI") + "</td>") +
          '<td class="admin-table__hide-sm">' + esc(fmtDate(a.published_at)) + "</td>" +
          '<td><div class="row-actions">' +
          '<button type="button" data-edit="' + a.id + '">Uredi</button>' +
          '<a class="btn btn--ghost btn--sm" style="padding:5px 9px;text-transform:none;letter-spacing:0" href="' + esc(a.url) + '" target="_blank" rel="noopener">Odpri</a>' +
          (compact ? "" : '<button type="button" class="danger" data-delete="' + a.id + '">Izbriši</button>') +
          "</div></td></tr>"
        );
      }).join("") +
      "</tbody></table>"
    );
  }

  function categoryOptions(selected) {
    return state.categories.map(function (c) {
      return '<option value="' + esc(c.slug) + '"' + (c.slug === selected ? " selected" : "") + ">" +
        esc(c.name) + "</option>";
    }).join("");
  }

  function openEditor(article, presetCategory) {
    state.editingId = article ? article.id : null;
    const form = $("[data-article-form]");
    form.reset();
    $("[data-editor-title]").textContent = article ? "Uredi članek" : "Nov članek";
    $("[data-delete-article]").hidden = !article;
    $("#f-category").innerHTML = categoryOptions(article ? article.category_slug : (presetCategory || "slovenija"));

    if (article) {
      $("#f-title").value = article.title || "";
      $("#f-slug").value = article.slug || "";
      $("#f-deck").value = article.deck || "";
      $("#f-body").value = article.body || "";
      $("#f-author").value = article.author || "Uredništvo";
      $("#f-published").value = toLocalInput(article.published_at);
      $("#f-image").value = article.image_url || "";
      $("#f-caption").value = article.image_caption || "";
      $("#f-tags").value = (article.tags || []).join(", ");
      $("#f-status").value = article.status || "published";
      form.elements.is_featured.checked = !!article.is_featured;
      form.elements.is_breaking.checked = !!article.is_breaking;
      form.elements.is_live.checked = !!article.is_live;
    } else {
      $("#f-author").value = "Uredništvo";
      $("#f-published").value = toLocalInput(new Date().toISOString());
      $("#f-image").value = "/assets/img/covers/cover-1.svg";
      $("#f-status").value = "published";
      form.elements.is_featured.checked = false;
      form.elements.is_breaking.checked = false;
      form.elements.is_live.checked = false;
    }
    showView("editor");
  }

  async function saveArticle(event) {
    event.preventDefault();
    const form = $("[data-article-form]");
    const payload = {
      title: form.elements.title.value.trim(),
      slug: form.elements.slug.value.trim(),
      deck: form.elements.deck.value.trim(),
      body: form.elements.body.value.trim(),
      category_slug: form.elements.category_slug.value,
      author: form.elements.author.value.trim(),
      image_url: form.elements.image_url.value.trim(),
      image_caption: form.elements.image_caption.value.trim(),
      tags: form.elements.tags.value.split(",").map(function (t) { return t.trim(); }).filter(Boolean),
      status: form.elements.status.value,
      is_featured: form.elements.is_featured.checked,
      is_breaking: form.elements.is_breaking.checked,
      is_live: form.elements.is_live.checked,
      // datetime-local is in the editor's local time; send a real UTC instant so
      // "publish now" is not stored in the future relative to the server clock.
      published_at: form.elements.published_at.value
        ? new Date(form.elements.published_at.value).toISOString()
        : null,
    };
    if (!payload.title) {
      toast("Naslov je obvezen.", true);
      return;
    }
    const button = $("[data-save-article]");
    button.disabled = true;
    try {
      if (state.editingId) {
        await api("/api/admin/articles/" + state.editingId, { method: "PUT", body: payload });
        toast(payload.status === "draft" ? "Osnutek je shranjen." : "Članek je posodobljen.");
      } else {
        await api("/api/admin/articles", { method: "POST", body: payload });
        toast(payload.status === "draft" ? "Osnutek je shranjen." : "Članek je objavljen.");
      }
      await loadArticles();
      showView("articles");
    } catch (err) {
      toast(err.message, true);
    } finally {
      button.disabled = false;
    }
  }

  async function deleteArticle(id) {
    if (!window.confirm("Res želite izbrisati ta članek? Dejanja ni mogoče razveljaviti.")) return;
    try {
      await api("/api/admin/articles/" + id, { method: "DELETE" });
      toast("Članek je izbrisan.");
      if (state.editingId === id) {
        state.editingId = null;
        showView("articles");
      }
      await loadArticles();
      await loadDashboard();
    } catch (err) {
      toast(err.message, true);
    }
  }

  // -------------------------------------------------------------------------
  // Categories
  // -------------------------------------------------------------------------

  async function loadCategories() {
    try {
      const data = await api("/api/admin/categories");
      state.categories = data.categories;
      $("[data-categories-table]").innerHTML = categoryTable(data.categories);
      $("#f-category").innerHTML = categoryOptions($("#f-category").value || "slovenija");
      refreshQuickCategories();
    } catch (err) {
      toast(err.message, true);
    }
  }

  function refreshQuickCategories() {
    const select = $("[data-quick-category]");
    if (!select) return;
    const current = select.value || "slovenija";
    select.innerHTML = categoryOptions(current);
  }

  function categoryTable(rows) {
    return (
      '<table class="admin-table"><thead><tr><th>Ime</th><th>Slug</th><th>Barva</th>' +
      '<th class="admin-table__hide-sm">Članki</th><th class="admin-table__hide-sm">Vrsta</th><th></th></tr></thead><tbody>' +
      rows.map(function (c) {
        return (
          "<tr><td><strong>" + esc(c.name) + "</strong></td>" +
          "<td>" + esc(c.slug) + "</td>" +
          '<td><span class="pill" style="background:' + esc(c.color) + ";color:#fff\">" + esc(c.color) + "</span></td>" +
          '<td class="admin-table__hide-sm">' + c.article_count + "</td>" +
          '<td class="admin-table__hide-sm">' + (c.in_nav ? "V navigaciji" : "Skrita") + "</td>" +
          '<td><div class="row-actions">' +
          '<button type="button" data-edit-cat="' + esc(c.slug) + '">Uredi</button>' +
          '<button type="button" class="danger" data-delete-cat="' + esc(c.slug) + '">Izbriši</button>' +
          "</div></td></tr>"
        );
      }).join("") +
      "</tbody></table>"
    );
  }

  function editCategory(slug) {
    const category = state.categories.find(function (c) { return c.slug === slug; });
    if (!category) return;
    state.editingCategory = slug;
    const form = $("[data-category-form]");
    form.elements.name.value = category.name;
    form.elements.slug.value = category.slug;
    form.elements.slug.readOnly = true;
    form.elements.color.value = category.color;
    form.elements.sort.value = category.sort;
    form.elements.description.value = category.description || "";
    form.querySelector("button[type=submit]").textContent = "Posodobi kategorijo";
    form.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  async function saveCategory(event) {
    event.preventDefault();
    const form = $("[data-category-form]");
    const payload = {
      name: form.elements.name.value.trim(),
      slug: form.elements.slug.value.trim(),
      color: form.elements.color.value,
      description: form.elements.description.value.trim(),
      sort: Number(form.elements.sort.value) || 0,
      in_nav: true,
    };
    try {
      if (state.editingCategory) {
        await api("/api/admin/categories/" + encodeURIComponent(state.editingCategory), { method: "PUT", body: payload });
        toast("Kategorija je posodobljena.");
      } else {
        await api("/api/admin/categories", { method: "POST", body: payload });
        toast("Kategorija je dodana.");
      }
      resetCategoryForm();
      await loadCategories();
      await loadDashboard();
    } catch (err) {
      toast(err.message, true);
    }
  }

  function resetCategoryForm() {
    state.editingCategory = null;
    const form = $("[data-category-form]");
    form.reset();
    form.elements.slug.readOnly = false;
    form.elements.color.value = "#e01b22";
    form.elements.sort.value = "99";
    form.querySelector("button[type=submit]").textContent = "Shrani kategorijo";
  }

  async function deleteCategory(slug) {
    if (!window.confirm("Izbrišete kategorijo " + slug + "?")) return;
    try {
      await api("/api/admin/categories/" + encodeURIComponent(slug), { method: "DELETE" });
      toast("Kategorija je izbrisana.");
      await loadCategories();
    } catch (err) {
      toast(err.message, true);
    }
  }

  // -------------------------------------------------------------------------
  // Settings
  // -------------------------------------------------------------------------

  async function loadSettings() {
    try {
      const data = await api("/api/admin/settings");
      const s = data.settings;
      $("#s-name").value = s.site_name || "";
      $("#s-tagline").value = s.site_tagline || "";
      $("#s-email").value = s.site_email || "";
      $("#s-city").value = s.site_city || "";
    } catch (err) {
      toast(err.message, true);
    }
  }

  async function saveSettings(event) {
    event.preventDefault();
    const payload = {
      site_name: $("#s-name").value.trim(),
      site_tagline: $("#s-tagline").value.trim(),
      site_email: $("#s-email").value.trim(),
      site_city: $("#s-city").value.trim(),
    };
    try {
      await api("/api/admin/settings", { method: "PUT", body: payload });
      applyBrand(payload.site_name);
      toast("Nastavitve so shranjene.");
    } catch (err) {
      toast(err.message, true);
    }
  }

  // -------------------------------------------------------------------------
  // Auth and events
  // -------------------------------------------------------------------------

  async function login(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const box = $("[data-login-error]");
    box.classList.remove("is-visible");
    try {
      const data = await api("/api/admin/login", {
        method: "POST",
        body: {
          email: form.elements.email.value.trim(),
          password: form.elements.password.value,
        },
      });
      state.user = data.user;
      showApp();
      await loadCategories();
      await loadDashboard();
      showView("dashboard");
    } catch (err) {
      box.textContent = err.message;
      box.classList.add("is-visible");
    }
  }

  async function logout() {
    try { await api("/api/admin/logout", { method: "POST" }); } catch (err) { /* ignore */ }
    state.user = null;
    showLogin();
  }

  function bindEvents() {
    $("[data-login-form]").addEventListener("submit", login);
    $("[data-logout]").addEventListener("click", logout);

    $$("[data-view]").forEach(function (link) {
      link.addEventListener("click", function () {
        const view = link.getAttribute("data-view");
        showView(view);
        if (view === "dashboard") loadDashboard();
        if (view === "articles") loadArticles();
        if (view === "categories") loadCategories();
        if (view === "settings") loadSettings();
      });
    });

    $$("[data-new-article]").forEach(function (button) {
      button.addEventListener("click", function () {
        const quick = state.view === "dashboard" ? $("[data-quick-category]") : null;
        openEditor(null, quick && quick.value ? quick.value : null);
      });
    });

    const quickNew = $("[data-quick-new]");
    if (quickNew) {
      quickNew.addEventListener("click", function () {
        const select = $("[data-quick-category]");
        openEditor(null, select && select.value ? select.value : null);
      });
    }

    $("[data-article-form]").addEventListener("submit", saveArticle);
    $("[data-category-form]").addEventListener("submit", saveCategory);
    $("[data-settings-form]").addEventListener("submit", saveSettings);

    $$("[data-close-editor]").forEach(function (button) {
      button.addEventListener("click", function () { showView("articles"); loadArticles(); });
    });

    $("[data-refresh-articles]").addEventListener("click", loadArticles);
    $("[data-article-search]").addEventListener("input", debounce(loadArticles, 300));
    $("[data-article-filter]").addEventListener("change", loadArticles);

    $("[data-delete-article]").addEventListener("click", function () {
      if (state.editingId) deleteArticle(state.editingId);
    });

    document.addEventListener("click", function (event) {
      const edit = event.target.closest("[data-edit]");
      if (edit) {
        const article = state.articles.find(function (a) { return String(a.id) === edit.getAttribute("data-edit"); });
        if (article) openEditor(article);
        return;
      }
      const del = event.target.closest("[data-delete]");
      if (del) {
        deleteArticle(Number(del.getAttribute("data-delete")));
        return;
      }
      const editCat = event.target.closest("[data-edit-cat]");
      if (editCat) {
        editCategory(editCat.getAttribute("data-edit-cat"));
        return;
      }
      const delCat = event.target.closest("[data-delete-cat]");
      if (delCat) {
        deleteCategory(delCat.getAttribute("data-delete-cat"));
      }
    });

    $("[data-category-form]").addEventListener("reset", function () {
      setTimeout(resetCategoryForm, 0);
    });
  }

  function debounce(fn, wait) {
    let timer;
    return function () {
      clearTimeout(timer);
      timer = setTimeout(fn, wait);
    };
  }

  function applyBrand(name) {
    if (!name) return;
    $$("[data-site-brand]").forEach(function (el) { el.textContent = name; });
  }

  async function boot() {
    bindEvents();
    try {
      const site = await api("/api/site");
      if (site && site.site) applyBrand(site.site.site_name);
    } catch (err) {
      /* brand falls back to the static markup */
    }
    try {
      const data = await api("/api/admin/me");
      if (data.user) {
        state.user = data.user;
        showApp();
        await loadCategories();
        await loadDashboard();
        showView("dashboard");
      } else {
        showLogin();
      }
    } catch (err) {
      showLogin();
    }
  }

  document.addEventListener("DOMContentLoaded", boot);
})();

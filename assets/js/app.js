/* Slovenec — shared helpers and page chrome. */
(function () {
  "use strict";

  const DAY = 86400000;

  const Portal = {
    site: null,
    categories: [],

    async api(path, options) {
      const opts = Object.assign({ credentials: "same-origin" }, options || {});
      if (opts.body && typeof opts.body !== "string") {
        opts.body = JSON.stringify(opts.body);
        opts.headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
      }
      const res = await fetch(path, opts);
      let data = null;
      try {
        data = await res.json();
      } catch (err) {
        data = null;
      }
      if (!res.ok) {
        const message = (data && data.detail) || "Prišlo je do napake.";
        const error = new Error(typeof message === "string" ? message : "Prišlo je do napake.");
        error.status = res.status;
        throw error;
      }
      return data;
    },

    escape(value) {
      return String(value == null ? "" : value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    },

    attr(value) {
      return Portal.escape(value);
    },

    initials(name) {
      return String(name || "")
        .trim()
        .split(/\s+/)
        .slice(0, 2)
        .map(function (part) {
          return part.charAt(0).toUpperCase();
        })
        .join("");
    },

    date(iso) {
      if (!iso) return "";
      const d = new Date(iso);
      if (Number.isNaN(d.getTime())) return "";
      return new Intl.DateTimeFormat("sl-SI", {
        day: "numeric",
        month: "long",
        year: "numeric",
      }).format(d);
    },

    time(iso) {
      if (!iso) return "";
      const d = new Date(iso);
      if (Number.isNaN(d.getTime())) return "";
      return new Intl.DateTimeFormat("sl-SI", {
        hour: "2-digit",
        minute: "2-digit",
      }).format(d);
    },

    dateTime(iso) {
      const d = Portal.date(iso);
      const t = Portal.time(iso);
      return d && t ? d + " ob " + t : d || t;
    },

    ago(iso) {
      if (!iso) return "";
      const then = new Date(iso).getTime();
      if (Number.isNaN(then)) return "";
      const diff = Date.now() - then;
      if (diff < 0) return Portal.dateTime(iso);
      if (diff < 3600000) {
        const min = Math.max(1, Math.round(diff / 60000));
        return "pred " + min + " min";
      }
      if (diff < DAY) {
        return "pred " + Math.round(diff / 3600000) + " h";
      }
      if (diff < 2 * DAY) return "včeraj";
      return Portal.date(iso);
    },

    image(article) {
      return article && article.image_url
        ? article.image_url
        : "/assets/img/covers/cover-1.svg";
    },

    card(article, options) {
      const o = options || {};
      const classes = ["card"];
      if (o.size === "sm") classes.push("card--sm");
      if (o.row) classes.push("card--row");
      const title = '<h3 class="card__title"><a href="' + Portal.attr(article.url) + '">' + Portal.escape(article.title) + "</a></h3>";
      return (
        '<article class="' + classes.join(" ") + '">' +
        '<a class="card__media" href="' + Portal.attr(article.url) + '" aria-hidden="true" tabindex="-1">' +
        '<img src="' + Portal.attr(Portal.image(article)) + '" alt="" loading="lazy" width="640" height="400">' +
        (article.category_name
          ? '<span class="card__cat" style="background:' + Portal.attr(article.category_color || "#e01b22") + '">' + Portal.escape(article.category_name) + "</span>"
          : "") +
        "</a>" +
        '<div class="card__body">' +
        title +
        (o.deck && article.deck ? '<p class="card__deck">' + Portal.escape(article.deck) + "</p>" : "") +
        '<div class="card__meta">' +
        (article.is_live ? '<span class="badge badge--live">V živo</span>' : "") +
        "<span>" + Portal.escape(Portal.ago(article.published_at)) + "</span>" +
        (article.reading_minutes ? "<span>" + article.reading_minutes + " min branja</span>" : "") +
        "</div>" +
        "</div>" +
        "</article>"
      );
    },

    renderNav() {
      const nav = document.querySelector("[data-nav]");
      if (!nav) return;
      const path = window.location.pathname;
      const links = Portal.categories
        .filter(function (c) { return c.in_nav; })
        .map(function (c) {
          const active = path === "/rubrika/" + c.slug;
          return (
            '<a class="nav__link' + (active ? " is-active" : "") + '" href="/rubrika/' +
            Portal.attr(c.slug) + '">' + Portal.escape(c.name) + "</a>"
          );
        })
        .join("");
      nav.innerHTML =
        links +
        '<a class="nav__link' + (path === "/live" ? " is-active" : "") + '" href="/live">V živo</a>' +
        '<a class="nav__more" href="/admin" title="Uredniški sistem">Uredništvo</a>';
    },

    renderFooter() {
      const target = document.querySelector("[data-footer-links]");
      if (target) {
        target.innerHTML = Portal.categories
          .filter(function (c) { return c.in_nav; })
          .slice(0, 8)
          .map(function (c) {
            return '<li><a href="/rubrika/' + Portal.attr(c.slug) + '">' + Portal.escape(c.name) + "</a></li>";
          })
          .join("");
      }
      const year = document.querySelector("[data-year]");
      if (year) year.textContent = new Date().getFullYear();
      const site = document.querySelector("[data-site-name]");
      if (site && Portal.site) site.textContent = Portal.site.site_name;
      const tagline = document.querySelector("[data-site-tagline]");
      if (tagline && Portal.site) tagline.textContent = Portal.site.site_tagline;
      document.querySelectorAll("[data-site-brand]").forEach(function (el) {
        if (Portal.site && Portal.site.site_name) el.textContent = Portal.site.site_name;
      });
    },

    renderTicker(items) {
      const track = document.querySelector("[data-ticker]");
      if (!track || !items || !items.length) {
        const ticker = document.querySelector(".ticker");
        if (ticker) ticker.hidden = true;
        return;
      }
      track.innerHTML = items
        .map(function (a) {
          return '<a class="ticker__item" href="' + Portal.attr(a.url) + '">' + Portal.escape(a.title) + "</a>";
        })
        .join("");
    },

    setActiveDate() {
      const el = document.querySelector("[data-today]");
      if (!el) return;
      el.textContent = new Intl.DateTimeFormat("sl-SI", {
        weekday: "long",
        day: "numeric",
        month: "long",
        year: "numeric",
      }).format(new Date());
    },

    setupSearch() {
      document.querySelectorAll("[data-search-form]").forEach(function (form) {
        form.addEventListener("submit", function (event) {
          event.preventDefault();
          const input = form.querySelector("input[name=q]");
          const q = (input && input.value.trim()) || "";
          window.location.href = "/iskanje" + (q ? "?q=" + encodeURIComponent(q) : "");
        });
      });
    },

    toast(message, isError) {
      let el = document.querySelector(".toast");
      if (!el) {
        el = document.createElement("div");
        el.className = "toast";
        document.body.appendChild(el);
      }
      el.textContent = message;
      el.classList.toggle("toast--error", !!isError);
      el.classList.add("is-visible");
      clearTimeout(Portal._toastTimer);
      Portal._toastTimer = setTimeout(function () {
        el.classList.remove("is-visible");
      }, 2800);
    },

    async initChrome() {
      Portal.setActiveDate();
      Portal.setupSearch();
      try {
        const data = await Portal.api("/api/site");
        Portal.site = data.site;
        Portal.categories = data.categories || [];
      } catch (err) {
        Portal.site = { site_name: "Slovenec", site_tagline: "Slovenske novice, brez šuma" };
        Portal.categories = [];
      }
      Portal.renderNav();
      Portal.renderFooter();
      document.querySelectorAll("[data-site-email]").forEach(function (el) {
        if (Portal.site) el.textContent = Portal.site.site_email || "";
      });
      document.querySelectorAll("[data-site-city]").forEach(function (el) {
        if (Portal.site) el.textContent = Portal.site.site_city || "";
      });
    },
  };

  window.Portal = Portal;
  Portal.ready = new Promise(function (resolve) {
    document.addEventListener("DOMContentLoaded", function () {
      Portal.initChrome().finally(resolve);
    });
  });
})();

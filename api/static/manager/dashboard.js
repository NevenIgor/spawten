/* Dashboard: periodically pulls newly created lead cards from /manager/api/new-cards/
   and prepends them to the wall, so cards appear as users contact the bot. */
(function () {
  "use strict";

  var wall = document.getElementById("cards");
  if (!wall) return; // not the dashboard page

  var banner = document.getElementById("new-cards-banner");
  var i18nEl = document.getElementById("mgr-i18n");
  var T = {};
  try { T = JSON.parse((i18nEl && i18nEl.textContent) || "{}"); } catch (e) { /* noop */ }

  function lastCreated() {
    var cards = wall.querySelectorAll(".card[data-created]");
    var max = "";
    for (var i = 0; i < cards.length; i++) {
      var v = cards[i].getAttribute("data-created") || "";
      if (v > max) max = v;
    }
    return max;
  }

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function cardNode(c) {
    var a = document.createElement("a");
    a.className = "card card-" + c.color;
    a.href = "/manager/lead/" + c.id + "/";
    a.setAttribute("data-id", c.id);
    a.setAttribute("data-created", c.created);
    var nf = T["mgr.not_filled"] || "—";
    a.innerHTML =
      '<div class="card-top"><span class="badge badge-' + c.color + '">' + esc(c.status_label) + "</span>" +
      '<span class="created">' + esc(T["mgr.card_created"] || "Created") + ": " + esc(c.created) + "</span></div>" +
      '<h3 class="rel-name">' + esc(c.relative_full_name || nf) + "</h3>" +
      '<ul class="facts">' +
      "<li><b>" + esc(T["lead.relative_birth_date"] || "Birth date") + ":</b> " + esc(c.relative_birth_date || nf) + "</li>" +
      "<li><b>" + esc(T["lead.relative_workplace"] || "Workplace") + ":</b> " + esc(c.relative_workplace || nf) + "</li>" +
      "<li><b>" + esc(T["lead.relative_location"] || "Location") + ":</b> " + esc(c.relative_location || nf) + "</li>" +
      "<li><b>" + esc(T["mgr.card_user"] || "User") + ":</b> " + esc(c.full_name || nf) + "</li>" +
      "<li><b>" + esc(T["mgr.card_phone"] || "Phone") + ":</b> " + esc(c.contact_phone || nf) + "</li>" +
      "<li><b>TG:</b> " + esc(c.tg_username || c.tg_id || (T["mgr.tg_none"] || "")) +
      (c.tg_phone ? "<br><b>" + esc(T["tgsnapshot.phone_number"] || "Phone") + ":</b> " + esc(c.tg_phone) : "") +
      "</li></ul>";
    return a;
  }

  var seen = new Set();
  wall.querySelectorAll(".card[data-id]").forEach(function (el) { seen.add(el.getAttribute("data-id")); });

  function poll() {
    var after = lastCreated();
    var url = "/manager/api/new-cards/" + (after ? "?after=" + encodeURIComponent(after) : "");
    fetch(url, { headers: { "X-Requested-With": "fetch" } })
      .then(function (r) { return r.ok ? r.json() : { cards: [] }; })
      .then(function (data) {
        var fresh = (data.cards || []).filter(function (c) { return !seen.has(String(c.id)); });
        if (!fresh.length) { return; }
        var empty = wall.querySelector(".empty");
        if (empty) { empty.remove(); }
        fresh.forEach(function (c) {
          seen.add(String(c.id));
          wall.insertBefore(cardNode(c), wall.firstChild);
        });
        if (banner) {
          banner.classList.remove("hidden");
          banner.innerHTML = (T["mgr.new_cards"] || "New cards") + ": " + fresh.length;
          setTimeout(function () { banner.classList.add("hidden"); }, 6000);
        }
      })
      .catch(function () { /* ignore transient errors */ });
  }

  setInterval(poll, 5000);
})();

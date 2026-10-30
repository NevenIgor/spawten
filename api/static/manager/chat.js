/* Live chat frame on the lead detail page.
   - renders server-provided history from <script id="chat-history">
   - opens a WebSocket /ws/manager/chat/<tg_id>/ for real-time messages
   - sends manager messages as JSON {type:"message", text:"..."} */
(function () {
  "use strict";

  var frame = document.getElementById("chat-frame");
  if (!frame) return;

  var tgId = frame.getAttribute("data-tg-id") || "";
  var log = document.getElementById("chat-log");
  var statusEl = document.getElementById("chat-status");
  var form = document.getElementById("chat-form");
  var input = document.getElementById("chat-input");

  var i18nEl = document.getElementById("mgr-i18n");
  var T = {};
  try { T = JSON.parse((i18nEl && i18nEl.textContent) || "{}"); } catch (e) { /* noop */ }

  function setStatus(text, cls) {
    if (!statusEl) return;
    statusEl.textContent = text || "";
    statusEl.className = "chat-status" + (cls ? " " + cls : "");
  }

  function addMessage(m) {
    var div = document.createElement("div");
    div.className = "msg " + (m.direction === "outgoing" ? "outgoing" : "incoming");
    var who = m.direction === "outgoing"
      ? ((T["mgr.you"] || "You") + (m.sent_by ? " (" + m.sent_by + ")" : ""))
      : (T["mgr.user"] || "User");
    var body = m.text || "";
    if (m.attachment_url) {
      body += ' <a href="' + m.attachment_url + '" target="_blank" rel="noopener">' +
              (T["mgr.attachment"] || "attachment") + "</a>";
    }
    div.innerHTML = "<span>" + escapeHtml(body).replace(/\n/g, "<br>") + "</span>" +
                    '<span class="meta">' + escapeHtml(who) + " · " + escapeHtml(m.time || "") + "</span>";
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }

  function escapeHtml(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  // --- history ---
  var histEl = document.getElementById("chat-history");
  var lastTs = "";
  try {
    var history = JSON.parse((histEl && histEl.textContent) || "[]");
    history.forEach(addMessage);
    if (history.length === 0 && log) {
      log.innerHTML = '<div class="empty" style="padding:12px">' + escapeHtml(T["mgr.chat_empty"] || "") + "</div>";
    }
  } catch (e) { /* noop */ }

  if (!tgId || tgId === "None" || tgId === "null") {
    setStatus("tg_id —", "off");
    return;
  }

  // --- websocket ---
  var ws = null;
  var reconnectDelay = 1000;

  function connect() {
    var proto = location.protocol === "https:" ? "wss://" : "ws://";
    var path = window.MGR_CHAT_WS_PATH || "/ws/manager/chat/";
    ws = new WebSocket(proto + location.host + path + tgId + "/");

    ws.onopen = function () {
      setStatus(T["mgr.chat_connected"] || "connected", "ok");
      reconnectDelay = 1000;
    };
    ws.onmessage = function (ev) {
      try {
        var m = JSON.parse(ev.data);
        if (m.type === "message") { addMessage(m); }
      } catch (e) { /* ignore malformed frames */ }
    };
    ws.onclose = function () {
      setStatus(T["mgr.chat_disconnected"] || "reconnecting…", "off");
      setTimeout(connect, reconnectDelay);
      reconnectDelay = Math.min(reconnectDelay * 2, 15000);
    };
    ws.onerror = function () { try { ws.close(); } catch (e) { /* noop */ } };
  }

  connect();

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var text = (input.value || "").trim();
    if (!text || !ws || ws.readyState !== 1) { return; }
    ws.send(JSON.stringify({ type: "message", text: text }));
    input.value = "";
  });

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.dispatchEvent(new Event("submit"));
    }
  });
})();

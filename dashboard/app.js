/* POLARIS console client.
   Direction: DESIGN.md. Filter: antislop (states R-27, keyboard R-32, no em dash R-02). */
'use strict';

const $ = (id) => document.getElementById(id);
const MAX_EVENTS = 150;
const RECONNECT_MS = 1500;
const SLOW_MS = 6000;          // setelah ini tanpa snapshot -> tampilkan error state

/* Kesalahan antarmuka tidak boleh hilang diam-diam: tampilkan sebagai error state. */
window.addEventListener('error', (e) => showBanner(`Kesalahan antarmuka: ${e.message || 'tidak diketahui'}`));
window.addEventListener('unhandledrejection', (e) =>
  showBanner(`Permintaan gagal: ${(e.reason && e.reason.message) || e.reason || 'tidak diketahui'}`));

const TYPE_LABEL = {
  decoy_connection: 'Koneksi ke port umpan',
  web_decoy_hit: 'Akses path umpan',
  decoy_login_attempt: 'Submit ke login palsu',
  honeytoken_file_access: 'Honeytoken file dibaca',
  canary_cred_used: 'Canary credential dipakai',
  honeytoken_url_fetch: 'Honeytoken URL diambil',
  decoy_ot_touch: 'Port OT/ICS disentuh',
};
const SEV_RANK = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
const sevClass = (s) => (SEV_RANK[s] ? String(s).toLowerCase() : 'low');
const reduceMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => (
  { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
/* Defensif: kolom JSON bisa tiba sebagai string pada rilis yang lebih tua.
   Lebih baik menampilkan sebagian daripada mengosongkan panel (C-4 resilience). */
const asList = (v) => {
  if (Array.isArray(v)) return v;
  if (typeof v === 'string') { try { const p = JSON.parse(v); return Array.isArray(p) ? p : []; } catch { return []; } }
  return [];
};
const clockOf = (ts) => {
  const t = String(ts || '');
  const i = t.indexOf(' ');
  const hhmmss = i >= 0 ? t.slice(i + 1, i + 9) : t.slice(11, 19);
  return hhmmss || '--:--:--';
};
const counts = (n, word) => `${n} ${word}`;

let events = [];
let incidents = new Map();
let ws = null;
let gotSnapshot = false;
let attempts = 0;
let lastTrigger = null;

/* ------------------------------------------------------------------ connection */
function setConn(state, text) {
  const el = $('conn');
  el.dataset.state = state;
  $('conn-text').textContent = text;
}

function showBanner(msg) {
  const b = $('banner');
  b.textContent = msg;
  b.hidden = false;
}

function hideBanner() { $('banner').hidden = true; }

function connect() {
  setConn('connecting', 'menghubungkan');
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/api/ws`);

  ws.onopen = () => { attempts = 0; setConn('live', 'live'); hideBanner(); };
  ws.onmessage = (m) => {
    let msg;
    try { msg = JSON.parse(m.data); } catch { return; }
    if (msg.type === 'snapshot') { gotSnapshot = true; applySnapshot(msg.data); }
    else if (msg.type === 'event') pushEvent(msg.data, true);
    else if (msg.type === 'incident') upsertIncident(msg.data);
  };
  ws.onclose = () => {
    attempts += 1;
    setConn('down', 'terputus, mencoba ulang');
    if (attempts >= 3) failStates('Koneksi ke collector terputus. Papan tidak menerima data baru.');
    setTimeout(connect, Math.min(RECONNECT_MS * attempts, 8000));
  };
  ws.onerror = () => ws.close();
}

function failStates(msg) {
  showBanner(msg);
  if (!gotSnapshot) {
    $('feed').innerHTML = `<li class="state error">Tidak dapat memuat feed: ${esc(msg)}</li>`;
    $('incidents').innerHTML = `<p class="state error">Tidak dapat memuat incident: ${esc(msg)}</p>`;
  }
}

/* ------------------------------------------------------------------ snapshot */
function applySnapshot(s) {
  const st = s.stats || {};
  set('stat-events', st.events);
  set('stat-incidents', st.incidents);
  set('stat-attackers', st.distinct_attackers);
  set('stat-fp', st.false_positives);
  set('stat-suppressed', st.suppressed_events);

  incidents = new Map((s.incidents || []).map((i) => [i.id, i]));
  events = (s.events || []).slice().reverse();
  renderIncidents();
  renderEvents();
  renderAttackers();
  hideBanner();
  openFromHash();
}

const set = (id, v) => { $(id).textContent = v ?? 0; };

/* ------------------------------------------------------------------ feed */
function eventItem(ev, fresh) {
  const chip = ev.tier === 1
    ? '<span class="chip chip-t1">T1</span>'
    : (ev.event_type === 'decoy_ot_touch'
      ? '<span class="chip chip-ot">OT/ICS</span>'
      : '<span class="chip chip-t2">T2</span>');
  const label = TYPE_LABEL[ev.event_type] || ev.event_type;
  const target = ev.http_path || (ev.file_path ? ev.file_path.split('/').pop() : '');
  const bits = [ev.decoy || ev.service || '', target, ev.dst_port ? `port ${ev.dst_port}` : '']
    .filter(Boolean).join(' · ');
  const ref = ev.incident_id && !ev.suppressed
    ? ` <span class="inc-ref">inc#${esc(ev.incident_id)}</span>` : '';
  return `<li class="ev ${fresh ? 'fresh' : ''}">
    <span class="idx">${esc(String(ev.id ?? '').padStart(4, '0'))}</span>
    <time datetime="${esc(ev.ts)}">${esc(clockOf(ev.ts))}</time>
    <div class="body">
      <div class="head">${chip}<span class="label">${esc(label)}</span>
        <span class="ip">${esc(ev.src_ip || 'tidak diketahui')}</span>${ref}</div>
      <div class="detail">${esc(bits)}</div>
    </div></li>`;
}

function renderEvents() {
  const feed = $('feed');
  if (!events.length) {
    feed.innerHTML = '<li class="state">Menunggu interaksi pertama dengan umpan…</li>';
    return;
  }
  feed.innerHTML = events.slice(-MAX_EVENTS).reverse().map((e) => eventItem(e, false)).join('');
  set('ev-count', events.length);
}

function pushEvent(ev, fresh) {
  if (!events.some((e) => e.id === ev.id)) events.push(ev);
  if (events.length > MAX_EVENTS) events = events.slice(-MAX_EVENTS);

  const feed = $('feed');
  if (feed.querySelector('.state')) feed.innerHTML = '';
  feed.insertAdjacentHTML('afterbegin', eventItem(ev, fresh && !reduceMotion()));
  if (fresh && !reduceMotion()) {
    const first = feed.firstElementChild;
    setTimeout(() => first && first.classList.remove('fresh'), 1400);
  }
  while (feed.children.length > MAX_EVENTS) feed.removeChild(feed.lastChild);

  set('ev-count', events.length);
  renderAttackers();
}

/* ------------------------------------------------------------------ incidents */
function incidentCard(i) {
  const tags = asList(i.mitre).slice(0, 6)
    .map((t) => `<span class="tag" title="${esc(t.name)} (${esc(t.tactic)})">${esc(t.id)}</span>`).join('');
  const pct = i.tool_conf ? ` (${Math.round(i.tool_conf * 100)}%)` : '';
  return `<button type="button" class="inc sev-${sevClass(i.severity)}" data-id="${i.id}"
      aria-label="Buka detail incident ${i.id}, ${esc(i.severity)}, skor ${esc(i.score)}, ${esc(i.title)}">
    <span class="row">
      <span class="score">${esc(i.score)}<small>skor</small></span>
      <span>
        <span class="title">${esc(i.title || 'Incident')}</span>
        <span class="meta">
          <span>inc#${i.id}</span>
          <code>${esc(i.src_ip)}</code>
          <span>${counts(i.event_count, 'event')}</span>
          <span>tool: ${esc(i.tool_guess || 'belum pasti')}${esc(pct)}</span>
        </span>
        <span class="tags">${tags}</span>
      </span>
      <span class="sev ${sevClass(i.severity)}">${esc(i.severity)}</span>
    </span>
  </button>`;
}

function renderIncidents(focusId) {
  const box = $('incidents');
  const list = [...incidents.values()].sort((a, b) =>
    (SEV_RANK[b.severity] - SEV_RANK[a.severity]) || (b.updated_ts < a.updated_ts ? -1 : 1));
  if (!list.length) {
    box.innerHTML = '<p class="state">Belum ada incident. Sistem bersih, nol alert.</p>';
  } else {
    box.innerHTML = list.map(incidentCard).join('');
  }
  set('inc-count', list.length);
  box.querySelectorAll('.inc').forEach((el) => {
    el.addEventListener('click', () => openIncident(el.dataset.id, el));
  });
  if (focusId) {
    const again = box.querySelector(`.inc[data-id="${focusId}"]`);
    if (again) again.focus();
  }
}

function upsertIncident(i) {
  const prev = incidents.get(i.id);
  incidents.set(i.id, i);
  renderIncidents();
  set('stat-incidents', incidents.size);

  if (!prev || SEV_RANK[i.severity] > SEV_RANK[prev.severity]) {
    $('live-region').textContent =
      `Incident baru ${i.severity} dari ${i.src_ip}, ${i.event_count} event. ${i.title}`;
  }
}

/* ------------------------------------------------------------------ attackers */
function renderAttackers() {
  const byIp = new Map();
  for (const e of events) {
    const ip = e.src_ip || 'tidak diketahui';
    const a = byIp.get(ip) || { ip, n: 0, types: new Set(), ports: new Set() };
    a.n += 1;
    a.types.add(e.event_type);
    if (e.dst_port) a.ports.add(e.dst_port);
    byIp.set(ip, a);
  }
  const list = [...byIp.values()].sort((x, y) => y.n - x.n).slice(0, 6);
  const box = $('attackers');
  if (!list.length) {
    box.innerHTML = '<li class="state">Belum ada penyerang terdeteksi.</li>';
    set('atk-count', 0);
    return;
  }
  box.innerHTML = list.map((a) => {
    const inc = [...incidents.values()].filter((i) => i.src_ip === a.ip)
      .sort((x, y) => SEV_RANK[y.severity] - SEV_RANK[x.severity])[0];
    return `<li>
      <div class="atk-head">
        <span class="ip">${esc(a.ip)}</span>
        ${inc ? `<span class="sev ${sevClass(inc.severity)}">${esc(inc.severity)}</span>` : ''}
        ${inc ? `<span class="inc-ref" style="color:var(--muted);font-size:11px">${esc(inc.tool_guess || '')}</span>` : ''}
      </div>
      <dl class="spec">
        <dt>Interaksi umpan</dt><dd class="hi">${esc(a.n)}</dd>
        <dt>Port umpan disentuh</dt><dd>${esc(a.ports.size)}</dd>
        <dt>Jenis umpan</dt><dd>${esc(a.types.size)}</dd>
        <dt>Incident</dt><dd>${esc(inc ? '#' + inc.id : 'belum dikorelasi')}</dd>
      </dl>
      <div class="atk-sep"></div>
    </li>`;
  }).join('');
  set('atk-count', list.length);
}

/* ------------------------------------------------------------------ modal */
function trapTab(e) {
  const box = $('m-box');
  const focusables = box.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
  if (!focusables.length) return;
  const first = focusables[0];
  const last = focusables[focusables.length - 1];
  if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
  else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
}

async function openIncident(id, triggerEl) {
  if (!id) return;
  lastTrigger = triggerEl || null;
  if (location.hash !== `#incident-${id}`) {
    history.replaceState(null, '', `#incident-${id}`);   // deep link, bisa dibagikan ke analis lain
  }
  $('modal-body').innerHTML = '<p class="state">Memuat detail incident…</p>';
  $('modal').hidden = false;
  $('modal-close').focus();

  let i;
  try {
    const r = await fetch(`/api/incidents/${id}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    i = await r.json();
  } catch (err) {
    $('modal-body').innerHTML =
      `<p class="state error">Gagal memuat incident #${esc(id)}: ${esc(err.message)}.
       Tutup dialog lalu pilih incident lain.</p>`;
    return;
  }

  const allEvents = asList(i.events);
  const shown = allEvents.slice(-30);
  const byTactic = new Map();
  for (const t of asList(i.mitre)) {
    const k = t.tactic || 'lain-lain';
    if (!byTactic.has(k)) byTactic.set(k, []);
    byTactic.get(k).push(t);
  }
  const mitre = [...byTactic.entries()].map(([tactic, list]) =>
    `<div class="mitre-row">
      <span class="tactic">${esc(tactic)}</span>
      <span class="tags">${list.map((t) => `<span class="tag">${esc(t.id)} · ${esc(t.name)}</span>`).join('')}</span>
    </div>`).join('');
  const timeline = shown.map((e) => {
    const target = e.http_path || (e.file_path ? e.file_path.split('/').pop() : '');
    return `<li><span class="when">${esc(clockOf(e.ts))} · #${e.id} · ${esc(e.event_type)}</span>
      <div>${esc([e.decoy, target, e.dst_port ? `port ${e.dst_port}` : ''].filter(Boolean).join(' · '))}</div></li>`;
  }).join('');
  const evidence = asList(i.evidence).slice(-12).map((e) =>
    `<tr><td><code>${esc(clockOf(e.ts))}</code></td><td>${esc(e.event)}</td>
     <td>${esc(e.decoy || '')}</td><td>${esc(e.dst_port || e.path || '')}</td>
     <td><code>${e.sha256 ? esc(e.sha256.slice(0, 16)) + '…' : 'tidak ada'}</code></td></tr>`).join('');

  $('modal-body').innerHTML = `
    <h3 class="m-title" id="m-title">${esc(i.title)}</h3>
    <p class="m-sub">inc#${i.id} · sumber <code>${esc(i.src_ip)}</code> ·
      ${esc(i.first_ts)} sampai ${esc(i.last_ts)}<br>
      tool terduga <strong>${esc(i.tool_guess || 'belum pasti')}</strong>${i.tool_conf ? ` (${Math.round(i.tool_conf * 100)}% keyakinan)` : ''}</p>

    <dl class="spec">
      <dt>Severity</dt><dd>${esc(i.severity)}</dd>
      <dt>Skor</dt><dd class="hi">${esc(i.score)}</dd>
      <dt>Event ter-korelasi</dt><dd>${esc(i.event_count)}</dd>
      <dt>Tool terduga</dt><dd>${esc(i.tool_guess || 'belum pasti')}${i.tool_conf ? ` (${Math.round(i.tool_conf * 100)}%)` : ''}</dd>
      <dt>False positive</dt><dd class="hi">0</dd>
    </dl>

    <h4 class="m-h">Ringkasan otomatis</h4>
    <p class="m-sum">${esc(i.summary)}</p>

    <h4 class="m-h">Pemetaan MITRE ATT&CK</h4>
    <div class="mitre">${mitre || '<span class="tactic">belum ada teknik terpetakan</span>'}</div>

    <h4 class="m-h">Timeline${allEvents.length > shown.length ? ` (30 terakhir dari ${allEvents.length} event)` : ''}</h4>
    <ol class="tl">${timeline || '<li>tidak ada event</li>'}</ol>

    <h4 class="m-h">Evidence siap forensik</h4>
    <div class="table-wrap">
      <table>
        <caption>12 event terakhir pada incident ini, terurut waktu</caption>
        <thead><tr><th scope="col">Waktu</th><th scope="col">Event</th><th scope="col">Decoy</th>
        <th scope="col">Target</th><th scope="col">Hash bukti</th></tr></thead>
        <tbody>${evidence || '<tr><td colspan="5">tidak ada evidence</td></tr>'}</tbody>
      </table>
    </div>`;
}

function closeModal() {
  $('modal').hidden = true;
  $('modal-body').innerHTML = '';
  if (location.hash) history.replaceState(null, '', location.pathname + location.search);
  if (lastTrigger && document.contains(lastTrigger)) lastTrigger.focus();
  lastTrigger = null;
}

/* Deep link: #incident-<id> membuka detail langsung (berguna saat serah terima shift). */
function openFromHash() {
  const m = /^#incident-(\d+)$/.exec(location.hash);
  if (m && incidents.has(Number(m[1]))) openIncident(m[1], null);
}
window.addEventListener('hashchange', openFromHash);

$('modal-close').addEventListener('click', closeModal);
$('modal').addEventListener('click', (e) => { if (e.target === $('modal')) closeModal(); });
document.addEventListener('keydown', (e) => {
  if ($('modal').hidden) return;
  if (e.key === 'Escape') closeModal();
  else if (e.key === 'Tab') trapTab(e);
});

/* ------------------------------------------------------------------ boot */
setTimeout(() => { if (!gotSnapshot) failStates('Belum menerima data dari collector. Periksa apakah collector berjalan.'); }, SLOW_MS);
connect();

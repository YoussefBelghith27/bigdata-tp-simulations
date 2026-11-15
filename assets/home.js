(function () {
  const C = window.CATALOG;
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const ready = C.tps.filter(t => !t.soon);

  /* ---------- Carte des TP (cluster animé) ---------- */
  (function topo() {
    const svg = document.getElementById("topo"); if (!svg) return;
    const tip = document.getElementById("topo-tip");
    const NS = "http://www.w3.org/2000/svg";
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const el = (tag, attrs = {}, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
    const byId = Object.fromEntries(C.tps.map(t => [t.id, t]));
    // couleur par technologie : [haut, corps, bas]
    const TECH = { mongo: ["#4fbf86", "#13aa52", "#0b7a53"], cass: ["#5cc3e6", "#1287b1", "#0b5f7e"],
                   hadoop: ["#ffd75a", "#e6b000", "#a67e00"], spark: ["#ff9a63", "#e25a1c", "#a63d0e"] };
    const N = {
      "tp1-installation":         { p: [104, 112], t: "mongo",  s: "Installation" },
      "tp2-resto":                { p: [280, 96],  t: "mongo",  s: "Requêtes find()" },
      "tp3-replication-sharding": { p: [150, 222], t: "mongo",  s: "Réplication, sharding" },
      "tp4-cassandra":            { p: [580, 120], t: "cass",   s: "Anneau Cassandra" },
      "tp5-hadoop":               { p: [330, 352], t: "hadoop", s: "HDFS, MapReduce, Hive" },
      "tp6-spark":                { p: [580, 352], t: "spark",  s: "Spark sur YARN" },
    };
    const L = [["tp1-installation", "tp2-resto"], ["tp1-installation", "tp3-replication-sharding"],
               ["tp2-resto", "tp4-cassandra"], ["tp3-replication-sharding", "tp5-hadoop"], ["tp5-hadoop", "tp6-spark"],
               ["tp4-cassandra", "tp6-spark"], ["tp3-replication-sharding", "tp2-resto"]];
    // zones (comme le nuage Frame Relay du site WAN)
    const Z = [
      { x: 24, y: 24, w: 390, h: 268, fill: "#eaf7f0", stroke: "#8fd1ae", c: "#0b7a53", label: "MongoDB · document" },
      { x: 466, y: 24, w: 230, h: 200, fill: "#e8f5fb", stroke: "#8cc9e0", c: "#0b5f7e", label: "Cassandra · colonnes" },
      { x: 236, y: 296, w: 460, h: 134, fill: "#fff7e0", stroke: "#e8c96a", c: "#8a6a00", label: "Hadoop · Spark" },
    ];
    Z.forEach(z => {
      el("rect", { x: z.x, y: z.y, width: z.w, height: z.h, rx: 12, fill: z.fill, stroke: z.stroke, class: "zone" }, svg);
      el("text", { x: z.x + 14, y: z.y + 20, class: "zone-label", fill: z.c }, svg).textContent = z.label;
    });
    const links = el("g", {}, svg), dots = el("g", {}, svg), packets = el("g", {}, svg), nodes = el("g", {}, svg);
    L.forEach(([a, b], i) => {
      if (!N[a] || !N[b]) return;
      const [x1, y1] = N[a].p, [x2, y2] = N[b].p;
      const dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy), ux = dx / len, uy = dy / len;
      const mx = (x1 + x2) / 2 - uy * 18, my = (y1 + y2) / 2 + ux * 18;   // légère courbe
      const path = el("path", { d: `M${x1},${y1} Q${mx.toFixed(1)},${my.toFixed(1)} ${x2},${y2}`, id: "lk" + i, class: "link" + (reduce ? "" : " draw"), pathLength: 1 }, links);
      path.style.animationDelay = (0.15 + i * 0.09) + "s";
      [[x1 + ux * 40, y1 + uy * 40], [x2 - ux * 40, y2 - uy * 40]].forEach(([cx, cy]) => {
        const c = el("circle", { cx, cy, r: 3.6, class: "portdot" }, dots);
        c.style.animationDelay = (1.3 + i * 0.05) + "s"; if (reduce) c.style.opacity = 1;
      });
      if (!reduce) [0, 1].forEach(k => {
        const begin = (2 + i * 0.37 + k * 1.8) + "s";
        const pk = el("circle", { r: 3.4, class: "packet", cx: 0, cy: 0, visibility: "hidden" }, packets);
        el("set", { attributeName: "visibility", to: "visible", begin }, pk);
        const am = el("animateMotion", { dur: (3.2 + (i % 4) * 0.7) + "s", repeatCount: "indefinite",
          begin, keyPoints: k ? "1;0" : "0;1", keyTimes: "0;1", calcMode: "linear" }, pk);
        el("mpath", { href: "#lk" + i }, am);
      });
    });
    Object.entries(N).forEach(([id, n], i) => {
      const t = byId[id]; if (!t) return;
      const [x, y] = n.p, [top, body, bot] = TECH[n.t];
      const href = t.soon ? "#" + id : `simulation.html?tp=${id}`;
      const a = el("a", { href, class: "node", "aria-label": `${t.num} : ${t.title}` }, nodes);
      a.style.animationDelay = (0.5 + i * 0.1) + "s"; if (reduce) a.style.opacity = 1;
      const g = el("g", { transform: `translate(${x},${y})` }, a);
      el("circle", { r: 46, fill: body, class: "halo" }, g);
      const b = el("g", { class: "body" }, el("g", { transform: "scale(1.22)" }, g));
      if (n.t === "cass") el("circle", { r: 38, class: "ring" }, b);
      // cylindre (base de données)
      el("path", { d: "M-26,-14 v30 c0,7 12,12 26,12 s26,-5 26,-12 v-30z", fill: body }, b);
      el("path", { d: "M-26,1 c0,7 12,12 26,12 s26,-5 26,-12", stroke: bot, "stroke-width": 2, fill: "none" }, b);
      el("ellipse", { cx: 0, cy: -14, rx: 26, ry: 10, fill: top }, b);
      el("text", { x: 0, y: 12, class: "tag" }, b).textContent = t.num;
      el("text", { x: 0, y: 52 }, g).textContent = t.num;
      el("text", { x: 0, y: 67, class: "sub" }, g).textContent = n.s;
      const show = () => {
        const r = svg.getBoundingClientRect(), box = svg.parentElement.getBoundingClientRect(), k = r.width / 720;
        tip.innerHTML = `<b>${esc(t.num)} · ${esc(t.title)}</b><span>${t.soon ? "Bientôt disponible" : `${t.slides} diapositives · ${t.commands} saisies — cliquez pour lancer`}</span>`;
        tip.style.left = (r.left - box.left + x * k) + "px"; tip.style.top = (r.top - box.top + (y + 72) * k) + "px";
        tip.hidden = false;
      };
      a.addEventListener("mouseenter", show); a.addEventListener("focus", show);
      a.addEventListener("mouseleave", () => tip.hidden = true); a.addEventListener("blur", () => tip.hidden = true);
    });
  })();

  const nS = ready.reduce((a, t) => a + t.slides, 0), nC = ready.reduce((a, t) => a + t.commands, 0), nK = ready.reduce((a, t) => a + (t.clicks || 0), 0);
  document.getElementById("totals").textContent =
    `${ready.length} TP disponible${ready.length > 1 ? "s" : ""} : ${nS} diapositives, ${nC} saisies${nK ? ` et ${nK} clics guidés` : ""}, sans rien installer.`;

  const ICON = {
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l12.5-7.5z" fill="currentColor"/></svg>',
    doc: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 2.8h8l4.2 4.2v14.2H6z M14 2.8V7h4.2 M8.8 12h6.4 M8.8 15.5h6.4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
    dl: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.5v11 M7.5 10.5 12 15l4.5-4.5 M4.5 19.5h15" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  };
  const main = document.getElementById("tps");
  Object.entries(C.groups).forEach(([gk, g]) => {
    const list = C.tps.filter(t => t.group === gk);
    if (!list.length) return;
    const sec = document.createElement("section");
    sec.className = "group";
    sec.innerHTML = `<h2>${esc(g.name)}</h2><p class="gdesc">${esc(g.desc)}</p>`;
    list.forEach(t => {
      const art = document.createElement("article");
      art.className = "tp" + (t.soon ? " soon" : ""); art.id = t.id;
      const facts = t.soon ? `<span class="badge soon">Bientôt disponible</span>` :
        `<span>${t.slides} diapositives</span><span>${t.commands} saisies</span>${t.clicks ? `<span>${t.clicks} clics guidés</span>` : ""}<span class="badge">${esc(t.origin)}</span>`;
      const actions = t.soon ? `<a class="btn btn-primary" aria-disabled="true">${ICON.play}Simulation à venir</a>` : `
          <a class="btn btn-primary" href="simulation.html?tp=${t.id}">${ICON.play}Lancer la simulation</a>
          <a class="btn" href="${t.cr}" target="_blank" rel="noopener">${ICON.doc}Compte rendu (PDF)</a>
          <a class="btn btn-quiet" href="${t.approj}" download>${ICON.dl}Projet ActivePresenter</a>`;
      art.innerHTML = `
        <div class="num">${esc(t.num)}<small>${esc(t.tool)}</small></div>
        <div>
          <h3>${esc(t.title)}</h3>
          <p>${esc(t.desc)}</p>
          <div class="cmds">${t.cmds.map(c => `<code>${esc(c)}</code>`).join("")}</div>
          <div class="facts">${facts}</div>
        </div>
        <div class="actions">${actions}</div>`;
      sec.appendChild(art);
    });
    main.appendChild(sec);
  });
})();

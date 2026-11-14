(function () {
  const C = window.CATALOG;
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const ready = C.tps.filter(t => !t.soon);

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

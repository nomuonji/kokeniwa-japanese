/* Pure, bounded layout calculation shared by the browser and the sanity checks. */
(function (root) {
  'use strict';
  function calculateGrid(width, height, diameter, gap, margin) {
    if (![width, height, diameter, gap, margin].every(Number.isFinite) ||
        width < 1 || width > 2000 || height < 1 || height > 2000 ||
        diameter < 1 || diameter > 500 || gap < 0 || gap > 500 || margin < 0 || margin > 1000) {
      throw new RangeError('Use the measurement ranges shown in the form.');
    }
    const usableW = Math.max(0, width - 2 * margin);
    const usableH = Math.max(0, height - 2 * margin);
    const columns = Math.max(0, Math.floor((usableW + gap) / (diameter + gap) + 1e-10));
    const rows = Math.max(0, Math.floor((usableH + gap) / (diameter + gap) + 1e-10));
    const usedW = columns ? columns * diameter + (columns - 1) * gap : 0;
    const usedH = rows ? rows * diameter + (rows - 1) * gap : 0;
    return {columns, rows, count: columns * rows, usedW, usedH, spareW: usableW - usedW, spareH: usableH - usedH};
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = calculateGrid;
  if (typeof document === 'undefined') return;
  const form = document.getElementById('badge-grid');
  if (!form) return;
  const result = document.getElementById('grid-result');
  const preview = document.getElementById('grid-preview');
  const ns = 'http://www.w3.org/2000/svg';
  const round = n => Math.round(n * 10) / 10;
  function draw(width, height, diameter, gap, g) {
    preview.replaceChildren();
    preview.setAttribute('viewBox', `0 0 ${width} ${height}`);
    preview.setAttribute('aria-label', `${g.columns} columns by ${g.rows} rows: ${g.count} badges in a non-overlapping grid`);
    const panel = document.createElementNS(ns, 'rect');
    for (const [key, value] of Object.entries({width, height, fill:'none', stroke:'currentColor', 'stroke-width':1})) panel.setAttribute(key, value);
    preview.append(panel);
    // Keep large but valid numerical estimates responsive; do not create millions of SVG nodes.
    if (g.count > 1000) return false;
    for (let y = 0; y < g.rows; y++) for (let x = 0; x < g.columns; x++) {
      const badge = document.createElementNS(ns, 'circle');
      const attrs = {cx:(width-g.usedW)/2+diameter/2+x*(diameter+gap), cy:(height-g.usedH)/2+diameter/2+y*(diameter+gap), r:diameter/2, fill:'var(--primary)', 'fill-opacity':.2, stroke:'currentColor', 'stroke-width':.7};
      for (const [key, value] of Object.entries(attrs)) badge.setAttribute(key, value);
      preview.append(badge);
    }
    return true;
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    const values = ['width','height','diameter','gap','margin'].map(name => Number(form.elements.namedItem(name).value));
    try {
      const g = calculateGrid(...values);
      const shown = draw(values[0], values[1], values[2], values[3], g);
      result.textContent = `${g.columns} columns × ${g.rows} rows = ${g.count} badges, with ${round(g.spareW)} mm spare across and ${round(g.spareH)} mm spare vertically after margins.${shown ? '' : ' Diagram omitted for layouts over 1,000 badges.'}`;
      if (typeof root.gtag === 'function') root.gtag('event', 'fan_tool_used', {tool_name:'badge_grid'});
    } catch (error) {
      result.textContent = error.message;
      preview.replaceChildren();
    }
  });
})(typeof window === 'undefined' ? globalThis : window);

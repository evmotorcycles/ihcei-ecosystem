// popup.js — loads the SAME on-device kernel as everything else. No network.
import { audit } from './src/helm-core.mjs';
const $ = id => document.getElementById(id);
$('grab').onclick = async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const [{ result }] = await chrome.scripting.executeScript({ target: { tabId: tab.id }, func: () => String(window.getSelection()) });
    if (result) { $('t').value = result; render(audit(result)); }
  } catch { /* no page access — paste path still works */ }
};
$('go').onclick = () => { const v = $('t').value.trim(); if (v) render(audit(v)); };
function render(r) {
  const chip = r.chip
    ? `<span class="chip ${r.verdict === 'BLOCK' ? 'block' : 'warn'}">⚠ ${r.verdict === 'BLOCK' ? 'Looks like manipulation' : 'Second look'}</span>`
    : `<span class="silent">✓ Nothing here trips the floor.</span>`;
  $('out').innerHTML = `${chip}${r.correction ? `<div class="why">${r.correction}</div>` : ''}` +
    `<div class="k">p=${r.p_manipulative} · CI[${r.ci95[0]}, ${r.ci95[1]}] · mechanism ${r.mechanismPresent ? 'present' : 'absent'}</div>`;
}

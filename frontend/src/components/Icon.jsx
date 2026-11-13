import React from 'react';
const paths = {
  overview: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="13" width="7" height="8" rx="1"/></>,
  incidents: <><path d="M8 3h8l4 4v14H4V3z"/><path d="M8 11h8M8 15h8M8 7h3"/></>,
  analyzer: <path d="M12 3 4 13h6l-1 8 8-11h-6z"/>,
  import: <><path d="M12 16V4m-4 4 4-4 4 4"/><path d="M4 14v5h16v-5"/></>,
  methodology: <><circle cx="12" cy="12" r="9"/><path d="M12 11v5m0-9h.01"/></>,
  menu: <path d="M4 6h16M4 12h16M4 18h16"/>,
  search: <><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/></>,
  refresh: <><path d="M20 7v5h-5M4 17v-5h5"/><path d="M5.6 9A7 7 0 0 1 18 6l2 6M4 12l2 6a7 7 0 0 0 12.4-3"/></>,
  close: <path d="m6 6 12 12M18 6 6 18"/>,
  shield: <><path d="M12 3 20 6v5c0 5-3 8-8 10-5-2-8-5-8-10V6z"/><path d="m9 12 2 2 4-4"/></>,
  arrow: <path d="M5 12h14m-6-6 6 6-6 6"/>,
};
export function Icon({ name, size = 18 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] || paths.overview}</svg>;
}

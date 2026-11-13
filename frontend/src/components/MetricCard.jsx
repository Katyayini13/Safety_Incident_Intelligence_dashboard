import React from 'react';
export function MetricCard({ label, value, caption, icon, tone = 'green', loading = false }) { return <article className="metric-card"><div className="metric-top"><span>{label}</span><i className={`metric-icon ${tone}`}>{icon}</i></div>{loading ? <div className="skeleton-number"/> : <strong>{value ?? '—'}</strong>}<small>{caption}</small></article>; }

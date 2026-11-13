import React from 'react';
export function SeverityBadge({ value }) { const v = String(value || 'unknown').toLowerCase(); return <span className={`severity-badge severity-${v}`}><i/>{v}</span>; }
export function CategoryBadge({ value }) { const v = String(value || 'unknown').toLowerCase(); const label = v === 'esg_compliance' ? 'ESG compliance' : v.charAt(0).toUpperCase() + v.slice(1); return <span className={`category-badge category-${v}`}>{label}</span>; }

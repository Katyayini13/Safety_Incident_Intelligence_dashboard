import React from 'react';
export function Panel({ title, eyebrow, action, children, className = '' }) { return <section className={`panel ${className}`}><div className="panel-heading"><div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h2>{title}</h2></div>{action}</div>{children}</section>; }

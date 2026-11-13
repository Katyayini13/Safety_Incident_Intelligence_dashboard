import React, { useEffect, useRef, useState } from 'react';
import { Icon } from './Icon.jsx';
export function Topbar({ page, onMenu, onRefresh, loading, connected }) {
  const [supportOpen, setSupportOpen] = useState(false);
  const supportRef = useRef(null);
  useEffect(() => {
    function dismiss(event) { if (!supportRef.current?.contains(event.target)) setSupportOpen(false); }
    function escape(event) { if (event.key === 'Escape') setSupportOpen(false); }
    document.addEventListener('pointerdown', dismiss);
    document.addEventListener('keydown', escape);
    return () => { document.removeEventListener('pointerdown', dismiss); document.removeEventListener('keydown', escape); };
  }, []);
  return <header className="topbar"><button className="topbar-menu" aria-label="Open navigation" onClick={onMenu}><Icon name="menu"/></button><div className="breadcrumbs"><span>Operations</span><b>/</b><strong>{page.label}</strong></div><div className="topbar-actions"><div className={`system-state ${connected ? '' : 'system-offline'}`}><i/>{loading ? 'Connecting…' : connected ? 'API connected' : 'API unavailable'}</div><button className="icon-button" aria-label="Refresh dashboard data" onClick={onRefresh} disabled={loading}><Icon name="refresh"/></button><div className="support-anchor" ref={supportRef}><button className="user-chip support-trigger" aria-label="Open HSE Operations Support" aria-expanded={supportOpen} onClick={() => setSupportOpen(value => !value)}><span><Icon name="shield" size={15}/></span><b>HSE Support</b></button>{supportOpen && <section className="support-popover" role="dialog" aria-label="HSE Operations Support"><div className="support-heading"><span className="support-icon"><Icon name="shield" size={19}/></span><div><b>HSE Operations Support</b><small>Decision-support guidance</small></div><button className="support-close" aria-label="Close HSE support" onClick={() => setSupportOpen(false)}>×</button></div><div className="support-content"><p><b>Platform purpose</b><span>Organize incident narratives, retrieve similar historical records and surface screening signals for operations teams.</span></p><p><b>Human review required</b><span>Validate all predictions and recommendations with qualified site HSE personnel before acting.</span></p><p><b>Verify severity</b><span>Severity labels use simple text rules and may miss context or misread wording. Confirm using the site risk process.</span></p><p><b>Emergency response</b><span>For active danger, follow site emergency procedures and contact the designated response team. Do not wait for this tool.</span></p></div><div className="support-version"><span>Application version</span><b>1.0.0</b></div></section>}</div></div></header>;
}

import React from 'react';
import { Icon } from './Icon.jsx';
const nav = [['overview','Overview'],['incidents','Incident intelligence'],['analyzer','AI analyzer'],['import','Data import'],['methodology','Methodology']];
export function Sidebar({ active, onNavigate, collapsed, onToggle, mobileOpen, onClose }) {
  return <><div className={`sidebar-scrim ${mobileOpen ? 'is-open' : ''}`} onClick={onClose}/><aside className={`sidebar ${collapsed ? 'is-collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
    <div className="brand-lockup"><div className="brand-mark">G<span>+</span></div><div className="brand-copy"><b>GREENKO</b><small>OPERATIONS INTELLIGENCE</small></div><button className="mobile-close" aria-label="Close menu" onClick={onClose}><Icon name="close"/></button></div>
    <div className="sidebar-label">WORKSPACE</div><nav className="side-nav" aria-label="Main navigation">{nav.map(([key,label]) => <button key={key} className={`nav-item ${active === key ? 'active' : ''}`} onClick={() => onNavigate(key)} title={collapsed ? label : undefined}><Icon name={key}/><span>{label}</span>{active === key && <i/>}</button>)}</nav>
    <div className="sidebar-bottom"><div className="dataset-status"><span className="status-dot"/><div><b>Connected to dataset</b><small>Bundled incident register</small></div></div><button className="collapse-button" onClick={onToggle}><span>{collapsed ? 'Expand sidebar' : 'Collapse sidebar'}</span><span className="collapse-glyph">‹</span></button><div className="sidebar-foot">SCREENING SUPPORT · V1.0</div></div>
  </aside></>;
}

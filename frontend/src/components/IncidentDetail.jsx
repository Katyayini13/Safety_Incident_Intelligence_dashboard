import React from 'react';
import { CategoryBadge, SeverityBadge } from './SeverityBadge.jsx';
import { Icon } from './Icon.jsx';
export function IncidentDetail({ incident, onClose }) {
  if (!incident) return null;
  return <div className="modal-backdrop" role="presentation" onMouseDown={e => e.target === e.currentTarget && onClose()}><section className="detail-modal" role="dialog" aria-modal="true" aria-labelledby="detail-title"><div className="modal-head"><div><span className="eyebrow">INCIDENT RECORD</span><h2 id="detail-title">{incident.incident_id}</h2></div><button className="icon-button" aria-label="Close details" onClick={onClose}><Icon name="close"/></button></div><div className="detail-badges"><CategoryBadge value={incident.target_category || incident.category}/><SeverityBadge value={incident.target_severity || incident.severity}/></div><h3>Incident narrative</h3><p>{incident.narrative}</p><div className="detail-note"><Icon name="shield"/><span>Historical record from the bundled dataset. Validate context before using as operational guidance.</span></div></section></div>;
}

import React from 'react';
import { SeverityBadge, CategoryBadge } from './SeverityBadge.jsx';
import { EmptyState } from './Feedback.jsx';
export function IncidentTable({ rows, onSelect, compact = false }) {
  if (!rows?.length) return <EmptyState title="No incidents found" detail="Try changing your search or filter selections."/>;
  return <div className="table-wrap"><table className="incident-table"><thead><tr><th>Incident</th><th>Narrative</th><th>Category</th><th>Severity</th>{!compact && <th>Review</th>}</tr></thead><tbody>{rows.map((r,i) => <tr key={r.incident_id || i} onClick={() => onSelect?.(r)} className={onSelect ? 'clickable-row' : ''}><td><b className="incident-id">{r.incident_id}</b></td><td className="narrative-cell">{r.narrative}</td><td><CategoryBadge value={r.target_category || r.category}/></td><td><SeverityBadge value={r.target_severity || r.severity}/></td>{!compact && <td><button className="text-link" onClick={e => { e.stopPropagation(); onSelect?.(r); }}>View details ↗</button></td>}</tr>)}</tbody></table></div>;
}

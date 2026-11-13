import React, { useEffect, useState } from 'react';
import { Icon } from '../components/Icon.jsx';
import { PageHeader } from '../components/PageHeader.jsx';
import { Panel } from '../components/Panel.jsx';
import { IncidentTable } from '../components/IncidentTable.jsx';
import { IncidentDetail } from '../components/IncidentDetail.jsx';
import { LoadingBlock, ErrorState } from '../components/Feedback.jsx';
import { getIncidents } from '../services/api.js';

export function IncidentIntelligence() {
  const [query,setQuery]=useState(''),[category,setCategory]=useState(''),[severity,setSeverity]=useState('');
  const [rows,setRows]=useState([]),[busy,setBusy]=useState(true),[error,setError]=useState(''),[selected,setSelected]=useState(null);
  async function search() { setBusy(true);setError('');try{setRows(await getIncidents({q:query,category,severity}))}catch(e){setError(e.message)}finally{setBusy(false)} }
  useEffect(()=>{search()},[]);
  return <><PageHeader eyebrow="INCIDENT REGISTER" title="Incident intelligence" subtitle="Search the historical register and inspect recorded category and severity labels." action={<span className="record-count">{busy?'…':`${rows.length} records`}</span>}/>
    <Panel title="Incident register" eyebrow="SEARCH & FILTER"><div className="filter-toolbar"><label className="search-field"><Icon name="search"/><input value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>e.key==='Enter'&&search()} placeholder="Search incident narratives or IDs"/></label><select value={category} onChange={e=>setCategory(e.target.value)} aria-label="Filter by category"><option value="">All categories</option><option value="safety">Safety</option><option value="environment">Environment</option><option value="esg_compliance">ESG compliance</option></select><select value={severity} onChange={e=>setSeverity(e.target.value)} aria-label="Filter by severity"><option value="">All severities</option><option value="low">Low severity</option><option value="medium">Medium severity</option><option value="high">High severity</option></select><button className="button button-primary" onClick={search}>Apply filters</button></div>{error?<ErrorState message={error} onRetry={search}/>:busy?<LoadingBlock label="Searching incident records…"/>:<IncidentTable rows={rows} onSelect={setSelected}/>}</Panel>
    <IncidentDetail incident={selected} onClose={()=>setSelected(null)}/>
  </>;
}

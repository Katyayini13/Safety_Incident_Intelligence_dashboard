import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, CartesianGrid } from 'recharts';
import { PageHeader } from '../components/PageHeader.jsx';
import { MetricCard } from '../components/MetricCard.jsx';
import { Panel } from '../components/Panel.jsx';
import { IncidentTable } from '../components/IncidentTable.jsx';
import { LoadingBlock, EmptyState } from '../components/Feedback.jsx';
const severityColors = { low:'#54b88a', medium:'#d6a648', high:'#d8675f' };

export function Overview({ analytics, evaluation, incidents, loading, onNavigate }) {
  const categories = analytics?.categories || [];
  const severities = analytics?.severities || [];
  const indicators = analytics?.risk_indicators || [];
  const count = name => categories.find(item => item.name === name)?.count ?? 0;
  return <>
    <PageHeader eyebrow="LIVE INCIDENT REGISTER" title="Operations overview" subtitle="Current incident profile and signals that deserve operational attention." action={<button className="button button-primary" onClick={() => onNavigate('analyzer')}>Analyze an incident <span>↗</span></button>}/>
    <div className="section-label">INCIDENT SNAPSHOT <span>{loading ? 'Updating…' : 'Based on bundled records'}</span></div>
    <div className="metric-grid">
      <MetricCard label="Total incidents" value={analytics?.total} caption="Historical records loaded" tone="green" icon="01" loading={loading}/>
      <MetricCard label="Safety" value={count('safety')} caption="Category records" tone="navy" icon="02" loading={loading}/>
      <MetricCard label="Environment" value={count('environment')} caption="Category records" tone="teal" icon="03" loading={loading}/>
      <MetricCard label="ESG compliance" value={count('esg_compliance')} caption="Category records" tone="violet" icon="04" loading={loading}/>
      <MetricCard label="High severity" value={analytics?.high_severity} caption="Historical severity labels" tone="red" icon="!" loading={loading}/>
    </div>
    <div className="chart-grid">
      <Panel title="Incidents by category" eyebrow="CATEGORY DISTRIBUTION" action={<span className="panel-note">Count</span>}>
        {loading ? <LoadingBlock/> : categories.length ? <div className="chart-box"><ResponsiveContainer width="100%" height="100%"><BarChart data={categories} margin={{top:12,right:12,left:-18,bottom:4}}><CartesianGrid vertical={false} stroke="#edf1ef"/><XAxis dataKey="name" tick={{fill:'#72817a',fontSize:12}} axisLine={false} tickLine={false}/><YAxis allowDecimals={false} tick={{fill:'#93a09a',fontSize:12}} axisLine={false} tickLine={false}/><Tooltip contentStyle={{fontSize:13,borderRadius:8,borderColor:'#e4ebe6'}}/><Bar dataKey="count" fill="#18886a" radius={[5,5,0,0]} maxBarSize={52}/></BarChart></ResponsiveContainer></div> : <EmptyState title="No category data" detail="Analytics are not available yet."/>}
      </Panel>
      <Panel title="Severity profile" eyebrow="RISK DISTRIBUTION" action={<span className="panel-note">Count</span>}>
        {loading ? <LoadingBlock/> : severities.length ? <div className="severity-chart"><div className="chart-box chart-donut"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={severities} dataKey="count" nameKey="name" innerRadius={62} outerRadius={88} paddingAngle={3} stroke="none">{severities.map(item => <Cell key={item.name} fill={severityColors[item.name] || '#9aa8a1'}/>)}</Pie><Tooltip contentStyle={{fontSize:13,borderRadius:8,borderColor:'#e4ebe6'}}/></PieChart></ResponsiveContainer><div className="donut-total"><b>{analytics?.total ?? 0}</b><span>incidents</span></div></div><div className="legend-list">{severities.map(item => <div key={item.name}><i style={{background:severityColors[item.name] || '#9aa8a1'}}/><span>{item.name}</span><b>{item.count}</b></div>)}</div></div> : <EmptyState title="No severity data" detail="Severity counts are unavailable."/>}
      </Panel>
    </div>
    <div className="lower-grid">
      <Panel title="Frequently tagged indicators" eyebrow="RISK SIGNALS" action={<span className="data-chip">DATASET-DERIVED</span>}>
        {loading ? <LoadingBlock/> : <div className="risk-list">{indicators.length ? indicators.map((item,index) => <div className="risk-row" key={item.name}><span className="risk-rank">{String(index+1).padStart(2,'0')}</span><span className="risk-name">{item.name}</span><div className="risk-track"><i style={{width:`${analytics.total ? Math.max(4,item.count/analytics.total*100) : 0}%`}}/></div><b>{item.count}</b></div>) : <EmptyState title="No risk signals" detail="The backend has not returned indicators."/>}</div>}
      </Panel>
      <Panel title="Evaluation at a glance" eyebrow="MODEL CONTEXT"><div className="eval-callout"><div className="eval-number">{analytics?.total ?? '—'}</div><div><b>original labeled records</b><p>Real-data validation is unavailable. A separate {evaluation?.synthetic_development?.records ?? 'synthetic'}-record synthetic development evaluation is shown on the methodology page and is not production accuracy.</p></div></div><button className="text-link methodology-link" onClick={() => onNavigate('methodology')}>Read methodology & safeguards →</button></Panel>
    </div>
    <Panel title="Incident records" eyebrow="BUNDLED REGISTER" action={<button className="text-link" onClick={() => onNavigate('incidents')}>Open incident intelligence →</button>}>{loading ? <LoadingBlock label="Loading incident records…"/> : <IncidentTable rows={incidents.slice(0,5)} compact/>}</Panel>
  </>;
}

import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Sidebar } from './components/Sidebar.jsx';
import { Topbar } from './components/Topbar.jsx';
import { Overview } from './pages/Overview.jsx';
import { IncidentIntelligence } from './pages/IncidentIntelligence.jsx';
import { Analyzer } from './pages/Analyzer.jsx';
import { DataImport } from './pages/DataImport.jsx';
import { Methodology } from './pages/Methodology.jsx';
import { getAnalytics, getIncidents } from './services/api.js';
import './styles.css';
import './typography.css';

const pages = {
  overview: { label: 'Overview', title: 'Operations overview', subtitle: 'A live view of incident activity and risk signals.' },
  incidents: { label: 'Incident intelligence', title: 'Incident intelligence', subtitle: 'Search and review the historical incident register.' },
  analyzer: { label: 'AI analyzer', title: 'AI incident analyzer', subtitle: 'Screen a narrative and review the evidence behind the result.' },
  import: { label: 'Data import', title: 'Data import', subtitle: 'Validate an incident CSV against the supported format.' },
  methodology: { label: 'Methodology', title: 'Methodology & safeguards', subtitle: 'How the screening, retrieval and limitations work.' },
};

function App() {
  const [active, setActive] = useState('overview');
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');

  async function refreshOverview() {
    setLoading(true); setLoadError('');
    try {
      const [data, rows] = await Promise.all([getAnalytics(), getIncidents()]);
      setAnalytics(data); setIncidents(rows);
    } catch (error) { setLoadError(error.message); }
    finally { setLoading(false); }
  }
  useEffect(() => { refreshOverview(); }, []);
  function navigate(key) { setActive(key); setMobileOpen(false); }

  return <div className="app-shell">
    <Sidebar active={active} onNavigate={navigate} collapsed={collapsed} onToggle={() => setCollapsed(v => !v)} mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />
    <div className={`main-column ${collapsed ? 'sidebar-collapsed' : ''}`}>
      <Topbar page={pages[active]} onMenu={() => setMobileOpen(v => !v)} onRefresh={refreshOverview} loading={loading} connected={!loading && !loadError} />
      <main className="workspace">
        {loadError && <div className="global-error" role="alert"><span>{loadError}</span><button className="button button-quiet" onClick={refreshOverview}>Retry</button></div>}
        {active === 'overview' && <Overview analytics={analytics?.analytics} evaluation={analytics?.evaluation} incidents={incidents} loading={loading} onNavigate={navigate} />}
        {active === 'incidents' && <IncidentIntelligence />}
        {active === 'analyzer' && <Analyzer />}
        {active === 'import' && <DataImport />}
        {active === 'methodology' && <Methodology evaluation={analytics?.evaluation} recordCount={analytics?.analytics?.total} loading={loading} />}
        <footer className="app-footer"><span>GREENKO OPERATIONS INTELLIGENCE</span><span>Decision support only · Verify actions with site HSE leadership</span></footer>
      </main>
    </div>
  </div>;
}

createRoot(document.getElementById('root')).render(<App />);

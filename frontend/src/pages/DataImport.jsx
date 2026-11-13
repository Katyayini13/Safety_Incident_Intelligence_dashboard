import React, { useRef, useState } from 'react';
import { PageHeader } from '../components/PageHeader.jsx';
import { Panel } from '../components/Panel.jsx';
import { Icon } from '../components/Icon.jsx';
import { LoadingBlock } from '../components/Feedback.jsx';
import { validateCsv } from '../services/api.js';

const MAX_BYTES = 10 * 1024 * 1024;
function emptyValidation(filename, error, status = 'Not checked') {
  return { filename, totalRows: null, validRows: null, invalidRows: null, requiredColumn: status, errors: [error], preview: [] };
}

export function DataImport() {
  const input = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [validation, setValidation] = useState(null);

  async function validate(file) {
    setValidation(null);
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setValidation(emptyValidation(file.name, 'Unsupported file type. Choose a .csv file.'));
      return;
    }
    if (file.size > MAX_BYTES) {
      setValidation(emptyValidation(file.name, 'File exceeds the 10 MB frontend validation limit. It was not sent to the API.'));
      return;
    }

    setBusy(true);
    try {
      const response = await validateCsv(file);
      const validRows = Number(response.usable_narratives ?? 0);
      const totalRows = Number(response.rows ?? 0);
      const invalidRows = Math.max(0, totalRows - validRows);
      const hasNarrative = Array.isArray(response.columns) && response.columns.includes('narrative');
      setValidation({
        filename: file.name,
        totalRows,
        validRows,
        invalidRows,
        requiredColumn: hasNarrative ? 'Present' : 'Missing',
        errors: response.valid === false ? [response.message || 'The API reported a validation failure.'] : invalidRows ? [`${invalidRows} row(s) have an empty narrative, derived from the API usable_narratives count. The API does not provide row numbers.`] : [],
        message: response.message,
        preview: Array.isArray(response.preview) ? response.preview.slice(0, 5) : null,
        columns: response.columns || [],
      });
    } catch (error) {
      const requiredStatus = error.status === 422 && /narrative/i.test(error.message) ? 'Missing' : 'Not confirmed';
      setValidation(emptyValidation(file.name, error.message, requiredStatus));
    } finally {
      setBusy(false);
      if (input.current) input.current.value = '';
    }
  }
  function resetAndBrowse() { setValidation(null); input.current?.click(); }

  return <><PageHeader eyebrow="DATA QUALITY" title="Data import" subtitle="Validate an incident CSV before considering it for a reviewed data workflow."/><div className="import-layout">
    <Panel title="Validate a CSV file" eyebrow="FILE CHECK">
      <input ref={input} type="file" accept=".csv,text/csv" hidden onChange={event => validate(event.target.files?.[0])}/>
      {!validation && <div className={`drop-zone ${dragging ? 'drag-active' : ''} ${busy ? 'is-busy' : ''}`} onDragOver={event => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={event => { event.preventDefault(); setDragging(false); validate(event.dataTransfer.files?.[0]); }} onClick={() => !busy && input.current?.click()} role="button" tabIndex="0" aria-label="Choose or drop a CSV file" onKeyDown={event => (event.key === 'Enter' || event.key === ' ') && input.current?.click()}>
        <div className="upload-icon"><Icon name="import" size={24}/></div><b>{busy ? 'Uploading and validating…' : 'Drop your CSV file here'}</b><span>or <em>browse files</em> from your computer</span><small>CSV format · Maximum 10 MB</small>
        {busy && <div className="upload-progress" role="status"><i/><span>Sending file to the validation API. The API does not provide percentage progress.</span></div>}
      </div>}
      {busy && <LoadingBlock label="Checking CSV structure and narrative rows…"/>}
      {validation && <div className={`validation-result ${validation.errors.length ? 'has-errors' : 'is-valid'}`} aria-live="polite">
        <div className="validation-banner"><span className="validation-mark">{validation.errors.length ? '!' : '✓'}</span><div><b>{validation.errors.length ? 'Validation needs attention' : 'CSV structure validated'}</b><span>{validation.errors.length ? 'Review the details below and select another file when ready.' : validation.message || 'The API accepted the CSV structure.'}</span></div></div>
        <div className="validation-file"><span className="file-symbol">CSV</span><div><b>{validation.filename}</b><small>{validation.errors.length ? 'Validation failed' : 'Validation complete'}</small></div></div>
        <div className="validation-metrics"><div><small>Total rows</small><b>{validation.totalRows ?? '—'}</b></div><div><small>Valid rows</small><b>{validation.validRows ?? '—'}</b></div><div><small>Invalid rows</small><b>{validation.invalidRows ?? '—'}</b></div></div>
        <div className="required-check"><span>Required column · <code>narrative</code></span><b className={validation.requiredColumn === 'Present' ? 'check-pass' : validation.requiredColumn === 'Missing' ? 'check-fail' : ''}>{validation.requiredColumn}</b></div>
        <div className="validation-errors"><b>Validation errors</b>{validation.errors.length ? <ul>{validation.errors.map((item, index) => <li key={index}>{item}</li>)}</ul> : <span>No validation errors returned by the API.</span>}</div>
        {validation.preview?.length ? <div className="preview-block"><b>Uploaded record preview · first {validation.preview.length}</b><pre>{JSON.stringify(validation.preview, null, 2)}</pre></div> : <div className="preview-unavailable"><b>Record preview unavailable</b><span>The current validation API returns row counts and column names, but no uploaded row data. No preview is fabricated.</span></div>}
        <button className="button button-primary validate-another" onClick={resetAndBrowse}>Validate another file</button>
      </div>}
      {!validation && <div className="persist-warning"><Icon name="shield"/><p>Validation only: uploaded rows are not saved, added to the incident register, or used to update a model.</p></div>}
    </Panel>
    <Panel title="Expected CSV format" eyebrow="FORMAT GUIDE"><p className="format-intro">The backend requires a header named <code>narrative</code>. Other columns are accepted but are not ingested.</p><pre className="csv-example">{'incident_id,narrative,target_category,target_severity\nS007,"Oil leak observed near turbine",environment,medium'}</pre><div className="format-check"><span>Required column</span><b>narrative</b></div><div className="format-check"><span>Optional columns</span><b>Any additional fields</b></div><div className="format-check"><span>File type</span><b>.csv</b></div><p className="format-footnote">Valid rows are counted as rows containing a non-empty narrative, matching the current API’s `usable_narratives` field.</p></Panel>
  </div></>;
}

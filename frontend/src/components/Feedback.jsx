import React from 'react';
export function LoadingBlock({ label = 'Loading data…' }) { return <div className="loading-block"><span className="spinner"/>{label}</div>; }
export function EmptyState({ title, detail }) { return <div className="empty-state"><b>{title}</b><span>{detail}</span></div>; }
export function ErrorState({ message, onRetry }) { return <div className="error-state" role="alert"><span>{message}</span>{onRetry && <button className="button button-quiet" onClick={onRetry}>Try again</button>}</div>; }

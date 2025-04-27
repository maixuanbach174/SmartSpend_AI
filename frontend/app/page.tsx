'use client'; // If using App Router

import { useState } from 'react';

export default function Home() {
  const [data, setData] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const res = await fetch('http://localhost:8008/admin/');
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      setData(JSON.stringify(json, null, 2));
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <main style={{ padding: '2rem' }}>
      <h1>Test Local API</h1>
      <button onClick={fetchData}>Fetch from API</button>
      {data && <pre>{data}</pre>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </main>
  );
}

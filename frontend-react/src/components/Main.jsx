import React, { useEffect, useState } from 'react'

const Main = () => {
  const [commodities, setCommodities] = useState({ gold: null, silver: null, oil: null })
  const [currencies, setCurrencies] = useState({ usd_inr: null, eur_inr: null, gbp_inr: null })
  const [bonds, setBonds] = useState({ india_10y: null, india_5y: null, india_2y: null })

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAll = () => {
    setError(null);
    setLoading(true);

    // Single call to Django backend – all market data proxied server-side
    fetch('http://127.0.0.1:8000/api/v1/market-data/')
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          setError(data.error);
          return;
        }
        const c = data.commodities || {};
        setCommodities({
          gold: c.gold ?? null,
          silver: c.silver ?? null,
          oil: c.oil ?? null,
        });
        const cur = data.currencies || {};
        setCurrencies({
          usd_inr: cur.usd_inr ?? null,
          eur_inr: cur.eur_inr ?? null,
          gbp_inr: cur.gbp_inr ?? null,
        });
        const b = data.bonds || {};
        setBonds({
          india_10y: b.india_10y ?? null,
          india_5y: b.india_5y ?? null,
          india_2y: b.india_2y ?? null,
        });
      })
      .catch(() => setError('Failed to fetch market data – is the backend running?'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 60000); // auto-refresh every 60s
    return () => clearInterval(interval);
  }, []);

  if (loading && !error && !commodities.gold && !commodities.silver && !commodities.oil) {
    return <div className='container text-center py-5'><h2 className='text-info'>Loading live prices...</h2></div>;
  }
  return (
    <div className='container py-5'>
      <h1 className='text-center text-info mb-5'>Market Live Prices</h1>
      {error && <div className='alert alert-danger text-center'>{error}</div>}
      <div className='row g-4 justify-content-center'>
        {/* Commodities */}
        <div className='col-md-4'>
          <div className='card bg-dark text-light h-100'>
            <div className='card-header text-warning text-center fs-4'>Commodities</div>
            <div className='card-body text-center'>
              <p className='mb-2'>Gold (per oz): <span className='fw-bold'>{commodities.gold ? `₹${Number(commodities.gold).toLocaleString('en-IN')}` : '--'}</span></p>
              <p className='mb-2'>Silver (per oz): <span className='fw-bold'>{commodities.silver ? `₹${Number(commodities.silver).toLocaleString('en-IN')}` : '--'}</span></p>
              <p className='mb-2'>Crude Oil (per bbl): <span className='fw-bold'>{commodities.oil ? `₹${Number(commodities.oil).toLocaleString('en-IN')}` : '--'}</span></p>
            </div>
          </div>
        </div>
        {/* Currencies */}
        <div className='col-md-4'>
          <div className='card bg-dark text-light h-100'>
            <div className='card-header text-success text-center fs-4'>Currencies</div>
            <div className='card-body text-center'>
              <p className='mb-2'>USD/INR: <span className='fw-bold'>{currencies.usd_inr ? `₹${currencies.usd_inr}` : '--'}</span></p>
              <p className='mb-2'>EUR/INR: <span className='fw-bold'>{currencies.eur_inr ? `₹${currencies.eur_inr}` : '--'}</span></p>
              <p className='mb-2'>GBP/INR: <span className='fw-bold'>{currencies.gbp_inr ? `₹${currencies.gbp_inr}` : '--'}</span></p>
            </div>
          </div>
        </div>
        {/* Bonds */}
        <div className='col-md-4'>
          <div className='card bg-dark text-light h-100'>
            <div className='card-header text-primary text-center fs-4'>Bonds</div>
            <div className='card-body text-center'>
              <p className='mb-2'>India 10Y G-Sec: <span className='fw-bold'>{bonds.india_10y ? `${bonds.india_10y}%` : '--'}</span></p>
              <p className='mb-2'>India 5Y G-Sec: <span className='fw-bold'>{bonds.india_5y ? `${bonds.india_5y}%` : '--'}</span></p>
              <p className='mb-2'>India 2Y G-Sec: <span className='fw-bold'>{bonds.india_2y ? `${bonds.india_2y}%` : '--'}</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
// Removed duplicate/old JSX after the new return statement

export default Main
import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSpinner, faArrowLeft, faChartLine } from '@fortawesome/free-solid-svg-icons'

const StockDetail = () => {
  const [stock, setStock] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { symbol } = useParams()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    fetchStockMetrics()
  }, [symbol])

  const fetchStockMetrics = async () => {
    const token = localStorage.getItem('accessToken')
    
    if (!token) {
      navigate('/login')
      return
    }

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';
      const params = new URLSearchParams(location.search)
      const exchange = params.get('exchange')
      const endpoint = exchange
        ? `${apiUrl}/stocks/${symbol}/?exchange=${encodeURIComponent(exchange)}`
        : `${apiUrl}/stocks/${symbol}/`

      const response = await axios.get(endpoint, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      setStock(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching stock metrics:', error)
      if (error.response?.status === 401) {
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        navigate('/login')
      } else {
        setError('Failed to load stock metrics')
        setLoading(false)
      }
    }
  }

  const formatValue = (value) => {
    if (value === null || value === undefined || Number.isNaN(value)) return 'N/A'
    return typeof value === 'number' ? value.toFixed(2) : value
  }

  const formatPercent = (value) => {
    if (value === null || value === undefined || Number.isNaN(value)) return 'N/A'
    return `${(Number(value) * 100).toFixed(2)}%`
  }

  const MetricCard = ({ title, value, desc }) => (
    <div className='col-md-4 mb-3'>
      <div className='metric-card p-3 rounded bg-dark h-100'>
        <h6 className='text-info mb-1'>{title}</h6>
        <h4 className='text-light mb-1'>{value ?? 'N/A'}</h4>
        <p className='text-muted mb-0 small'>{desc}</p>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className='container text-center mt-5'>
        <FontAwesomeIcon icon={faSpinner} spin size='3x' className='text-info' />
        <p className='text-light mt-3'>Loading stock metrics...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className='container mt-5'>
        <div className='alert alert-danger'>{error}</div>
        <button className='btn btn-info' onClick={() => navigate('/dashboard')}>
          <FontAwesomeIcon icon={faArrowLeft} /> Back to Dashboard
        </button>
      </div>
    )
  }

  return (
    <div className='container mt-4'>
      <button className='btn btn-outline-info mb-4' onClick={() => navigate('/dashboard')}>
        <FontAwesomeIcon icon={faArrowLeft} /> Back to Dashboard
      </button>

      <div className='card bg-light-dark text-light'>
        <div className='card-header bg-dark'>
          <div className='d-flex justify-content-between align-items-start'>
            <div>
              <h2 className='text-info mb-0'>
                <FontAwesomeIcon icon={faChartLine} /> {stock.symbol}
                <span className='badge bg-secondary ms-2 fs-6'>{stock.exchange}</span>
              </h2>
              <small className='text-muted'>Last Updated: {new Date(stock.last_updated).toLocaleString()}</small>
            </div>
            {stock.current_price != null && (
              <div className='text-end'>
                <h2 className='text-success mb-0'>₹ {formatValue(stock.current_price)}</h2>
                {stock.fifty_two_week_high != null && stock.fifty_two_week_low != null && (
                  <small className='text-muted'>
                    52W: {formatValue(stock.fifty_two_week_low)} – {formatValue(stock.fifty_two_week_high)}
                  </small>
                )}
              </div>
            )}
          </div>
        </div>

        <div className='card-body'>
          {/* Valuation */}
          <h5 className='text-warning mb-3 border-bottom border-secondary pb-1'>Valuation</h5>
          <div className='row'>
            <MetricCard title='EPS (Trailing)' value={formatValue(stock.eps)} desc='Earnings per share (trailing 12m)' />
            <MetricCard title='EPS (Forward)' value={formatValue(stock.forward_eps)} desc='Expected earnings per share' />
            <MetricCard title='P/E (Trailing)' value={formatValue(stock.pe_ratio)} desc='Price relative to trailing earnings' />
            <MetricCard title='P/E (Forward)' value={formatValue(stock.forward_pe)} desc='Price relative to expected earnings' />
            <MetricCard title='Price/Book' value={formatValue(stock.price_to_book)} desc='Price relative to book value' />
            <MetricCard title='EV/EBITDA' value={formatValue(stock.ev_to_ebitda)} desc='Enterprise value to EBITDA' />
          </div>

          {/* Profitability */}
          <h5 className='text-warning mb-3 mt-3 border-bottom border-secondary pb-1'>Profitability & Returns</h5>
          <div className='row'>
            <MetricCard title='ROE' value={formatPercent(stock.roe)} desc='Return on equity' />
            <MetricCard title='ROA' value={formatPercent(stock.roa)} desc='Return on assets' />
            <MetricCard title='Gross Margin' value={formatPercent(stock.gross_margin)} desc='Gross profit margin' />
            <MetricCard title='Operating Margin' value={formatPercent(stock.operating_margin)} desc='Operating profit margin' />
            <MetricCard title='Profit Margin' value={formatPercent(stock.profit_margin)} desc='Net profit margin' />
            {stock.roce != null && <MetricCard title='ROCE' value={formatValue(stock.roce)} desc='Return on capital employed' />}
          </div>

          {/* Growth */}
          <h5 className='text-warning mb-3 mt-3 border-bottom border-secondary pb-1'>Growth</h5>
          <div className='row'>
            <MetricCard title='Revenue Growth' value={formatPercent(stock.revenue_growth)} desc='YoY revenue growth' />
            <MetricCard title='Earnings Growth' value={formatPercent(stock.earnings_growth)} desc='YoY earnings growth' />
          </div>

          {/* Risk & Balance */}
          <h5 className='text-warning mb-3 mt-3 border-bottom border-secondary pb-1'>Risk & Balance Sheet</h5>
          <div className='row'>
            <MetricCard title='Debt/Equity' value={formatValue(stock.debt_to_equity)} desc='Total debt relative to equity' />
            <MetricCard title='Current Ratio' value={formatValue(stock.current_ratio)} desc='Short-term liquidity ratio' />
            <MetricCard title='Beta' value={formatValue(stock.beta)} desc='Volatility vs market' />
            {stock.dividend_yield != null && <MetricCard title='Dividend Yield' value={formatPercent(stock.dividend_yield / 100)} desc='Annual dividend / price' />}
            {stock.market_cap != null && (
              <MetricCard title='Market Cap' value={'₹ ' + (stock.market_cap / 1e7).toFixed(0) + ' Cr'} desc='Total market capitalisation' />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default StockDetail

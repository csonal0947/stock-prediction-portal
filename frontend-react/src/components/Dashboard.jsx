import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSpinner, faChartLine } from '@fortawesome/free-solid-svg-icons'

const Dashboard = () => {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [exchangeFilter, setExchangeFilter] = useState('BOTH')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const navigate = useNavigate()

  useEffect(() => {
    fetchStocks()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [exchangeFilter, page])

  const fetchStocks = async (querySearch) => {
    const token = localStorage.getItem('accessToken')
    if (!token) {
      navigate('/login')
      return
    }

    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (exchangeFilter && exchangeFilter !== 'BOTH') params.append('exchange', exchangeFilter)
      params.append('page', page)
      params.append('page_size', 10)
      params.append('has_metrics', '1')
      const searchTerm = typeof querySearch !== 'undefined' ? querySearch : search
      if (searchTerm) params.append('search', searchTerm)

      const response = await axios.get(`http://127.0.0.1:8000/api/v1/stocks/?${params.toString()}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      setStocks(response.data.stocks || [])
      setTotalPages(response.data.pagination?.total_pages || 1)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching stocks:', err)
      if (err.response?.status === 401) {
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        navigate('/login')
      } else {
        setError('Failed to load stocks')
        setLoading(false)
      }
    }
  }

  const handleStockClick = (symbol, exchange) => navigate(`/stock/${symbol}?exchange=${encodeURIComponent(exchange || '')}`)

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    setPage(1)
    fetchStocks(search)
  }

  const handleExchangeChange = (e) => {
    setExchangeFilter(e.target.value)
    setPage(1)
  }

  if (loading) {
    return (
      <div className='container text-center mt-5'>
        <FontAwesomeIcon icon={faSpinner} spin size='3x' className='text-info' />
        <p className='text-light mt-3'>Loading stocks...</p>
      </div>
    )
  }

  return (
    <div className='container mt-4'>
      <div className='d-flex justify-content-between align-items-center mb-4'>
        <h2 className='text-light'>
          <FontAwesomeIcon icon={faChartLine} /> Stock Dashboard
        </h2>
        <div className='d-flex gap-2'>
          <select className='form-select' value={exchangeFilter} onChange={handleExchangeChange} style={{width: '140px'}}>
            <option value='BOTH'>Both</option>
            <option value='NSE'>NSE</option>
            <option value='BSE'>BSE</option>
          </select>
        </div>
      </div>

      {error && <div className='alert alert-danger'>{error}</div>}

      <form className='mb-3' onSubmit={handleSearchSubmit}>
        <div className='input-group'>
          <input type='text' className='form-control' placeholder='Search symbol...' value={search} onChange={(e) => setSearch(e.target.value)} />
          <button className='btn btn-info' type='submit'>Search</button>
        </div>
      </form>

      <div className='row'>
        {stocks.length > 0 ? stocks.map((stock) => (
          <div key={`${stock.symbol}-${stock.exchange}`} className='col-md-4 mb-3'>
            <div
              className='card bg-light-dark text-light h-100 stock-card'
              onClick={() => handleStockClick(stock.symbol, stock.exchange)}
              style={{ cursor: 'pointer' }}
            >
              <div className='card-body text-center'>
                <h4 className='card-title text-info'>{stock.symbol}</h4>
                <p className='card-text text-muted mb-1'>
                  {stock.exchange}
                </p>
                {stock.current_price != null
                  ? <h5 className='text-success mb-1'>₹ {Number(stock.current_price).toFixed(2)}</h5>
                  : <h5 className='text-muted mb-1'>Price N/A</h5>
                }
                <p className='card-text text-muted small'>
                  {stock.eps != null ? `EPS: ${Number(stock.eps).toFixed(2)}` : ''}
                  {stock.pe_ratio != null ? `  •  P/E: ${Number(stock.pe_ratio).toFixed(1)}` : ''}
                </p>
                <button className='btn btn-sm btn-outline-info'>View Metrics</button>
              </div>
            </div>
          </div>
        )) : (
          <div className='alert alert-warning'>No stocks available</div>
        )}
      </div>

      <div className='d-flex justify-content-between align-items-center mt-4'>
        <div className='text-muted'>Page {page} of {totalPages}</div>
        <div>
          <button className='btn btn-outline-light me-2' disabled={page <= 1} onClick={() => { setPage(page - 1) }}>Previous</button>
          <button className='btn btn-outline-light' disabled={page >= totalPages} onClick={() => { setPage(page + 1) }}>Next</button>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

import React from 'react'
import Button from './button'

const Main = () => {
  return (
    <>
    
    <div className='container'>
        <div className='p-5 text-center bg-light-dark rounded'>
            <h1 className='text-light'>Stock Prediction Portal</h1>
            <p className='text-light lead'>This Stock Prediction Portal making informed investment decisions shouldn't require years of financial expertise. Stock Prediction Portal bridges the gap between complex market data and actionable insights by providing users with easy-to-understand predictions, real-time stock data, 
            and powerful analytical tools — all in one place. it forecasts future stock prices by analyzing 100-days and 200-days moving averages, essential indicators widely used by stock analysts to inform trading and investment decisions. </p>
            <Button text='Login' class="btn-outline-warning"/>
        </div>

    </div>
   
    </>
  )
}

export default Main
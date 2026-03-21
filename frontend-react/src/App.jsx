import { useState } from 'react'
import './assets/css/style.css'
import Main from './components/Main'
import {BrowserRouter,Routes, Route} from "react-router-dom"
import Register from './components/Register'
import Header  from './components/Header'
import Footer from './components/Footer'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import StockDetail from './components/StockDetail'

function App() {
  
  return (
    <>
      <BrowserRouter>
      <Header/>
       <Routes>
         <Route path='/' element={<Main/>}/>
         <Route path='/register' element={<Register/>}/>
         <Route path='/login' element={<Login/>}/>
         <Route path='/dashboard' element={<Dashboard/>}/>
         <Route path='/stock/:symbol' element={<StockDetail/>}/>
       </Routes>
        <Footer/>
      </BrowserRouter>
     
      

    </>
  )
}

export default App

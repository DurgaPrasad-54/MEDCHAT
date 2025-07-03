import './App.css'
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom'
import Login from './componnts/Login'
import Register from './componnts/Register'
import Chat from './componnts/Chat'

function App() {

  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </Router>
    
    </>
  )
}

export default App

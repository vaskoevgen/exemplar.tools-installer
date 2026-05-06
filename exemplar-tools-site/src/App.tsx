import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import HomePage from './pages/HomePage'
import ToolPage from './pages/ToolPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-[#0a0a0f]">
        <Sidebar />
        <div className="flex-1 ml-56 min-h-screen">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/tool/:slug" element={<ToolPage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}

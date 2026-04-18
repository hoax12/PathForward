import { Navigate, Route, Routes } from 'react-router-dom'
import IntakePage from './pages/IntakePage'
import ResultsPage from './pages/ResultsPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<IntakePage />} />
      <Route path="/results/:sessionId" element={<ResultsPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

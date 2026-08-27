import { Routes, Route } from 'react-router-dom'
import './App.css'
import { AuthProvider } from './Context/AuthContext'
import RequireAuth from './Components/RequireAuth/RequireAuth'
import HomePage from './Pages/HomePage'
import AccountsPage from './Pages/AccountsPage'
import AccountDetailPage from './Pages/AccountDetailPage'
import AboutPage from './Pages/AboutPage'
import ContactPage from './Pages/ContactPage'
import LoginPage from './Pages/LoginPage'
import TransferPage from './Pages/TransferPage'
import AdminDashboardPage from './Pages/AdminDashboardPage'
import NotFoundPage from './Pages/NotFoundPage'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/accounts" element={<AccountsPage />} />
        <Route
          path="/accounts/:accountId"
          element={
            <RequireAuth>
              <AccountDetailPage />
            </RequireAuth>
          }
        />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/transfer"
          element={
            <RequireAuth>
              <TransferPage />
            </RequireAuth>
          }
        />
        <Route
          path="/admin"
          element={
            <RequireAuth>
              <AdminDashboardPage />
            </RequireAuth>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AuthProvider>
  )
}

export default App

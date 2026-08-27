import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { post } from '../api/client'

// Matches the shape your FastAPI /login endpoint returns.
type User = {
  user_id: number
  name: string
  email: string
  role: 'Admin' | 'Manager' | 'Staff' | 'Customer'
  branch_code: string | null
}

type AuthContextValue = {
  isLoggedIn: boolean
  customer: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)
const STORAGE_KEY = 'bankapp_customer'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [customer, setCustomer] = useState<User | null>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  })

  useEffect(() => {
    try {
      if (customer) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(customer))
      } else {
        localStorage.removeItem(STORAGE_KEY)
      }
    } catch {
      // ignore storage failures (e.g. private browsing)
    }
  }, [customer])

  async function login(email: string, password: string) {
    // If this throws (wrong password, network error, etc.), the caller's
    // try/catch handles it — customer stays null until it actually succeeds.
    const loggedInCustomer = await post<User>('/login', { email, password })
    setCustomer(loggedInCustomer)
  }

  function logout() {
    setCustomer(null)
  }

  return (
    <AuthContext.Provider value={{ isLoggedIn: customer !== null, customer, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

import { useEffect, useState } from 'react'
import { get } from '../../api/client'

// Matches the shape your FastAPI /accounts endpoint returns.
export type Account = {
  account_id: string
  owner_id: number
  balance: number
  branch_code: string
  account_type: 'Checking' | 'Savings'
  status: 'active' | 'inactive'
}

export function useAccounts(requestingUserId: number | undefined) {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    if (requestingUserId === undefined) {
      setAccounts([])
      return
    }

    // Guards against setting state after this effect has been superseded
    // (requestingUserId changed again, or the component unmounted) while
    // the fetch was still in flight.
    let cancelled = false
    setIsLoading(true)
    setError(null)

    get<Account[]>(`/accounts?requesting_user_id=${requestingUserId}`)
      .then((data) => {
        if (!cancelled) setAccounts(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load accounts.')
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [requestingUserId, reloadKey])

  function refetch() {
    setReloadKey((key) => key + 1)
  }

  return { accounts, isLoading, error, refetch }
}

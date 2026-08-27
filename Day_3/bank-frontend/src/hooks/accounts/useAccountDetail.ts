import { useEffect, useState } from 'react'
import { get } from '../../api/client'
import type { Account } from './useAccounts'

// Matches the shape entries in your FastAPI /accounts/{id}/transactions
// endpoint returns (Accounts model's transaction_history entries).
export type Transaction = {
  type: string
  amount: number
  status: string
  timestamp: number
}

export function useAccountDetail(accountId: string | undefined, requestingUserId: number | undefined) {
  const [account, setAccount] = useState<Account | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    if (!accountId || requestingUserId === undefined) {
      setAccount(null)
      setTransactions([])
      return
    }

    let cancelled = false
    setIsLoading(true)
    setError(null)

    Promise.all([
      get<Account>(`/accounts/${accountId}?requesting_user_id=${requestingUserId}`),
      get<Transaction[]>(`/accounts/${accountId}/transactions?requesting_user_id=${requestingUserId}`),
    ])
      .then(([accountData, transactionsData]) => {
        if (cancelled) return
        setAccount(accountData)
        // Newest first.
        setTransactions([...transactionsData].reverse())
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load account.')
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [accountId, requestingUserId, reloadKey])

  function refetch() {
    setReloadKey((key) => key + 1)
  }

  return { account, transactions, isLoading, error, refetch }
}

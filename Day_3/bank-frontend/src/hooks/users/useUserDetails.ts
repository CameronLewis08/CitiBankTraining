import { useEffect, useState } from 'react'
import { get } from '../../api/client'
import type { User } from './useUsers'

// Backend note: GET /users/{user_id} in app.py takes NO requesting_user_id -
// it's an unauthenticated lookup (unlike GET /accounts/{id}, which does
// require one). So this hook only needs userId, not a requesting user.
export function useUserDetail(userId: number | undefined) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    if (userId === undefined) {
      setUser(null)
      return
    }

    let cancelled = false
    setIsLoading(true)
    setError(null)

    // TODO: call get<User>(`/users/${userId}`) and set state from it.
    // Follow useAccountDetail.ts's shape - same cancelled-guard pattern,
    // same .then/.catch/.finally chain. No Promise.all needed here since
    // there's only one endpoint to hit (users don't have a transactions
    // sub-resource the way accounts do).
    get<User>(`/users/${userId}`)
      .then((data) => {
        if (!cancelled) setUser(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load user.')
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [userId, reloadKey])

  function refetch() {
    setReloadKey((key) => key + 1)
  }

  return { user, isLoading, error, refetch }
}

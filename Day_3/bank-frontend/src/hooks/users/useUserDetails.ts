import { useEffect, useState } from 'react'
import { get } from '../../api/client'
import type { User } from './useUsers'

// Backend note: GET /users/{user_id} now requires requesting_user_id and
// applies the same self/branch/admin scoping as GET /users
// (UsersService.view_user_profile) - it used to be a fully unauthenticated
// lookup, which made every user_id (a small sequential int) enumerable by
// anyone with no login at all.
export function useUserDetail(userId: number | undefined, requestingUserId: number | undefined) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    if (userId === undefined || requestingUserId === undefined) {
      setUser(null)
      return
    }

    let cancelled = false
    setIsLoading(true)
    setError(null)

    get<User>(`/users/${userId}?requesting_user_id=${requestingUserId}`)
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
  }, [userId, requestingUserId, reloadKey])

  function refetch() {
    setReloadKey((key) => key + 1)
  }

  return { user, isLoading, error, refetch }
}

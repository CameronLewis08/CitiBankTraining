import { useEffect, useState } from 'react'
import { get } from '../../api/client'

// Matches the shape your FastAPI /users endpoint returns (_serialize_user
// in app.py) - note it never includes password_hash.
export type User = {
  user_id: number
  name: string
  email: string
  role: 'Admin' | 'Manager' | 'Staff' | 'Customer'
  branch_code: string | null
}

export function useUsers(requestingUserId: number | undefined) {
  const [users, setUsers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    if (requestingUserId === undefined) {
      setUsers([])
      return
    }

    // Guards against setting state after this effect has been superseded
    // (requestingUserId changed again, or the component unmounted) while
    // the fetch was still in flight.
    let cancelled = false
    setIsLoading(true)
    setError(null)

    get<User[]>(`/users?requesting_user_id=${requestingUserId}`)
      .then((data) => {
        if (!cancelled) setUsers(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load users.')
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

  return { users, isLoading, error, refetch }
}

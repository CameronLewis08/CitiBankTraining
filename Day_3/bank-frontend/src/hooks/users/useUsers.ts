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

type PaginationOptions = {
  // Page size. Omit entirely for the old "fetch everything in one shot"
  // behavior - pagination is opt-in so non-dashboard callers, if any ever
  // show up, are unaffected.
  limit?: number
  search?: string
  // Server-side role filter (e.g. 'Manager') - also omit `limit` when using
  // this to get the complete matching set in one shot, for cases like
  // populating a "pick a manager" dropdown where a partial page would be
  // actively wrong, not just incomplete.
  role?: User['role']
}

export function useUsers(requestingUserId: number | undefined, options?: PaginationOptions) {
  const { limit, search, role } = options ?? {}

  const [users, setUsers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const [hasMore, setHasMore] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)
  const [skip, setSkip] = useState(0)

  const queryKey = `${requestingUserId}|${search ?? ''}|${role ?? ''}|${reloadKey}`
  const [lastQueryKey, setLastQueryKey] = useState(queryKey)
  if (queryKey !== lastQueryKey) {
    setLastQueryKey(queryKey)
    if (skip !== 0) setSkip(0)
  }

  useEffect(() => {
    if (requestingUserId === undefined) {
      setUsers([])
      return
    }

    let cancelled = false
    if (skip === 0) setIsLoading(true)
    else setIsLoadingMore(true)
    setError(null)

    const params = new URLSearchParams({ requesting_user_id: String(requestingUserId) })
    if (limit !== undefined) params.set('limit', String(limit))
    if (search) params.set('search', search)
    if (role) params.set('role', role)
    if (skip) params.set('skip', String(skip))

    get<User[]>(`/users?${params.toString()}`)
      .then((data) => {
        if (cancelled) return
        setUsers((previous) => (skip === 0 ? data : [...previous, ...data]))
        setHasMore(limit !== undefined && data.length === limit)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load users.')
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false)
          setIsLoadingMore(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [requestingUserId, limit, search, role, skip, reloadKey])

  function refetch() {
    setReloadKey((key) => key + 1)
  }

  function loadMore() {
    setSkip(users.length)
  }

  return { users, isLoading, isLoadingMore, hasMore, error, refetch, loadMore }
}

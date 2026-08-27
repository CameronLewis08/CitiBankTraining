import { useEffect, useState } from 'react'
import { get } from '../../api/client'

// Matches the shape your FastAPI /accounts endpoint returns.
export type Account = {
  account_id: string
  owner_id: number
  // Resolved server-side (one batch lookup per page, not stored on the
  // account itself) - see app.py's GET /accounts. Null if the owner
  // couldn't be resolved (shouldn't normally happen).
  owner_name: string | null
  balance: number
  branch_code: string
  account_type: 'Checking' | 'Savings'
  status: 'active' | 'inactive'
}

type PaginationOptions = {
  // Page size. Omit entirely for the old "fetch everything in one shot"
  // behavior (Home/Accounts/Transfer pages) - pagination is opt-in so
  // those callers are unaffected.
  limit?: number
  search?: string
}

// ownerId is optional and separate from requestingUserId on purpose:
// without it, GET /accounts falls back to the backend's role-based default
// (AccountsService.get_all_accounts) - Admin sees every account,
// Manager/Staff see their whole branch's. Pass ownerId explicitly to pin
// the results to one specific owner regardless of the caller's role - e.g.
// "just my own accounts" on the home page, even when logged in as Admin.
export function useAccounts(
  requestingUserId: number | undefined,
  ownerId?: number,
  options?: PaginationOptions,
) {
  const { limit, search } = options ?? {}

  const [accounts, setAccounts] = useState<Account[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const [hasMore, setHasMore] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)
  const [skip, setSkip] = useState(0)

  // Whenever who/what we're querying for changes (owner, search term, or an
  // explicit refetch), start back over at page one. Done inline during
  // render (React's documented "adjust state when a derived value changes"
  // pattern) instead of a useEffect, to avoid an extra render pass.
  const queryKey = `${requestingUserId}|${ownerId}|${search ?? ''}|${reloadKey}`
  const [lastQueryKey, setLastQueryKey] = useState(queryKey)
  if (queryKey !== lastQueryKey) {
    setLastQueryKey(queryKey)
    if (skip !== 0) setSkip(0)
  }

  useEffect(() => {
    if (requestingUserId === undefined) {
      setAccounts([])
      return
    }

    // Guards against setting state after this effect has been superseded
    // while the fetch was still in flight.
    let cancelled = false
    if (skip === 0) setIsLoading(true)
    else setIsLoadingMore(true)
    setError(null)

    const params = new URLSearchParams({ requesting_user_id: String(requestingUserId) })
    if (ownerId !== undefined) params.set('owner_id', String(ownerId))
    if (limit !== undefined) params.set('limit', String(limit))
    if (search) params.set('search', search)
    if (skip) params.set('skip', String(skip))

    get<Account[]>(`/accounts?${params.toString()}`)
      .then((data) => {
        if (cancelled) return
        setAccounts((previous) => (skip === 0 ? data : [...previous, ...data]))
        // The backend hands back a full page (length === limit) only when
        // another page might exist - a short page means we've hit the end.
        setHasMore(limit !== undefined && data.length === limit)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load accounts.')
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
  }, [requestingUserId, ownerId, limit, search, skip, reloadKey])

  function refetch() {
    setReloadKey((key) => key + 1)
  }

  function loadMore() {
    setSkip(accounts.length)
  }

  return { accounts, isLoading, isLoadingMore, hasMore, error, refetch, loadMore }
}

import { useEffect, useState } from 'react'
import { get } from '../../api/client'

// Matches the shape your FastAPI /branches endpoint returns
// (_serialize_branch in app.py).
export type Branch = {
  branch_code: string
  location: string
  manager_id: number | null
  staff_list: number[]
}

type PaginationOptions = {
  limit?: number
  search?: string
}

export function useBranches(requestingUserId: number | undefined, options?: PaginationOptions) {
  const { limit, search } = options ?? {}

  const [branches, setBranches] = useState<Branch[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const [hasMore, setHasMore] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)
  const [skip, setSkip] = useState(0)

  const queryKey = `${requestingUserId}|${search ?? ''}|${reloadKey}`
  const [lastQueryKey, setLastQueryKey] = useState(queryKey)
  if (queryKey !== lastQueryKey) {
    setLastQueryKey(queryKey)
    if (skip !== 0) setSkip(0)
  }

  useEffect(() => {
    if (requestingUserId === undefined) {
      setBranches([])
      return
    }

    let cancelled = false
    if (skip === 0) setIsLoading(true)
    else setIsLoadingMore(true)
    setError(null)

    const params = new URLSearchParams({ requesting_user_id: String(requestingUserId) })
    if (limit !== undefined) params.set('limit', String(limit))
    if (search) params.set('search', search)
    if (skip) params.set('skip', String(skip))

    get<Branch[]>(`/branches?${params.toString()}`)
      .then((data) => {
        if (cancelled) return
        setBranches((previous) => (skip === 0 ? data : [...previous, ...data]))
        setHasMore(limit !== undefined && data.length === limit)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load branches.')
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
  }, [requestingUserId, limit, search, skip, reloadKey])

  function refetch() {
    setReloadKey((key) => key + 1)
  }

  function loadMore() {
    setSkip(branches.length)
  }

  return { branches, isLoading, isLoadingMore, hasMore, error, refetch, loadMore }
}

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

export function useBranches(requestingUserId: number | undefined) {
  const [branches, setBranches] = useState<Branch[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (requestingUserId === undefined) {
      setBranches([])
      return
    }

    let cancelled = false
    setIsLoading(true)
    setError(null)

    get<Branch[]>(`/branches?requesting_user_id=${requestingUserId}`)
      .then((data) => {
        if (!cancelled) setBranches(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load branches.')
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [requestingUserId])

  return { branches, isLoading, error }
}

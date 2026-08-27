const base_url = import.meta.env.VITE_API_BASE_URL


// FastAPI's `detail` is usually a plain string, but on a request
// validation error (app.py's handle_validation_error) it's a list of
// Pydantic error objects instead - stringifying that directly (the old
// behavior here) produced "[object Object]" per item.
type ApiErrorBody = {
    detail?: string | { msg?: string }[]
}

function formatErrorDetail(detail: ApiErrorBody['detail']): string {
    if (!detail) return 'An error occurred'
    if (typeof detail === 'string') return detail
    return detail.map((item) => item?.msg ?? 'Invalid request').join('; ') || 'An error occurred'
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${base_url}${path}`, {
        ...options,
        headers: {
            ...options?.headers,
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        const errorBody: ApiErrorBody = await response.json().catch(() => ({}));
        throw new Error(formatErrorDetail(errorBody.detail));
    }

    return response.json() as Promise<T>;
}

export function get<T>(path: string): Promise<T> {
  return request<T>(path)
}

export function post<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function put<T>(path: string, body: any): Promise<T> {
    return request<T>(path, {
        method: 'PUT',
        body: JSON.stringify(body),
    });
}

// Named `del`, not `delete` - the latter is a reserved word and can't be
// used as a function name.
export function del<T>(path: string): Promise<T> {
    return request<T>(path, {
        method: 'DELETE',
    });
}



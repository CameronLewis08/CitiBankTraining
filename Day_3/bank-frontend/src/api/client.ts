const base_url = import.meta.env.VITE_API_BASE_URL


type ApiErrorBody = {
    detail?:string

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
        throw new Error(errorBody.detail || 'An error occurred');
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



# Day_3 Frontend — Architecture Reference

As of 2026-08-27. Companion to `day2-day3-codebase-notes.md`, focused specifically on
the hook/component/state pattern and end-to-end request flow, for reasoning about the
frontend without re-deriving it from source each time.

## Backend: Controller → Service → Repo → Model

Every resource (Users, Accounts, Branches) follows the same four-layer stack, and
requests always flow one direction — a layer never calls back up:

```
app.py (FastAPI routes)
    | resolves requesting_user_id -> Users object via _require_user
Controller (thin pass-through, e.g. UsersController)
    |
Service (permission checks live here, before any DB call)
    |
Repo (the only layer that touches MongoDB)
    |
Model (Users/Accounts/Branches - domain objects, business rules like overdraft/permission checks on mutation)
```

- `_require_user(requesting_user_id)` in `app.py` is the choke point every
  authenticated route runs through first — it resolves *who's asking* via
  `UsersService.get_user_by_id` (deliberately unauthenticated, since it's what identity
  resolution itself depends on) and 401s if the ID doesn't exist.
- Services own every permission rule — e.g. `UsersService.update_user` blocking
  non-Admins from changing `branch_code`, `AccountsService.get_all_accounts`
  branch-scoping Manager/Staff. Repos never make authorization decisions, only
  Services do.
- `PermissionError` -> 403 and `RequestValidationError` -> 400 are both global
  exception handlers registered once in `app.py`, so individual routes just `raise`
  and don't format responses themselves.

## Frontend: Page → Hook → api/client → Backend

```
Page component (owns UI state: search text, modal open/closed, form fields)
    | calls a hook
Hook (owns server state: the fetched data, isLoading, error, refetch)
    | calls
api/client.ts (get/post/put/del - thin fetch wrapper, formats FastAPI's error `detail`)
    |
Backend
```

Every list-fetching hook (`useUsers`, `useAccounts`, `useBranches`) follows the
identical shape: `useState` for the data array + `isLoading` + `error`, a `reloadKey`
counter that a `refetch()` function bumps to force a re-fetch, and a `useEffect` keyed
on its real params (plus `reloadKey`) that does the actual `get()` call with a
`cancelled` flag to avoid setting state after the component's moved on.

## Every hook

| Hook | Returns | Notes |
|---|---|---|
| `useAuth()` (Context, not a hook file) | `{ isLoggedIn, customer, login, logout, updateCustomer }` | `customer` is the logged-in `User`, persisted to `localStorage` so refresh doesn't log you out. `updateCustomer` is how ProfilePage pushes a saved edit back into the header/home page without a re-fetch. |
| `useUsers(requestingUserId, options?)` | `{ users, isLoading, isLoadingMore, hasMore, error, refetch, loadMore }` | `options: { limit, search }` opt-in - omit for "fetch everything" (unused by any page currently), pass it for real pagination (Admin Dashboard). |
| `useUserDetail(userId, requestingUserId)` | `{ user, isLoading, error }` | Backs the dashboard's user-detail modal; hits `GET /users/{id}`. |
| `useAccounts(requestingUserId, ownerId?, options?)` | `{ accounts, isLoading, isLoadingMore, hasMore, error, refetch, loadMore }` | `ownerId` pins results to one owner regardless of the caller's role (Home/Accounts/Transfer pass their own ID so Admin only sees their own accounts there). |
| `useAccountDetail(accountId, requestingUserId)` | `{ account, transactions, isLoading, error, refetch }` | One hook, two parallel fetches (`Promise.all`) - the account itself plus its transaction history, reversed to newest-first. |
| `useBranches(requestingUserId, options?)` | `{ branches, isLoading, isLoadingMore, hasMore, error, refetch, loadMore }` | Same pagination shape as the other two. |

## Every component

| Component | Purpose |
|---|---|
| `Layout` | Wraps every page: `Header` + page content + `Footer`. |
| `Header` | Sticky nav bar; shows `UserMenu` when logged in (Dashboard link only for non-Customer roles), login/signup links otherwise. |
| `UserMenu` | Name-triggered dropdown (Profile / Log Out), replaces the old plain logout button. |
| `RequireAuth` | Route guard - redirects to `/login` if `isLoggedIn` is false. Wraps every protected route in `App.tsx`. |
| `Table` (+ `.styled`) | Generic `Table/Thead/Tbody/Tr/Th/Td/EmptyRow` - every list page (dashboard's 3 tabs) builds on this, no per-page table CSS. |
| `FilterDropdown<T>` | Generic labeled `<select>`-like dropdown; used for the dashboard's Users/Accounts/Branches view switcher. |
| `Modal` | Generic overlay+card shell - open/close, Escape/backdrop-click to dismiss, optional footer. Everything else modal-shaped builds on this. |
| `ConfirmModal` | Built on `Modal` - the shared "are you sure, Cancel/Delete" pattern used for delete-user/account/branch and Close Account. |
| `Form.styled` (not a component, but central) | `FormGroup/Label/Input/Select/SubmitButton/ErrorMessage` - every form in the app (login, signup, profile, transfer, branch create/edit) is built from these same primitives. |

## Every page — key `useState`

- **`LoginPage`/`AboutPage`/`ContactPage`/`NotFoundPage`** - simple, mostly form-local
  state, nothing structurally interesting.
- **`HomePage`** - `useAccounts(customer.user_id, customer.user_id)`; no local state
  beyond what the hook gives it, just renders account cards with type/balance/id and a
  personalized "Welcome back, {name}" pill.
- **`AccountsPage`** - same `useAccounts` call, plus `OpenAccountForm`'s local form
  fields (`accountType`, `initialBalance`, etc.) and an `isSubmitting`/`formError` pair
  for the POST.
- **`AccountDetailPage`** - `useAccountDetail(accountId, customer.user_id)`; local
  state for deposit/withdraw amounts, `isClosingAccount` (drives the `ConfirmModal` for
  Close Account -> `del()` -> navigate away).
- **`TransferPage`** - `useAccounts` for the "from" dropdown (own accounts only) +
  local state for `fromAccountId`, `toAccountId` (free-text, any account), `amount`,
  `isSubmitting`, `error`/`success`.
- **`ProfilePage`** - local `name`/`email`/`branchCode` form fields seeded from
  `customer`, `isSubmitting`/`error`; branch dropdown only rendered for
  `role === 'Admin'`.
- **`AdminDashboardPage`** - the big one. Roughly:
  - `view: 'users' | 'accounts' | 'branches'` - active tab
  - `search` (raw input) + `debouncedSearch` (300ms-delayed, what actually hits the
    server)
  - Three hook instances (`useUsers`/`useAccounts`/`useBranches`) all fed
    `{ limit: 25, search: debouncedSearch }`
  - `viewUserId`/`viewAccount`/`viewBranch` - which row's detail modal is open
  - `isCreatingBranch` + `newBranchCode`/`newBranchLocation`/`newBranchManagerId` - New
    Branch modal
  - `editingBranch` + `editBranchLocation`/`editBranchManagerId` - Edit Branch modal
  - `deleteTarget: {kind, id, label} | null` - one shared state driving one
    `ConfirmModal` for deleting a user/account/branch
  - `statusUpdatingId` - which account's Activate/Deactivate button is mid-request

## End-to-end example: loading the Admin Dashboard and searching

1. You navigate to `/admin` -> `RequireAuth` checks `useAuth().isLoggedIn` (reads
   `customer` from Context, originally hydrated from `localStorage`).
2. `AdminDashboardPage` mounts, calls `useUsers(customer.user_id, { limit: 25 })` (and
   the accounts/branches equivalents).
3. Each hook's `useEffect` fires, builds `GET /users?requesting_user_id=1&limit=26`
   (backend requests `limit+1` to detect "more pages exist" without a separate count
   query), calls `client.ts`'s `get()`.
4. `app.py`'s `get_all_users` route resolves `requesting_user` via `_require_user`,
   calls `UsersController.get_all_users` -> `UsersService.get_all_users` (role-scopes:
   Admin sees all, Manager/Staff see their branch) -> `UsersRepository.get_all_users`
   (Mongo `find().skip().limit()`).
5. Response trims to 25, hook sets `users` state, `hasMore` becomes true if the 26th
   row came back.
6. You type in the search box -> `search` state updates every keystroke, but the
   `useEffect` debounce timer only commits it to `debouncedSearch` after 300ms of no
   typing.
7. `debouncedSearch` changing is one of the hook's dependencies -> each hook's internal
   "query key changed" check resets `skip` to 0 and re-fetches with `&search=...`,
   replacing (not appending) the current page.
8. Click "Load more" -> `loadMore()` sets `skip = users.length`, effect re-fires, new
   page's rows get **appended** to the existing array instead of replacing it.
9. Click a row -> `setViewUserId(user.user_id)` opens the `Modal`, which triggers
   `useUserDetail` to fetch that one user fresh via `GET /users/{id}` (permission-
   checked separately from the list endpoint, since profile enumeration was the whole
   reason that route got locked down earlier).

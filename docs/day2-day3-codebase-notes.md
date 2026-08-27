# Day_2 Backend / Day_3 Frontend — Codebase Notes

Investigation date: 2026-08-26, refreshed 2026-08-27. Primary sources are the source
files themselves (no external docs exist for these directories). All paths are
relative to the repo root.

> **2026-08-27 refresh note**: the original version of this doc (see git history)
> described a `Customers`-centric domain (flat customer CRUD, no roles). The backend
> has since been fully rewritten (commits `ab53b1a`..`062680d`, message "Refactored
> day 2 backend") to a role-based `Users`/`Branches`/`Accounts` domain model. The
> `Customers` model/service/repo/controller no longer exist. This revision documents
> the current state; see git log on this file for the superseded version.

## Overview

`Day_2/BackendWithRestApi/` is a **FastAPI** REST API for a toy banking domain, built
with a layered Controller → Service → Repo → Model architecture on top of MongoDB
(via `pymongo`). It now models four roles (Admin/Manager/Staff/Customer) across
Users, Branches, and Accounts, with role- and branch-scoped permission checks in the
Service layer, public self-signup, deposit/withdraw/transfer, and account
activate/deactivate.

`Day_3/bank-frontend/` is a **React 19 + TypeScript + Vite** single-page app
("Bank App") with `react-router-dom` v7 routing and `styled-components` for styling.
It has marketing-style pages (Home, About, Contact, Accounts) plus a combined
login/signup page, an authenticated account-detail page, and an authenticated
Transfer page, all talking to the FastAPI backend through a small typed `fetch`
wrapper. This directory is entirely untracked in git (never committed) but present
and functional on disk.

## Day_2 Backend

### Structure

```
Day_2/BackendWithRestApi/
  requirements.txt                 (pymongo, python-dotenv, fastapi, uvicorn, pytest, bcrypt, httpx)
  pytest.ini
  .env / .env.example              (MONGO_URI, MONGO_DB_NAME)
  CitiCollection.postman_collection_Cameron_Lewis.json
  src/main/Python/
    app.py                         (FastAPI app + all routes)
    main.py                        (console/demo script exercising the Controller/Service layer directly)
    Controllers/UsersController.py, BranchesController.py, AccountsController.py
    Services/UsersService.py, BranchesService.py, AccountsService.py
    Repos/UsersRepo.py, BranchesRepo.py, AccountsRepo.py
    Models/Users.py, Branches.py, Accounts.py
    Utilities/Database.py          (Mongo connection singleton, index setup)
    Utilities/SeedMongo.py         (one-time seed script)
    Utilities/Status.py            (OutcomeStatus, AccountType, AccountStatus, UserRole enums)
    tests/                         (pytest suite — see Testing section)
```

`requirements.txt` now includes `pytest` and `httpx` (needed for FastAPI's
`TestClient`) in addition to the original `pymongo`/`python-dotenv`/`fastapi`/
`uvicorn`/`bcrypt` — a real automated test suite now exists (see Testing below),
unlike the earlier version of this doc which found none.

### Entry point / run mode

`app.py` docstring still says to run with `uvicorn app:app --reload` (uvicorn's
default port 8000). CORS middleware (`app.py:29-35`) is unchanged:

```python
allow_origins=["http://localhost:5173"]
```

— exactly the Vite dev-server default origin.

### Domain model

Four `UserRole`s (`Utilities/Status.py`): `ADMIN`, `MANAGER`, `STAFF`, `CUSTOMER`.
Every `Users` document carries a `role` and an optional `branch_code`. `Branches`
have a `manager_id` and a `staff_list` of user IDs. `Accounts` belong to a
`branch_code` and an `owner_id` (a user), and are one of two concrete subclasses:

- `Models/Accounts.py`: abstract `Accounts` base class with `CheckingAccount`
  (allows a $500 overdraft, `OVERDRAFT_LIMIT`) and `SavingsAccount` (balance can
  never go negative). Every deposit/withdraw/transfer appends a dict to an in-memory
  `transaction_history` list that's persisted alongside the account document and
  exposed via `GET /accounts/{id}/transactions`. `build_account(...)` is a factory
  that picks the subclass from `AccountType`. Accounts also have an `AccountStatus`
  (`active`/`inactive`) — `deactivate_account`/`reactivate_account` block deposits
  and withdrawals while inactive.
- `Models/Users.py`: `Users(user_id, name, email, role, branch_code=None,
  password_hash=None)`. Validates email format, stores a bcrypt hash
  (`verify_password`). Permission checks that require an *acting* user (e.g.
  `set_role`, `set_branch_code`) live as methods here, taking the acting user as an
  argument — but in practice the Service layer (below) does its own role checks
  before ever calling into these, so this model-level layer is mostly redundant with
  the Service layer.
- `Models/Branches.py`: `Branches(branch_code, location, manager_id=None,
  staff_list=None)`. Accounts are **not** embedded — they live in their own
  collection with a `branch_code` field pointing back.

### Permission model (enforced in the Service layer, before any Repo/Mongo call)

This is the core addition since the last version of this doc. Every Service method
takes a `requesting_user` (a `Users` instance, resolved from `requesting_user_id` in
`app.py`'s `_require_user` helper) and checks its role/branch before delegating to
the Repo. Summary by resource:

- **Users** (`Services/UsersService.py`): `CUSTOMER`s cannot list all users
  (`get_all_users`). Creating a user normally requires `ADMIN`/`MANAGER`, **except**
  the public self-signup path — `POST /users` with no `requesting_user_id` skips the
  permission check entirely and force-overwrites any client-supplied `role` to
  `CUSTOMER` (`UsersService.create_user`, lines 30-34). Updating another user's
  `branch_code` requires `ADMIN`; updating anyone else's profile at all requires
  `ADMIN`/`MANAGER` (self-updates are always allowed). Deleting a user requires
  `ADMIN`/`MANAGER`. Searching users by branch requires `ADMIN`.
- **Branches** (`Services/BranchesService.py`): create/update/delete all require
  `ADMIN`. Reading branches has no role restriction (`get_all_branches` ignores
  `requesting_user` entirely — any authenticated user can list branches).
- **Accounts** (`Services/AccountsService.py`): the most granular scoping.
  - `CUSTOMER`s only ever see/act on their own accounts (`owner_id` forced to
    `requesting_user.get_user_id()` server-side on both reads and account creation,
    regardless of what the client sends).
  - `STAFF`/`MANAGER` are scoped to their own branch: listing without an `owner_id`
    returns their branch's accounts; passing an `owner_id` outside their branch
    raises `PermissionError`.
  - `ADMIN` has no scoping — can list/filter by any `owner_id` or see everything.
  - Deposit/withdraw/delete/status-change: `ADMIN`/`MANAGER`/`STAFF` can act on any
    account; a `CUSTOMER` can only act on an account it owns (verified via a
    branch/owner-scoped repo lookup before the mutation).
  - `transfer_funds`: staff roles can transfer from any account; non-staff can only
    transfer **out of** their own account (moving money **into** someone else's
    account is intentionally unrestricted — comment in
    `Repos/AccountsRepo.py:156-160`).
  - `search_accounts_by_branch` requires `ADMIN`.

`app.py` registers a `PermissionError` exception handler (lines 43-45) that maps
these to HTTP 403; `ValueError`s from the Service/Repo layers are mapped to 400 (or
401 for login) at each route.

### Endpoints (all defined in `app.py`)

Nearly every endpoint now requires a `requesting_user_id` (resolved server-side via
`_require_user`, which 401s if the ID doesn't match a known user) — the sole
exception is public signup.

| Method | Path                          | Notes |
|--------|-------------------------------|-------|
| POST   | `/login`                      | `{email, password}`; 401 on failure; returns serialized user (no token) |
| GET    | `/users`                      | Requires `requesting_user_id`; 403 for `CUSTOMER` |
| GET    | `/users/{user_id}`             | No auth required; 404 if missing |
| POST   | `/users`                       | `requesting_user_id` **optional** — omit it for public self-signup (role forced to Customer); include it to have an Admin/Manager create a user with an explicit role |
| PUT    | `/users/{user_id}`             | Self-update or Admin/Manager; branch_code change on another user requires Admin |
| DELETE | `/users/{user_id}`             | Admin/Manager only |
| GET    | `/branches`                    | Any authenticated user |
| POST   | `/branches`                    | Admin only |
| PUT    | `/branches/{branch_code}`      | Admin only |
| DELETE | `/branches/{branch_code}`      | Admin only |
| GET    | `/branches/{branch_code}/accounts` | Admin only (search by type/status) |
| GET    | `/branches/{branch_code}/users`    | Admin only (search by role/name) |
| GET    | `/accounts`                    | Optional `owner_id` query param; scoping per role (see above) |
| GET    | `/accounts/{account_id}`       | 404 if not found or not visible to requester |
| POST   | `/accounts`                    | `{account_id?, owner_id?, balance, branch_code, account_type, requesting_user_id}` — `account_id` auto-generated (`ACC-xxxxxxxx`) if omitted; Customers' `owner_id` is always forced to themselves |
| POST   | `/accounts/{account_id}/deposit`   | `{amount, requesting_user_id}` |
| POST   | `/accounts/{account_id}/withdraw`  | `{amount, requesting_user_id}` |
| GET    | `/accounts/{account_id}/transactions` | Returns the account's `transaction_history` |
| POST   | `/accounts/{account_id}/deactivate` | Staff roles only |
| POST   | `/accounts/{account_id}/reactivate` | Staff roles only |
| DELETE | `/accounts/{account_id}`       | Staff roles only |
| POST   | `/accounts/transfer`           | `{requesting_user_id, from_account_id, to_account_id, amount}` |

There is still **no explicit `/logout` endpoint** and **no JWT/session token** —
see Auth Flow below, which is otherwise materially unchanged from the previous
version of this doc.

### Persistence layer (MongoDB via `Utilities/Database.py`)

`get_database()` now creates unique indexes on `users.user_id`, `users.email`,
`branches.branch_code`, and `accounts.account_id` (previously: `customers.customer_id`,
`customers.email`, `accounts.account_id`).

- `Repos/UsersRepo.py`: CRUD against `users`; translates `DuplicateKeyError` into a
  `ValueError` distinguishing duplicate email vs. duplicate ID. Also has
  `get_user_by_email` (used by login) and `search_users_by_branch`.
- `Repos/BranchesRepo.py`: straightforward CRUD against `branches`.
- `Repos/AccountsRepo.py`: CRUD + `deposit`/`withdraw`/`transfer_funds`/`set_status`
  against `accounts`. Same "ownership-scoped lookup fails closed and
  indistinguishably" pattern as before (`get_account_by_id` with an `owner_id`
  narrows the Mongo query so someone else's account looks like a 404), now also
  used to scope deposit/withdraw/delete for non-staff callers. `transfer_funds`
  still only restricts the **source** account's owner, not the target's.

### Services / Controllers

`Services/UsersService.py`, `BranchesService.py`, and `AccountsService.py` hold all
the permission-check business logic described above (this is new — the old
`CustomersService`/`AccountsService` were thin pass-throughs plus password hashing).
`Controllers/UsersController.py`, `BranchesController.py`, and
`AccountsController.py` remain thin pass-throughs to their Services — the
"Controller" layer still does not touch HTTP (that's entirely in `app.py`).

`user_id` generation: `UsersService.create_user` computes
`max(existing_ids, default=0) + 1` by scanning all users on every create
(`UsersService.py:43-45`) when the client doesn't supply one — a full-collection
scan with a real (if low-probability in this training context) race condition
under concurrent signups, and no Mongo-native autoincrement. `account_id`
generation (`AccountsService._generate_account_id`) instead uses
`secrets.token_hex(4)` with a collision-check retry loop, which does not have the
same race condition.

### Seed data (`Utilities/SeedMongo.py`)

Now seeds 7 users (one per role, two Managers/Staff across two branches) sharing
password `password123`, 2 branches (`BR001` "Downtown Chicago", `BR002` "Uptown
Chicago"), and 3 accounts (2 Checking/Savings for a `BR001` customer, 1 Checking for
a `BR002` customer) — all upserted via `update_one(..., upsert=True)`.

### Testing

A real `tests/` directory now exists under `src/main/Python/`, run via `pytest.ini`
+ `pytest`/`httpx` in `requirements.txt` (previously: no automated tests at all,
only the `main.py` console script). Files:

- `test_accounts_model.py`, `test_branches_model.py`, `test_users_model.py` — model
  unit tests.
- `test_accounts_service.py`, `test_branches_service.py`, `test_users_service.py` —
  Service-layer permission-check tests (Repo layer monkeypatched, DB-free).
- `test_app_authorization.py` — HTTP-layer tests against `app.py` via FastAPI's
  `TestClient`, covering the role/ownership permission gates end-to-end.
- `test_app_users_signup.py` — HTTP-layer test proving `POST /users` without
  `requesting_user_id` succeeds unauthenticated and always forces `role: Customer`
  regardless of what the client sends (guards against a signup-path privilege
  escalation).
- `test_status.py` — enum sanity tests.

All Service/HTTP tests follow the same pattern: monkeypatch the Repo layer's static
methods rather than hitting real MongoDB, keeping the suite DB-free.

### Other backend notes

- `main.py` is still a standalone console script exercising the Controller/Service
  layer directly, now updated for the Users/Branches/Accounts domain; still not part
  of the automated suite but no longer the *only* test coverage.
- `.env` (gitignored, not in git history) still contains a live MongoDB Atlas
  connection string — same live-secret-on-disk caveat as before.
- `.env.example` still documents `MONGO_URI`, `MONGO_DB_NAME`.

## Day_3 Frontend

### Structure

```
Day_3/bank-frontend/                (entirely untracked in git — see note below)
  package.json, vite.config.ts, tsconfig*.json, eslint.config.js, README.md
  .env                              (VITE_API_BASE_URL)
  src/
    main.tsx, App.tsx, App.css, index.css
    api/client.ts                   (fetch wrapper)
    Context/AuthContext.tsx         (login/logout/session state)
    hooks/useAccounts.ts            (GET /accounts?requesting_user_id=)
    hooks/useAccountDetail.ts       (GET /accounts/{id} + /accounts/{id}/transactions) — NEW
    hooks/useBranches.ts            (GET /branches?requesting_user_id=) — NEW
    data/accounts.ts                (formatCurrency utility only)
    Components/
      Layout/, Header/, Footer/, RequireAuth/, PageHero/, Form/, Card/, Button/
    Pages/
      HomePage.tsx, AccountsPage.tsx, AccountDetailPage.tsx (NEW), TransferPage.tsx,
      LoginPage.tsx, AboutPage.tsx, ContactPage.tsx, NotFoundPage.tsx
```

**Git status note**: unlike the backend (which has real commit history — see the
refresh note at the top), the entire `Day_3/bank-frontend/` directory shows as
untracked (`git status`) with no commits — it exists and works on disk but has never
been added to the repo.

### Routing / pages (`src/App.tsx`)

| Path | Component | Auth-gated? |
|------|-----------|-------------|
| `/` | `HomePage` | No |
| `/accounts` | `AccountsPage` | No |
| `/accounts/:accountId` | `AccountDetailPage` | **Yes** — new since last version |
| `/about` | `AboutPage` | No |
| `/contact` | `ContactPage` | No |
| `/login` | `LoginPage` | No |
| `/transfer` | `TransferPage` | **Yes** |
| `*` | `NotFoundPage` | — |

`RequireAuth` is unchanged: redirects to `/login` if `useAuth().isLoggedIn` is
false (client-side route guard only).

### API integration

- `src/api/client.ts`: unchanged shape (`get`/`post`/`put` typed `fetch` wrapper
  reading `VITE_API_BASE_URL`, throwing on FastAPI's `{"detail": ...}` error shape).
- `Day_3/bank-frontend/.env`: still `VITE_API_BASE_URL=http://localhost:8000`,
  consistent with the backend's uvicorn default and CORS allow-list.
- `src/Context/AuthContext.tsx`: `User` type now includes `role` and `branch_code`
  (matching the new `/login` response shape), otherwise unchanged — still stores the
  plain login response in React state + `localStorage` (`bankapp_customer`), still
  no token.
- **Signup is now wired up** (previously a stub): `LoginPage.tsx`'s
  `handleSignup` (lines 48-72) calls `post('/users', { name, email, password })`
  with no `role`/`requesting_user_id`, matching the backend's public self-signup
  path, then immediately calls `login(email, password)` and navigates home. The
  earlier version of this doc flagged this as an unwired TODO — that gap is closed.
- `src/hooks/useAccounts.ts`: now calls `GET /accounts?requesting_user_id=` (was
  `customer_id=`), matching the renamed backend param; takes `requestingUserId`
  rather than `customerId`.
- `src/hooks/useAccountDetail.ts` (**new**): fetches a single account plus its
  transaction history in parallel via `Promise.all`, used by the new
  `AccountDetailPage`.
- `src/hooks/useBranches.ts` (**new**): fetches `GET /branches`, present but not yet
  obviously wired into a page in the files read for this note — worth confirming
  where it's consumed if you touch branch-related UI.
- `src/Pages/TransferPage.tsx`: sends `{requesting_user_id, from_account_id,
  to_account_id, amount}` (renamed from `customer_id`), otherwise same shape/flow as
  before, still keyed off `customer.user_id` from `AuthContext`.
- The previously-noted debug leftover in `App.tsx` (`useEffect` fetching
  `/customers` and `console.log`-ing on every mount) is **gone** — `App.tsx` is now
  just route declarations, no stray fetch. (It couldn't have kept working anyway
  since `/customers` no longer exists.)

### Notable patterns (unchanged from previous version)

- Hand-matched, independently-duplicated response-shape types across
  `AuthContext.tsx`/`useAccounts.ts`/`useAccountDetail.ts`/`useBranches.ts` rather
  than a shared types module.
- No dev-server proxy (`vite.config.ts` is the default scaffold) — relies on CORS +
  `VITE_API_BASE_URL`.
- `styled-components` throughout (`*.styled.ts` files alongside components/pages).

## Frontend-Backend Connection & Auth Flow

- **Ports/origins still line up correctly**: backend `:8000`, frontend
  `VITE_API_BASE_URL=http://localhost:8000`, backend CORS `allow_origins` exactly
  `http://localhost:5173`.
- **Login**: unchanged shape of flow, now returns `{user_id, name, email, role,
  branch_code}` instead of the old `{customer_id, name, email}`.
- **Signup**: now fully wired end-to-end (see above) — this closes Gap #2 from the
  previous version of this doc.
- **Still no token-based session**: `POST /login` returns a plain object, no JWT/
  cookie/auth header. The frontend re-sends `requesting_user_id` as a plain
  query/body field on every request. The backend's permission checks are real and
  much more thorough now (role + branch scoping, not just "does this ID match"), but
  they still trust a **client-supplied** `requesting_user_id` with nothing
  cryptographically binding it to whoever actually logged in — anyone hitting the
  API directly (curl/Postman) can claim to be any `user_id` they know. This is the
  same category of gap as before, just sitting on a more sophisticated
  authorization layer now.

## Gaps / Mismatches / Incomplete Items (current)

1. **No real auth/session security**: still the single biggest gap — see Auth Flow
   above. Role/branch permission logic is now solid; identity verification
   underneath it is not.
2. **`user_id` generation race/scan** (`UsersService.py:43-45`): `max(existing)+1`
   over a full collection scan, no atomic Mongo counter. Low-stakes in a training
   context but worth knowing if this ever needs to handle concurrent signups. (See
   chat history for a sketched fix using an atomic `$inc` counter document, not yet
   implemented.)
3. **`Day_3/bank-frontend/` has no git history**: the entire directory is untracked
   on the `React_Frontend_` branch. Nothing is lost since it's present on disk, but
   it isn't committed/backed up in git yet.
4. **`useBranches.ts` consumption unconfirmed**: exists and looks correctly wired to
   `GET /branches`, but this note didn't trace which page(s) actually call it —
   check before assuming it's dead code or live.
5. **`Models/Users.py`/`Models/Branches.py` permission methods are likely redundant**:
   methods like `Users.set_role`, `Branches.set_manager`/`set_location` take an
   acting user and re-check roles, but the Service layer already gates these calls
   before they're ever reached — two places doing the same authorization check is a
   maintenance hazard if they ever drift.
6. **`data/accounts.ts` is still not account data** — just `formatCurrency`, same
   naming leftover noted previously.
7. **Live secret on disk**: `Day_2/BackendWithRestApi/.env` still contains a real
   MongoDB Atlas URI with embedded credentials (gitignored, not in history).
8. **Task-brief mismatch** (historical, unchanged): the actual backend is FastAPI,
   not Flask, if any brief assumed otherwise.

### Resolved since the previous version of this doc

- ~~Signup entirely unwired~~ — now wired (`LoginPage.tsx`).
- ~~Debug leftover in `App.tsx`~~ — removed.
- ~~`GET /accounts` required-param mismatch~~ — `owner_id`/`requesting_user_id` are
  consistently optional/handled across `app.py`/Controller/Service/Repo now; no
  unreachable "list all" capability gap found in this pass (Admin gets that
  behavior legitimately via `GET /accounts` with no `owner_id`).
- ~~No automated test suite~~ — a real pytest suite now exists (see Testing above).
- ~~`Customers` model's in-memory account list dead code~~ — moot; `Customers` no
  longer exists, replaced by `Users` which has no such list.

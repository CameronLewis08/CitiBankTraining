# Day_2 Backend Domain Rewrite — Design Spec

Date: 2026-08-26
Status: Approved by user, ready for implementation planning
Sub-project 1 of 2 (Day_2 backend). Sub-project 2 (Day_3 frontend rebuild) follows once this lands.

## Context

`Day_1/Banking_Domain_console_app` is a console app with a rich domain model: a `Bank`
owning `Branches`, `Branches` owning `Accounts`, and `Users` with roles
(Admin/Manager/Staff/Customer) whose methods enforce role-based permissions
(`PermissionError` on violation). Accounts are polymorphic (`CheckingAccount` with a
$500 overdraft limit, `SavingsAccount` with none), track a transaction history, and
have an active/inactive status.

`Day_2/BackendWithRestApi` is a FastAPI + MongoDB REST API that reimplemented only a
thin slice of this: a flat `Customers` (customer_id, name, email, password_hash) and
`Accounts` (account_id, customer_id, balance) — no roles, no branches, no account
types, no transaction history, no active/inactive state. See
`docs/day2-day3-codebase-notes.md` for the full prior investigation of Day_2/Day_3 as
they exist today.

The user wants Day_2 rebuilt to have the same functional richness as Day_1 (full
domain model: roles, branches, account types, transaction history, active/inactive
accounts), while keeping the FastAPI/MongoDB REST layer. This is a **clean-break**
rewrite — breaking API/schema changes are acceptable, existing Mongo collections can
be dropped and reseeded. Email-based login (Day_2's current approach) is kept; Day_1's
username-based login is not restored.

A companion sub-project will later update Day_3 (frontend) to match — role-based
views, branch management UI, account-type selection, transaction history display —
but that is out of scope for this spec and gets its own design.

## Goals

1. Port Day_1's domain richness (roles/permissions, branches, account types +
   overdraft rules, transaction history, active/inactive accounts) onto Day_2's
   existing layered architecture (Controller → Service → Repo → Model) and MongoDB
   persistence.
2. Keep the existing layering pattern intact — extend it, don't restructure it
   (Approach 1, chosen over collapsing Controller+Service).
3. Enforce permissions server-side using the *stored* role of the requesting user
   (looked up from Mongo), never a client-asserted role — closing the role-spoofing
   gap while accepting the existing, already-documented `requesting_user_id`
   trust model (same shape as today's `customer_id` trust model).
4. Keep email-based login.

## Non-goals

- Token/session-based authentication (JWT, cookies). Explicitly deferred — the
  existing trust model (client sends an id, server treats it as "who's asking") is
  kept, just extended to look up a real stored role instead of trusting an
  asserted one.
- Any Day_3 frontend changes (separate sub-project).
- Preserving backward compatibility with the current `/customers` API shape — this is
  an intentional breaking rewrite.

## Data model / MongoDB schema

### `users` collection (replaces `customers`)

| Field | Type | Notes |
|---|---|---|
| `user_id` | int | PK, replaces `customer_id` |
| `name` | str | |
| `email` | str | unique index, login identifier |
| `password_hash` | str | bcrypt, unchanged mechanism from today |
| `role` | str enum | `Admin` / `Manager` / `Staff` / `Customer` |
| `branch_code` | str, nullable | `None` for Admin; required for Manager/Staff/Customer |

### `branches` collection (new)

| Field | Type | Notes |
|---|---|---|
| `branch_code` | str | PK |
| `location` | str | |
| `manager_id` | int, nullable | references a `users.user_id` with role Manager |
| `staff_list` | list[int] | user_ids of staff assigned to this branch |

### `accounts` collection (extended)

| Field | Type | Notes |
|---|---|---|
| `account_id` | str | PK, unchanged |
| `owner_id` | int | renamed from `customer_id`, references `users.user_id` |
| `account_type` | str enum | `Checking` / `Savings`, chosen at creation, immutable after |
| `balance` | float | non-negative for Savings; may go to -500 for Checking (overdraft) |
| `status` | str enum | `active` / `inactive` |
| `branch_code` | str | references `branches.branch_code` |
| `transaction_history` | list[dict] | embedded array: `{type, amount, status, timestamp}` |

## Layered modules (Approach 1: extend existing pattern)

### Models

- **`Models/Users.py`**: `role` field, `authenticate(email, password)` (bcrypt,
  replaces Day_1's username-based check), `set_role(staff, new_role)` /
  `set_branch_code(staff, new_branch_code)` gated by caller's role — direct port of
  Day_1's `Users` methods, swapped to email identity.
- **`Models/Branches.py`**: direct port of Day_1's `Branches` — `get_manager_id`,
  `get_staff_list`, `add_account`/`remove_account`/`get_account(s)`, `set_manager`,
  `set_location`, same permission gates (Customer can't view manager/staff list,
  only Admin can change location).
- **`Models/Accounts.py`**: becomes an abstract `Accounts` base +
  `CheckingAccount`/`SavingsAccount` subclasses (port of Day_1's hierarchy,
  `Overdraft_limit = 500`), gains `transaction_history`, `status`,
  `deposit`/`withdraw`/`transfer` returning `{status, type, amount}` dicts (matching
  Day_1's return shape) instead of raising/returning bare values,
  `deactivate_account`/`reactivate_account`.

### Repos

- **`Repos/UsersRepo.py`** (new, replaces `CustomersRepo.py`): CRUD against `users`,
  same duplicate-key → `ValueError` translation pattern as today.
- **`Repos/BranchesRepo.py`** (new): CRUD against `branches`.
- **`Repos/AccountsRepo.py`** (extended): handles new fields
  (`account_type`, `status`, `branch_code`, `transaction_history`), keeps the
  existing ownership-scoped-lookup pattern but renamed `customer_id` →
  `owner_id`/`requesting_user_id` throughout.

### Services

- **`Services/UsersService.py`** (new, replaces `CustomersService.py`): same
  password-hashing-on-create and email-based login pass-through as today's
  `CustomerService`, plus **all new permission checks** live here (mirrors Day_1's
  `Bank` methods): `create_user` requires caller role Admin/Manager,
  `remove_user` requires Admin/Manager, role/branch changes gated per Model rules.
- **`Services/BranchesService.py`** (new): `create_branch`/`remove_branch` require
  Admin; `get_branch(es)` requires non-Customer caller — direct port of Day_1's
  `Bank.create_branch`/`remove_branch`/`get_branch_codes` permission logic.
- **`Services/AccountsService.py`** (extended): `create_account` requires
  Admin/Manager/Staff (port of Day_1's `Bank.create_account`), account-type
  branching (`CheckingAccount` vs `SavingsAccount`), deposit/withdraw/transfer
  delegate to the Model methods and surface their status-dict results,
  deactivate/reactivate pass-throughs.

**Permission-check convention**: every Service method that enforces a role
requirement takes the resolved acting `Users` object (looked up server-side by
`requesting_user_id`, never trusted from the client's claimed role) as its first
argument, exactly like Day_1's `Bank`/`Branches` methods take `staff`/`user`. Raises
`PermissionError` with a descriptive message on violation.

### Controllers

- `Controllers/UsersController.py` (new, replaces `CustomersController.py`),
  `Controllers/BranchesController.py` (new), `Controllers/AccountsController.py`
  (extended) — all stay thin pass-throughs to their Service, as today.

## REST API surface (`app.py`)

All protected endpoints add a `requesting_user_id: int` field (POST/PUT bodies) or
query param (GET/DELETE), matching the existing `customer_id`-as-query-param
convention. The endpoint handler resolves that id to a `Users` object via
`UsersService`/`UsersRepo` and passes it into the Service call, which enforces the
role check.

| Method | Path | Notes |
|---|---|---|
| POST | `/login` | body `{email, password}`; response now includes `role`, `branch_code` |
| GET | `/users` | requires `requesting_user_id` of a non-Customer |
| GET | `/users/{user_id}` | |
| POST | `/users` | body includes `role`, `branch_code`, `requesting_user_id`; Admin/Manager only |
| PUT | `/users/{user_id}` | profile/role/branch updates, permission-gated per field |
| DELETE | `/users/{user_id}` | requires `requesting_user_id` of Admin/Manager |
| GET | `/branches` | requires `requesting_user_id` of a non-Customer |
| POST | `/branches` | Admin only |
| PUT | `/branches/{branch_code}` | location/manager updates, Admin only (manager assignment) |
| DELETE | `/branches/{branch_code}` | Admin only |
| GET | `/accounts` | unchanged shape, `owner_id` replaces `customer_id` |
| GET | `/accounts/{account_id}` | unchanged shape |
| POST | `/accounts` | body gains `account_type`, `branch_code`; requires `requesting_user_id` of Admin/Manager/Staff |
| PUT | `/accounts/{account_id}` | balance updates via explicit deposit/withdraw, not direct balance PUT (see below) |
| DELETE | `/accounts/{account_id}` | requires `requesting_user_id` of Admin/Manager/Staff |
| POST | `/accounts/{account_id}/deposit` | new; body `{amount}` |
| POST | `/accounts/{account_id}/withdraw` | new; body `{amount}` |
| POST | `/accounts/transfer` | unchanged path, response becomes a status dict |
| GET | `/accounts/{account_id}/transactions` | new; returns `transaction_history` |
| POST | `/accounts/{account_id}/deactivate` | new; Admin/Manager/Staff only |
| POST | `/accounts/{account_id}/reactivate` | new; Admin/Manager/Staff only |

Note: today's `PUT /accounts/{id}` directly overwrites `balance`. That's replaced by
explicit `/deposit` and `/withdraw` endpoints so the overdraft/no-negative-balance
rules and transaction history are always applied consistently, matching how Day_1
never allows direct balance mutation outside `deposit`/`withdraw`/`transfer`.

## Error handling

- `ValueError` → HTTP 400 (existing pattern, unchanged).
- **New**: `PermissionError` → HTTP 403, via a new `@app.exception_handler` in
  `app.py`, mirroring the existing `RequestValidationError` handler.
- Not-found → HTTP 404 (existing pattern, unchanged).

## Seed data

`Utilities/SeedMongo.py` rewritten to mirror Day_1's `seed_data.py` structure and
credentials style, adapted to email logins:

- 1 Admin (no branch)
- 2 branches
- 2 Managers (one per branch), assigned as branch manager
- 2 Staff (one per branch)
- 2 Customers, each with a Checking + Savings account, in their respective branch
- A printed credentials summary (email/password/role) analogous to Day_1's
  `SEED_CREDENTIALS`, for manual testing convenience.

## Testing

No automated test suite exists in Day_2 today (confirmed prior investigation). This
rewrite adds `pytest` unit tests for the Service-layer permission checks, since RBAC
logic fails silently when wrong and is easy to regress. Scope: one test module per
new/changed Service (`test_users_service.py`, `test_branches_service.py`,
`test_accounts_service.py`) covering the role-gated methods (e.g. "Staff cannot
create a branch", "Customer cannot view another user's accounts", "Checking account
can overdraft to -500, Savings cannot go negative"). Integration/HTTP-level testing
of `app.py` is out of scope for this pass — Service-layer coverage is the priority
given that's where the new logic lives.

## Migration / rollout

Since this is a clean break: drop the `customers` collection (or leave it
orphaned/unused — user's call at implementation time), create `users`/`branches`
collections fresh, run the rewritten `SeedMongo.py`. The existing `.env`/Mongo
connection setup (`Utilities/Database.py`) is unchanged. The standalone
`src/main/Python/main.py` demo script should be updated to exercise the new
Service-layer surface (roles, branches, account types) the same way it exercises
today's Customers/Accounts surface, as informal smoke coverage alongside the new
pytest suite.

## Explicitly out of scope for this spec

- Day_3 frontend changes (sub-project 2, separate spec).
- Token/session-based auth.
- Any change to the CORS/port setup already documented as working
  (`docs/day2-day3-codebase-notes.md`).

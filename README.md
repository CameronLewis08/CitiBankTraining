# Bank App

A full-stack toy banking application: a role-based REST API backend and a React
single-page frontend, built as a training project. It models four user roles
(Admin, Manager, Staff, Customer) across Users, Branches, and Accounts, with
role- and branch-scoped permissions enforced end to end.

This is the `Day_2` (backend) + `Day_3` (frontend) pairing in this repo. `Day_1`
is an earlier console-only iteration of the same domain model and isn't part
of this app.

## What it can do

**Every logged-in user**, regardless of role, can:
- Sign up / log in
- View their own accounts and open new ones (Checking or Savings)
- Deposit, withdraw, and transfer money (including to another user's account
  by account ID)
- View an account's transaction history
- Update their own name/email from a Profile page

**Staff, Manager, and Admin** additionally get a **Dashboard**
(`/admin` — "Branch Dashboard" for Staff/Manager, "Admin Dashboard" for Admin)
to look up and manage:
- **Users** — search, view profile detail, delete (Admin/Manager)
- **Accounts** — search, view detail, activate/deactivate, delete
- **Branches** (**Admin only**) — search, view detail, create, edit, delete

Permission scoping throughout:
- **Customer** — sees only their own accounts/profile.
- **Staff / Manager** — scoped to their own branch for the dashboard's
  Users/Accounts lists, but can always view/manage their *own* account(s)
  regardless of which branch those were opened at.
- **Admin** — unrestricted; only Admin can create/edit/delete branches or
  change a user's assigned branch.

Business rules worth knowing:
- Checking accounts allow a $500 overdraft; Savings accounts never go
  negative.
- A deactivated account blocks deposits, withdrawals, and transfers (both as
  sender and recipient) with an explicit "contact the bank" message, but can
  still be viewed and reactivated.
- A Customer's home branch is auto-assigned from the branch of their first
  opened account.

## Tech stack

**Backend** (`Day_2/BackendWithRestApi`)
- **Python 3.13**, **FastAPI** (REST API + automatic request validation),
  **uvicorn** (ASGI server)
- **MongoDB** via **pymongo** (no ORM — direct collection queries)
- **bcrypt** for password hashing
- **pytest** + **httpx** for testing (unit tests on the Service layer, plus
  black-box tests against the FastAPI app)
- Layered architecture: `Controller → Service → Repo → Model`, with every
  permission check living in the Service layer before any database call

**Frontend** (`Day_3/bank-frontend`)
- **React 19** + **TypeScript**, built with **Vite**
- **react-router-dom v7** for routing
- **styled-components** for all styling (no CSS files, no inline styles)
- **ESLint** (flat config, `typescript-eslint`, `react-hooks`) for linting
- Plain `fetch` wrapper (`src/api/client.ts`) — no data-fetching library;
  one custom hook per backend resource owns its own loading/error/refetch
  state

## Project structure

```
Day_2/BackendWithRestApi/
  src/main/Python/
    app.py                 FastAPI routes, request/response models
    Controllers/            Thin pass-through to Services
    Services/                Permission checks + business logic
    Repos/                    MongoDB queries
    Models/                    Domain objects (Users, Accounts, Branches)
    Utilities/                Database connection, seed script, enums
    tests/                     pytest suite
  requirements.txt
  .env.example               MONGO_URI / MONGO_DB_NAME template

Day_3/bank-frontend/
  src/
    Pages/                  One component per route
    Components/              Shared, reusable pieces (Table, Modal, Form, …)
    hooks/                     One hook per backend resource
    Context/                   AuthContext (session state)
    api/client.ts             fetch wrapper
  .env                        VITE_API_BASE_URL


```

## Setup

### Prerequisites
- Python 3.13
- Node.js (18+) and npm
- A MongoDB instance (local, or a free MongoDB Atlas cluster) — the app
  needs a connection string and a database name

### 1. Backend

```bash
cd Day_2/BackendWithRestApi
pip install -r requirements.txt
```

Create a `.env` file in `Day_2/BackendWithRestApi/` (copy `.env.example`):

```
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
MONGO_DB_NAME=banking
```

Seed the database with sample data — **this wipes and replaces** the
`users`/`branches`/`accounts`/`counters` collections, so only run it against a
database you're fine resetting:

```bash
cd src/main/Python
python -m Utilities.SeedMongo
```

This prints the seeded accounts' email/password pairs (all use password
`password123`) — see [Seeded accounts](#seeded-accounts) below.

Run the API:

```bash
uvicorn app:app --port 8000
```

It should now be reachable at `http://localhost:8000`.

### 2. Frontend

```bash
cd Day_3/bank-frontend
npm install
```

Create a `.env` file in `Day_3/bank-frontend/`:

```
VITE_API_BASE_URL=http://localhost:8000
```

Run the dev server:

```bash
npm run dev
```

It should now be reachable at `http://localhost:5173`. Log in with any of the
seeded accounts below.

### Running the tests

```bash
cd Day_2/BackendWithRestApi
pytest
```

## Seeded accounts

All seeded users share the password `password123`:

| Email | Role | Branch |
|---|---|---|
| admin@citibank.com | Admin | — |
| mgr.jones@citibank.com | Manager | BR001 |
| mgr.lee@citibank.com | Manager | BR002 |
| staff.amy@citibank.com | Staff | BR001 |
| staff.ravi@citibank.com | Staff | BR002 |
| staff.jordan@citibank.com | Staff | BR002 |
| bob.customer@example.com | Customer | BR001 |
| amy.customer@example.com | Customer | BR002 |

## Navigating the application

| Route | Who can see it | What it's for |
|---|---|---|
| `/` (Home) | Everyone | Your own accounts, at a glance |
| `/accounts` | Everyone | Your accounts list + "Open a new account" form |
| `/accounts/:accountId` | Owner, or Staff/Manager/Admin | Balance, deposit/withdraw, transaction history, Close Account (non-Customer roles only) |
| `/transfer` | Logged in | Move money between your own accounts, or to any recipient's account ID |
| `/profile` | Logged in | Edit your name/email (Admin can also reassign a user's branch) |
| `/admin` | Staff, Manager, Admin | Search/manage Users, Accounts, and (Admin only) Branches |
| `/login` | Everyone | Combined log in / sign up |
| `/about`, `/contact` | Everyone | Static marketing pages |

The header shows a "Dashboard" link only for non-Customer roles, and your
name in the header opens a Profile / Log Out menu once logged in.

## End-to-end user flow

**A new customer:**
1. Land on `/login`, switch to the Sign Up tab, and register (always creates
   a Customer — self-signup can't grant a privileged role).
2. Land on Home with no accounts yet — go to `/accounts` and open one
   (Checking or Savings, pick a branch). This becomes your home branch
   automatically.
3. Deposit some money from the account's detail page.
4. Open a second account, then use `/transfer` to move money between your
   own two accounts, or to a friend's account ID.
5. Check `/profile` any time to update your name or email.

**A Staff/Manager assisting customers:**
1. Log in with a seeded Staff/Manager account.
2. Open `/admin` ("Branch Dashboard") — search the Users or Accounts tabs,
   scoped to your own branch by default.
3. Click a row to view full detail in a modal; deactivate/reactivate or
   delete an account, or delete a user, directly from the table.
4. Your own personal accounts (Home/Accounts/Transfer) work exactly like a
   Customer's, even if you opened one at a different branch than your own.

**An Admin managing the bank:**
1. Log in as Admin — the dashboard now also has a Branches tab.
2. Create a new branch, assign it a Manager from a dropdown of real Managers,
   or edit an existing branch's location/manager.
3. Reassign a user's branch from their Profile page (Admin-only field) or via
   the dashboard's user delete/view flow.
4. Everything Staff/Manager can do, but with no branch restriction.

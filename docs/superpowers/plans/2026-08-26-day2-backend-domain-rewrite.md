# Day_2 Backend Domain Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `Day_2/BackendWithRestApi` so it has the same domain richness as
`Day_1/Banking_Domain_console_app` (roles/permissions, branches, Checking/Savings
account types with overdraft rules, transaction history, active/inactive accounts)
while keeping the existing FastAPI + MongoDB REST layer and email-based login.

**Architecture:** Extend Day_2's existing Controller → Service → Repo → Model
layering (Approach 1 from the design spec) with new `Users` (replacing `Customers`)
and `Branches` modules, and an extended `Accounts` module. Permission checks live in
the Service layer, operating on a `Users` object resolved server-side from a
client-supplied `requesting_user_id` (never a client-asserted role). `ValueError` →
400, new `PermissionError` → 403.

**Tech Stack:** Python, FastAPI, uvicorn, MongoDB via `pymongo`, `bcrypt`, `pytest`
(new dependency for this plan).

**Spec:** `docs/superpowers/specs/2026-08-26-day2-backend-domain-rewrite-design.md`

## Global Constraints

- Clean-break rewrite: breaking API/schema changes are fine, `customers` collection
  is superseded by `users`, no backward-compat shims.
- Login stays email-based (not Day_1's username-based login).
- Every permission-gated Service method takes the resolved acting `Users` object as
  its first argument and raises `PermissionError` (not `ValueError`) on a role
  violation, checked **before** any Repo/Mongo call.
- No token/session auth — `requesting_user_id` is a plain client-supplied field,
  same trust model Day_2 already uses for `customer_id` today.
- Direct balance mutation via `PUT /accounts/{id}` is removed; balance only changes
  via `/deposit`, `/withdraw`, or `/transfer`.
- All new/changed files live under `Day_2/BackendWithRestApi/src/main/Python/`.

---

## Task 1: Test infrastructure + shared enums

**Files:**
- Create: `Day_2/BackendWithRestApi/src/main/Python/Utilities/Status.py`
- Create: `Day_2/BackendWithRestApi/pytest.ini`
- Create: `Day_2/BackendWithRestApi/src/main/Python/tests/__init__.py` (empty)
- Create: `Day_2/BackendWithRestApi/src/main/Python/tests/test_status.py`
- Modify: `Day_2/BackendWithRestApi/requirements.txt`

**Interfaces:**
- Produces: `Utilities.Status.OutcomeStatus` (enum: `SUCCESS="Success"`,
  `FAILURE="Failure"`), `Utilities.Status.AccountType` (enum: `CHECKING="Checking"`,
  `SAVINGS="Savings"`), `Utilities.Status.AccountStatus` (enum: `ACTIVE="active"`,
  `INACTIVE="inactive"`), `Utilities.Status.UserRole` (enum: `ADMIN="Admin"`,
  `MANAGER="Manager"`, `STAFF="Staff"`, `CUSTOMER="Customer"`). Every later task
  imports these exact names from `Utilities.Status`.

- [ ] **Step 1: Add pytest to requirements and create pytest.ini**

Append `pytest` as a new line to `Day_2/BackendWithRestApi/requirements.txt`.

Create `Day_2/BackendWithRestApi/pytest.ini`:

```ini
[pytest]
pythonpath = src/main/Python
testpaths = src/main/Python/tests
```

Create empty `Day_2/BackendWithRestApi/src/main/Python/tests/__init__.py` (zero
bytes).

- [ ] **Step 2: Write the failing test**

Create `Day_2/BackendWithRestApi/src/main/Python/tests/test_status.py`:

```python
from Utilities.Status import AccountStatus, AccountType, OutcomeStatus, UserRole


def test_account_type_values():
    assert AccountType.CHECKING.value == "Checking"
    assert AccountType.SAVINGS.value == "Savings"


def test_account_status_values():
    assert AccountStatus.ACTIVE.value == "active"
    assert AccountStatus.INACTIVE.value == "inactive"


def test_user_role_values():
    assert UserRole.ADMIN.value == "Admin"
    assert UserRole.MANAGER.value == "Manager"
    assert UserRole.STAFF.value == "Staff"
    assert UserRole.CUSTOMER.value == "Customer"


def test_outcome_status_values():
    assert OutcomeStatus.SUCCESS.value == "Success"
    assert OutcomeStatus.FAILURE.value == "Failure"
```

- [ ] **Step 3: Run test to verify it fails**

Run (from `Day_2/BackendWithRestApi/`): `pip install -r requirements.txt && pytest -v`
Expected: FAIL / collection error — `Utilities.Status` does not exist yet.

- [ ] **Step 4: Implement Utilities/Status.py**

Create `Day_2/BackendWithRestApi/src/main/Python/Utilities/Status.py`:

```python
from enum import Enum


class OutcomeStatus(Enum):
    SUCCESS = "Success"
    FAILURE = "Failure"


class AccountType(Enum):
    CHECKING = "Checking"
    SAVINGS = "Savings"


class AccountStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class UserRole(Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    STAFF = "Staff"
    CUSTOMER = "Customer"
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest -v`
Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add Day_2/BackendWithRestApi/requirements.txt Day_2/BackendWithRestApi/pytest.ini Day_2/BackendWithRestApi/src/main/Python/Utilities/Status.py Day_2/BackendWithRestApi/src/main/Python/tests/
git commit -m "Add pytest infra and shared Status enums for Day_2 domain rewrite"
```

---

## Task 2: Accounts model — Checking/Savings, transaction history, active/inactive

**Files:**
- Modify (full rewrite): `Day_2/BackendWithRestApi/src/main/Python/Models/Accounts.py`
- Create: `Day_2/BackendWithRestApi/src/main/Python/tests/test_accounts_model.py`

**Interfaces:**
- Consumes: `Utilities.Status.{AccountType, AccountStatus, OutcomeStatus}` (Task 1).
- Produces: `Models.Accounts.Accounts` (abstract), `Models.Accounts.CheckingAccount`,
  `Models.Accounts.SavingsAccount`, `Models.Accounts.build_account(account_type,
  account_id, owner_id, balance, branch_code, status=AccountStatus.ACTIVE,
  transaction_history=None) -> Accounts`. Instance methods used by later tasks:
  `get_account_id()`, `get_owner_id()`, `get_balance()`, `get_branch_code()`,
  `get_account_type()`, `get_status()`, `get_transaction_history()`, `is_active()`,
  `deposit(amount) -> dict`, `withdraw(amount) -> dict`, `transfer(amount,
  target_account) -> dict`, `deactivate_account()`, `reactivate_account()`,
  `to_dict() -> dict`. Each of `deposit`/`withdraw`/`transfer` returns
  `{"status": OutcomeStatus.SUCCESS.value | OutcomeStatus.FAILURE.value, "type":
  "deposit"|"withdrawal"|"transfer", "amount": amount}`.

- [ ] **Step 1: Write the failing tests**

Create `Day_2/BackendWithRestApi/src/main/Python/tests/test_accounts_model.py`:

```python
import pytest

from Models.Accounts import CheckingAccount, SavingsAccount, build_account
from Utilities.Status import AccountType, AccountStatus, OutcomeStatus


def test_checking_account_allows_overdraft_within_limit():
    account = CheckingAccount("ACC-1", 1, 100.0, "BR001")
    result = account.withdraw(600.0)
    assert result["status"] == OutcomeStatus.SUCCESS.value
    assert account.get_balance() == -500.0


def test_checking_account_rejects_overdraft_beyond_limit():
    account = CheckingAccount("ACC-1", 1, 100.0, "BR001")
    result = account.withdraw(601.0)
    assert result["status"] == OutcomeStatus.FAILURE.value
    assert account.get_balance() == 100.0


def test_savings_account_cannot_go_negative():
    account = SavingsAccount("ACC-2", 1, 100.0, "BR001")
    result = account.withdraw(150.0)
    assert result["status"] == OutcomeStatus.FAILURE.value
    assert account.get_balance() == 100.0


def test_savings_account_withdraw_within_balance_succeeds():
    account = SavingsAccount("ACC-2", 1, 100.0, "BR001")
    result = account.withdraw(50.0)
    assert result["status"] == OutcomeStatus.SUCCESS.value
    assert account.get_balance() == 50.0


def test_deposit_and_withdraw_recorded_in_transaction_history():
    account = SavingsAccount("ACC-2", 1, 100.0, "BR001")
    account.deposit(20.0)
    account.withdraw(10.0)
    history = account.get_transaction_history()
    assert [entry["type"] for entry in history] == ["deposit", "withdrawal"]


def test_deposit_fails_on_inactive_account():
    account = SavingsAccount("ACC-2", 1, 100.0, "BR001")
    account.deactivate_account()
    result = account.deposit(10.0)
    assert result["status"] == OutcomeStatus.FAILURE.value
    assert account.get_balance() == 100.0


def test_reactivate_allows_deposit_again():
    account = SavingsAccount("ACC-2", 1, 100.0, "BR001")
    account.deactivate_account()
    account.reactivate_account()
    result = account.deposit(10.0)
    assert result["status"] == OutcomeStatus.SUCCESS.value


def test_transfer_moves_balance_between_accounts():
    source = CheckingAccount("ACC-1", 1, 200.0, "BR001")
    target = SavingsAccount("ACC-2", 2, 50.0, "BR001")
    result = source.transfer(100.0, target)
    assert result["status"] == OutcomeStatus.SUCCESS.value
    assert source.get_balance() == 100.0
    assert target.get_balance() == 150.0


def test_build_account_checking():
    account = build_account(AccountType.CHECKING, "ACC-1", 1, 100.0, "BR001")
    assert isinstance(account, CheckingAccount)
    assert account.get_account_type() == AccountType.CHECKING


def test_build_account_savings():
    account = build_account(AccountType.SAVINGS, "ACC-2", 1, 100.0, "BR001")
    assert isinstance(account, SavingsAccount)


def test_build_account_unknown_type_raises():
    with pytest.raises(ValueError):
        build_account("Bogus", "ACC-3", 1, 100.0, "BR001")


def test_to_dict_shape():
    account = CheckingAccount("ACC-1", 1, 100.0, "BR001")
    account.deposit(10.0)
    data = account.to_dict()
    assert data["account_id"] == "ACC-1"
    assert data["owner_id"] == 1
    assert data["balance"] == 110.0
    assert data["branch_code"] == "BR001"
    assert data["account_type"] == "Checking"
    assert data["status"] == "active"
    assert len(data["transaction_history"]) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest src/main/Python/tests/test_accounts_model.py -v` (from
`Day_2/BackendWithRestApi/`)
Expected: FAIL / collection error — current `Models/Accounts.py` has a different
constructor signature (`account_id, customer_id, balance` only, no `branch_code`,
no subclasses).

- [ ] **Step 3: Rewrite Models/Accounts.py**

Replace the full contents of
`Day_2/BackendWithRestApi/src/main/Python/Models/Accounts.py` with:

```python
"""
Account Model for the Banking Domain REST API:
    Defines the Accounts abstract base class and its CheckingAccount /
    SavingsAccount subclasses. Ported from Day_1's console-app account
    hierarchy: Checking allows a $500 overdraft, Savings never goes
    negative, and every deposit/withdraw/transfer is recorded in an
    in-memory transaction history that gets persisted alongside the
    account document.
"""

import time
from abc import ABC, abstractmethod
from typing import override

from Utilities.Status import AccountType, AccountStatus, OutcomeStatus

OVERDRAFT_LIMIT = 500


class Accounts(ABC):
    """Abstract base class for all bank accounts. Use CheckingAccount or SavingsAccount."""

    def __init__(self, account_id, owner_id, balance, branch_code, account_type=None,
                 status=AccountStatus.ACTIVE, transaction_history=None):
        self.set_account_id(account_id)
        self.set_owner_id(owner_id)
        self.set_balance(balance)
        self.branch_code = branch_code
        self.account_type = account_type
        self.status = status if isinstance(status, AccountStatus) else AccountStatus(status)
        self.transaction_history = transaction_history if transaction_history is not None else []

    def get_account_id(self):
        return self._account_id

    def get_owner_id(self):
        return self._owner_id

    def get_balance(self):
        return self._balance

    def get_branch_code(self):
        return self.branch_code

    def get_account_type(self):
        return self.account_type

    def get_status(self):
        return self.status

    def get_transaction_history(self):
        return self.transaction_history

    def is_active(self):
        return self.status == AccountStatus.ACTIVE

    def set_account_id(self, account_id):
        if not account_id:
            raise ValueError("Account ID cannot be empty.")
        self._account_id = account_id

    def set_owner_id(self, owner_id):
        if not owner_id:
            raise ValueError("Owner ID cannot be empty.")
        self._owner_id = owner_id

    def set_balance(self, balance):
        if balance < 0:
            raise ValueError("Initial balance cannot be negative.")
        self._balance = balance

    def deactivate_account(self):
        self.status = AccountStatus.INACTIVE

    def reactivate_account(self):
        self.status = AccountStatus.ACTIVE

    def add_transaction(self, transaction):
        self.transaction_history.append(transaction)

    def deposit(self, amount):
        if amount > 0 and self.is_active():
            self._balance += amount
            self.add_transaction({"type": "deposit", "amount": amount,
                                   "status": OutcomeStatus.SUCCESS.value, "timestamp": time.time()})
            return {"status": OutcomeStatus.SUCCESS.value, "type": "deposit", "amount": amount}

        self.add_transaction({"type": "deposit", "amount": amount,
                               "status": OutcomeStatus.FAILURE.value, "timestamp": time.time()})
        return {"status": OutcomeStatus.FAILURE.value, "type": "deposit", "amount": amount}

    @abstractmethod
    def withdraw(self, amount):
        ...

    def transfer(self, amount, target_account):
        if target_account.is_active() and self.withdraw(amount)["status"] == OutcomeStatus.SUCCESS.value:
            target_account.deposit(amount)
            self.add_transaction({"type": "transfer", "amount": amount,
                                   "status": OutcomeStatus.SUCCESS.value, "timestamp": time.time()})
            return {"status": OutcomeStatus.SUCCESS.value, "type": "transfer", "amount": amount}

        self.add_transaction({"type": "transfer", "amount": amount,
                               "status": OutcomeStatus.FAILURE.value, "timestamp": time.time()})
        return {"status": OutcomeStatus.FAILURE.value, "type": "transfer", "amount": amount}

    def to_dict(self):
        return {
            "account_id": self._account_id,
            "owner_id": self._owner_id,
            "balance": self._balance,
            "branch_code": self.branch_code,
            "account_type": self.account_type.value if isinstance(self.account_type, AccountType) else self.account_type,
            "status": self.status.value,
            "transaction_history": self.transaction_history,
        }

    def __repr__(self):
        type_label = self.account_type.value if isinstance(self.account_type, AccountType) else self.account_type
        return (f"Account ID: {self._account_id}, Type: {type_label}, Balance: {self._balance}, "
                f"Owner ID: {self._owner_id}, Status: {self.status.value}")


class CheckingAccount(Accounts):
    def __init__(self, account_id, owner_id, balance, branch_code,
                 status=AccountStatus.ACTIVE, transaction_history=None):
        super().__init__(account_id, owner_id, balance, branch_code, AccountType.CHECKING,
                          status, transaction_history)

    @override
    def withdraw(self, amount):
        if self.is_active() and amount > 0 and amount <= OVERDRAFT_LIMIT + self._balance:
            self._balance -= amount
            self.add_transaction({"type": "withdrawal", "amount": amount,
                                   "status": OutcomeStatus.SUCCESS.value, "timestamp": time.time()})
            return {"status": OutcomeStatus.SUCCESS.value, "type": "withdrawal", "amount": amount}

        self.add_transaction({"type": "withdrawal", "amount": amount,
                               "status": OutcomeStatus.FAILURE.value, "timestamp": time.time()})
        return {"status": OutcomeStatus.FAILURE.value, "type": "withdrawal", "amount": amount}


class SavingsAccount(Accounts):
    def __init__(self, account_id, owner_id, balance, branch_code,
                 status=AccountStatus.ACTIVE, transaction_history=None):
        super().__init__(account_id, owner_id, balance, branch_code, AccountType.SAVINGS,
                          status, transaction_history)

    @override
    def withdraw(self, amount):
        if self.is_active() and 0 < amount <= self._balance:
            self._balance -= amount
            self.add_transaction({"type": "withdrawal", "amount": amount,
                                   "status": OutcomeStatus.SUCCESS.value, "timestamp": time.time()})
            return {"status": OutcomeStatus.SUCCESS.value, "type": "withdrawal", "amount": amount}

        self.add_transaction({"type": "withdrawal", "amount": amount,
                               "status": OutcomeStatus.FAILURE.value, "timestamp": time.time()})
        return {"status": OutcomeStatus.FAILURE.value, "type": "withdrawal", "amount": amount}


def build_account(account_type, account_id, owner_id, balance, branch_code,
                   status=AccountStatus.ACTIVE, transaction_history=None):
    resolved_type = account_type if isinstance(account_type, AccountType) else None
    if resolved_type is None:
        try:
            resolved_type = AccountType(account_type)
        except ValueError:
            resolved_type = None

    if resolved_type == AccountType.CHECKING:
        return CheckingAccount(account_id, owner_id, balance, branch_code, status, transaction_history)
    if resolved_type == AccountType.SAVINGS:
        return SavingsAccount(account_id, owner_id, balance, branch_code, status, transaction_history)
    raise ValueError(f"Unknown account type: {account_type}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest src/main/Python/tests/test_accounts_model.py -v`
Expected: 12 passed.

- [ ] **Step 5: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/Models/Accounts.py Day_2/BackendWithRestApi/src/main/Python/tests/test_accounts_model.py
git commit -m "Rewrite Accounts model with Checking/Savings types, history, active/inactive"
```

---

## Task 3: Users model (replaces Customers) with roles

**Files:**
- Create: `Day_2/BackendWithRestApi/src/main/Python/Models/Users.py`
- Delete: `Day_2/BackendWithRestApi/src/main/Python/Models/Customers.py`
- Create: `Day_2/BackendWithRestApi/src/main/Python/tests/test_users_model.py`

**Interfaces:**
- Consumes: `Utilities.Status.UserRole` (Task 1).
- Produces: `Models.Users.Users(user_id, name, email, role, branch_code=None,
  password_hash=None)` with `get_user_id()`, `get_name()`, `get_email()`,
  `get_role()`, `get_branch_code()`, `get_password_hash()`, `set_name(name)`,
  `set_email(email)`, `set_password_hash(password_hash)`, `set_role(staff,
  new_role)` (raises `PermissionError` unless `staff.get_role() == UserRole.ADMIN`),
  `set_branch_code(staff, new_branch_code)` (raises `PermissionError` if
  `staff.get_role() == UserRole.CUSTOMER`), `verify_password(plain_password) ->
  bool`, `to_dict() -> dict`.

- [ ] **Step 1: Write the failing tests**

Create `Day_2/BackendWithRestApi/src/main/Python/tests/test_users_model.py`:

```python
import bcrypt
import pytest

from Models.Users import Users
from Utilities.Status import UserRole


def make_user(role, user_id=1, branch_code="BR001"):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code=branch_code)


def test_set_role_requires_admin():
    admin = make_user(UserRole.ADMIN, user_id=1)
    target = make_user(UserRole.STAFF, user_id=2)
    target.set_role(admin, UserRole.MANAGER)
    assert target.get_role() == UserRole.MANAGER


def test_set_role_rejects_non_admin():
    manager = make_user(UserRole.MANAGER, user_id=1)
    target = make_user(UserRole.STAFF, user_id=2)
    with pytest.raises(PermissionError):
        target.set_role(manager, UserRole.ADMIN)


def test_set_branch_code_rejects_customer():
    customer = make_user(UserRole.CUSTOMER, user_id=1)
    target = make_user(UserRole.STAFF, user_id=2)
    with pytest.raises(PermissionError):
        target.set_branch_code(customer, "BR002")


def test_set_branch_code_allows_staff():
    staff = make_user(UserRole.STAFF, user_id=1)
    target = make_user(UserRole.STAFF, user_id=2)
    target.set_branch_code(staff, "BR002")
    assert target.get_branch_code() == "BR002"


def test_verify_password_roundtrip():
    user = make_user(UserRole.CUSTOMER)
    password_hash = bcrypt.hashpw(b"Secret123", bcrypt.gensalt()).decode("utf-8")
    user.set_password_hash(password_hash)
    assert user.verify_password("Secret123") is True
    assert user.verify_password("wrong") is False


def test_invalid_email_rejected():
    with pytest.raises(ValueError):
        Users(1, "Test User", "not-an-email", UserRole.CUSTOMER)


def test_to_dict_shape():
    user = make_user(UserRole.MANAGER)
    data = user.to_dict()
    assert data["user_id"] == 1
    assert data["role"] == "Manager"
    assert data["branch_code"] == "BR001"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest src/main/Python/tests/test_users_model.py -v`
Expected: FAIL / collection error — `Models.Users` does not exist yet.

- [ ] **Step 3: Create Models/Users.py and delete Models/Customers.py**

Create `Day_2/BackendWithRestApi/src/main/Python/Models/Users.py`:

```python
"""
User Model for the Banking Domain REST API:
    Represents a user of any role (Admin/Manager/Staff/Customer). Ported
    from Day_1's console-app Users class, with email-based identity
    (Day_2's existing convention) instead of Day_1's username-based one.
"""

import bcrypt

from Utilities.Status import UserRole


class Users:
    def __init__(self, user_id, name, email, role, branch_code=None, password_hash=None):
        self.set_user_id(user_id)
        self.set_name(name)
        self.set_email(email)
        self.role = role if isinstance(role, UserRole) else UserRole(role)
        self.branch_code = branch_code
        self.password_hash = password_hash

    def get_user_id(self):
        return self.user_id

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email

    def get_role(self):
        return self.role

    def get_branch_code(self):
        return self.branch_code

    def get_password_hash(self):
        return self.password_hash

    def set_user_id(self, user_id):
        if not user_id:
            raise ValueError("User ID cannot be empty.")
        self.user_id = user_id

    def set_name(self, name):
        if not name:
            raise ValueError("Name cannot be empty.")
        self.name = name

    def set_email(self, email):
        if not email or "@" not in email or "." not in email:
            raise ValueError("Invalid email format.")
        self.email = email

    def set_password_hash(self, password_hash):
        if not password_hash:
            raise ValueError("Password hash cannot be empty.")
        self.password_hash = password_hash

    def set_role(self, staff, new_role):
        if staff.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admin users can change roles.")
        self.role = new_role if isinstance(new_role, UserRole) else UserRole(new_role)

    def set_branch_code(self, staff, new_branch_code):
        if staff.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only non-Customer users can change branch codes.")
        if not new_branch_code:
            raise ValueError("Branch code cannot be empty.")
        self.branch_code = new_branch_code

    def verify_password(self, plain_password):
        if not self.password_hash or not plain_password:
            return False
        return bcrypt.checkpw(plain_password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "branch_code": self.branch_code,
            "password_hash": self.password_hash,
        }

    def __repr__(self):
        return f"User ID: {self.user_id}, Name: {self.name}, Email: {self.email}, Role: {self.role.value}"
```

Delete `Day_2/BackendWithRestApi/src/main/Python/Models/Customers.py`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest src/main/Python/tests/test_users_model.py -v`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/Models/Users.py Day_2/BackendWithRestApi/src/main/Python/tests/test_users_model.py
git rm Day_2/BackendWithRestApi/src/main/Python/Models/Customers.py
git commit -m "Replace Customers model with role-aware Users model"
```

---

## Task 4: Branches model

**Files:**
- Create: `Day_2/BackendWithRestApi/src/main/Python/Models/Branches.py`
- Create: `Day_2/BackendWithRestApi/src/main/Python/tests/test_branches_model.py`

**Interfaces:**
- Consumes: `Utilities.Status.UserRole` (Task 1).
- Produces: `Models.Branches.Branches(branch_code, location, manager_id=None,
  staff_list=None)` with `get_branch_code()`, `get_location()`,
  `get_manager_id(staff)` (raises `PermissionError` for `UserRole.CUSTOMER`),
  `get_staff_list(staff)` (same gate), `add_staff(user_id)`,
  `remove_staff(user_id)`, `set_manager(staff, manager_id)` (raises
  `PermissionError` unless staff role is Admin or Manager), `set_location(staff,
  new_location)` (raises `PermissionError` unless Admin), `to_dict() -> dict`.
  Public attributes `manager_id` and `staff_list` are read directly by later
  serialization code.

- [ ] **Step 1: Write the failing tests**

Create `Day_2/BackendWithRestApi/src/main/Python/tests/test_branches_model.py`:

```python
import pytest

from Models.Branches import Branches
from Models.Users import Users
from Utilities.Status import UserRole


def make_user(role, user_id=1):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code="BR001")


def test_get_manager_id_rejects_customer():
    branch = Branches("BR001", "Downtown", manager_id=2)
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        branch.get_manager_id(customer)


def test_get_manager_id_allows_staff():
    branch = Branches("BR001", "Downtown", manager_id=2)
    staff = make_user(UserRole.STAFF)
    assert branch.get_manager_id(staff) == 2


def test_set_location_requires_admin():
    branch = Branches("BR001", "Downtown")
    manager = make_user(UserRole.MANAGER)
    with pytest.raises(PermissionError):
        branch.set_location(manager, "Uptown")


def test_set_location_allows_admin():
    branch = Branches("BR001", "Downtown")
    admin = make_user(UserRole.ADMIN)
    branch.set_location(admin, "Uptown")
    assert branch.get_location() == "Uptown"


def test_set_manager_rejects_staff():
    branch = Branches("BR001", "Downtown")
    staff = make_user(UserRole.STAFF)
    with pytest.raises(PermissionError):
        branch.set_manager(staff, 5)


def test_set_manager_allows_admin():
    branch = Branches("BR001", "Downtown")
    admin = make_user(UserRole.ADMIN)
    branch.set_manager(admin, 5)
    assert branch.manager_id == 5


def test_add_and_remove_staff():
    branch = Branches("BR001", "Downtown")
    branch.add_staff(9)
    assert 9 in branch.staff_list
    branch.remove_staff(9)
    assert 9 not in branch.staff_list


def test_to_dict_shape():
    branch = Branches("BR001", "Downtown", manager_id=2, staff_list=[3, 4])
    data = branch.to_dict()
    assert data == {"branch_code": "BR001", "location": "Downtown", "manager_id": 2, "staff_list": [3, 4]}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest src/main/Python/tests/test_branches_model.py -v`
Expected: FAIL / collection error — `Models.Branches` does not exist yet.

- [ ] **Step 3: Create Models/Branches.py**

Create `Day_2/BackendWithRestApi/src/main/Python/Models/Branches.py`:

```python
"""
Branch Model for the Banking Domain REST API:
    Ported from Day_1's console-app Branches class. Accounts are NOT
    embedded here (unlike Day_1) - they live in their own MongoDB
    collection with a branch_code field pointing back to a branch.
"""

from Utilities.Status import UserRole


class Branches:
    def __init__(self, branch_code, location, manager_id=None, staff_list=None):
        self.branch_code = branch_code
        self.location = location
        self.manager_id = manager_id
        self.staff_list = staff_list if staff_list is not None else []

    def get_branch_code(self):
        return self.branch_code

    def get_location(self):
        return self.location

    def get_manager_id(self, staff):
        if staff.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only staff can view the branch manager.")
        return self.manager_id

    def get_staff_list(self, staff):
        if staff.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only staff can view the branch staff list.")
        return self.staff_list

    def add_staff(self, user_id):
        if user_id not in self.staff_list:
            self.staff_list.append(user_id)

    def remove_staff(self, user_id):
        if user_id in self.staff_list:
            self.staff_list.remove(user_id)

    def set_manager(self, staff, manager_id):
        if staff.get_role() not in (UserRole.ADMIN, UserRole.MANAGER):
            raise PermissionError("Only Admins or Managers can assign a branch manager.")
        self.manager_id = manager_id

    def set_location(self, staff, new_location):
        if staff.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admins can change the branch location.")
        if not new_location:
            raise ValueError("Location cannot be empty.")
        self.location = new_location

    def to_dict(self):
        return {
            "branch_code": self.branch_code,
            "location": self.location,
            "manager_id": self.manager_id,
            "staff_list": self.staff_list,
        }

    def __repr__(self):
        return (f"Branch Code: {self.branch_code}, Location: {self.location}, "
                f"Manager ID: {self.manager_id}, Staff List: {self.staff_list}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest src/main/Python/tests/test_branches_model.py -v`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/Models/Branches.py Day_2/BackendWithRestApi/src/main/Python/tests/test_branches_model.py
git commit -m "Add Branches model ported from Day_1"
```

---

## Task 5: Database.py — users/branches indexes

**Files:**
- Modify: `Day_2/BackendWithRestApi/src/main/Python/Utilities/Database.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `get_database()` unchanged signature; now also ensures unique indexes on
  `users.user_id`, `users.email`, and `branches.branch_code`, plus the existing
  `accounts.account_id` index.

- [ ] **Step 1: Update the index setup**

In `Day_2/BackendWithRestApi/src/main/Python/Utilities/Database.py`, replace lines
29–34 (the `customers_collection`/`accounts_collection` index block) with:

```python
        users_collection = _client[db_name].users
        users_collection.create_index("user_id", unique=True)
        users_collection.create_index("email", unique=True)

        branches_collection = _client[db_name].branches
        branches_collection.create_index("branch_code", unique=True)

        accounts_collection = _client[db_name].accounts
        accounts_collection.create_index("account_id", unique=True)
```

- [ ] **Step 2: Manual verification**

This function only runs against a live MongoDB connection (per the spec, Repo/DB
code is out of scope for automated tests in this plan). Verify by running, from
`Day_2/BackendWithRestApi/src/main/Python/`:

```bash
python -c "from Utilities.Database import get_database; db = get_database(); print(db.list_collection_names())"
```

Expected: no exceptions; prints the current collection list (requires `.env` with a
valid `MONGO_URI` — reuse the existing one already on disk per the spec's migration
notes).

- [ ] **Step 3: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/Utilities/Database.py
git commit -m "Add users/branches indexes to Database setup"
```

---

## Task 6: UsersRepo (replaces CustomersRepo)

**Files:**
- Create: `Day_2/BackendWithRestApi/src/main/Python/Repos/UsersRepo.py`
- Delete: `Day_2/BackendWithRestApi/src/main/Python/Repos/CustomersRepo.py`

**Interfaces:**
- Consumes: `Models.Users.Users` (Task 3), `Utilities.Database.get_database` (Task
  5).
- Produces: `Repos.UsersRepo.UsersRepository` with static methods
  `get_all_users() -> list[Users]`, `get_user_by_id(user_id: int) -> Users | None`,
  `get_user_by_email(email: str) -> Users | None`, `create_user(user_data: dict) ->
  Users` (raises `ValueError` on missing fields or duplicate id/email),
  `update_user(user_id, user_data: dict) -> Users`, `delete_user(user_id: int) ->
  bool`.

- [ ] **Step 1: Create Repos/UsersRepo.py**

Create `Day_2/BackendWithRestApi/src/main/Python/Repos/UsersRepo.py`:

```python
"""
User Repository for the Banking Domain REST API:
    CRUD against the 'users' MongoDB collection. Replaces CustomersRepo -
    same pattern (duplicate-key -> ValueError translation), renamed
    customer_id -> user_id and with a role/branch_code field.
"""

from Utilities.Database import get_database
from Models.Users import Users
from pymongo.errors import DuplicateKeyError


def _to_user(doc) -> Users:
    return Users(
        doc["user_id"], doc["name"], doc["email"], doc["role"],
        branch_code=doc.get("branch_code"), password_hash=doc.get("password_hash"),
    )


class UsersRepository:

    @staticmethod
    def get_all_users() -> list:
        collection = get_database().users
        return [_to_user(doc) for doc in collection.find()]

    @staticmethod
    def get_user_by_id(user_id: int) -> Users:
        if not user_id:
            raise ValueError("User ID must be provided.")

        collection = get_database().users
        doc = collection.find_one({"user_id": user_id})
        return _to_user(doc) if doc else None

    @staticmethod
    def get_user_by_email(email: str) -> Users:
        if not email:
            raise ValueError("Email must be provided.")

        collection = get_database().users
        doc = collection.find_one({"email": email})
        return _to_user(doc) if doc else None

    @staticmethod
    def create_user(user_data: dict) -> Users:
        required = ("user_id", "name", "email", "role")
        if not all(user_data.get(field) for field in required):
            raise ValueError("User data must include 'user_id', 'name', 'email', and 'role' fields.")

        collection = get_database().users
        try:
            collection.insert_one(user_data)
        except DuplicateKeyError as e:
            if "email" in e.details.get("keyPattern", {}):
                raise ValueError(f"User with email {user_data['email']} already exists.")
            raise ValueError(f"User with ID {user_data['user_id']} already exists.")

        return UsersRepository.get_user_by_id(user_data["user_id"])

    @staticmethod
    def update_user(user_id: int, user_data: dict) -> Users:
        if not user_id:
            raise ValueError("User ID must be provided for update.")
        if not user_data:
            raise ValueError("User data must not be empty.")
        if "user_id" in user_data and user_data["user_id"] != user_id:
            raise ValueError("User ID in the data does not match the provided user ID.")

        user = UsersRepository.get_user_by_id(user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} does not exist.")

        if "name" in user_data:
            user.set_name(user_data["name"])
        if "email" in user_data:
            user.set_email(user_data["email"])
        if "branch_code" in user_data:
            user.branch_code = user_data["branch_code"]

        collection = get_database().users
        collection.update_one({"user_id": user_id}, {"$set": user.to_dict()})

        return user

    @staticmethod
    def delete_user(user_id: int) -> bool:
        if not user_id:
            raise ValueError("User ID must be provided for deletion.")

        collection = get_database().users
        result = collection.delete_one({"user_id": user_id})
        if result.deleted_count == 0:
            raise ValueError(f"User with ID {user_id} does not exist.")

        return True
```

Delete `Day_2/BackendWithRestApi/src/main/Python/Repos/CustomersRepo.py`.

- [ ] **Step 2: Manual verification**

Requires a live MongoDB connection. From
`Day_2/BackendWithRestApi/src/main/Python/`, run:

```bash
python -c "
from Repos.UsersRepo import UsersRepository
u = UsersRepository.create_user({'user_id': 9001, 'name': 'Smoke Test', 'email': 'smoke.test@example.com', 'role': 'Customer'})
print(u)
print(UsersRepository.get_user_by_id(9001))
UsersRepository.delete_user(9001)
print('deleted ok')
"
```

Expected: prints the created user, the fetched user, then `deleted ok`, no
exceptions.

- [ ] **Step 3: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/Repos/UsersRepo.py
git rm Day_2/BackendWithRestApi/src/main/Python/Repos/CustomersRepo.py
git commit -m "Replace CustomersRepo with UsersRepo"
```

---

## Task 7: BranchesRepo

**Files:**
- Create: `Day_2/BackendWithRestApi/src/main/Python/Repos/BranchesRepo.py`

**Interfaces:**
- Consumes: `Models.Branches.Branches` (Task 4), `Utilities.Database.get_database`
  (Task 5).
- Produces: `Repos.BranchesRepo.BranchesRepository` with static methods
  `get_all_branches() -> list[Branches]`, `get_branch_by_code(branch_code: str) ->
  Branches | None`, `create_branch(branch_data: dict) -> Branches`,
  `update_branch(branch_code, branch_data: dict) -> Branches`,
  `delete_branch(branch_code: str) -> bool`.

- [ ] **Step 1: Create Repos/BranchesRepo.py**

Create `Day_2/BackendWithRestApi/src/main/Python/Repos/BranchesRepo.py`:

```python
"""
Branch Repository for the Banking Domain REST API:
    CRUD against the 'branches' MongoDB collection.
"""

from Utilities.Database import get_database
from Models.Branches import Branches
from pymongo.errors import DuplicateKeyError


def _to_branch(doc) -> Branches:
    return Branches(doc["branch_code"], doc["location"],
                     manager_id=doc.get("manager_id"), staff_list=doc.get("staff_list", []))


class BranchesRepository:

    @staticmethod
    def get_all_branches() -> list:
        collection = get_database().branches
        return [_to_branch(doc) for doc in collection.find()]

    @staticmethod
    def get_branch_by_code(branch_code: str) -> Branches:
        if not branch_code:
            raise ValueError("Branch code must be provided.")

        collection = get_database().branches
        doc = collection.find_one({"branch_code": branch_code})
        return _to_branch(doc) if doc else None

    @staticmethod
    def create_branch(branch_data: dict) -> Branches:
        if not branch_data.get("branch_code") or not branch_data.get("location"):
            raise ValueError("Branch data must include 'branch_code' and 'location' fields.")

        collection = get_database().branches
        try:
            collection.insert_one(branch_data)
        except DuplicateKeyError:
            raise ValueError(f"Branch with code {branch_data['branch_code']} already exists.")

        return BranchesRepository.get_branch_by_code(branch_data["branch_code"])

    @staticmethod
    def update_branch(branch_code: str, branch_data: dict) -> Branches:
        branch = BranchesRepository.get_branch_by_code(branch_code)
        if branch is None:
            raise ValueError(f"Branch with code {branch_code} does not exist.")

        if "location" in branch_data:
            branch.location = branch_data["location"]
        if "manager_id" in branch_data:
            branch.manager_id = branch_data["manager_id"]

        collection = get_database().branches
        collection.update_one({"branch_code": branch_code}, {"$set": branch.to_dict()})

        return branch

    @staticmethod
    def delete_branch(branch_code: str) -> bool:
        if not branch_code:
            raise ValueError("Branch code must be provided for deletion.")

        collection = get_database().branches
        result = collection.delete_one({"branch_code": branch_code})
        if result.deleted_count == 0:
            raise ValueError(f"Branch with code {branch_code} does not exist.")

        return True
```

- [ ] **Step 2: Manual verification**

From `Day_2/BackendWithRestApi/src/main/Python/`, run:

```bash
python -c "
from Repos.BranchesRepo import BranchesRepository
b = BranchesRepository.create_branch({'branch_code': 'BR999', 'location': 'Smoke Test'})
print(b)
print(BranchesRepository.get_branch_by_code('BR999'))
BranchesRepository.delete_branch('BR999')
print('deleted ok')
"
```

Expected: prints the created branch, the fetched branch, then `deleted ok`, no
exceptions.

- [ ] **Step 3: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/Repos/BranchesRepo.py
git commit -m "Add BranchesRepo"
```

---

## Task 8: AccountsRepo rewrite — types, deposit/withdraw, status

**Files:**
- Modify (full rewrite): `Day_2/BackendWithRestApi/src/main/Python/Repos/AccountsRepo.py`

**Interfaces:**
- Consumes: `Models.Accounts.build_account` (Task 2), `Utilities.Status.{AccountType,
  AccountStatus}` (Task 1), `Utilities.Database.get_database` (Task 5).
- Produces: `Repos.AccountsRepo.AccountsRepository` with static methods
  `get_all_accounts(owner_id=None) -> list[Accounts]`, `get_account_by_id(account_id,
  owner_id=None) -> Accounts | None`, `get_accounts_by_branch(branch_code) ->
  list[Accounts]`, `create_account(account_data: dict) -> Accounts`,
  `deposit(account_id, amount, requesting_user_id=None) -> tuple[Accounts, dict]`,
  `withdraw(account_id, amount, requesting_user_id=None) -> tuple[Accounts, dict]`,
  `delete_account(account_id, requesting_user_id=None) -> bool`,
  `set_status(account_id, status: AccountStatus, requesting_user_id=None) ->
  Accounts`, `transfer_funds(source_account_id, target_account_id, amount,
  requesting_user_id=None) -> dict`. Note: `update_account` (direct balance PUT) is
  **removed** — later tasks must not call it.

- [ ] **Step 1: Rewrite Repos/AccountsRepo.py**

Replace the full contents of
`Day_2/BackendWithRestApi/src/main/Python/Repos/AccountsRepo.py` with:

```python
"""
Account Repository for the Banking Domain REST API:
    CRUD + deposit/withdraw/transfer against the 'accounts' MongoDB
    collection. Balance only ever changes through deposit/withdraw/
    transfer (never a direct PUT), so overdraft rules and transaction
    history stay consistent.
"""

from Utilities.Database import get_database
from Models.Accounts import build_account
from Utilities.Status import AccountType, AccountStatus
from pymongo.errors import DuplicateKeyError


def _to_account(doc):
    return build_account(
        AccountType(doc["account_type"]),
        doc["account_id"],
        doc["owner_id"],
        doc["balance"],
        doc["branch_code"],
        status=AccountStatus(doc.get("status", AccountStatus.ACTIVE.value)),
        transaction_history=doc.get("transaction_history", []),
    )


class AccountsRepository:

    @staticmethod
    def get_all_accounts(owner_id=None):
        collection = get_database().accounts
        query = {"owner_id": owner_id} if owner_id is not None else {}
        return [_to_account(doc) for doc in collection.find(query)]

    @staticmethod
    def get_account_by_id(account_id, owner_id=None):
        if not account_id:
            raise ValueError("Account ID must be provided.")

        collection = get_database().accounts
        query = {"account_id": account_id}
        if owner_id is not None:
            # Scope the lookup so someone else's account looks identical to
            # one that doesn't exist at all.
            query["owner_id"] = owner_id
        doc = collection.find_one(query)
        return _to_account(doc) if doc else None

    @staticmethod
    def get_accounts_by_branch(branch_code):
        collection = get_database().accounts
        return [_to_account(doc) for doc in collection.find({"branch_code": branch_code})]

    @staticmethod
    def create_account(account_data: dict):
        required = ("account_id", "owner_id", "balance", "branch_code", "account_type")
        if not all(field in account_data and account_data[field] not in (None, "") for field in required):
            raise ValueError(
                "Account data must include 'account_id', 'owner_id', 'balance', 'branch_code', and 'account_type' fields."
            )

        account = build_account(
            account_data["account_type"],
            account_data["account_id"],
            account_data["owner_id"],
            account_data["balance"],
            account_data["branch_code"],
        )

        collection = get_database().accounts
        try:
            collection.insert_one(account.to_dict())
        except DuplicateKeyError:
            raise ValueError(f"Account with ID {account_data['account_id']} already exists.")

        return account

    @staticmethod
    def _save(account):
        collection = get_database().accounts
        collection.update_one({"account_id": account.get_account_id()}, {"$set": account.to_dict()})
        return account

    @staticmethod
    def deposit(account_id, amount, requesting_user_id=None):
        account = AccountsRepository.get_account_by_id(account_id, requesting_user_id)
        if account is None:
            raise ValueError(f"Account with ID {account_id} does not exist.")
        result = account.deposit(amount)
        AccountsRepository._save(account)
        return account, result

    @staticmethod
    def withdraw(account_id, amount, requesting_user_id=None):
        account = AccountsRepository.get_account_by_id(account_id, requesting_user_id)
        if account is None:
            raise ValueError(f"Account with ID {account_id} does not exist.")
        result = account.withdraw(amount)
        AccountsRepository._save(account)
        return account, result

    @staticmethod
    def delete_account(account_id, requesting_user_id=None):
        if not account_id:
            raise ValueError("Account ID must be provided for deletion.")

        collection = get_database().accounts
        query = {"account_id": account_id}
        if requesting_user_id is not None:
            query["owner_id"] = requesting_user_id
        result = collection.delete_one(query)
        return result.deleted_count > 0

    @staticmethod
    def set_status(account_id, status: AccountStatus, requesting_user_id=None):
        account = AccountsRepository.get_account_by_id(account_id, requesting_user_id)
        if account is None:
            raise ValueError(f"Account with ID {account_id} does not exist.")
        if status == AccountStatus.ACTIVE:
            account.reactivate_account()
        else:
            account.deactivate_account()
        AccountsRepository._save(account)
        return account

    @staticmethod
    def transfer_funds(source_account_id, target_account_id, amount, requesting_user_id=None):
        if not source_account_id or not target_account_id:
            raise ValueError("Both source and target account IDs must be provided.")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")

        source_account = AccountsRepository.get_account_by_id(source_account_id)
        target_account = AccountsRepository.get_account_by_id(target_account_id)

        if source_account is None:
            raise ValueError(f"Source account with ID {source_account_id} does not exist.")
        if target_account is None:
            raise ValueError(f"Target account with ID {target_account_id} does not exist.")

        if requesting_user_id is not None and source_account.get_owner_id() != requesting_user_id:
            # You can only ever move money OUT of your own account (moving
            # money INTO someone else's account is fine and intentionally
            # not restricted here).
            raise ValueError("You do not have permission to transfer from this account.")

        result = source_account.transfer(amount, target_account)
        AccountsRepository._save(source_account)
        AccountsRepository._save(target_account)
        return result
```

- [ ] **Step 2: Manual verification**

From `Day_2/BackendWithRestApi/src/main/Python/`, run:

```bash
python -c "
from Repos.AccountsRepo import AccountsRepository
a = AccountsRepository.create_account({'account_id': 'ACC-9001', 'owner_id': 9001, 'balance': 100.0, 'branch_code': 'BR001', 'account_type': 'Checking'})
print(a)
account, result = AccountsRepository.withdraw('ACC-9001', 50.0)
print(result, account.get_balance())
AccountsRepository.delete_account('ACC-9001')
print('deleted ok')
"
```

Expected: prints the created account, a success withdrawal result with balance
`50.0`, then `deleted ok`, no exceptions.

- [ ] **Step 3: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/Repos/AccountsRepo.py
git commit -m "Rewrite AccountsRepo for account types, deposit/withdraw, status"
```

---

## Task 9: UsersService (replaces CustomersService) with permission checks

**Files:**
- Create: `Day_2/BackendWithRestApi/src/main/Python/Services/UsersService.py`
- Delete: `Day_2/BackendWithRestApi/src/main/Python/Services/CustomersService.py`
- Create: `Day_2/BackendWithRestApi/src/main/Python/tests/test_users_service.py`

**Interfaces:**
- Consumes: `Repos.UsersRepo.UsersRepository` (Task 6), `Models.Users.Users` (Task
  3), `Utilities.Status.UserRole` (Task 1).
- Produces: `Services.UsersService.UsersService` with static methods
  `get_all_users()`, `get_user_by_id(user_id)`, `create_user(requesting_user,
  user_data: dict)` (raises `PermissionError` unless `requesting_user.get_role()` is
  Admin or Manager; hashes an optional `password` field before delegating to the
  Repo, same as today's `CustomerService.create_customer`), `update_user(user_id,
  user_data)`, `delete_user(requesting_user, user_id)` (same role gate as create),
  `login(email, password)` (unchanged behavior from today's `CustomerService.login`,
  raises `ValueError` on bad credentials).

- [ ] **Step 1: Write the failing tests**

Create `Day_2/BackendWithRestApi/src/main/Python/tests/test_users_service.py`:

```python
import pytest

from Models.Users import Users
from Services.UsersService import UsersService
from Utilities.Status import UserRole


def make_user(role, user_id=1):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code="BR001")


def test_create_user_rejects_staff():
    staff = make_user(UserRole.STAFF)
    with pytest.raises(PermissionError):
        UsersService.create_user(staff, {"user_id": 2, "name": "New", "email": "new@example.com", "role": "Customer"})


def test_create_user_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        UsersService.create_user(customer, {"user_id": 2, "name": "New", "email": "new@example.com", "role": "Customer"})


def test_delete_user_rejects_staff():
    staff = make_user(UserRole.STAFF)
    with pytest.raises(PermissionError):
        UsersService.delete_user(staff, 2)


def test_delete_user_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        UsersService.delete_user(customer, 2)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest src/main/Python/tests/test_users_service.py -v`
Expected: FAIL / collection error — `Services.UsersService` does not exist yet.

- [ ] **Step 3: Create Services/UsersService.py and delete CustomersService.py**

Create `Day_2/BackendWithRestApi/src/main/Python/Services/UsersService.py`:

```python
"""
User Service for the Banking Domain REST API:
    Business logic for users, including role-based permission checks
    ported from Day_1's Bank.create_user/remove_user. Checks happen
    before any Repo/Mongo call so they're unit-testable without a
    database connection.
"""

import bcrypt

from Repos.UsersRepo import UsersRepository
from Utilities.Status import UserRole


class UsersService:
    @staticmethod
    def get_all_users():
        return UsersRepository.get_all_users()

    @staticmethod
    def get_user_by_id(user_id):
        return UsersRepository.get_user_by_id(user_id)

    @staticmethod
    def create_user(requesting_user, user_data):
        if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER):
            raise PermissionError("Only Admins and Managers can create users.")

        user_data = dict(user_data)
        password = user_data.pop("password", None)
        if password:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            user_data["password_hash"] = hashed.decode("utf-8")
        return UsersRepository.create_user(user_data)

    @staticmethod
    def update_user(user_id, user_data):
        return UsersRepository.update_user(user_id, user_data)

    @staticmethod
    def delete_user(requesting_user, user_id):
        if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER):
            raise PermissionError("Only Admins and Managers can remove users.")
        return UsersRepository.delete_user(user_id)

    @staticmethod
    def login(email, password):
        user = UsersRepository.get_user_by_email(email)
        if not user or not user.verify_password(password):
            raise ValueError("Invalid email or password.")
        return user
```

Delete `Day_2/BackendWithRestApi/src/main/Python/Services/CustomersService.py`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest src/main/Python/tests/test_users_service.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/Services/UsersService.py Day_2/BackendWithRestApi/src/main/Python/tests/test_users_service.py
git rm Day_2/BackendWithRestApi/src/main/Python/Services/CustomersService.py
git commit -m "Replace CustomersService with role-gated UsersService"
```

---

## Task 10: BranchesService with permission checks

**Files:**
- Create: `Day_2/BackendWithRestApi/src/main/Python/Services/BranchesService.py`
- Create: `Day_2/BackendWithRestApi/src/main/Python/tests/test_branches_service.py`

**Interfaces:**
- Consumes: `Repos.BranchesRepo.BranchesRepository` (Task 7), `Utilities.Status.UserRole`
  (Task 1).
- Produces: `Services.BranchesService.BranchesService` with static methods
  `get_all_branches(requesting_user)` (raises `PermissionError` for
  `UserRole.CUSTOMER`), `get_branch_by_code(branch_code)`,
  `create_branch(requesting_user, branch_data)` (raises `PermissionError` unless
  Admin), `update_branch(requesting_user, branch_code, branch_data)` (Admin only),
  `delete_branch(requesting_user, branch_code)` (Admin only).

- [ ] **Step 1: Write the failing tests**

Create `Day_2/BackendWithRestApi/src/main/Python/tests/test_branches_service.py`:

```python
import pytest

from Models.Users import Users
from Services.BranchesService import BranchesService
from Utilities.Status import UserRole


def make_user(role, user_id=1):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code="BR001")


def test_get_all_branches_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        BranchesService.get_all_branches(customer)


def test_create_branch_rejects_manager():
    manager = make_user(UserRole.MANAGER)
    with pytest.raises(PermissionError):
        BranchesService.create_branch(manager, {"branch_code": "BR999", "location": "Test"})


def test_update_branch_rejects_staff():
    staff = make_user(UserRole.STAFF)
    with pytest.raises(PermissionError):
        BranchesService.update_branch(staff, "BR001", {"location": "New"})


def test_delete_branch_rejects_manager():
    manager = make_user(UserRole.MANAGER)
    with pytest.raises(PermissionError):
        BranchesService.delete_branch(manager, "BR001")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest src/main/Python/tests/test_branches_service.py -v`
Expected: FAIL / collection error — `Services.BranchesService` does not exist yet.

- [ ] **Step 3: Create Services/BranchesService.py**

Create `Day_2/BackendWithRestApi/src/main/Python/Services/BranchesService.py`:

```python
"""
Branch Service for the Banking Domain REST API:
    Permission checks ported from Day_1's Bank.create_branch/remove_branch/
    get_branch_codes, checked before any Repo/Mongo call.
"""

from Repos.BranchesRepo import BranchesRepository
from Utilities.Status import UserRole


class BranchesService:
    @staticmethod
    def get_all_branches(requesting_user):
        if requesting_user.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only Staff can view all branch codes.")
        return BranchesRepository.get_all_branches()

    @staticmethod
    def get_branch_by_code(branch_code):
        return BranchesRepository.get_branch_by_code(branch_code)

    @staticmethod
    def create_branch(requesting_user, branch_data):
        if requesting_user.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admins can create branches.")
        return BranchesRepository.create_branch(branch_data)

    @staticmethod
    def update_branch(requesting_user, branch_code, branch_data):
        if requesting_user.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admins can update branches.")
        return BranchesRepository.update_branch(branch_code, branch_data)

    @staticmethod
    def delete_branch(requesting_user, branch_code):
        if requesting_user.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admins can remove branches.")
        return BranchesRepository.delete_branch(branch_code)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest src/main/Python/tests/test_branches_service.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/Services/BranchesService.py Day_2/BackendWithRestApi/src/main/Python/tests/test_branches_service.py
git commit -m "Add BranchesService with Admin-gated permission checks"
```

---

## Task 11: AccountsService rewrite with permission checks

**Files:**
- Modify (full rewrite): `Day_2/BackendWithRestApi/src/main/Python/Services/AccountsService.py`
- Create: `Day_2/BackendWithRestApi/src/main/Python/tests/test_accounts_service.py`

**Interfaces:**
- Consumes: `Repos.AccountsRepo.AccountsRepository` (Task 8),
  `Utilities.Status.{UserRole, AccountStatus}` (Task 1).
- Produces: `Services.AccountsService.AccountsService` with static methods
  `get_all_accounts(owner_id=None)`, `get_account_by_id(account_id, owner_id=None)`,
  `create_account(requesting_user, account_data)` (raises `PermissionError` unless
  Admin/Manager/Staff), `deposit(account_id, amount, requesting_user_id=None)`,
  `withdraw(account_id, amount, requesting_user_id=None)`,
  `delete_account(requesting_user, account_id)` (Admin/Manager/Staff only),
  `set_status(requesting_user, account_id, status: AccountStatus)`
  (Admin/Manager/Staff only), `transfer_funds(from_account_id, to_account_id, amount,
  requesting_user_id=None)`.

- [ ] **Step 1: Write the failing tests**

Create `Day_2/BackendWithRestApi/src/main/Python/tests/test_accounts_service.py`:

```python
import pytest

from Models.Users import Users
from Services.AccountsService import AccountsService
from Utilities.Status import AccountStatus, UserRole


def make_user(role, user_id=1):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code="BR001")


def test_create_account_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        AccountsService.create_account(customer, {
            "account_id": "ACC-1", "owner_id": 1, "balance": 100.0,
            "branch_code": "BR001", "account_type": "Checking",
        })


def test_delete_account_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        AccountsService.delete_account(customer, "ACC-1")


def test_set_status_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        AccountsService.set_status(customer, "ACC-1", AccountStatus.INACTIVE)


def test_set_status_allows_staff_to_reach_repo_layer():
    # Staff passes the permission gate; it will only fail later once it
    # tries to reach a real Mongo connection, proving the gate itself did
    # not block a legitimate role.
    staff = make_user(UserRole.STAFF)
    with pytest.raises(Exception) as exc_info:
        AccountsService.set_status(staff, "ACC-DOES-NOT-EXIST", AccountStatus.INACTIVE)
    assert not isinstance(exc_info.value, PermissionError)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest src/main/Python/tests/test_accounts_service.py -v`
Expected: FAIL — current `Services/AccountsService.py` has no permission checks at
all (calls pass straight through to the Repo).

- [ ] **Step 3: Rewrite Services/AccountsService.py**

Replace the full contents of
`Day_2/BackendWithRestApi/src/main/Python/Services/AccountsService.py` with:

```python
"""
Account Service for the Banking Domain REST API:
    Permission checks ported from Day_1's Bank.create_account/
    remove_account, checked before any Repo/Mongo call.
"""

from Repos.AccountsRepo import AccountsRepository
from Utilities.Status import UserRole, AccountStatus


class AccountsService:
    @staticmethod
    def get_all_accounts(owner_id=None):
        return AccountsRepository.get_all_accounts(owner_id)

    @staticmethod
    def get_account_by_id(account_id, owner_id=None):
        return AccountsRepository.get_account_by_id(account_id, owner_id)

    @staticmethod
    def create_account(requesting_user, account_data):
        if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF):
            raise PermissionError("Only Admins, Managers, and Staff can create accounts.")
        return AccountsRepository.create_account(account_data)

    @staticmethod
    def deposit(account_id, amount, requesting_user_id=None):
        return AccountsRepository.deposit(account_id, amount, requesting_user_id)

    @staticmethod
    def withdraw(account_id, amount, requesting_user_id=None):
        return AccountsRepository.withdraw(account_id, amount, requesting_user_id)

    @staticmethod
    def delete_account(requesting_user, account_id):
        if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF):
            raise PermissionError("Only Admins, Managers, and Staff can remove accounts.")
        return AccountsRepository.delete_account(account_id)

    @staticmethod
    def set_status(requesting_user, account_id, status: AccountStatus):
        if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF):
            raise PermissionError("Only Admins, Managers, and Staff can change account status.")
        return AccountsRepository.set_status(account_id, status)

    @staticmethod
    def transfer_funds(from_account_id, to_account_id, amount, requesting_user_id=None):
        return AccountsRepository.transfer_funds(from_account_id, to_account_id, amount, requesting_user_id)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest src/main/Python/tests/test_accounts_service.py -v`
Expected: 4 passed. (The 4th test reaches `AccountsRepository.set_status`, which
calls `get_database()` — if no `.env`/`MONGO_URI` is configured in the test
environment this raises `RuntimeError`, which the test accepts via `Exception`; it
only asserts the failure is *not* a `PermissionError`.)

- [ ] **Step 5: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/Services/AccountsService.py Day_2/BackendWithRestApi/src/main/Python/tests/test_accounts_service.py
git commit -m "Add permission checks to AccountsService"
```

---

## Task 12: Controllers — UsersController, BranchesController, AccountsController

**Files:**
- Create: `Day_2/BackendWithRestApi/src/main/Python/Controllers/UsersController.py`
- Delete: `Day_2/BackendWithRestApi/src/main/Python/Controllers/CustomersController.py`
- Create: `Day_2/BackendWithRestApi/src/main/Python/Controllers/BranchesController.py`
- Modify (full rewrite): `Day_2/BackendWithRestApi/src/main/Python/Controllers/AccountsController.py`

**Interfaces:**
- Consumes: `Services.UsersService.UsersService` (Task 9),
  `Services.BranchesService.BranchesService` (Task 10),
  `Services.AccountsService.AccountsService` (Task 11).
- Produces: `Controllers.UsersController.UsersController` (instance methods:
  `get_all_users()`, `get_user_by_id(user_id)`, `create_user(requesting_user,
  user_data)`, `update_user(user_id, user_data)`, `delete_user(requesting_user,
  user_id)`, `login(email, password)`); `Controllers.BranchesController.BranchesController`
  (`get_all_branches(requesting_user)`, `get_branch_by_code(branch_code)`,
  `create_branch(requesting_user, branch_data)`, `update_branch(requesting_user,
  branch_code, branch_data)`, `delete_branch(requesting_user, branch_code)`);
  `Controllers.AccountsController.AccountsController` (`get_all_accounts(owner_id=None)`,
  `get_account_by_id(account_id, owner_id=None)`, `create_account(requesting_user,
  account_data)`, `deposit(account_id, amount, requesting_user_id=None)`,
  `withdraw(account_id, amount, requesting_user_id=None)`,
  `delete_account(requesting_user, account_id)`, `set_status(requesting_user,
  account_id, status)`, `transfer_funds(from_account_id, to_account_id, amount,
  requesting_user_id=None)`). All Controllers stay thin pass-throughs (no logic of
  their own), matching the existing pattern.

- [ ] **Step 1: Create UsersController.py, delete CustomersController.py**

Create `Day_2/BackendWithRestApi/src/main/Python/Controllers/UsersController.py`:

```python
"""
User Controller for the Banking Domain REST API:
    Thin pass-through to UsersService, mirroring the existing Controller
    pattern (no HTTP concerns here - that's all in app.py).
"""

from Services.UsersService import UsersService


class UsersController:
    def __init__(self):
        self.users_service = UsersService()

    def get_all_users(self):
        return self.users_service.get_all_users()

    def get_user_by_id(self, user_id):
        return self.users_service.get_user_by_id(user_id)

    def create_user(self, requesting_user, user_data):
        return self.users_service.create_user(requesting_user, user_data)

    def update_user(self, user_id, user_data):
        return self.users_service.update_user(user_id, user_data)

    def delete_user(self, requesting_user, user_id):
        return self.users_service.delete_user(requesting_user, user_id)

    def login(self, email, password):
        return self.users_service.login(email, password)
```

Delete `Day_2/BackendWithRestApi/src/main/Python/Controllers/CustomersController.py`.

- [ ] **Step 2: Create BranchesController.py**

Create `Day_2/BackendWithRestApi/src/main/Python/Controllers/BranchesController.py`:

```python
"""
Branch Controller for the Banking Domain REST API:
    Thin pass-through to BranchesService.
"""

from Services.BranchesService import BranchesService


class BranchesController:
    def __init__(self):
        self.branches_service = BranchesService()

    def get_all_branches(self, requesting_user):
        return self.branches_service.get_all_branches(requesting_user)

    def get_branch_by_code(self, branch_code):
        return self.branches_service.get_branch_by_code(branch_code)

    def create_branch(self, requesting_user, branch_data):
        return self.branches_service.create_branch(requesting_user, branch_data)

    def update_branch(self, requesting_user, branch_code, branch_data):
        return self.branches_service.update_branch(requesting_user, branch_code, branch_data)

    def delete_branch(self, requesting_user, branch_code):
        return self.branches_service.delete_branch(requesting_user, branch_code)
```

- [ ] **Step 3: Rewrite AccountsController.py**

Replace the full contents of
`Day_2/BackendWithRestApi/src/main/Python/Controllers/AccountsController.py` with:

```python
"""
Account Controller for the Banking Domain REST API:
    Thin pass-through to AccountsService.
"""

from Services.AccountsService import AccountsService


class AccountsController:
    def __init__(self):
        self.accounts_service = AccountsService()

    def get_all_accounts(self, owner_id=None):
        return self.accounts_service.get_all_accounts(owner_id)

    def get_account_by_id(self, account_id, owner_id=None):
        return self.accounts_service.get_account_by_id(account_id, owner_id)

    def create_account(self, requesting_user, account_data):
        return self.accounts_service.create_account(requesting_user, account_data)

    def deposit(self, account_id, amount, requesting_user_id=None):
        return self.accounts_service.deposit(account_id, amount, requesting_user_id)

    def withdraw(self, account_id, amount, requesting_user_id=None):
        return self.accounts_service.withdraw(account_id, amount, requesting_user_id)

    def delete_account(self, requesting_user, account_id):
        return self.accounts_service.delete_account(requesting_user, account_id)

    def set_status(self, requesting_user, account_id, status):
        return self.accounts_service.set_status(requesting_user, account_id, status)

    def transfer_funds(self, from_account_id, to_account_id, amount, requesting_user_id=None):
        return self.accounts_service.transfer_funds(from_account_id, to_account_id, amount, requesting_user_id)
```

- [ ] **Step 4: Manual verification**

Controllers are pure pass-throughs with no branching logic of their own (consistent
with the existing pattern, and out of this plan's automated-test scope per the
spec). Verify by import-checking, from
`Day_2/BackendWithRestApi/src/main/Python/`:

```bash
python -c "
from Controllers.UsersController import UsersController
from Controllers.BranchesController import BranchesController
from Controllers.AccountsController import AccountsController
print('all controllers import cleanly')
"
```

Expected: `all controllers import cleanly`, no exceptions.

- [ ] **Step 5: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/Controllers/
git rm Day_2/BackendWithRestApi/src/main/Python/Controllers/CustomersController.py
git commit -m "Add Users/Branches Controllers, rewrite AccountsController"
```

---

## Task 13: app.py — REST endpoints, PermissionError handling

**Files:**
- Modify (full rewrite): `Day_2/BackendWithRestApi/src/main/Python/app.py`

**Interfaces:**
- Consumes: `Controllers.{UsersController, BranchesController, AccountsController}`
  (Tasks 9/10/12), `Models.{Users, Branches, Accounts}` (Tasks 2/3/4),
  `Utilities.Status.AccountStatus` (Task 1).
- Produces: the full REST API surface listed in the spec's endpoint table. No other
  task consumes this module directly (it's the outermost layer).

- [ ] **Step 1: Rewrite app.py**

Replace the full contents of
`Day_2/BackendWithRestApi/src/main/Python/app.py` with:

```python
"""
REST API entry point for the Banking Domain application:
    Exposes HTTP endpoints for user (role-based), branch, and account
    operations, backed by the Controller/Service/Repo layers. Run with:
        uvicorn app:app --reload
"""

from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from Controllers.UsersController import UsersController
from Controllers.BranchesController import BranchesController
from Controllers.AccountsController import AccountsController
from Models.Users import Users
from Models.Branches import Branches
from Models.Accounts import Accounts
from Utilities.Status import AccountStatus

app = FastAPI(title="Banking Domain REST API")
users_controller = UsersController()
branches_controller = BranchesController()
accounts_controller = AccountsController()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


@app.exception_handler(PermissionError)
def handle_permission_error(request: Request, exc: PermissionError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


def _require_user(user_id: int) -> Users:
    user = users_controller.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Unknown requesting_user_id.")
    return user


class UserCreate(BaseModel):
    user_id: int
    name: str
    email: str
    role: str
    branch_code: Optional[str] = None
    password: Optional[str] = None
    requesting_user_id: int


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    branch_code: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class BranchCreate(BaseModel):
    branch_code: str
    location: str
    manager_id: Optional[int] = None
    requesting_user_id: int


class BranchUpdate(BaseModel):
    location: Optional[str] = None
    manager_id: Optional[int] = None
    requesting_user_id: int


class AccountCreate(BaseModel):
    account_id: str
    owner_id: int
    balance: float
    branch_code: str
    account_type: str
    requesting_user_id: int


class AmountRequest(BaseModel):
    amount: float
    requesting_user_id: Optional[int] = None


class AccountTransfer(BaseModel):
    requesting_user_id: int
    from_account_id: str
    to_account_id: str
    amount: float


def _serialize_user(user: Users) -> dict:
    return {
        "user_id": user.get_user_id(),
        "name": user.get_name(),
        "email": user.get_email(),
        "role": user.get_role().value,
        "branch_code": user.get_branch_code(),
    }


def _serialize_branch(branch: Branches) -> dict:
    return {
        "branch_code": branch.get_branch_code(),
        "location": branch.get_location(),
        "manager_id": branch.manager_id,
        "staff_list": branch.staff_list,
    }


def _serialize_account(account: Accounts) -> dict:
    return {
        "account_id": account.get_account_id(),
        "owner_id": account.get_owner_id(),
        "balance": account.get_balance(),
        "branch_code": account.get_branch_code(),
        "account_type": account.get_account_type().value,
        "status": account.get_status().value,
    }


@app.post("/login")
def login(payload: LoginRequest):
    try:
        user = users_controller.login(payload.email, payload.password)
        return _serialize_user(user)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/users")
def get_all_users(requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    if requesting_user.get_role().value == "Customer":
        raise HTTPException(status_code=403, detail="Only Staff can view all users.")
    return [_serialize_user(user) for user in users_controller.get_all_users()]


@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    user = users_controller.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _serialize_user(user)


@app.post("/users")
def create_user(payload: UserCreate):
    requesting_user = _require_user(payload.requesting_user_id)
    try:
        data = payload.model_dump(exclude={"requesting_user_id"})
        new_user = users_controller.create_user(requesting_user, data)
        return _serialize_user(new_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdate):
    try:
        updated_user = users_controller.update_user(user_id, payload.model_dump(exclude_unset=True))
        return _serialize_user(updated_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/users/{user_id}")
def delete_user(user_id: int, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    try:
        users_controller.delete_user(requesting_user, user_id)
        return {"detail": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/branches")
def get_all_branches(requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    branches = branches_controller.get_all_branches(requesting_user)
    return [_serialize_branch(branch) for branch in branches]


@app.post("/branches")
def create_branch(payload: BranchCreate):
    requesting_user = _require_user(payload.requesting_user_id)
    try:
        data = payload.model_dump(exclude={"requesting_user_id"})
        new_branch = branches_controller.create_branch(requesting_user, data)
        return _serialize_branch(new_branch)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/branches/{branch_code}")
def update_branch(branch_code: str, payload: BranchUpdate):
    requesting_user = _require_user(payload.requesting_user_id)
    try:
        data = payload.model_dump(exclude={"requesting_user_id"}, exclude_unset=True)
        updated_branch = branches_controller.update_branch(requesting_user, branch_code, data)
        return _serialize_branch(updated_branch)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/branches/{branch_code}")
def delete_branch(branch_code: str, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    try:
        branches_controller.delete_branch(requesting_user, branch_code)
        return {"detail": "Branch deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/accounts")
def get_all_accounts(owner_id: int):
    accounts = accounts_controller.get_all_accounts(owner_id)
    return [_serialize_account(account) for account in accounts]


@app.get("/accounts/{account_id}")
def get_account_by_id(account_id: str, owner_id: int):
    account = accounts_controller.get_account_by_id(account_id, owner_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return _serialize_account(account)


@app.post("/accounts")
def create_account(payload: AccountCreate):
    requesting_user = _require_user(payload.requesting_user_id)
    try:
        data = payload.model_dump(exclude={"requesting_user_id"})
        new_account = accounts_controller.create_account(requesting_user, data)
        return _serialize_account(new_account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/deposit")
def deposit(account_id: str, payload: AmountRequest):
    try:
        account, result = accounts_controller.deposit(account_id, payload.amount, payload.requesting_user_id)
        return {"account": _serialize_account(account), "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/withdraw")
def withdraw(account_id: str, payload: AmountRequest):
    try:
        account, result = accounts_controller.withdraw(account_id, payload.amount, payload.requesting_user_id)
        return {"account": _serialize_account(account), "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/accounts/{account_id}/transactions")
def get_transactions(account_id: str, owner_id: int):
    account = accounts_controller.get_account_by_id(account_id, owner_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account.get_transaction_history()


@app.post("/accounts/{account_id}/deactivate")
def deactivate_account(account_id: str, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    try:
        account = accounts_controller.set_status(requesting_user, account_id, AccountStatus.INACTIVE)
        return _serialize_account(account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/reactivate")
def reactivate_account(account_id: str, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    try:
        account = accounts_controller.set_status(requesting_user, account_id, AccountStatus.ACTIVE)
        return _serialize_account(account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/accounts/{account_id}")
def delete_account(account_id: str, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    try:
        deleted = accounts_controller.delete_account(requesting_user, account_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Account not found")
        return {"detail": "Account deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/transfer")
def transfer_funds(payload: AccountTransfer):
    try:
        result = accounts_controller.transfer_funds(
            payload.from_account_id, payload.to_account_id, payload.amount, payload.requesting_user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

- [ ] **Step 2: Manual verification**

Requires a live MongoDB connection and the seed data from Task 14 — if Task 14 has
not run yet, skip straight to it and come back to verify both together. Once seeded,
from `Day_2/BackendWithRestApi/src/main/Python/`, run the server:

```bash
uvicorn app:app --reload
```

In a second terminal, verify the permission handler and a basic flow:

```bash
curl -s -X POST http://127.0.0.1:8000/login -H "Content-Type: application/json" -d "{\"email\": \"bob.customer@example.com\", \"password\": \"password123\"}"
curl -s "http://127.0.0.1:8000/branches?requesting_user_id=6"
```

Expected: the login call returns the customer's serialized user (with `role`); the
`/branches` call (customer's `user_id`, e.g. `6` from Task 14's seed data) returns
HTTP 403 with `{"detail": "Only Staff can view all branch codes."}`.

- [ ] **Step 3: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/app.py
git commit -m "Rewrite app.py with users/branches/accounts endpoints and PermissionError handling"
```

---

## Task 14: Seed data + console smoke script

**Files:**
- Modify (full rewrite): `Day_2/BackendWithRestApi/src/main/Python/Utilities/SeedMongo.py`
- Modify (full rewrite): `Day_2/BackendWithRestApi/src/main/Python/main.py`

**Interfaces:**
- Consumes: `Utilities.Database.get_database` (Task 5), `Controllers.{UsersController,
  BranchesController, AccountsController}` (Task 12), `Models.Users.Users` (Task 3),
  `Utilities.Status.{UserRole, AccountType, AccountStatus}` (Task 1).
- Produces: seeded `users`/`branches`/`accounts` collections; an updated smoke-test
  script. Nothing else depends on these two files.

- [ ] **Step 1: Rewrite Utilities/SeedMongo.py**

Replace the full contents of
`Day_2/BackendWithRestApi/src/main/Python/Utilities/SeedMongo.py` with:

```python
"""
One-time seed script:
    Loads sample users (one per role), branches, and accounts into
    MongoDB. Mirrors Day_1's seed_data.py structure, adapted to
    Day_2's email-based login.
    Run directly: python Utilities/SeedMongo.py
"""

import bcrypt

from Utilities.Database import get_database

SAMPLE_PASSWORD = "password123"

SAMPLE_USERS = [
    {"user_id": 1, "name": "Alex Admin", "email": "admin@citibank.com", "role": "Admin", "branch_code": None},
    {"user_id": 2, "name": "Jamie Jones", "email": "mgr.jones@citibank.com", "role": "Manager", "branch_code": "BR001"},
    {"user_id": 3, "name": "Lee Park", "email": "mgr.lee@citibank.com", "role": "Manager", "branch_code": "BR002"},
    {"user_id": 4, "name": "Amy Staff", "email": "staff.amy@citibank.com", "role": "Staff", "branch_code": "BR001"},
    {"user_id": 5, "name": "Ravi Staff", "email": "staff.ravi@citibank.com", "role": "Staff", "branch_code": "BR002"},
    {"user_id": 6, "name": "Bob Customer", "email": "bob.customer@example.com", "role": "Customer", "branch_code": "BR001"},
    {"user_id": 7, "name": "Amy Customer", "email": "amy.customer@example.com", "role": "Customer", "branch_code": "BR002"},
]

SAMPLE_BRANCHES = [
    {"branch_code": "BR001", "location": "Downtown Chicago", "manager_id": 2, "staff_list": [4]},
    {"branch_code": "BR002", "location": "Uptown Chicago", "manager_id": 3, "staff_list": [5]},
]

SAMPLE_ACCOUNTS = [
    {"account_id": "ACC-1001", "owner_id": 6, "balance": 1500.00, "branch_code": "BR001",
     "account_type": "Checking", "status": "active", "transaction_history": []},
    {"account_id": "ACC-1002", "owner_id": 6, "balance": 5000.00, "branch_code": "BR001",
     "account_type": "Savings", "status": "active", "transaction_history": []},
    {"account_id": "ACC-2001", "owner_id": 7, "balance": 750.00, "branch_code": "BR002",
     "account_type": "Checking", "status": "active", "transaction_history": []},
]

if __name__ == "__main__":
    users_collection = get_database().users
    password_hash = bcrypt.hashpw(SAMPLE_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    for user in SAMPLE_USERS:
        user_doc = dict(user)
        user_doc["password_hash"] = password_hash
        users_collection.update_one({"user_id": user_doc["user_id"]}, {"$set": user_doc}, upsert=True)
    print(f"Seeded {len(SAMPLE_USERS)} users into MongoDB (password: '{SAMPLE_PASSWORD}').")

    branches_collection = get_database().branches
    for branch in SAMPLE_BRANCHES:
        branches_collection.update_one({"branch_code": branch["branch_code"]}, {"$set": branch}, upsert=True)
    print(f"Seeded {len(SAMPLE_BRANCHES)} branches into MongoDB.")

    accounts_collection = get_database().accounts
    for account in SAMPLE_ACCOUNTS:
        accounts_collection.update_one({"account_id": account["account_id"]}, {"$set": account}, upsert=True)
    print(f"Seeded {len(SAMPLE_ACCOUNTS)} accounts into MongoDB.")

    print("\nSeed accounts (email / password / role / branch):")
    for user in SAMPLE_USERS:
        branch_label = user["branch_code"] or "-"
        print(f"  {user['email']:<28} / {SAMPLE_PASSWORD} ({user['role']}, {branch_label})")
```

- [ ] **Step 2: Run the seed script**

From `Day_2/BackendWithRestApi/src/main/Python/`, run:

```bash
python Utilities/SeedMongo.py
```

Expected: prints `Seeded 7 users...`, `Seeded 2 branches...`, `Seeded 3 accounts...`,
then the credentials list. Requires `.env` with a valid `MONGO_URI`.

- [ ] **Step 3: Rewrite main.py smoke script**

Replace the full contents of
`Day_2/BackendWithRestApi/src/main/Python/main.py` with:

```python
"""
Console smoke-test script for the Banking Domain REST API layers:
    Exercises the Controller/Service layer directly (Users, Branches,
    Accounts) against the seeded MongoDB data, printing pass/fail for a
    set of edge cases. Not an automated test suite - see src/main/Python/tests/
    for pytest coverage of the Service-layer permission checks.
    Run after Utilities/SeedMongo.py: python main.py
"""

from Controllers.UsersController import UsersController
from Controllers.BranchesController import BranchesController
from Controllers.AccountsController import AccountsController
from Utilities.Status import AccountStatus


def expect_error(description, action, expected_exception=ValueError):
    try:
        action()
        print(f"FAIL - {description}: expected {expected_exception.__name__} but none was raised.")
    except expected_exception as e:
        print(f"PASS - {description}: {e}")


def main():
    print("Banking Domain REST API - console smoke test")
    users = UsersController()
    branches = BranchesController()
    accounts = AccountsController()

    admin = users.login("admin@citibank.com", "password123")
    manager = users.login("mgr.jones@citibank.com", "password123")
    staff = users.login("staff.amy@citibank.com", "password123")
    customer = users.login("bob.customer@example.com", "password123")
    print(f"Logged in as: {admin}, {manager}, {staff}, {customer}")

    print("\n--- Users ---")
    print("All users:", [str(u) for u in users.get_all_users()])

    print("\n--- Branches ---")
    print("All branches (as manager):", [str(b) for b in branches.get_all_branches(manager)])

    print("\n--- Accounts ---")
    bob_accounts = accounts.get_all_accounts(customer.get_user_id())
    print("Bob's accounts:", [str(a) for a in bob_accounts])

    print("\nDeposit 100 into ACC-1001:")
    account, result = accounts.deposit("ACC-1001", 100.0, customer.get_user_id())
    print(result, "new balance:", account.get_balance())

    print("\nWithdraw 200 from ACC-1001 (Checking, overdraft allowed):")
    account, result = accounts.withdraw("ACC-1001", 2000.0, customer.get_user_id())
    print(result, "new balance:", account.get_balance())

    print("\nTransfer 50 from ACC-1001 to ACC-1002:")
    print(accounts.transfer_funds("ACC-1001", "ACC-1002", 50.0, customer.get_user_id()))

    print("\nDeactivate ACC-1002 (as staff), then try to deposit:")
    accounts.set_status(staff, "ACC-1002", AccountStatus.INACTIVE)
    account, result = accounts.deposit("ACC-1002", 10.0)
    print(result)
    accounts.set_status(staff, "ACC-1002", AccountStatus.ACTIVE)

    print("\n--- Edge cases ---")

    expect_error(
        "customer cannot view all branches",
        lambda: branches.get_all_branches(customer),
        expected_exception=PermissionError,
    )

    expect_error(
        "staff cannot create a branch",
        lambda: branches.create_branch(staff, {"branch_code": "BR999", "location": "Nowhere"}),
        expected_exception=PermissionError,
    )

    expect_error(
        "customer cannot create an account",
        lambda: accounts.create_account(customer, {
            "account_id": "ACC-9999", "owner_id": customer.get_user_id(), "balance": 10.0,
            "branch_code": "BR001", "account_type": "Checking",
        }),
        expected_exception=PermissionError,
    )

    expect_error(
        "staff cannot create a user",
        lambda: users.create_user(staff, {
            "user_id": 999, "name": "Nobody", "email": "nobody@example.com", "role": "Customer",
        }),
        expected_exception=PermissionError,
    )

    expect_error(
        "login with wrong password",
        lambda: users.login("bob.customer@example.com", "wrong-password"),
    )

    expect_error(
        "get account belonging to someone else returns None, not raise",
        lambda: (_ for _ in ()).throw(AssertionError("should not reach here"))
        if accounts.get_account_by_id("ACC-2001", customer.get_user_id()) is not None
        else (_ for _ in ()).throw(ValueError("account correctly hidden from non-owner")),
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the smoke script**

From `Day_2/BackendWithRestApi/src/main/Python/`, run (after Step 2's seed):

```bash
python main.py
```

Expected: prints login confirmations, users/branches/accounts listings, successful
deposit/withdraw/transfer results, and `PASS` for every edge case in the "Edge
cases" section.

- [ ] **Step 5: Commit**

```bash
git add Day_2/BackendWithRestApi/src/main/Python/Utilities/SeedMongo.py Day_2/BackendWithRestApi/src/main/Python/main.py
git commit -m "Rewrite seed data and console smoke script for the new domain model"
```

---

## Final verification (run once all tasks are complete)

- [ ] Run the full pytest suite from `Day_2/BackendWithRestApi/`: `pytest -v` —
  expect all tests across Tasks 1–11 to pass (43 tests: 4 status + 12 accounts model
  + 7 users model + 8 branches model + 4 users service + 4 branches service + 4
  accounts service).
- [ ] Re-run `python Utilities/SeedMongo.py` then `python main.py` from Task 14 — all
  `PASS`, no `FAIL`.
- [ ] Start `uvicorn app:app --reload` and manually exercise `/login`, `/branches`,
  `/accounts`, `/accounts/{id}/deposit`, `/accounts/{id}/withdraw`,
  `/accounts/transfer` with `curl` using the seeded credentials from Task 14 to
  confirm the full HTTP surface behaves as documented in the spec's endpoint table.

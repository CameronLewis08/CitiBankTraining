"""
Seed Data for the Banking Domain Console Application:
    Builds a Banks instance pre-populated with branches, users of every role,
    and accounts so the console app has data to explore without manual setup.
"""

from Models.banks import Banks
from Models.users import Users, UserRole
from status import AccountType


def create_seed_data():
    bank = Banks("Citi Bank")

    # Bootstrap the first Admin directly - every other user/branch/account is
    # created through Banks methods, which all require an Admin/Manager caller.
    admin = Users("admin", "Admin@123", UserRole.ADMIN, "admin@citibank.com", None)
    bank.users[admin.username] = admin

    bank.create_branch(admin, "BR001", "Downtown Chicago", "mgr_jones", [])
    bank.create_branch(admin, "BR002", "Uptown Chicago", "mgr_lee", [])

    bank.create_user(admin, "mgr_jones", "Manager@123", UserRole.MANAGER, "jones@citibank.com", "BR001")
    bank.create_user(admin, "mgr_lee", "Manager@123", UserRole.MANAGER, "lee@citibank.com", "BR002")
    bank.create_user(admin, "staff_amy", "Staff@123", UserRole.STAFF, "amy@citibank.com", "BR001")
    bank.create_user(admin, "staff_ravi", "Staff@123", UserRole.STAFF, "ravi@citibank.com", "BR002")

    manager1 = bank.users["mgr_jones"]
    manager2 = bank.users["mgr_lee"]

    bank.branch_codes["BR001"].set_manager(admin, manager1.username)
    bank.branch_codes["BR002"].set_manager(admin, manager2.username)

    bank.create_user(manager1, "cust_bob", "Customer@123", UserRole.CUSTOMER, "bob@example.com", "BR001")
    bank.create_user(manager2, "cust_amy", "Customer@123", UserRole.CUSTOMER, "amy.customer@example.com", "BR002")

    bank.create_account(manager1, "1001", AccountType.CHECKING, 1500.00, "cust_bob", "BR001")
    bank.create_account(manager1, "1002", AccountType.SAVINGS, 5000.00, "cust_bob", "BR001")
    bank.create_account(manager2, "2001", AccountType.CHECKING, 750.00, "cust_amy", "BR002")

    return bank


SEED_CREDENTIALS = """Seed accounts (username / password):
  admin       / Admin@123      (Admin)
  mgr_jones   / Manager@123    (Manager, BR001)
  mgr_lee     / Manager@123    (Manager, BR002)
  staff_amy   / Staff@123      (Staff, BR001)
  staff_ravi  / Staff@123      (Staff, BR002)
  cust_bob    / Customer@123   (Customer, BR001, accounts 1001 checking / 1002 savings)
  cust_amy    / Customer@123   (Customer, BR002, account 2001 checking)"""

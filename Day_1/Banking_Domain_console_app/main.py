"""
Banking Domain Console App:
    This file will act as the entry point for the Banking Domain Console Application. It will handle user interactions, display menus, and invoke the appropriate functions from the banking domain modules based on user input.

"""
from status import AccountType
from Models.users import UserRole
from seed_data import create_seed_data, SEED_CREDENTIALS
from input import user_input, get_choice, get_float


def login(bank):
    print("\n--- Login ---")
    username = user_input("Username: ")
    password = user_input("Password: ")
    user = bank.users.get(username)
    if user is None:
        print("User not found.")
        return None

    try:
        if user.authenticate(username, password):
            print(f"Welcome, {user.username} ({user.get_role().value})!")
            return user
        print("Incorrect password.")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None


def find_account(bank, account_number):
    for branch in bank.branch_codes.values():
        account = branch.get_account(account_number)
        if account is not None:
            return account, branch
    return None, None


def get_owner_accounts(bank, username):
    accounts = []
    for branch in bank.branch_codes.values():
        for account in branch.get_accounts():
            if account.owner_id == username:
                accounts.append(account)
    return accounts


def select_own_account(accounts, prompt):
    if not accounts:
        print("You have no accounts.")
        return None
    account_number = user_input(prompt)
    for account in accounts:
        if str(account.account_number) == account_number:
            return account
    print("Account not found or not yours.")
    return None


def admin_menu(bank, user):
    while True:
        print("\n--- Admin Menu ---")
        print("1. Create Branch")
        print("2. Remove Branch")
        print("3. View Branch Codes")
        print("4. Create User")
        print("5. Remove User")
        print("6. View Users")
        print("0. Logout")
        choice = user_input("Choose an option: ")

        try:
            if choice == "1":
                branch_code = user_input("Branch code: ")
                location = user_input("Location: ")
                manager_id = user_input("Manager username (leave blank for none): ") or None
                print(bank.create_branch(user, branch_code, location, manager_id, []))
            elif choice == "2":
                branch_code = user_input("Branch code to remove: ")
                print(bank.remove_branch(user, branch_code))
            elif choice == "3":
                print(bank.get_branch_codes(user))
            elif choice == "4":
                username = user_input("New username: ")
                password = user_input("New password (min 8 chars): ")
                role = UserRole(get_choice("Role (Admin/Manager/Staff/Customer): ", [r.value for r in UserRole]))
                email = user_input("Email: ")
                branch_code = user_input("Branch code: ")
                print(bank.create_user(user, username, password, role, email, branch_code))
            elif choice == "5":
                username = user_input("Username to remove: ")
                target = bank.users.get(username)
                if target is None:
                    print("User not found.")
                    continue
                print(bank.remove_user(user, target))
            elif choice == "6":
                print(bank.get_users(user))
            elif choice == "0":
                break
            else:
                print("Invalid option.")
        except (ValueError, PermissionError) as e:
            print(f"Error: {e}")


def staff_menu(bank, user):
    while True:
        print(f"\n--- {user.get_role().value} Menu ---")
        print("1. Create Account")
        print("2. Remove Account")
        print("3. View Branch Accounts")
        print("4. Deposit")
        print("5. Withdraw")
        print("6. Transfer")
        print("0. Logout")
        choice = user_input("Choose an option: ")

        try:
            if choice == "1":
                account_number = user_input("New account number: ")
                account_type = AccountType(get_choice("Account type (Checking/Savings): ", [t.value for t in AccountType]))
                balance = get_float("Initial balance: ")
                owner_id = user_input("Owner username: ")
                branch_code = user_input("Branch code: ")
                print(bank.create_account(user, account_number, account_type, balance, owner_id, branch_code))
            elif choice == "2":
                account_number = user_input("Account number to remove: ")
                branch_code = user_input("Branch code: ")
                print(bank.remove_account(user, account_number, branch_code))
            elif choice == "3":
                branch_code = user_input("Branch code: ")
                branch = bank.branch_codes.get(branch_code)
                if branch is None:
                    print("Branch not found.")
                    continue
                accounts = branch.get_accounts()
                if not accounts:
                    print("No accounts in this branch.")
                for account in accounts:
                    print(account)
            elif choice == "4":
                account_number = user_input("Account number: ")
                account, _ = find_account(bank, account_number)
                if account is None:
                    print("Account not found.")
                    continue
                amount = get_float("Deposit amount: ")
                print(account.deposit(amount))
            elif choice == "5":
                account_number = user_input("Account number: ")
                account, _ = find_account(bank, account_number)
                if account is None:
                    print("Account not found.")
                    continue
                amount = get_float("Withdrawal amount: ")
                print(account.withdraw(amount))
            elif choice == "6":
                from_number = user_input("From account number: ")
                to_number = user_input("To account number: ")
                from_account, _ = find_account(bank, from_number)
                to_account, _ = find_account(bank, to_number)
                if from_account is None or to_account is None:
                    print("One or both accounts not found.")
                    continue
                amount = get_float("Transfer amount: ")
                print(from_account.transfer(amount, to_account))
            elif choice == "0":
                break
            else:
                print("Invalid option.")
        except (ValueError, PermissionError) as e:
            print(f"Error: {e}")


def customer_menu(bank, user):
    while True:
        my_accounts = get_owner_accounts(bank, user.username)

        print("\n--- Customer Menu ---")
        print("1. View My Accounts")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer")
        print("5. View Transaction History")
        print("0. Logout")
        choice = user_input("Choose an option: ")

        try:
            if choice == "1":
                if not my_accounts:
                    print("You have no accounts.")
                for account in my_accounts:
                    print(account)
            elif choice == "2":
                account = select_own_account(my_accounts, "Deposit to which account number? ")
                if account is None:
                    continue
                amount = get_float("Deposit amount: ")
                print(account.deposit(amount))
            elif choice == "3":
                account = select_own_account(my_accounts, "Withdraw from which account number? ")
                if account is None:
                    continue
                amount = get_float("Withdrawal amount: ")
                print(account.withdraw(amount))
            elif choice == "4":
                account = select_own_account(my_accounts, "Transfer from which account number? ")
                if account is None:
                    continue
                to_number = user_input("Transfer to account number: ")
                to_account, _ = find_account(bank, to_number)
                if to_account is None:
                    print("Target account not found.")
                    continue
                amount = get_float("Transfer amount: ")
                print(account.transfer(amount, to_account))
            elif choice == "5":
                account = select_own_account(my_accounts, "View history for which account number? ")
                if account is None:
                    continue
                history = account.get_transaction_history()
                if not history:
                    print("No transactions yet.")
                for transaction in history:
                    print(transaction)
            elif choice == "0":
                break
            else:
                print("Invalid option.")
        except (ValueError, PermissionError) as e:
            print(f"Error: {e}")


ROLE_MENUS = {
    UserRole.ADMIN: admin_menu,
    UserRole.MANAGER: staff_menu,
    UserRole.STAFF: staff_menu,
    UserRole.CUSTOMER: customer_menu,
}


def main():
    print("Welcome to the Banking Domain Console Application!")
    bank = create_seed_data()
    print(f"\nLoaded {bank.get_bank_name()}")
    print(SEED_CREDENTIALS)

    while True:
        print("\n=== Main Menu ===")
        print("1. Login")
        print("0. Exit")
        choice = user_input("Choose an option: ")

        if choice == "1":
            user = login(bank)
            if user is None:
                continue
            ROLE_MENUS[user.get_role()](bank, user)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()

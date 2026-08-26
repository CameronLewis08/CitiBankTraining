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

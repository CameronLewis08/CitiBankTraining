import { useMemo, useState } from 'react'
import type { ChangeEvent } from 'react'
import Layout from '../Components/Layout/Layout'
import { useAuth } from '../Context/AuthContext'
import { useUsers } from '../hooks/users/useUsers'
import { useAccounts } from '../hooks/accounts/useAccounts'
import { useBranches } from '../hooks/accounts/useBranches'
import FilterDropdown from '../Components/FilterDropdown/FilterDropdown'
import { PageWrapper, PageTitle, PageSubtitle } from '../Components/PageHero/PageHero.styled'
import { TableWrapper, Table, Thead, Tbody, Tr, Th, Td, EmptyRow } from '../Components/Table/Table.styled'
import { FormGroup, Label, Input, ErrorMessage } from '../Components/Form/Form.styled'
import { formatCurrency } from '../data/accounts'
import { ControlsRow, SearchBar } from './AdminDashboardPage.styled'

type View = 'users' | 'accounts' | 'branches'

const viewOptions: { value: View; label: string }[] = [
  { value: 'users', label: 'Usernames' },
  { value: 'accounts', label: 'Accounts' },
  { value: 'branches', label: 'Branches' },
]

const searchPlaceholders: Record<View, string> = {
  users: 'e.g. Amy, BR001, or ACC-5d2171a3…',
  accounts: 'e.g. ACC-5d2171a3, BR001, or an owner’s name…',
  branches: 'e.g. BR001 or Downtown Chicago…',
}

// Backend note: UsersService.get_all_users 403s for role CUSTOMER
// (Services/UsersService.py), so this page is gated up front rather than
// letting the hooks fire and surfacing a raw permission error.
//
// The accounts fetch (GET /accounts with no owner_id) self-scopes per role
// on the backend (AccountsService.get_all_accounts): Admin gets every
// account, Manager/Staff only their own branch's - so a Manager/Staff
// viewer's search naturally can't match accounts outside their branch, no
// extra frontend logic needed for that.
function AdminDashboardPage() {
  const { customer } = useAuth()
  const isCustomer = customer?.role === 'Customer'
  const requestingUserId = isCustomer ? undefined : customer?.user_id

  const { users, isLoading: isLoadingUsers, error: usersError } = useUsers(requestingUserId)
  const { accounts, isLoading: isLoadingAccounts, error: accountsError } = useAccounts(requestingUserId)
  const { branches, isLoading: isLoadingBranches, error: branchesError } = useBranches(requestingUserId)

  const [view, setView] = useState<View>('users')
  const [search, setSearch] = useState('')

  const isLoading = isLoadingUsers || isLoadingAccounts || isLoadingBranches
  const error = usersError || accountsError || branchesError

  const usersById = useMemo(() => {
    const map = new Map<number, (typeof users)[number]>()
    for (const user of users) map.set(user.user_id, user)
    return map
  }, [users])

  const accountsByOwner = useMemo(() => {
    const map = new Map<number, string[]>()
    for (const account of accounts) {
      const existing = map.get(account.owner_id)
      if (existing) existing.push(account.account_id)
      else map.set(account.owner_id, [account.account_id])
    }
    return map
  }, [accounts])

  function nameFor(userId: number | null): string {
    if (userId === null) return '—'
    return usersById.get(userId)?.name ?? `#${userId}`
  }

  const term = search.trim().toLowerCase()

  const visibleUsers = useMemo(() => {
    const withAccounts = users.map((user) => ({
      user,
      accountIds: accountsByOwner.get(user.user_id) ?? [],
    }))

    const filtered = term
      ? withAccounts.filter(({ user, accountIds }) => {
          const matchesName = user.name.toLowerCase().includes(term)
          const matchesBranch = (user.branch_code ?? '').toLowerCase().includes(term)
          const matchesAccount = accountIds.some((accountId) => accountId.toLowerCase().includes(term))
          return matchesName || matchesBranch || matchesAccount
        })
      : withAccounts

    return filtered.sort((a, b) => a.user.name.localeCompare(b.user.name))
  }, [users, accountsByOwner, term])

  const visibleAccounts = useMemo(() => {
    const filtered = term
      ? accounts.filter((account) => {
          const matchesId = account.account_id.toLowerCase().includes(term)
          const matchesBranch = account.branch_code.toLowerCase().includes(term)
          const matchesOwner = nameFor(account.owner_id).toLowerCase().includes(term)
          return matchesId || matchesBranch || matchesOwner
        })
      : accounts

    return [...filtered].sort((a, b) => a.account_id.localeCompare(b.account_id))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accounts, term, usersById])

  const visibleBranches = useMemo(() => {
    const filtered = term
      ? branches.filter((branch) => {
          const matchesCode = branch.branch_code.toLowerCase().includes(term)
          const matchesLocation = branch.location.toLowerCase().includes(term)
          return matchesCode || matchesLocation
        })
      : branches

    return [...filtered].sort((a, b) => a.branch_code.localeCompare(b.branch_code))
  }, [branches, term])

  function handleSearchChange(event: ChangeEvent<HTMLInputElement>) {
    setSearch(event.target.value)
  }

  return (
    <Layout>
      <PageWrapper>
        <PageTitle>Admin Dashboard</PageTitle>
        <PageSubtitle>Look up staff, customers, accounts, and branches in one place.</PageSubtitle>

        {isCustomer && (
          <ErrorMessage role="alert">You do not have permission to view this page.</ErrorMessage>
        )}

        {!isCustomer && (
          <>
            <ControlsRow>
              <SearchBar>
                <FormGroup>
                  <Label htmlFor="admin-search">Search</Label>
                  <Input
                    id="admin-search"
                    type="search"
                    placeholder={searchPlaceholders[view]}
                    value={search}
                    onChange={handleSearchChange}
                  />
                </FormGroup>
              </SearchBar>

              <FilterDropdown<View>
                id="admin-view"
                label="Show"
                value={view}
                options={viewOptions}
                onChange={setView}
              />
            </ControlsRow>

            {isLoading && <PageSubtitle>Loading…</PageSubtitle>}
            {error && <ErrorMessage role="alert">{error}</ErrorMessage>}

            {!isLoading && !error && view === 'users' && (
              <TableWrapper>
                <Table>
                  <Thead>
                    <Tr>
                      <Th>Name</Th>
                      <Th>Email</Th>
                      <Th>Role</Th>
                      <Th>Branch</Th>
                      <Th>Accounts</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {visibleUsers.map(({ user, accountIds }) => (
                      <Tr key={user.user_id}>
                        <Td>{user.name}</Td>
                        <Td>{user.email}</Td>
                        <Td>{user.role}</Td>
                        <Td>{user.branch_code ?? '—'}</Td>
                        <Td>{accountIds.length > 0 ? accountIds.join(', ') : '—'}</Td>
                      </Tr>
                    ))}
                    {visibleUsers.length === 0 && (
                      <Tr>
                        <EmptyRow colSpan={5}>No users match "{search}".</EmptyRow>
                      </Tr>
                    )}
                  </Tbody>
                </Table>
              </TableWrapper>
            )}

            {!isLoading && !error && view === 'accounts' && (
              <TableWrapper>
                <Table>
                  <Thead>
                    <Tr>
                      <Th>Account ID</Th>
                      <Th>Owner</Th>
                      <Th>Branch</Th>
                      <Th>Type</Th>
                      <Th>Balance</Th>
                      <Th>Status</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {visibleAccounts.map((account) => (
                      <Tr key={account.account_id}>
                        <Td>{account.account_id}</Td>
                        <Td>{nameFor(account.owner_id)}</Td>
                        <Td>{account.branch_code}</Td>
                        <Td>{account.account_type}</Td>
                        <Td>{formatCurrency(account.balance)}</Td>
                        <Td>{account.status}</Td>
                      </Tr>
                    ))}
                    {visibleAccounts.length === 0 && (
                      <Tr>
                        <EmptyRow colSpan={6}>No accounts match "{search}".</EmptyRow>
                      </Tr>
                    )}
                  </Tbody>
                </Table>
              </TableWrapper>
            )}

            {!isLoading && !error && view === 'branches' && (
              <TableWrapper>
                <Table>
                  <Thead>
                    <Tr>
                      <Th>Branch Code</Th>
                      <Th>Location</Th>
                      <Th>Manager</Th>
                      <Th>Staff</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {visibleBranches.map((branch) => (
                      <Tr key={branch.branch_code}>
                        <Td>{branch.branch_code}</Td>
                        <Td>{branch.location}</Td>
                        <Td>{nameFor(branch.manager_id)}</Td>
                        <Td>{branch.staff_list.length > 0 ? branch.staff_list.map(nameFor).join(', ') : '—'}</Td>
                      </Tr>
                    ))}
                    {visibleBranches.length === 0 && (
                      <Tr>
                        <EmptyRow colSpan={4}>No branches match "{search}".</EmptyRow>
                      </Tr>
                    )}
                  </Tbody>
                </Table>
              </TableWrapper>
            )}
          </>
        )}
      </PageWrapper>
    </Layout>
  )
}

export default AdminDashboardPage

import { useEffect, useMemo, useState } from 'react'
import type { ChangeEvent } from 'react'
import Layout from '../Components/Layout/Layout'
import { useAuth } from '../Context/AuthContext'
import { useUsers } from '../hooks/users/useUsers'
import { useUserDetail } from '../hooks/users/useUserDetails'
import { useAccounts } from '../hooks/accounts/useAccounts'
import type { Account } from '../hooks/accounts/useAccounts'
import { useBranches } from '../hooks/accounts/useBranches'
import type { Branch } from '../hooks/accounts/useBranches'
import FilterDropdown from '../Components/FilterDropdown/FilterDropdown'
import Modal from '../Components/Modal/Modal'
import ConfirmModal from '../Components/Modal/ConfirmModal'
import { PageWrapper, PageTitle, PageSubtitle } from '../Components/PageHero/PageHero.styled'
import { TableWrapper, Table, Thead, Tbody, Tr, Th, Td, EmptyRow } from '../Components/Table/Table.styled'
import { FormGroup, Label, Input, SubmitButton, ErrorMessage } from '../Components/Form/Form.styled'
import { formatCurrency } from '../data/accounts'
import { post, put, del } from '../api/client'
import {
  ControlsRow, SearchBar, ClickableTr, ActionsCell, RowActionButton, RowDeleteButton, NewBranchRow, LoadMoreRow,
} from './AdminDashboardPage.styled'
import { ReadOnlyList, ReadOnlyLabel, ReadOnlyValue } from './ProfilePage.styled'

type View = 'users' | 'accounts' | 'branches'

const allViewOptions: { value: View; label: string }[] = [
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
// Both the accounts and users fetches self-scope per role on the backend
// (AccountsService.get_all_accounts / UsersService.get_all_users): Admin
// gets everything, Manager/Staff only their own branch's - so a
// Manager/Staff viewer's search naturally can't match anything outside
// their branch, no extra frontend filtering logic needed for that. The
// Branches tab is hidden for non-Admins below since branch management
// (create/update/delete) is Admin-only - viewing the list isn't actually
// restricted by the backend, but showing it here would imply a
// capability Manager/Staff don't have.
function AdminDashboardPage() {
  const { customer } = useAuth()
  const isCustomer = customer?.role === 'Customer'
  const isAdmin = customer?.role === 'Admin'
  const requestingUserId = isCustomer ? undefined : customer?.user_id

  // Debounced so typing doesn't fire a request per keystroke - search now
  // hits the server (GET /users|/accounts|/branches's `search` param)
  // instead of filtering an already-fully-fetched array in the browser.
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')

  useEffect(() => {
    const timeout = setTimeout(() => setDebouncedSearch(search.trim()), 300)
    return () => clearTimeout(timeout)
  }, [search])

  const PAGE_SIZE = 25
  const pageOptions = { limit: PAGE_SIZE, search: debouncedSearch || undefined }

  const {
    users, isLoading: isLoadingUsers, isLoadingMore: isLoadingMoreUsers, hasMore: hasMoreUsers,
    error: usersError, refetch: refetchUsers, loadMore: loadMoreUsers,
  } = useUsers(requestingUserId, pageOptions)
  const {
    accounts, isLoading: isLoadingAccounts, isLoadingMore: isLoadingMoreAccounts, hasMore: hasMoreAccounts,
    error: accountsError, refetch: refetchAccounts, loadMore: loadMoreAccounts,
  } = useAccounts(requestingUserId, undefined, pageOptions)
  const {
    branches, isLoading: isLoadingBranches, isLoadingMore: isLoadingMoreBranches, hasMore: hasMoreBranches,
    error: branchesError, refetch: refetchBranches, loadMore: loadMoreBranches,
  } = useBranches(requestingUserId, pageOptions)

  // Delete User is Admin/Manager only, matching UsersService.delete_user.
  // Account status/delete have no extra role check here beyond the
  // dashboard's own isCustomer gate - Admin, Manager, and Staff can all
  // deposit/withdraw/deactivate/delete accounts per AccountsService, so
  // every non-Customer viewer of this page already qualifies.
  const canDeleteUsers = customer?.role === 'Admin' || customer?.role === 'Manager'

  const viewOptions = isAdmin ? allViewOptions : allViewOptions.filter((option) => option.value !== 'branches')

  const [view, setView] = useState<View>('users')

  // If the role changes (e.g. a different user logs in) and the current
  // view is no longer offered, fall back to a view everyone can see.
  useEffect(() => {
    if (!isAdmin && view === 'branches') {
      setView('users')
    }
  }, [isAdmin, view])

  const isLoading = isLoadingUsers || isLoadingAccounts || isLoadingBranches
  const error = usersError || accountsError || branchesError

  // --- User detail modal (view-only, read via GET /users/{id}) ---
  const [viewUserId, setViewUserId] = useState<number | null>(null)
  const {
    user: viewedUser, isLoading: isLoadingViewedUser, error: viewedUserError,
  } = useUserDetail(viewUserId ?? undefined, customer?.user_id)

  // --- Account/Branch detail modals: unlike the user one, these just show
  // the row's already-loaded data rather than re-fetching - every field is
  // already present in the table row (no hidden fields the way a fresh
  // fetch might reveal), and branches don't even have a GET-by-code
  // endpoint to fetch from. ---
  const [viewAccount, setViewAccount] = useState<Account | null>(null)
  const [viewBranch, setViewBranch] = useState<Branch | null>(null)

  // --- Create branch (Admin only, matches BranchesService.create_branch) ---
  const [isCreatingBranch, setIsCreatingBranch] = useState(false)
  const [newBranchCode, setNewBranchCode] = useState('')
  const [newBranchLocation, setNewBranchLocation] = useState('')
  const [newBranchManagerId, setNewBranchManagerId] = useState('')
  const [isSubmittingBranch, setIsSubmittingBranch] = useState(false)
  const [createBranchError, setCreateBranchError] = useState<string | null>(null)

  function openCreateBranch() {
    setNewBranchCode('')
    setNewBranchLocation('')
    setNewBranchManagerId('')
    setCreateBranchError(null)
    setIsCreatingBranch(true)
  }

  async function handleCreateBranch() {
    if (!customer) return
    setIsSubmittingBranch(true)
    setCreateBranchError(null)
    try {
      await post('/branches', {
        branch_code: newBranchCode.trim(),
        location: newBranchLocation.trim(),
        manager_id: newBranchManagerId.trim() === '' ? null : Number(newBranchManagerId),
        requesting_user_id: customer.user_id,
      })
      refetchBranches()
      setIsCreatingBranch(false)
    } catch (err) {
      setCreateBranchError(err instanceof Error ? err.message : 'Could not create branch.')
    } finally {
      setIsSubmittingBranch(false)
    }
  }

  // --- Edit branch (Admin only, matches BranchesService.update_branch).
  // branch_code isn't editable here - it's the document's key, changing it
  // is really a delete+recreate, not an update. ---
  const [editingBranch, setEditingBranch] = useState<Branch | null>(null)
  const [editBranchLocation, setEditBranchLocation] = useState('')
  const [editBranchManagerId, setEditBranchManagerId] = useState('')
  const [isSubmittingBranchEdit, setIsSubmittingBranchEdit] = useState(false)
  const [editBranchError, setEditBranchError] = useState<string | null>(null)

  function openEditBranch(branch: Branch) {
    setEditBranchLocation(branch.location)
    setEditBranchManagerId(branch.manager_id === null ? '' : String(branch.manager_id))
    setEditBranchError(null)
    setEditingBranch(branch)
  }

  async function handleEditBranch() {
    if (!customer || !editingBranch) return
    setIsSubmittingBranchEdit(true)
    setEditBranchError(null)
    try {
      await put(`/branches/${editingBranch.branch_code}`, {
        location: editBranchLocation.trim(),
        manager_id: editBranchManagerId.trim() === '' ? null : Number(editBranchManagerId),
        requesting_user_id: customer.user_id,
      })
      refetchBranches()
      setEditingBranch(null)
    } catch (err) {
      setEditBranchError(err instanceof Error ? err.message : 'Could not update branch.')
    } finally {
      setIsSubmittingBranchEdit(false)
    }
  }

  // --- Delete confirmation, shared across users/accounts/branches ---
  type DeleteTarget =
    | { kind: 'user'; id: number; label: string }
    | { kind: 'account'; id: string; label: string }
    | { kind: 'branch'; id: string; label: string }

  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  async function handleConfirmDelete() {
    if (!deleteTarget || !customer) return
    setIsDeleting(true)
    setDeleteError(null)
    try {
      if (deleteTarget.kind === 'user') {
        await del(`/users/${deleteTarget.id}?requesting_user_id=${customer.user_id}`)
        refetchUsers()
      } else if (deleteTarget.kind === 'account') {
        await del(`/accounts/${deleteTarget.id}?requesting_user_id=${customer.user_id}`)
        refetchAccounts()
      } else {
        await del(`/branches/${deleteTarget.id}?requesting_user_id=${customer.user_id}`)
        refetchBranches()
      }
      setDeleteTarget(null)
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setIsDeleting(false)
    }
  }

  // --- Account status toggle (reversible, so no confirmation needed) ---
  const [statusUpdatingId, setStatusUpdatingId] = useState<string | null>(null)
  const [statusError, setStatusError] = useState<string | null>(null)

  async function handleToggleStatus(account: Account) {
    if (!customer) return
    setStatusUpdatingId(account.account_id)
    setStatusError(null)
    const action = account.status === 'active' ? 'deactivate' : 'reactivate'
    try {
      // deactivate/reactivate take requesting_user_id as a query param, not
      // a body field (no Pydantic body model on that route, unlike
      // deposit/withdraw's AmountRequest) - sending it in the body caused a
      // FastAPI validation error whose detail is an array of objects,
      // which client.ts naively stringified to "[object Object]".
      await post(`/accounts/${account.account_id}/${action}?requesting_user_id=${customer.user_id}`, {})
      refetchAccounts()
    } catch (err) {
      setStatusError(err instanceof Error ? err.message : 'Could not update status.')
    } finally {
      setStatusUpdatingId(null)
    }
  }

  // Filtering and pagination both happen server-side now (GET
  // /users|/accounts|/branches's search/skip/limit params) - what's left
  // here is just sorting the page(s) already loaded into memory, which
  // stays cheap since it's bounded by how much has been paged in, not the
  // total collection size.
  const sortedUsers = useMemo(
    () => [...users].sort((a, b) => a.name.localeCompare(b.name)),
    [users],
  )
  const sortedAccounts = useMemo(
    () => [...accounts].sort((a, b) => a.account_id.localeCompare(b.account_id)),
    [accounts],
  )
  const sortedBranches = useMemo(
    () => [...branches].sort((a, b) => a.branch_code.localeCompare(b.branch_code)),
    [branches],
  )

  function handleSearchChange(event: ChangeEvent<HTMLInputElement>) {
    setSearch(event.target.value)
  }

  return (
    <Layout>
      <PageWrapper>
        <PageTitle>{isAdmin ? 'Admin Dashboard' : 'Branch Dashboard'}</PageTitle>
        <PageSubtitle>
          {isAdmin
            ? 'Look up staff, customers, accounts, and branches in one place.'
            : 'Look up staff, customers, and accounts in your branch.'}
        </PageSubtitle>

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
                      {canDeleteUsers && <Th>Actions</Th>}
                    </Tr>
                  </Thead>
                  <Tbody>
                    {sortedUsers.map((user) => (
                      <ClickableTr key={user.user_id} onClick={() => setViewUserId(user.user_id)}>
                        <Td>{user.name}</Td>
                        <Td>{user.email}</Td>
                        <Td>{user.role}</Td>
                        <Td>{user.branch_code ?? '—'}</Td>
                        {canDeleteUsers && (
                          <Td>
                            <RowDeleteButton
                              type="button"
                              onClick={(event) => {
                                event.stopPropagation()
                                setDeleteTarget({ kind: 'user', id: user.user_id, label: user.name })
                              }}
                            >
                              Delete
                            </RowDeleteButton>
                          </Td>
                        )}
                      </ClickableTr>
                    ))}
                    {sortedUsers.length === 0 && (
                      <Tr>
                        <EmptyRow colSpan={canDeleteUsers ? 5 : 4}>No users match "{search}".</EmptyRow>
                      </Tr>
                    )}
                  </Tbody>
                </Table>
                {hasMoreUsers && (
                  <LoadMoreRow>
                    <RowActionButton type="button" disabled={isLoadingMoreUsers} onClick={loadMoreUsers}>
                      {isLoadingMoreUsers ? 'Loading…' : 'Load more'}
                    </RowActionButton>
                  </LoadMoreRow>
                )}
              </TableWrapper>
            )}

            {!isLoading && !error && view === 'accounts' && (
              <TableWrapper>
                {statusError && <ErrorMessage role="alert">{statusError}</ErrorMessage>}
                <Table>
                  <Thead>
                    <Tr>
                      <Th>Account ID</Th>
                      <Th>Owner</Th>
                      <Th>Branch</Th>
                      <Th>Type</Th>
                      <Th>Balance</Th>
                      <Th>Status</Th>
                      <Th>Actions</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {sortedAccounts.map((account) => (
                      <ClickableTr key={account.account_id} onClick={() => setViewAccount(account)}>
                        <Td>{account.account_id}</Td>
                        <Td>{account.owner_name ?? `#${account.owner_id}`}</Td>
                        <Td>{account.branch_code}</Td>
                        <Td>{account.account_type}</Td>
                        <Td>{formatCurrency(account.balance)}</Td>
                        <Td>{account.status}</Td>
                        <Td>
                          <ActionsCell>
                            <RowActionButton
                              type="button"
                              disabled={statusUpdatingId === account.account_id}
                              onClick={(event) => {
                                event.stopPropagation()
                                handleToggleStatus(account)
                              }}
                            >
                              {statusUpdatingId === account.account_id
                                ? 'Working…'
                                : account.status === 'active' ? 'Deactivate' : 'Activate'}
                            </RowActionButton>
                            <RowDeleteButton
                              type="button"
                              onClick={(event) => {
                                event.stopPropagation()
                                setDeleteTarget({ kind: 'account', id: account.account_id, label: account.account_id })
                              }}
                            >
                              Delete
                            </RowDeleteButton>
                          </ActionsCell>
                        </Td>
                      </ClickableTr>
                    ))}
                    {sortedAccounts.length === 0 && (
                      <Tr>
                        <EmptyRow colSpan={7}>No accounts match "{search}".</EmptyRow>
                      </Tr>
                    )}
                  </Tbody>
                </Table>
                {hasMoreAccounts && (
                  <LoadMoreRow>
                    <RowActionButton type="button" disabled={isLoadingMoreAccounts} onClick={loadMoreAccounts}>
                      {isLoadingMoreAccounts ? 'Loading…' : 'Load more'}
                    </RowActionButton>
                  </LoadMoreRow>
                )}
              </TableWrapper>
            )}

            {!isLoading && !error && isAdmin && view === 'branches' && (
              <TableWrapper>
                <NewBranchRow>
                  <SubmitButton type="button" onClick={openCreateBranch}>
                    New Branch
                  </SubmitButton>
                </NewBranchRow>
                <Table>
                  <Thead>
                    <Tr>
                      <Th>Branch Code</Th>
                      <Th>Location</Th>
                      <Th>Manager ID</Th>
                      <Th>Staff IDs</Th>
                      <Th>Actions</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {sortedBranches.map((branch) => (
                      <ClickableTr key={branch.branch_code} onClick={() => setViewBranch(branch)}>
                        <Td>{branch.branch_code}</Td>
                        <Td>{branch.location}</Td>
                        <Td>{branch.manager_id ?? '—'}</Td>
                        <Td>{branch.staff_list.length > 0 ? branch.staff_list.join(', ') : '—'}</Td>
                        <Td>
                          <ActionsCell>
                            <RowActionButton
                              type="button"
                              onClick={(event) => {
                                event.stopPropagation()
                                openEditBranch(branch)
                              }}
                            >
                              Edit
                            </RowActionButton>
                            <RowDeleteButton
                              type="button"
                              onClick={(event) => {
                                event.stopPropagation()
                                setDeleteTarget({ kind: 'branch', id: branch.branch_code, label: branch.branch_code })
                              }}
                            >
                              Delete
                            </RowDeleteButton>
                          </ActionsCell>
                        </Td>
                      </ClickableTr>
                    ))}
                    {sortedBranches.length === 0 && (
                      <Tr>
                        <EmptyRow colSpan={5}>No branches match "{search}".</EmptyRow>
                      </Tr>
                    )}
                  </Tbody>
                </Table>
                {hasMoreBranches && (
                  <LoadMoreRow>
                    <RowActionButton type="button" disabled={isLoadingMoreBranches} onClick={loadMoreBranches}>
                      {isLoadingMoreBranches ? 'Loading…' : 'Load more'}
                    </RowActionButton>
                  </LoadMoreRow>
                )}
              </TableWrapper>
            )}
          </>
        )}

        <Modal open={viewUserId !== null} onClose={() => setViewUserId(null)} title="User profile">
          {isLoadingViewedUser && <PageSubtitle>Loading…</PageSubtitle>}
          {viewedUserError && <ErrorMessage role="alert">{viewedUserError}</ErrorMessage>}
          {!isLoadingViewedUser && !viewedUserError && viewedUser && (
            <ReadOnlyList>
              <ReadOnlyLabel>User ID</ReadOnlyLabel>
              <ReadOnlyValue>{viewedUser.user_id}</ReadOnlyValue>
              <ReadOnlyLabel>Name</ReadOnlyLabel>
              <ReadOnlyValue>{viewedUser.name}</ReadOnlyValue>
              <ReadOnlyLabel>Email</ReadOnlyLabel>
              <ReadOnlyValue>{viewedUser.email}</ReadOnlyValue>
              <ReadOnlyLabel>Role</ReadOnlyLabel>
              <ReadOnlyValue>{viewedUser.role}</ReadOnlyValue>
              <ReadOnlyLabel>Branch</ReadOnlyLabel>
              <ReadOnlyValue>{viewedUser.branch_code ?? '—'}</ReadOnlyValue>
            </ReadOnlyList>
          )}
        </Modal>

        <Modal open={viewAccount !== null} onClose={() => setViewAccount(null)} title="Account details">
          {viewAccount && (
            <ReadOnlyList>
              <ReadOnlyLabel>Account ID</ReadOnlyLabel>
              <ReadOnlyValue>{viewAccount.account_id}</ReadOnlyValue>
              <ReadOnlyLabel>Owner</ReadOnlyLabel>
              <ReadOnlyValue>{viewAccount.owner_name ?? `#${viewAccount.owner_id}`}</ReadOnlyValue>
              <ReadOnlyLabel>Branch</ReadOnlyLabel>
              <ReadOnlyValue>{viewAccount.branch_code}</ReadOnlyValue>
              <ReadOnlyLabel>Type</ReadOnlyLabel>
              <ReadOnlyValue>{viewAccount.account_type}</ReadOnlyValue>
              <ReadOnlyLabel>Balance</ReadOnlyLabel>
              <ReadOnlyValue>{formatCurrency(viewAccount.balance)}</ReadOnlyValue>
              <ReadOnlyLabel>Status</ReadOnlyLabel>
              <ReadOnlyValue>{viewAccount.status}</ReadOnlyValue>
            </ReadOnlyList>
          )}
        </Modal>

        <Modal open={viewBranch !== null} onClose={() => setViewBranch(null)} title="Branch details">
          {viewBranch && (
            <ReadOnlyList>
              <ReadOnlyLabel>Branch Code</ReadOnlyLabel>
              <ReadOnlyValue>{viewBranch.branch_code}</ReadOnlyValue>
              <ReadOnlyLabel>Location</ReadOnlyLabel>
              <ReadOnlyValue>{viewBranch.location}</ReadOnlyValue>
              <ReadOnlyLabel>Manager ID</ReadOnlyLabel>
              <ReadOnlyValue>{viewBranch.manager_id ?? '—'}</ReadOnlyValue>
              <ReadOnlyLabel>Staff IDs</ReadOnlyLabel>
              <ReadOnlyValue>
                {viewBranch.staff_list.length > 0 ? viewBranch.staff_list.join(', ') : '—'}
              </ReadOnlyValue>
            </ReadOnlyList>
          )}
        </Modal>

        <Modal open={isCreatingBranch} onClose={() => setIsCreatingBranch(false)} title="New branch">
          <FormGroup>
            <Label htmlFor="new-branch-code">Branch code</Label>
            <Input
              id="new-branch-code"
              value={newBranchCode}
              onChange={(event) => setNewBranchCode(event.target.value)}
              placeholder="e.g. BR003"
            />
          </FormGroup>
          <FormGroup>
            <Label htmlFor="new-branch-location">Location</Label>
            <Input
              id="new-branch-location"
              value={newBranchLocation}
              onChange={(event) => setNewBranchLocation(event.target.value)}
              placeholder="e.g. West Loop Chicago"
            />
          </FormGroup>
          <FormGroup>
            <Label htmlFor="new-branch-manager">Manager ID (optional)</Label>
            <Input
              id="new-branch-manager"
              type="number"
              value={newBranchManagerId}
              onChange={(event) => setNewBranchManagerId(event.target.value)}
              placeholder="e.g. 2"
            />
          </FormGroup>
          {createBranchError && <ErrorMessage role="alert">{createBranchError}</ErrorMessage>}
          <SubmitButton
            type="button"
            disabled={isSubmittingBranch || !newBranchCode.trim() || !newBranchLocation.trim()}
            onClick={handleCreateBranch}
          >
            {isSubmittingBranch ? 'Creating…' : 'Create branch'}
          </SubmitButton>
        </Modal>

        <Modal open={editingBranch !== null} onClose={() => setEditingBranch(null)} title={`Edit ${editingBranch?.branch_code ?? 'branch'}`}>
          <FormGroup>
            <Label htmlFor="edit-branch-location">Location</Label>
            <Input
              id="edit-branch-location"
              value={editBranchLocation}
              onChange={(event) => setEditBranchLocation(event.target.value)}
            />
          </FormGroup>
          <FormGroup>
            <Label htmlFor="edit-branch-manager">Manager ID (optional)</Label>
            <Input
              id="edit-branch-manager"
              type="number"
              value={editBranchManagerId}
              onChange={(event) => setEditBranchManagerId(event.target.value)}
              placeholder="e.g. 2"
            />
          </FormGroup>
          {editBranchError && <ErrorMessage role="alert">{editBranchError}</ErrorMessage>}
          <SubmitButton
            type="button"
            disabled={isSubmittingBranchEdit || !editBranchLocation.trim()}
            onClick={handleEditBranch}
          >
            {isSubmittingBranchEdit ? 'Saving…' : 'Save changes'}
          </SubmitButton>
        </Modal>

        <ConfirmModal
          open={deleteTarget !== null}
          onClose={() => setDeleteTarget(null)}
          onConfirm={handleConfirmDelete}
          title={`Delete this ${deleteTarget?.kind ?? 'item'}?`}
          message={
            <>
              This cannot be undone. "{deleteTarget?.label}" will be permanently deleted.
            </>
          }
          confirmLabel="Delete"
          isConfirming={isDeleting}
          error={deleteError}
        />
      </PageWrapper>
    </Layout>
  )
}

export default AdminDashboardPage

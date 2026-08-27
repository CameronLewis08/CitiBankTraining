import { useState } from 'react'
import type { FormEvent } from 'react'
import Layout from '../Components/Layout/Layout'
import { useAuth } from '../Context/AuthContext'
import type { User } from '../Context/AuthContext'
import { useBranches } from '../hooks/accounts/useBranches'
import { put } from '../api/client'
import { PageWrapper, PageTitle, PageSubtitle } from '../Components/PageHero/PageHero.styled'
import { CardTitle } from '../Components/Card/Card.styled'
import { FormGroup, Label, Input, Select, SubmitButton, StatusMessage, ErrorMessage } from '../Components/Form/Form.styled'
import { ProfileCard, ProfileForm, ReadOnlyList, ReadOnlyLabel, ReadOnlyValue } from './ProfilePage.styled'

// Backend note: UsersService.update_user lets any user edit their own
// name/email freely, but branch_code is Admin-only, full stop - no
// self-service exception for any role, including an Admin editing their
// own (that one's allowed only because they ARE the Admin, not because
// it's "their own"). Role and user_id aren't editable at all (no backend
// support for changing either).
function ProfilePage() {
  const { customer, updateCustomer } = useAuth()
  const canEditBranch = customer?.role === 'Admin'
  const { branches, isLoading: isLoadingBranches, error: branchesError } = useBranches(
    canEditBranch ? customer?.user_id : undefined,
  )

  const [name, setName] = useState(customer?.name ?? '')
  const [email, setEmail] = useState(customer?.email ?? '')
  const [branchCode, setBranchCode] = useState(customer?.branch_code ?? '')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (!customer) return null

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSuccess(false)

    if (!customer) return

    const payload: Record<string, unknown> = {
      name,
      email,
      requesting_user_id: customer.user_id,
    }
    if (canEditBranch) {
      payload.branch_code = branchCode
    }

    setIsSubmitting(true)
    try {
      const updated = await put<User>(`/users/${customer.user_id}`, payload)
      updateCustomer(updated)
      setSuccess(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Layout>
      <PageWrapper>
        <PageTitle>Your Profile</PageTitle>
        <PageSubtitle>Update your name and email{canEditBranch ? ', or reassign your branch' : ''}.</PageSubtitle>

        <ProfileCard>
          <CardTitle>Account details</CardTitle>
          <ReadOnlyList>
            <ReadOnlyLabel>User ID</ReadOnlyLabel>
            <ReadOnlyValue>{customer.user_id}</ReadOnlyValue>
            <ReadOnlyLabel>Role</ReadOnlyLabel>
            <ReadOnlyValue>{customer.role}</ReadOnlyValue>
          </ReadOnlyList>

          <ProfileForm onSubmit={handleSubmit}>
            <FormGroup>
              <Label htmlFor="profile-name">Name</Label>
              <Input id="profile-name" value={name} onChange={(event) => setName(event.target.value)} required />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="profile-email">Email</Label>
              <Input
                id="profile-email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </FormGroup>

            {canEditBranch && (
              <FormGroup>
                <Label htmlFor="profile-branch">Branch</Label>
                <Select
                  id="profile-branch"
                  value={branchCode}
                  onChange={(event) => setBranchCode(event.target.value)}
                  disabled={isLoadingBranches || branches.length === 0}
                  required
                >
                  {branches.map((branch) => (
                    <option key={branch.branch_code} value={branch.branch_code}>
                      {branch.location} ({branch.branch_code})
                    </option>
                  ))}
                </Select>
                {branchesError && <ErrorMessage role="alert">{branchesError}</ErrorMessage>}
              </FormGroup>
            )}

            {error && <ErrorMessage role="alert">{error}</ErrorMessage>}

            <SubmitButton type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Saving…' : 'Save changes'}
            </SubmitButton>

            <StatusMessage role="status" aria-live="polite">
              {success ? 'Profile updated.' : ''}
            </StatusMessage>
          </ProfileForm>
        </ProfileCard>
      </PageWrapper>
    </Layout>
  )
}

export default ProfilePage

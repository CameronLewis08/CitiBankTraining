import { useState } from 'react'
import type { FormEvent } from 'react'
import Layout from '../Components/Layout/Layout'
import { useAuth } from '../Context/AuthContext'
import { useAccounts } from '../hooks/accounts/useAccounts'
import { useBranches } from '../hooks/accounts/useBranches'
import { post } from '../api/client'
import type { Account } from '../hooks/accounts/useAccounts'
import { formatCurrency } from '../data/accounts'
import { PageWrapper, PageTitle, PageSubtitle } from '../Components/PageHero/PageHero.styled'
import { CardGrid, Card, CardLink, CardIcon, CardTitle, CardText, CardBalance, CardFooter } from '../Components/Card/Card.styled'
import { SecondaryButton } from '../Components/Button/Button.styled'
import { FormGroup, Label, Select, Input, SubmitButton, ErrorMessage } from '../Components/Form/Form.styled'

const accountTypes = [
  {
    icon: '🏦',
    title: 'Checking',
    text: 'No monthly fees, unlimited transactions, and a debit card for everyday spending.',
  },
  {
    icon: '💰',
    title: 'Savings',
    text: 'Earn competitive interest on your balance while keeping funds easy to access.',
  },
]

type OpenAccountFormProps = {
  customerId: number
  onCreated: () => void
}

function OpenAccountForm({ customerId, onCreated }: OpenAccountFormProps) {
  const { branches, isLoading: isLoadingBranches, error: branchesError } = useBranches(customerId)
  const [submitError, setSubmitError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitError('')

    const form = event.currentTarget
    const formData = new FormData(form)
    const accountType = formData.get('accountType') as string
    const branchCode = formData.get('branchCode') as string
    const balance = Number(formData.get('balance'))

    setIsSubmitting(true)
    try {
      await post<Account>('/accounts', {
        account_type: accountType,
        branch_code: branchCode,
        balance,
        requesting_user_id: customerId,
      })
      form.reset()
      onCreated()
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card as="form" onSubmit={handleSubmit}>
      <CardTitle>Open a new account</CardTitle>
      <FormGroup>
        <Label htmlFor="open-account-type">Account type</Label>
        <Select id="open-account-type" name="accountType" defaultValue="Checking" required>
          <option value="Checking">Checking</option>
          <option value="Savings">Savings</option>
        </Select>
      </FormGroup>
      <FormGroup>
        <Label htmlFor="open-account-branch">Branch</Label>
        <Select id="open-account-branch" name="branchCode" required disabled={isLoadingBranches || branches.length === 0}>
          {branches.map((branch) => (
            <option key={branch.branch_code} value={branch.branch_code}>
              {branch.location} ({branch.branch_code})
            </option>
          ))}
        </Select>
      </FormGroup>
      <FormGroup>
        <Label htmlFor="open-account-balance">Starting deposit</Label>
        <Input id="open-account-balance" name="balance" type="number" min="0" step="0.01" defaultValue="0" required />
      </FormGroup>
      {branchesError && <ErrorMessage role="alert">{branchesError}</ErrorMessage>}
      {submitError && <ErrorMessage role="alert">{submitError}</ErrorMessage>}
      <CardFooter>
        <SubmitButton type="submit" disabled={isSubmitting || isLoadingBranches || branches.length === 0}>
          {isSubmitting ? 'Opening…' : 'Open account'}
        </SubmitButton>
      </CardFooter>
    </Card>
  )
}

function AccountsPage() {
  const { isLoggedIn, customer } = useAuth()
  const { accounts, isLoading, error, refetch } = useAccounts(customer?.user_id)

  if (isLoggedIn && customer) {
    return (
      <Layout>
        <PageWrapper>
          <PageTitle>Your accounts</PageTitle>
          <PageSubtitle>Review your balances, then send a transfer whenever you're ready.</PageSubtitle>
          {isLoading && <PageSubtitle>Loading your accounts…</PageSubtitle>}
          {error && <ErrorMessage role="alert">{error}</ErrorMessage>}
          {!isLoading && !error && (
            <CardGrid>
              {accounts.map((account) => (
                <Card key={account.account_id}>
                  <CardTitle>{account.account_id}</CardTitle>
                  <CardBalance>{formatCurrency(account.balance)}</CardBalance>
                  <CardFooter>
                    <SecondaryButton to={`/accounts/${account.account_id}`}>View Details</SecondaryButton>
                    <SecondaryButton to={`/transfer?from=${account.account_id}`}>Transfer</SecondaryButton>
                  </CardFooter>
                </Card>
              ))}
              <OpenAccountForm customerId={customer.user_id} onCreated={refetch} />
            </CardGrid>
          )}
        </PageWrapper>
      </Layout>
    )
  }

  return (
    <Layout>
      <PageWrapper>
        <PageTitle>Accounts built for every goal</PageTitle>
        <PageSubtitle>Whether you're saving for a rainy day or growing your wealth, we have an account that fits. Select an account to get started.</PageSubtitle>
        <CardGrid>
          {accountTypes.map((account) => (
            <CardLink key={account.title} to="/login" aria-label={`Open a ${account.title} account — log in or sign up`}>
              <CardIcon aria-hidden="true">{account.icon}</CardIcon>
              <CardTitle>{account.title}</CardTitle>
              <CardText>{account.text}</CardText>
            </CardLink>
          ))}
        </CardGrid>
      </PageWrapper>
    </Layout>
  )
}

export default AccountsPage

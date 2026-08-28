import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import Layout from '../Components/Layout/Layout'
import { useAuth } from '../Context/AuthContext'
import { useAccounts } from '../hooks/accounts/useAccounts'
import { formatCurrency } from '../data/accounts'
import { post } from '../api/client'
import { PageWrapper, PageTitle, PageSubtitle } from '../Components/PageHero/PageHero.styled'
import { FormGroup, Label, Input, SubmitButton, StatusMessage, ErrorMessage } from '../Components/Form/Form.styled'
import { TransferForm, Select, AmountField, CurrencyPrefix, AmountInput } from './TransferPage.styled'

function TransferPage() {
  const { customer } = useAuth()
  // owner_id pinned to self, same reasoning as HomePage.tsx/AccountsPage.tsx:
  // the From/To pickers should only ever list the logged-in user's own
  // accounts, not the broader Admin/Manager view the backend would
  // otherwise default to.
  const { accounts, isLoading, error: loadError, refetch } = useAccounts(customer?.user_id, customer?.user_id)
  const [searchParams] = useSearchParams()
  const initialFrom = searchParams.get('from')

  const [fromId, setFromId] = useState('')
  const [toId, setToId] = useState('')
  const [amount, setAmount] = useState('')
  const [error, setError] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Once accounts have loaded, pick a starting "From" account: the one
  // passed in the URL (e.g. from the Accounts page's Transfer button) if
  // it's valid, otherwise just the first account.
  useEffect(() => {
    if (accounts.length === 0) return
    setFromId((current) => current || initialFrom || accounts[0].account_id)
  }, [accounts, initialFrom])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitted(false)
    setError('')

    const trimmedToId = toId.trim()

    if (fromId === trimmedToId) {
      setError('From and To accounts must be different.')
      return
    }

    if (!customer) return

    setIsSubmitting(true)
    try {
      // A 200 here only means the request was well-formed, not that money
      // actually moved - Accounts.transfer (Models/Accounts.py) returns
      // {"status": "Failure", ...} with a normal 200 response on
      // insufficient funds/inactive accounts rather than raising, the same
      // way deposit/withdraw do (see AccountDetailPage's handleAction).
      // Skipping this check was exactly why an over-the-balance transfer
      // used to report success while the transaction history showed it
      // never went through.
      const result = await post<{ status: string }>('/accounts/transfer', {
        requesting_user_id: customer.user_id,
        from_account_id: fromId,
        to_account_id: trimmedToId,
        amount: Number(amount),
      })
      if (result.status !== 'Success') {
        setError('Transfer could not be completed — check the balance and try again.')
        return
      }
      setSubmitted(true)
      setAmount('')
      refetch()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Transfer failed.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Layout>
      <PageWrapper>
        <PageTitle>Transfer Money</PageTitle>
        <PageSubtitle>Move money between your accounts, or send to someone else's account ID.</PageSubtitle>

        {isLoading && <PageSubtitle>Loading your accounts…</PageSubtitle>}
        {loadError && <ErrorMessage role="alert">{loadError}</ErrorMessage>}

        {!isLoading && !loadError && (
          <TransferForm onSubmit={handleSubmit}>
            <FormGroup>
              <Label htmlFor="fromAccount">From account</Label>
              <Select id="fromAccount" name="fromAccount" value={fromId} onChange={(event) => setFromId(event.target.value)} required>
                {accounts.map((account) => (
                  <option key={account.account_id} value={account.account_id}>
                    {account.account_id} — {formatCurrency(account.balance)}
                  </option>
                ))}
              </Select>
            </FormGroup>

            <FormGroup>
              <Label htmlFor="toAccount">Recipient account ID</Label>
              <Input
                id="toAccount"
                name="toAccount"
                type="text"
                placeholder="e.g. ACC-5d2171a3"
                value={toId}
                onChange={(event) => setToId(event.target.value)}
                required
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="amount">Amount</Label>
              <AmountField>
                <CurrencyPrefix aria-hidden="true">$</CurrencyPrefix>
                <AmountInput
                  id="amount"
                  name="amount"
                  type="number"
                  inputMode="decimal"
                  min="0.01"
                  step="0.01"
                  value={amount}
                  onChange={(event) => setAmount(event.target.value)}
                  required
                />
              </AmountField>
            </FormGroup>

            {error && (
              <ErrorMessage role="alert" id="transfer-error">
                {error}
              </ErrorMessage>
            )}

            <SubmitButton type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Transferring…' : 'Transfer Funds'}
            </SubmitButton>

            <StatusMessage role="status" aria-live="polite">
              {submitted ? 'Transfer completed successfully.' : ''}
            </StatusMessage>
          </TransferForm>
        )}
      </PageWrapper>
    </Layout>
  )
}

export default TransferPage

import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Layout from '../Components/Layout/Layout'
import { useAuth } from '../Context/AuthContext'
import { useAccountDetail } from '../hooks/accounts/useAccountDetail'
import { post, del } from '../api/client'
import { formatCurrency } from '../data/accounts'
import ConfirmModal from '../Components/Modal/ConfirmModal'
import { PageWrapper, PageTitle, PageSubtitle } from '../Components/PageHero/PageHero.styled'
import { Card, CardTitle } from '../Components/Card/Card.styled'
import { SubmitButton, ErrorMessage } from '../Components/Form/Form.styled'
import {
  DetailGrid, SummaryList, SummaryLabel, SummaryValue,
  ActionForm, ActionRow, AmountField, CurrencyPrefix, AmountInput,
  TransactionList, TransactionRow, TransactionMeta, TransactionType, TransactionTimestamp, TransactionAmount,
  CloseAccountButton,
} from './AccountDetailPage.styled'

function AccountDetailPage() {
  const { accountId } = useParams<{ accountId: string }>()
  const { customer } = useAuth()
  const navigate = useNavigate()
  const { account, transactions, isLoading, error, refetch } = useAccountDetail(accountId, customer?.user_id)
  const [actionError, setActionError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isCloseModalOpen, setIsCloseModalOpen] = useState(false)
  const [isClosing, setIsClosing] = useState(false)
  const [closeError, setCloseError] = useState<string | null>(null)

  async function handleCloseAccount() {
    if (!customer || !accountId) return

    setIsClosing(true)
    setCloseError(null)
    try {
      await del(`/accounts/${accountId}?requesting_user_id=${customer.user_id}`)
      navigate('/accounts')
    } catch (err) {
      setCloseError(err instanceof Error ? err.message : 'Could not close this account.')
      setIsClosing(false)
    }
  }

  async function handleAction(kind: 'deposit' | 'withdraw', event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setActionError('')

    const form = event.currentTarget
    const formData = new FormData(form)
    const amount = Number(formData.get('amount'))

    if (!customer || !accountId) return

    setIsSubmitting(true)
    try {
      const { result } = await post<{ result: { status: string } }>(`/accounts/${accountId}/${kind}`, {
        amount,
        requesting_user_id: customer.user_id,
      })
      if (result.status !== 'Success') {
        setActionError(kind === 'deposit' ? 'Deposit could not be completed.' : 'Withdrawal could not be completed — check your balance and try again.')
      } else {
        form.reset()
      }
      refetch()
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Layout>
      <PageWrapper>
        <PageTitle>{accountId}</PageTitle>
        <PageSubtitle>Review your balance, move money, and see recent activity.</PageSubtitle>

        {isLoading && <PageSubtitle>Loading account…</PageSubtitle>}
        {error && <ErrorMessage role="alert">{error}</ErrorMessage>}

        {!isLoading && !error && account && (
          <DetailGrid>
            <Card>
              <CardTitle>Account summary</CardTitle>
              <SummaryList>
                <SummaryLabel>Balance</SummaryLabel>
                <SummaryValue>{formatCurrency(account.balance)}</SummaryValue>
                <SummaryLabel>Type</SummaryLabel>
                <SummaryValue>{account.account_type}</SummaryValue>
                <SummaryLabel>Branch</SummaryLabel>
                <SummaryValue>{account.branch_code}</SummaryValue>
                <SummaryLabel>Status</SummaryLabel>
                <SummaryValue>{account.status}</SummaryValue>
              </SummaryList>
              <CloseAccountButton type="button" onClick={() => setIsCloseModalOpen(true)}>
                Close Account
              </CloseAccountButton>
            </Card>

            <Card>
              <CardTitle>Deposit or withdraw</CardTitle>
              <ActionRow>
                <ActionForm onSubmit={(event) => handleAction('deposit', event)}>
                  <AmountField>
                    <CurrencyPrefix aria-hidden="true">$</CurrencyPrefix>
                    <AmountInput name="amount" type="number" inputMode="decimal" min="0.01" step="0.01" required />
                  </AmountField>
                  <SubmitButton type="submit" disabled={isSubmitting}>Deposit</SubmitButton>
                </ActionForm>
                <ActionForm onSubmit={(event) => handleAction('withdraw', event)}>
                  <AmountField>
                    <CurrencyPrefix aria-hidden="true">$</CurrencyPrefix>
                    <AmountInput name="amount" type="number" inputMode="decimal" min="0.01" step="0.01" required />
                  </AmountField>
                  <SubmitButton type="submit" disabled={isSubmitting}>Withdraw</SubmitButton>
                </ActionForm>
              </ActionRow>
              {actionError && <ErrorMessage role="alert">{actionError}</ErrorMessage>}
            </Card>

            <Card>
              <CardTitle>Transaction history</CardTitle>
              {transactions.length === 0 && <PageSubtitle>No transactions yet.</PageSubtitle>}
              <TransactionList>
                {transactions.map((transaction, index) => {
                  const failed = transaction.status !== 'Success'
                  const negative = transaction.type === 'withdrawal'
                  return (
                    <TransactionRow key={index}>
                      <TransactionMeta>
                        <TransactionType>{transaction.type}</TransactionType>
                        <TransactionTimestamp>
                          {new Date(transaction.timestamp * 1000).toLocaleString()}
                        </TransactionTimestamp>
                      </TransactionMeta>
                      <TransactionAmount $negative={negative} $failed={failed}>
                        {negative ? '-' : '+'}{formatCurrency(transaction.amount)}
                      </TransactionAmount>
                    </TransactionRow>
                  )
                })}
              </TransactionList>
            </Card>
          </DetailGrid>
        )}

        <ConfirmModal
          open={isCloseModalOpen}
          onClose={() => setIsCloseModalOpen(false)}
          onConfirm={handleCloseAccount}
          title="Close this account?"
          message={
            <>
              This cannot be undone. Withdraw any remaining balance before closing —
              once this account is closed, its funds and history are gone for good.
            </>
          }
          confirmLabel="Close Account"
          isConfirming={isClosing}
          error={closeError}
        />
      </PageWrapper>
    </Layout>
  )
}

export default AccountDetailPage

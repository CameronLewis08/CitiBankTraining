import styled from 'styled-components'

export const DetailGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  width: 100%;
  max-width: 60rem;
  margin-top: 2rem;
  align-items: start;
`

export const SummaryList = styled.dl`
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.5rem 1rem;
  margin: 1rem 0 0;
`

export const SummaryLabel = styled.dt`
  color: var(--text);
  font-size: 0.9rem;
`

export const SummaryValue = styled.dd`
  margin: 0;
  color: var(--text-h);
  font-weight: 600;
  text-align: right;
`

export const ActionForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`

export const ActionRow = styled.div`
  display: flex;
  gap: 0.75rem;
`

export const AmountField = styled.div`
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
`

export const CurrencyPrefix = styled.span`
  position: absolute;
  left: 0.9rem;
  color: var(--text);
  font-size: 1rem;
  pointer-events: none;
`

export const AmountInput = styled.input`
  font: inherit;
  width: 100%;
  padding: 0.7rem 0.9rem 0.7rem 1.75rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text-h);
  box-sizing: border-box;

  &:focus-visible {
    outline: 3px solid var(--accent-strong);
    outline-offset: 1px;
    border-color: var(--accent-strong);
  }
`

export const TransactionList = styled.ul`
  list-style: none;
  margin: 1rem 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`

export const TransactionRow = styled.li`
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border);

  &:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }
`

export const TransactionMeta = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
`

export const TransactionType = styled.span`
  color: var(--text-h);
  font-weight: 600;
  text-transform: capitalize;
`

export const TransactionTimestamp = styled.span`
  color: var(--text);
  font-size: 0.85rem;
`

export const TransactionAmount = styled.span<{ $negative: boolean; $failed: boolean }>`
  font-weight: 700;
  color: ${({ $failed, $negative }) => ($failed ? 'var(--text)' : $negative ? '#a4133c' : '#2e8b57')};
  text-decoration: ${({ $failed }) => ($failed ? 'line-through' : 'none')};
`

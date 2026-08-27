import styled from 'styled-components'

export const TransferForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
  max-width: 26rem;
  margin-top: 1rem;
`

export const Select = styled.select`
  font: inherit;
  padding: 0.7rem 0.9rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text-h);

  &:focus-visible {
    outline: 3px solid var(--accent-strong);
    outline-offset: 1px;
    border-color: var(--accent-strong);
  }
`

export const AmountField = styled.div`
  position: relative;
  display: flex;
  align-items: center;
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



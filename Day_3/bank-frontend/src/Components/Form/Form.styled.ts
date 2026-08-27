import styled from 'styled-components'

export const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  text-align: left;
`

export const Label = styled.label`
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-h);
`

export const Input = styled.input`
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

export const TextArea = styled.textarea`
  font: inherit;
  padding: 0.7rem 0.9rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text-h);
  min-height: 8rem;
  resize: vertical;

  &:focus-visible {
    outline: 3px solid var(--accent-strong);
    outline-offset: 1px;
    border-color: var(--accent-strong);
  }
`

export const SubmitButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  font: inherit;
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  background: var(--accent-strong);
  border: none;
  cursor: pointer;
  padding: 0.75rem 1.5rem;
  border-radius: 999px;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;

  &:hover {
    background: var(--accent);
    transform: translateY(-1px);
    box-shadow: var(--shadow);
  }

  &:focus-visible {
    outline: 3px solid var(--accent-strong);
    outline-offset: 3px;
  }
`

export const StatusMessage = styled.p`
  font-size: 0.9rem;
  color: var(--accent-text);
  font-weight: 600;
`
export const ErrorMessage = styled.p`
  margin: 0;
  color: #a4133c;
  font-size: 0.9rem;
  font-weight: 600;
`

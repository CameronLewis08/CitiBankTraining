import styled from 'styled-components'
import { Card } from '../Components/Card/Card.styled'

export const ProfileCard = styled(Card)`
  width: 100%;
  max-width: 28rem;
  margin-top: 2rem;
  text-align: left;
`

export const ProfileForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  text-align: left;
`

export const ReadOnlyList = styled.dl`
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.5rem 1rem;
  margin: 0 0 0.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
`

export const ReadOnlyLabel = styled.dt`
  color: var(--text);
  font-size: 0.9rem;
`

export const ReadOnlyValue = styled.dd`
  margin: 0;
  color: var(--text-h);
  font-weight: 600;
  text-align: right;
`

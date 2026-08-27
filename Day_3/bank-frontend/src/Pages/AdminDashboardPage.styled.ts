import styled from 'styled-components'
import { Tr } from '../Components/Table/Table.styled'
import { CancelButton, DangerButton } from '../Components/Modal/Modal.styled'

// Rows in the Users tab open a detail modal on click - this is the only
// visual affordance beyond the cursor that a row is interactive.
export const ClickableTr = styled(Tr)`
  cursor: pointer;
`

export const ActionsCell = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
`

// Compact variants of the shared Modal buttons, sized to sit inline in a
// table row instead of a modal footer.
export const RowActionButton = styled(CancelButton)`
  min-height: 34px;
  padding: 0.35rem 0.8rem;
  font-size: 0.8rem;
`

export const RowDeleteButton = styled(DangerButton)`
  min-height: 34px;
  padding: 0.35rem 0.8rem;
  font-size: 0.8rem;
`

export const ControlsRow = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 1rem;
  width: 100%;
  max-width: 60rem;
  margin-top: 2rem;
`

export const SearchBar = styled.div`
  flex: 1 1 20rem;
  max-width: 24rem;
`

export const NewBranchRow = styled.div`
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
`

export const LoadMoreRow = styled.div`
  display: flex;
  justify-content: center;
  margin-top: 1.25rem;
`

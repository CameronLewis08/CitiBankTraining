import styled from 'styled-components'
import { Tr } from '../Components/Table/Table.styled'
import { CancelButton, DangerButton } from '../Components/Modal/Modal.styled'
import { SubmitButton } from '../Components/Form/Form.styled'

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

// Smaller than the standard form SubmitButton - sits inline in ControlsRow
// next to the search box and "Show" filter, not as a form's primary
// submit, so full form-button sizing read as oversized here.
export const NewBranchButton = styled(SubmitButton)`
  min-height: 38px;
  padding: 0.5rem 1.1rem;
  font-size: 0.85rem;
`

export const LoadMoreRow = styled.div`
  display: flex;
  justify-content: center;
  margin-top: 1.25rem;
`

// Modal is a generic overlay+card shell with no gap between stacked
// children, unlike every <form>-based page (ProfilePage's ProfileForm,
// TransferPage's TransferForm, etc.) which get spacing from their own
// styled `gap`. The branch create/edit modals stack multiple FormGroups
// plus a submit button as plain Modal children, so they need this wrapper
// for the same spacing rather than relying on a <form> wrapper Modal
// doesn't provide.
export const ModalFieldStack = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
`

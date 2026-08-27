import type { ReactNode } from 'react'
import Modal from './Modal'
import { CancelButton, DangerButton } from './Modal.styled'
import { ErrorMessage } from '../Form/Form.styled'

type ConfirmModalProps = {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: ReactNode
  confirmLabel?: string
  isConfirming?: boolean
  error?: string | null
}

// The shared "are you sure" pattern - delete user, delete account, delete
// branch, and close account all use this exact same shape (title +
// warning message + Cancel/danger-confirm footer + loading + error), so
// each call site only needs to supply its own wording and onConfirm.
function ConfirmModal({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = 'Delete',
  isConfirming = false,
  error = null,
}: ConfirmModalProps) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      footer={
        <>
          <CancelButton type="button" onClick={onClose} disabled={isConfirming}>
            Cancel
          </CancelButton>
          <DangerButton type="button" onClick={onConfirm} disabled={isConfirming}>
            {isConfirming ? 'Working…' : confirmLabel}
          </DangerButton>
        </>
      }
    >
      {message}
      {error && <ErrorMessage role="alert">{error}</ErrorMessage>}
    </Modal>
  )
}

export default ConfirmModal

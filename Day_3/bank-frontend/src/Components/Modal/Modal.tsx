import { useEffect } from 'react'
import type { MouseEvent, ReactNode } from 'react'
import { Overlay, ModalCard, ModalHeader, ModalTitle, CloseIconButton, ModalBody, ModalFooter } from './Modal.styled'

type ModalProps = {
  open: boolean
  onClose: () => void
  title: string
  children: ReactNode
  footer?: ReactNode
}

// Generic overlay + card shell - knows nothing about confirm/cancel or any
// other specific use case, just how to show/dismiss itself. ConfirmModal
// builds the "are you sure" pattern on top of this; the user-detail view
// uses this directly with its own body content and a plain Close footer.
function Modal({ open, onClose, title, children, footer }: ModalProps) {
  useEffect(() => {
    if (!open) return

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [open, onClose])

  if (!open) return null

  function handleOverlayClick(event: MouseEvent<HTMLDivElement>) {
    if (event.target === event.currentTarget) onClose()
  }

  return (
    <Overlay onClick={handleOverlayClick}>
      <ModalCard role="dialog" aria-modal="true" aria-label={title}>
        <ModalHeader>
          <ModalTitle>{title}</ModalTitle>
          <CloseIconButton type="button" aria-label="Close" onClick={onClose}>
            ✕
          </CloseIconButton>
        </ModalHeader>
        <ModalBody>{children}</ModalBody>
        {footer && <ModalFooter>{footer}</ModalFooter>}
      </ModalCard>
    </Overlay>
  )
}

export default Modal

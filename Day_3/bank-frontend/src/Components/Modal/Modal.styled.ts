import styled from 'styled-components'

export const Overlay = styled.div`
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: color-mix(in srgb, black 55%, transparent);
  z-index: 100;
`

export const ModalCard = styled.div`
  width: 100%;
  max-width: 26rem;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: var(--shadow);
  padding: 1.75rem;
  text-align: left;
`

export const ModalHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.75rem;
`

export const ModalTitle = styled.h2`
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-h);
`

export const CloseIconButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  flex-shrink: 0;
  font-size: 1.1rem;
  line-height: 1;
  color: var(--text);
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;

  &:hover {
    background: var(--accent-bg);
    color: var(--text-h);
  }
`

export const ModalBody = styled.div`
  color: var(--text);
  font-size: 0.95rem;
  line-height: 1.6;
`

export const ModalFooter = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
`

export const CancelButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text);
  background: transparent;
  border: 2px solid var(--border);
  padding: calc(0.6rem - 2px) calc(1.1rem - 2px);
  border-radius: 999px;
  cursor: pointer;
  transition: border-color 0.15s ease, color 0.15s ease;

  &:hover:not(:disabled) {
    border-color: var(--text);
    color: var(--text-h);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`

export const DangerButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 700;
  color: #fff;
  background: #a4133c;
  border: none;
  padding: 0.6rem 1.1rem;
  border-radius: 999px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease, opacity 0.15s ease;

  &:hover:not(:disabled) {
    background: #c81e5c;
    transform: translateY(-1px);
    box-shadow: var(--shadow);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`

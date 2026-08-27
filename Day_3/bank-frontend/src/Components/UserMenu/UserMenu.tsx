import { useEffect, useRef, useState } from 'react'
import { useAuth } from '../../Context/AuthContext'
import { MenuWrapper, TriggerButton, Caret, MenuPanel, MenuLink, MenuButton } from './UserMenu.styled'

// A name-triggered account menu (Profile / Log Out) rather than separate
// top-level nav links - closes on an outside click, Escape, or picking an
// item, and exposes the aria-haspopup/aria-expanded/role="menu" trio so
// it reads as a real popover to assistive tech, not just styled links.
function UserMenu() {
  const { customer, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const wrapperRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return

    function handlePointerDown(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpen(false)
    }

    document.addEventListener('mousedown', handlePointerDown)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handlePointerDown)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [open])

  if (!customer) return null

  function handleLogout() {
    setOpen(false)
    logout()
  }

  return (
    <MenuWrapper ref={wrapperRef}>
      <TriggerButton type="button" aria-haspopup="menu" aria-expanded={open} onClick={() => setOpen((value) => !value)}>
        {customer.name}
        <Caret $open={open} aria-hidden="true">▾</Caret>
      </TriggerButton>

      {open && (
        <MenuPanel role="menu">
          <MenuLink to="/profile" role="menuitem" onClick={() => setOpen(false)}>
            Profile
          </MenuLink>
          <MenuButton type="button" role="menuitem" onClick={handleLogout}>
            Log Out
          </MenuButton>
        </MenuPanel>
      )}
    </MenuWrapper>
  )
}

export default UserMenu

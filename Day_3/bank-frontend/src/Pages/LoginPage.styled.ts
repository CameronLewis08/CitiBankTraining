import styled from 'styled-components'

export const SlideViewport = styled.div`
  width: 100%;
  max-width: 24rem;
  overflow: hidden;
  margin-top: 1rem;
`

export const SlideTrack = styled.div<{ $mode: 'login' | 'signup' }>`
  display: flex;
  width: 200%;
  transform: translateX(${(props) => (props.$mode === 'login' ? '0%' : '-50%')});
  transition: transform 0.4s ease;

  @media (prefers-reduced-motion: reduce) {
    transition: none;
  }
`

export const SlidePanel = styled.div`
  flex: 0 0 50%;
  width: 50%;
  box-sizing: border-box;
  padding: 0 0.25rem;
`

export const AuthForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
`

export const ToggleGroup = styled.div`
  position: relative;
  display: inline-flex;
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0.25rem;
`

export const ToggleThumb = styled.span<{ $mode: 'login' | 'signup' }>`
  position: absolute;
  top: 0.25rem;
  left: 0.25rem;
  bottom: 0.25rem;
  width: calc(50% - 0.25rem);
  background: var(--accent-strong);
  border-radius: 999px;
  transform: translateX(${(props) => (props.$mode === 'signup' ? '100%' : '0')});
  transition: transform 0.3s ease;

  @media (prefers-reduced-motion: reduce) {
    transition: none;
  }
`

export const ToggleButton = styled.button<{ $active: boolean }>`
  position: relative;
  z-index: 1;
  min-height: 40px;
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 999px;
  background: transparent;
  font: inherit;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  color: ${(props) => (props.$active ? '#fff' : 'var(--text)')};
  transition: color 0.2s ease;

  &:hover {
    color: ${(props) => (props.$active ? '#fff' : 'var(--text-h)')};
  }

  &:focus-visible {
    outline: 3px solid var(--accent-strong);
    outline-offset: 2px;
  }
`

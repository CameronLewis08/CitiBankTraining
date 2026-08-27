import styled from 'styled-components'

// Wrapping the table in its own scroll container keeps a wide table from
// forcing the whole page to scroll horizontally on narrow viewports.
export const TableWrapper = styled.div`
  width: 100%;
  max-width: 60rem;
  margin-top: 2rem;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 14px;
`

export const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.95rem;
`

export const Thead = styled.thead`
  background: var(--code-bg);
`

export const Th = styled.th`
  padding: 0.9rem 1.25rem;
  color: var(--text-h);
  font-weight: 700;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
`

export const Tbody = styled.tbody``

export const Tr = styled.tr`
  &:not(:last-child) td {
    border-bottom: 1px solid var(--border);
  }

  &:hover td {
    background: var(--accent-bg);
  }
`

export const Td = styled.td`
  padding: 0.9rem 1.25rem;
  color: var(--text);
  vertical-align: middle;
`

export const EmptyRow = styled.td`
  padding: 1.5rem 1.25rem;
  color: var(--text);
  text-align: center;
`

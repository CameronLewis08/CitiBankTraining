import type { ChangeEvent } from 'react'
import { Label, Select } from '../Form/Form.styled'
import { FilterWrapper } from './FilterDropdown.styled'

export type FilterOption<T extends string> = {
  value: T
  label: string
}

type FilterDropdownProps<T extends string> = {
  id: string
  label: string
  value: T
  options: FilterOption<T>[]
  onChange: (value: T) => void
}

// Generic select-driven filter: give it a set of options and it reports the
// chosen value back via onChange. Not tied to any one page's data - reuse it
// anywhere a "switch what's displayed" dropdown is needed.
function FilterDropdown<T extends string>({ id, label, value, options, onChange }: FilterDropdownProps<T>) {
  function handleChange(event: ChangeEvent<HTMLSelectElement>) {
    onChange(event.target.value as T)
  }

  return (
    <FilterWrapper>
      <Label htmlFor={id}>{label}</Label>
      <Select id={id} value={value} onChange={handleChange}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </Select>
    </FilterWrapper>
  )
}

export default FilterDropdown

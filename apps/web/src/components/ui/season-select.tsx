"use client";

import type { Season } from "@/types/api";

type Props = {
  id: string;
  label: string;
  seasons: Season[];
  value: string;
  onChange: (seasonId: string) => void;
  placeholder?: string;
  required?: boolean;
};

export function SeasonSelect({
  id,
  label,
  seasons,
  value,
  onChange,
  placeholder = "Выберите сезон",
  required,
}: Props) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-medium text-muted">
        {label}
      </label>
      <select
        id={id}
        value={value}
        required={required}
        onChange={(event) => onChange(event.target.value)}
        className="max-w-md rounded-md border border-line bg-card px-3 py-2 text-foreground"
      >
        <option value="">{placeholder}</option>
        {seasons.map((season) => (
          <option key={season.id} value={season.id}>
            {season.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export function formatDateTime(value?: string | null): string {
  if (!value) {
    return '—';
  }

  return new Date(value).toLocaleString();
}

export function toDateTimeLocal(value?: string | null): string {
  if (!value) {
    return '';
  }

  const date = new Date(value);
  const pad = (part: number) => String(part).padStart(2, '0');

  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function fromDateTimeLocal(value: string): string | null {
  if (!value) {
    return null;
  }

  return new Date(value).toISOString();
}

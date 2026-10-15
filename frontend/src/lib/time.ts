/**
 * Utility to format timestamp in IST (Asia/Kolkata) with Date and Milliseconds (3 decimal digits)
 * Output example: 15 Oct 2026, 10:42:15.875 PM
 */
export function formatTimestampIST(timestamp?: string | number | Date | null): string {
  if (!timestamp) return 'Just now';

  try {
    const d = new Date(timestamp);
    if (isNaN(d.getTime())) return String(timestamp);

    // Format Date & Time parts in Asia/Kolkata
    const formatter = new Intl.DateTimeFormat('en-IN', {
      timeZone: 'Asia/Kolkata',
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    });

    const parts = formatter.formatToParts(d);
    const day = parts.find((p) => p.type === 'day')?.value || '';
    const month = parts.find((p) => p.type === 'month')?.value || '';
    const year = parts.find((p) => p.type === 'year')?.value || '';
    const hour = parts.find((p) => p.type === 'hour')?.value || '00';
    const minute = parts.find((p) => p.type === 'minute')?.value || '00';
    const second = parts.find((p) => p.type === 'second')?.value || '00';
    const dayPeriod = parts.find((p) => p.type === 'dayPeriod')?.value || 'AM';

    // Extract exact milliseconds padded to 3 digits
    const ms = String(d.getMilliseconds()).padStart(3, '0');

    return `${day} ${month} ${year}, ${hour}:${minute}:${second}.${ms} ${dayPeriod}`;
  } catch {
    return String(timestamp);
  }
}

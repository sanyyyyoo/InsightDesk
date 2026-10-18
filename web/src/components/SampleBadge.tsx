/** Marks a feature or result that comes from sample data, not the live backend. */
export function SampleBadge({ title = "Sample data – not from or saved to the live backend" }: { title?: string }) {
  return (
    <span className="badge badge-warning" title={title}>
      Sample
    </span>
  );
}

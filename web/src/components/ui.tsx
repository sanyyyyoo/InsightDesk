import type { ReactNode } from "react";

export function PageHeader({
  title,
  subtitle,
  badges,
  stats,
}: {
  title: string;
  subtitle?: string;
  badges?: ReactNode;
  stats?: { label: string; value: ReactNode }[];
}) {
  return (
    <header className="page-header">
      <h1>
        {title} {badges}
      </h1>
      {subtitle && <p>{subtitle}</p>}
      {stats && stats.length > 0 && (
        <div className="header-stats">
          {stats.map((s) => (
            <div className="header-stat" key={s.label}>
              <div className="num">{s.value}</div>
              <div className="label">{s.label}</div>
            </div>
          ))}
        </div>
      )}
    </header>
  );
}

export function Kpi({ label, value, hint }: { label: string; value: ReactNode; hint?: ReactNode }) {
  return (
    <div className="card kpi">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {hint && <div className="kpi-hint">{hint}</div>}
    </div>
  );
}

export function Card({ title, actions, children }: { title?: ReactNode; actions?: ReactNode; children: ReactNode }) {
  return (
    <section className="card">
      {(title || actions) && (
        <div className="card-title">
          {typeof title === "string" ? <h3>{title}</h3> : title}
          {actions}
        </div>
      )}
      {children}
    </section>
  );
}

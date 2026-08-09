import React from "react";

export function StatGrid({ items = [], columns = 4, sunken = false }) {
  return (
    <div className={"stat-grid" + (columns === 3 ? " stat-grid--3" : "") + (sunken ? " stat-grid--sunken" : "")}>
      {items.map((it, i) => (
        <div className="stat" key={i}>
          <span className="stat__value">{it.value}{it.unit ? <small> {it.unit}</small> : null}</span>
          <span className="stat__label">{it.label}</span>
        </div>
      ))}
    </div>
  );
}

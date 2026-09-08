import React from "react";

/** The ten sunglasses portraits as comic stamps. `groom` gets the cyan special accent. */
export function CastGrid({ members = [] }) {
  return (
    <ul className="cast-grid">
      {members.map((m, i) => (
        <li key={m.name || i} className={`cast-card${m.groom ? " cast-card--groom" : ""}`}>
          <span className="cast-card__frame">
            <img src={m.photo} alt={m.alt || `${m.name} mit Sonnenbrille`} loading="lazy" />
          </span>
          <p className="cast-card__name">{m.name}</p>
          {m.role && <p className="cast-card__role">{m.role}</p>}
        </li>
      ))}
    </ul>
  );
}

import React from "react";

const DEFAULT_ITEMS = [
  { href: "index.html", label: "Start" },
  { href: "film-vlog.html", label: "Roadtrip" },
  { href: "film-drone.html", label: "Drone Edit" },
  { href: "fakten.html", label: "Zahlen & Fakten" }
];

export function SiteNav({ current = "index.html", brand = "Norwegen 2026", items = DEFAULT_ITEMS }) {
  return (
    <header className="nav">
      <div className="wrap nav__inner">
        <a className="nav__brand" href="index.html"><span className="flagmark" aria-hidden="true"></span>{brand}</a>
        <nav aria-label="Hauptnavigation">
          <ul className="nav__list">
            {items.map((it) => (
              <li key={it.href}>
                <a className="nav__link" href={it.href} aria-current={it.href === current ? "page" : undefined}>{it.label}</a>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
}

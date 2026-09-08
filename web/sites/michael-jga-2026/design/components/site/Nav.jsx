import React from "react";

const links = [
  { href: "index.html", label: "Start" },
  { href: "film.html", label: "Der Film" },
  { href: "impressum.html", label: "Impressum" }
];

export function Nav({ current = "index.html", brand = "Micha im Delirium", items = links }) {
  return (
    <nav className="nav" aria-label="Hauptnavigation">
      <div className="nav__inner">
        <a className="nav__brand" href="index.html">{brand}</a>
        <ul className="nav__list">
          {items.map((l) => (
            <li key={l.href}>
              <a className="nav__link" href={l.href} aria-current={l.href === current ? "page" : undefined}>{l.label}</a>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}

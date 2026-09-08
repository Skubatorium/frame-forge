import React from "react";

export function SiteFooter({ mark = "Micha im Delirium 2026", links = [], children }) {
  return (
    <footer className="footer">
      <div className="footer__inner">
        <p className="footer__mark">{mark}</p>
        {links.length > 0 && (
          <ul className="footer__links">
            {links.map((l) => <li key={l.href}><a href={l.href}>{l.label}</a></li>)}
          </ul>
        )}
        <div className="footer__fine">{children}</div>
      </div>
    </footer>
  );
}

import React from "react";

const SHARE = "Bitte gib Link und Passwort nicht weiter — auf den Bildern sind Menschen zu sehen, die nicht gefragt wurden, und jeder Abruf kostet Serverdaten. Soll jemand die Filme sehen: sag Bescheid, ich schicke den Zugang.";

export function SiteFooter({ note = SHARE, imprintHref = "impressum.html", baseline = "Norwegen 2026 · privat, nicht kommerziell" }) {
  return (
    <footer className="footer">
      <div className="wrap">
        <div className="footer__grid">
          <div className="footer__share">
            <span className="flagmark" aria-hidden="true" style={{ marginBottom: "var(--space-4)" }}></span>
            <p><b>Diese Seite ist privat.</b> {note}</p>
          </div>
          <nav className="footer__nav" aria-label="Fußzeile">
            <a href="index.html">Start</a>
            <a href="film-vlog.html">Roadtrip</a>
            <a href="film-drone.html">Drone Edit</a>
            <a href="fakten.html">Zahlen & Fakten</a>
            <a href={imprintHref}>Impressum</a>
          </nav>
        </div>
        <div className="footer__base"><span>{baseline}</span></div>
      </div>
    </footer>
  );
}

import React from "react";

export function PageHeader({ eyebrow, title, sub, meta = [], quiet = false }) {
  return (
    <header className={"page-header" + (quiet ? " page-header--quiet" : "")}>
      <div className="wrap wrap--content">
        {eyebrow ? <p className="eyebrow page-header__eyebrow">{eyebrow}</p> : null}
        <h1 className="page-header__title">{title}</h1>
        {sub ? <p className="page-header__sub">{sub}</p> : null}
        {meta.length ? (
          <ul className="page-header__meta">
            {meta.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
        ) : null}
      </div>
    </header>
  );
}

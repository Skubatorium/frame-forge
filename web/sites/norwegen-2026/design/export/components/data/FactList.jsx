import React from "react";

export function FactList({ items = [], columns = false }) {
  return (
    <ul className={"fact-list" + (columns ? " fact-list--columns" : "")}>
      {items.map((it, i) => (
        <li className={"fact-list__item" + (it.mark ? " fact-list__item--mark" : "")} key={i}>
          <span className="fact-list__name">{it.name}</span>
          {it.note ? <span className="fact-list__note">{it.note}</span> : null}
        </li>
      ))}
    </ul>
  );
}

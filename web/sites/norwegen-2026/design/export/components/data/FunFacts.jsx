import React from "react";

export function FunFacts({ items = [] }) {
  return (
    <div className="fun-facts">
      {items.map((it, i) => (
        <div className={"fun-fact" + (it.wide ? " fun-fact--wide" : "") + (it.cool ? " fun-fact--cool" : "")} key={i}>
          <span className="fun-fact__value">{it.value}<small>{it.unit}</small></span>
          <p className="fun-fact__text">{it.text}</p>
        </div>
      ))}
    </div>
  );
}

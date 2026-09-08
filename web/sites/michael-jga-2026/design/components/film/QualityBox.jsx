import React from "react";
import { Button } from "../core/Button.jsx";

/** Streaming vs. Download side by side. */
export function QualityBox({ options = [] }) {
  return (
    <div className="quality-box">
      {options.map((o) => (
        <article className={`quality-option${o.recommended ? " quality-option--recommended" : ""}`} key={o.title}>
          {o.tag && <span className="quality-option__tag">{o.tag}</span>}
          <h3 className="quality-option__title">{o.title}</h3>
          <p className="quality-option__spec">{o.spec}</p>
          <p className="quality-option__text">{o.text}</p>
          {o.hint && <p className="quality-option__hint">{o.hint}</p>}
          {o.action && (
            <Button href={o.action.href} download={o.action.download || undefined}
              variant={o.recommended ? "primary" : "secondary"}>{o.action.label}</Button>
          )}
        </article>
      ))}
    </div>
  );
}

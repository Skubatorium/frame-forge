import React from "react";

export function Notice({ mark = "!", tone = "quiet", children, className = "", ...rest }) {
  return (
    <aside className={`notice${tone === "loud" ? " notice--loud" : ""} ${className}`.trim()} {...rest}>
      <span className="notice__mark" aria-hidden="true">{mark}</span>
      <div className="notice__body">{children}</div>
    </aside>
  );
}

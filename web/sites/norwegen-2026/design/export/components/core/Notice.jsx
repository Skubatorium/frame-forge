import React from "react";

export function Notice({ title, quiet = false, children }) {
  return (
    <div className={"notice" + (quiet ? " notice--quiet" : "")}>
      {title ? <span className="notice__title">{title}</span> : null}
      {children}
    </div>
  );
}

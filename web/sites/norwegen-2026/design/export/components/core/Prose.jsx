import React from "react";

export function Prose({ lead, wide = false, children }) {
  return (
    <div className={"prose stack" + (wide ? " prose--wide" : "")}>
      {lead ? <p className="lead">{lead}</p> : null}
      {children}
    </div>
  );
}

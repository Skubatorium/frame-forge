import React from "react";

/** Readable text column inside the loud surroundings. */
export function Prose({ wide = false, children, className = "", ...rest }) {
  return <div className={`prose${wide ? " prose--wide" : ""} ${className}`.trim()} {...rest}>{children}</div>;
}

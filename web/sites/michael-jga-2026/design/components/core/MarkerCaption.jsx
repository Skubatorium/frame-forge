import React from "react";

/** Hand-marker caption with a rough underline stroke, as on the poster edges. */
export function MarkerCaption({ children, rotate = -4, className = "", style, ...rest }) {
  return (
    <span className={`marker-caption ${className}`.trim()}
      style={{ transform: `rotate(${rotate}deg)`, ...style }} {...rest}>{children}</span>
  );
}

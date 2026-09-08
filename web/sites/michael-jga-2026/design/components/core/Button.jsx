import React from "react";

export function Button({ as, variant = "primary", children, className = "", ...rest }) {
  const Tag = as || (rest.href ? "a" : "button");
  return (
    <Tag className={`btn btn--${variant} ${className}`.trim()} {...rest}>
      {children}
    </Tag>
  );
}

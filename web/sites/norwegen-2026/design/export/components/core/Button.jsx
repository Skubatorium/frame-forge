import React from "react";

export function Button({ variant = "primary", href, children, size, arrow = false, disabled = false, download = false, onClick, ...rest }) {
  const cls = ["btn", "btn--" + variant].join(" ");
  const inner = (
    <>
      {children}
      {size ? <span className="btn__size">{size}</span> : null}
      {arrow ? <span className="btn__arrow" aria-hidden="true">→</span> : null}
    </>
  );
  if (href) {
    return (
      <a className={cls} href={href} aria-disabled={disabled || undefined} download={download || undefined} {...rest}>{inner}</a>
    );
  }
  return <button className={cls} type="button" disabled={disabled} onClick={onClick} {...rest}>{inner}</button>;
}

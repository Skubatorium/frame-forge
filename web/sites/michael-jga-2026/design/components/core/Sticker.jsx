import React from "react";

/** Neon doodle accent — a crown, star or heart glyph, glowing, CSS-only. */
export function Sticker({ glyph = "★", tone = "pink", size = "md", still = false, style, className = "", ...rest }) {
  const tones = { pink: "", gold: " sticker--gold", cyan: " sticker--cyan" };
  const sizes = { sm: " sticker--sm", md: "", lg: " sticker--lg" };
  return (
    <span aria-hidden="true" style={style}
      className={`sticker${tones[tone] || ""}${sizes[size] || ""}${still ? " sticker--still" : ""} ${className}`.trim()}
      {...rest}>{glyph}</span>
  );
}

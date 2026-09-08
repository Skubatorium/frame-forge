import * as React from "react";

export interface StickerProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** A single glyph: crown, star, heart, spark. */
  glyph?: string;
  tone?: "pink" | "gold" | "cyan";
  size?: "sm" | "md" | "lg";
  /** Disable the float animation (it is disabled under prefers-reduced-motion anyway). */
  still?: boolean;
}

export declare function Sticker(props: StickerProps): JSX.Element;

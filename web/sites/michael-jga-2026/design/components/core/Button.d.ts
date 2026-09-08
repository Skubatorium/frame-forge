import * as React from "react";

export interface ButtonProps extends React.HTMLAttributes<HTMLElement> {
  /** Rendered element. Defaults to "a" when href is set, otherwise "button". */
  as?: keyof JSX.IntrinsicElements;
  /** gold gradient | pink outline | quiet outline */
  variant?: "primary" | "secondary" | "ghost";
  href?: string;
  download?: boolean | string;
  children?: React.ReactNode;
}

export declare function Button(props: ButtonProps): JSX.Element;

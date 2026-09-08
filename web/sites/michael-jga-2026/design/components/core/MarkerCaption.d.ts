import * as React from "react";

export interface MarkerCaptionProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Rotation in degrees; keep between -8 and 8. */
  rotate?: number;
  children?: React.ReactNode;
}

export declare function MarkerCaption(props: MarkerCaptionProps): JSX.Element;

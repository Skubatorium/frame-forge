import * as React from "react";

export interface QualityOption {
  title: string;
  /** Resolution / codec / size line. */
  spec: string;
  text: string;
  /** Bandwidth or storage caveat. */
  hint?: string;
  tag?: string;
  recommended?: boolean;
  action?: { href: string; label: string; download?: boolean };
}

export interface QualityBoxProps { options?: QualityOption[] }

export declare function QualityBox(props: QualityBoxProps): JSX.Element;

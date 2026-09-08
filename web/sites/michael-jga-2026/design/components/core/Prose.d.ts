import * as React from "react";

export interface ProseProps extends React.HTMLAttributes<HTMLDivElement> {
  /** 78ch instead of the default 64ch measure. */
  wide?: boolean;
  children?: React.ReactNode;
}

export declare function Prose(props: ProseProps): JSX.Element;

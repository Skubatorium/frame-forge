import * as React from "react";

export interface NoticeProps extends React.HTMLAttributes<HTMLElement> {
  /** Single glyph in the neon ring. */
  mark?: string;
  tone?: "quiet" | "loud";
  children?: React.ReactNode;
}

export declare function Notice(props: NoticeProps): JSX.Element;

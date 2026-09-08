import * as React from "react";

export interface PageHeaderProps {
  /** Small line above the title. */
  kicker?: string;
  title: React.ReactNode;
  sub?: React.ReactNode;
  /** Still from the film, used full-bleed behind the title (loud variant only). */
  image?: string;
  imageAlt?: string;
  /** "loud" = gold comic title over a still; "quiet" = plain caps on a flat surface. */
  variant?: "loud" | "quiet";
  children?: React.ReactNode;
}

export declare function PageHeader(props: PageHeaderProps): JSX.Element;

import * as React from "react";

export interface PlayTeaserProps {
  href?: string;
  /** Poster frame, 16:9. */
  poster: string;
  title: React.ReactNode;
  /** Runtime / language / format line. */
  meta?: React.ReactNode;
  alt?: string;
}

export declare function PlayTeaser(props: PlayTeaserProps): JSX.Element;

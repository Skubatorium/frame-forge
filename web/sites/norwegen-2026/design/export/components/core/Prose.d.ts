import * as React from "react";

/** Textabschnitt mit 65–75 Zeichen Zeilenlänge. */
export interface ProseProps {
  /** Erster, größerer Absatz */
  lead?: React.ReactNode;
  /** Ohne Breitenbegrenzung (in schmalen Spalten) */
  wide?: boolean;
  children?: React.ReactNode;
}
export declare function Prose(props: ProseProps): JSX.Element;

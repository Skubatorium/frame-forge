import * as React from "react";

/**
 * Die kuriosen Zahlen — lockerer gesetzt, gleiche Farbwelt.
 * @startingPoint section="Daten" subtitle="Kuriositäten-Block" viewport="1280x420"
 */
export interface FunFactsProps {
  items: {
    value: string;
    /** Einheit unter der Zahl, z. B. "Fisch" */
    unit: string;
    text: React.ReactNode;
    /** Über beide Spalten */
    wide?: boolean;
    /** Zahl in Gletschertürkis statt Sandgold */
    cool?: boolean;
  }[];
}
export declare function FunFacts(props: FunFactsProps): JSX.Element;

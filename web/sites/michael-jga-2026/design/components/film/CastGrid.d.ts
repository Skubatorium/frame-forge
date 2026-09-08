import * as React from "react";

export interface CastMember {
  name: string;
  /** Square sunglasses portrait, assets/img/cast/<name>.jpg */
  photo: string;
  /** Optional line under the name, e.g. "Karaoke-Beauftragter". */
  role?: string;
  alt?: string;
  /** The groom — gets the cyan special accent. Exactly one. */
  groom?: boolean;
}

export interface CastGridProps { members?: CastMember[] }

export declare function CastGrid(props: CastGridProps): JSX.Element;

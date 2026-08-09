import React from "react";

export function MapFigure({ src, alt, caption, href, linkLabel = "In Google Maps öffnen →", width, height }) {
  return (
    <figure className="map-figure">
      <div className="map-figure__frame">
        <img src={src} alt={alt} loading="lazy" width={width} height={height} />
      </div>
      <figcaption>
        <span>{caption}</span>
        {href ? <a href={href} rel="noreferrer noopener">{linkLabel}</a> : null}
      </figcaption>
    </figure>
  );
}

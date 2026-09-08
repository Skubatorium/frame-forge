import React from "react";

export function PlayTeaser({ href = "film.html", poster, title, meta, alt = "" }) {
  return (
    <a className="play-teaser" href={href}>
      <img src={poster} alt={alt} />
      <span className="play-teaser__veil">
        <span className="play-teaser__badge" aria-hidden="true">
          <svg viewBox="0 0 24 24" role="presentation"><path d="M8 5.5v13l11-6.5z" /></svg>
        </span>
        <span className="play-teaser__title">{title}</span>
        {meta && <span className="play-teaser__meta">{meta}</span>}
      </span>
    </a>
  );
}

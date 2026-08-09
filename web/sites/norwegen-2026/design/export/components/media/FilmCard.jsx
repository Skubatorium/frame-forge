import React from "react";
import { Button } from "../core/Button.jsx";

export function FilmCard({ image, alt = "", kicker, title, text, href, cta = "Zum Film" }) {
  return (
    <article className="film-card">
      <img className="film-card__img" src={image} alt={alt} loading="lazy" />
      <div className="film-card__body">
        {kicker ? <p className="film-card__kicker"><span className="film-card__duration">{kicker}</span></p> : null}
        <h3 className="film-card__title">{title}</h3>
        {text ? <p className="film-card__text">{text}</p> : null}
        <div className="film-card__actions">
          <Button variant="primary" href={href} arrow>{cta}</Button>
        </div>
      </div>
    </article>
  );
}

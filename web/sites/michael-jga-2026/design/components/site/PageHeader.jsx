import React from "react";

/** Cinema-poster masthead. `variant="quiet"` is the plain-caps voice for subpages. */
export function PageHeader({ kicker, title, sub, image, imageAlt = "", variant = "loud", children }) {
  const quiet = variant === "quiet";
  return (
    <header className={`page-header${quiet ? " page-header--quiet" : ""}`}>
      {!quiet && image && (
        <div className="page-header__media">
          <img src={image} alt={imageAlt} />
        </div>
      )}
      <div className="page-header__body">
        {kicker && (quiet ? <p className="ruled-caps">{kicker}</p> : <p className="page-header__kicker">{kicker}</p>)}
        <h1 className="page-header__title">{title}</h1>
        {sub && <p className="page-header__sub">{sub}</p>}
        {children}
      </div>
    </header>
  );
}

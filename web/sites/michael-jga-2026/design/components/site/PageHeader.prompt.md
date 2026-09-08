The masthead. Its two variants ARE the film's two faces — loud party title vs. quiet, composed caps.

```jsx
<PageHeader kicker="Brüssel · Wochenende folgt" title="Micha im Delirium 2026"
  sub="Ein Film über gute Freunde und schlechte Entscheidungen."
  image="assets/img/hero.jpg" imageAlt="Die Gruppe bei der Kneipentour" />

<PageHeader variant="quiet" kicker="Rechtliches" title="Impressum" />
```

- `loud` for the landing page only. Subpages use `quiet`.
- The still behind the title always gets the protection gradient; do not skip `imageAlt`.

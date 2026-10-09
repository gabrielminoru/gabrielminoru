# minoru.rocks — site source

MkDocs (Material) source for https://minoru.rocks.

- Edit pages in `docs/`, navigation in `mkdocs.yml`.
- Push to `site-src` → GitHub Actions builds and publishes to `gh-pages`.
- Never edit `gh-pages` by hand; it is overwritten on every deploy.

Preview locally:

```sh
uv run --with-requirements requirements.txt mkdocs serve
```

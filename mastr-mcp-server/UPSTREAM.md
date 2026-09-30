# Vendored from UliRCS/mastr-mcp-server

This directory is a copy of <https://github.com/UliRCS/mastr-mcp-server>
(MIT, © Ulrich Haberland), vendored so the analysis code in the parent repo
can import `mastr_mcp` directly and so the MCP server can be run from here.

- Upstream commit: `7e24b6b98c2ca393f764ad41d8b05617fd339522` (v1.0.1)
- Vendored on: 2026-09-30

## Local changes

Keep this list short — every entry is a merge conflict waiting for the next
`rsync`. Re-apply all of them after updating.

1. `uv.lock` removed (the parent repo's workspace lockfile is authoritative).
2. This file added.
3. **`pyproject.toml` — packaging fix.** Added
   `[tool.hatch.build.targets.wheel]` with `only-include` and a
   `force-include` block for the dropdown JSONs.

   Upstream declares no wheel target, so hatchling auto-detects only the module
   matching the normalised project name — `mastr_mcp_server.py`, the 40-line
   launcher — and ships a wheel *without* the `mastr_mcp` package. It is
   invisible in this workspace because uv installs the member editable, which
   puts the source tree on `sys.path`. It breaks the moment another repo
   depends on this one over git:

   ```
   ModuleNotFoundError: No module named 'mastr_mcp'
   ```

   The dropdown JSONs sit beside `pyproject.toml`, outside the package, so they
   also needed force-including.

4. **`mastr_mcp/filters.py` — dropdown search path.** `_load_dropdowns` resolved
   paths against `Path(__file__).parent.parent`, which is `site-packages/` for
   an installed wheel. Missing files are handled by logging a warning and
   returning `{}`, documented as "dropdown filters pass through unchanged" —
   which means **silent wrong results**, not a failure: a filter of
   `Energieträger = "Solare Strahlungsenergie"` is sent as a literal string
   instead of its numeric MaStR ID (`2495`), and the query does not filter as
   intended. Now searches the package directory first.

   Both changes are worth upstreaming to <https://github.com/UliRCS/mastr-mcp-server>.

Verify after any update:

```bash
cd mastr-mcp-server && uv build --wheel -o /tmp/w
uv venv /tmp/v -p 3.12 && VIRTUAL_ENV=/tmp/v uv pip install 'mcp<2' /tmp/w/*.whl
/tmp/v/bin/python -c "from mastr_mcp import filters; assert filters.UNIT_DROPDOWN_VALUES"
```

To update:

```bash
git clone --depth 1 https://github.com/UliRCS/mastr-mcp-server.git /tmp/mastr-mcp-server
rsync -a --delete --exclude .git --exclude uv.lock --exclude UPSTREAM.md /tmp/mastr-mcp-server/ mastr-mcp-server/
# then update the commit hash above and run `uv lock` in the repo root
```

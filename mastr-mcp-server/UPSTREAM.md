# Vendored from UliRCS/mastr-mcp-server

This directory is a copy of <https://github.com/UliRCS/mastr-mcp-server>
(MIT, © Ulrich Haberland), vendored so the analysis code in the parent repo
can import `mastr_mcp` directly and so the MCP server can be run from here.

- Upstream commit: `7e24b6b98c2ca393f764ad41d8b05617fd339522` (v1.0.1)
- Vendored on: 2026-09-30
- Local changes: `uv.lock` removed (the parent repo's workspace lockfile is
  authoritative); this file added. Everything else is unmodified.

To update:

```bash
git clone --depth 1 https://github.com/UliRCS/mastr-mcp-server.git /tmp/mastr-mcp-server
rsync -a --delete --exclude .git --exclude uv.lock --exclude UPSTREAM.md /tmp/mastr-mcp-server/ mastr-mcp-server/
# then update the commit hash above and run `uv lock` in the repo root
```

# Copilot instructions for StarRoll

This file contains concise, actionable guidance for AI coding agents (Copilot-like) to be immediately productive in this repository.

1) Big picture (what to know first)
- The repo centers on a JSON/OpenAPI-driven backend for a star-visualization system. The canonical API is `idl/openapiv3.yaml`.
- Major logical components (inferred from the OpenAPI):
  - GUI endpoints: `GET /gui/*` and `POST /gui/*` — timeline, play speed, search. Tagged with `GUI` and some sections are annotated by contributor `huafu`.
  - Data collection & astronomy engine: `POST /api/*` — camera, GPS, attitude, star catalog, coordinate calculations.
  - Render engine: `POST /render/*` — `Renderstars` and `Renderstartrail` accept base64 camera frames and view coordinates; responses return base64 images and metadata.

2) Concrete patterns and conventions to follow
- The OpenAPI spec (`idl/openapiv3.yaml`) is authoritative: add or change API shapes there and mirror changes into code that serializes/deserializes requests/responses.
- Image payloads are encoded as base64 with a `mime` field and `width`/`height` metadata — expect large payloads and prefer streaming or chunking in tests when possible.
- `viewCoords` / star coordinate shapes are objects with `id`, `u`, `v` or references to `starMeta`/`viewCoordinate` schemas in the spec — use these names when generating types.
- Contributor tags/comments: sections marked with `# --------------huafu----------------` indicate ownership or recent edits — treat those areas as higher-sensitivity for API compatibility.

3) Integration points and external dependencies (discoverable)
- Primary integration surface is the OpenAPI file. Other external systems expected by the API: camera/image capture, GPS/IMU sensors, star catalogs — these are modeled by request/response shapes but actual adapters may live elsewhere (not present in repo snapshot).

4) Developer workflows (what an agent should ask/verify)
- There are no obvious build or test manifests in the current workspace (no `package.json`, `pyproject.toml`, `Makefile`, etc.). Before guessing build steps: ask the human for preferred language/runtime and the commands used to build/test.
- When adding code that implements or mocks endpoints, update `idl/openapiv3.yaml` first (if API changes), then implement server/client code and unit tests that use the exact schema names from the file.

5) Safety rules for automated edits
- Do NOT modify `idl/openapiv3.yaml` without (a) confirming intended API change and (b) updating any generated code or docs that depend on it.
- When touching rendering logic, avoid committing large binary blobs (base64 images) to the repo; use fixtures/fixtures metadata instead.

6) Useful examples (copyable patterns to follow)
- When referencing the render API, use the same JSON shape as `POST /render/Renderstars` in `idl/openapiv3.yaml`: include `cameraFrame.{mime,base64,width,height}`, `viewCoords` (array of `{id,u,v}`), `style.theme` and `output.{format,width,height}`.
- When producing types, name them after the schemas in the spec (e.g., `cameraMeta`, `starMeta`, `viewCoordinate`, `attitude`) to keep parity with existing names.

7) If something is missing
- If asked to implement build/test/run, request the target runtime (Node/Python/Go/etc.) and any existing CI settings or Dockerfiles from the repo maintainers.

Questions for the human
- Do you want Copilot edits to directly change `idl/openapiv3.yaml`, or should API changes be proposed as PRs first?
- What is the preferred runtime or repo-level build/test commands (if any)?

End of instructions — ask for clarifications or permission before making breaking API changes.

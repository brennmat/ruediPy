# Versioning & Releases

## Branches
- `main`: always releasable
- feature / bugfix branches: short-lived, merged into `main`
- No permanent `develop` branch

## What is a release
- A release is a **Git tag** on a specific commit
- Tags follow SemVer: `vMAJOR.MINOR.PATCH` (e.g. `v1.2.3`)
- Tags are the single source of truth for released versions

## Where released code lives
- In Git: on the tagged commit
- For users: built artifacts (wheel/sdist, optional `.deb`) published from that tag
- On GitHub: Releases page points to the tag

## Version numbers
- Versions are derived from Git tags
  - Tagged commit → `1.2.3`
  - Commits after tag → `1.2.4.devN+g<hash>`
- Only tags create fixed versions

## Release workflow
1. Merge intended changes into `main`
2. Ensure CI is green
3. Create tag `vX.Y.Z` on `main`
4. CI builds and publishes artifacts from the tag

## Bug fixes after release
- If only latest version is supported:
  - Fix on `main`, tag next patch
- If older minors are supported:
  - Create `release/X.Y` branch
  - Cherry-pick fixes
  - Tag `vX.Y.Z` on that branch

## CI
- CI runs tests and builds on every push/PR
- CI publishes artifacts only on `v*` tags
- CI runs in a Debian-based environment (container) to match users

## Rule of thumb
> Branches are for work.  
> Tags are for releases.  
> Users install tags.


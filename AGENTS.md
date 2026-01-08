# AGENTS.md

## Scope
This file applies to the entire `ihcei-ecosystem` repository.

## Coding Conventions
* Core logic must return standard Python types (float, int) for JSON serialization.
* Use `src.` prefix for imports.
* Ensure all code is verifiable via `pytest`.

## Architecture
* **CI (Centric Intelligence):** ADGE, TQG-CFE.
* **EI (Ethical Intelligence):** NERE.
* **SEH:** The extraction pipeline.

## Verification
* Run `pytest` to verify logic.

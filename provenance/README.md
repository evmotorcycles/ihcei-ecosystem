# provenance/ — cryptographic origin lock

Reproduce freely; the origin stays yours. See `../PROVENANCE.md` for the full story.

```bash
python3 provenance/verify_provenance.py    # anyone reproducing: confirm you match the origin
python3 provenance/build_provenance.py     # author, at a release: (re)build the lock
python3 -m pytest -q provenance/test_provenance.py
```

- `provenance_core.py` — shared logic: which frozen artifacts are fingerprinted, per-file SHA-256, and the domain-separated binary Merkle root.
- `build_provenance.py` — writes `../PROVENANCE.lock.json` (author, origin, root, per-file leaves).
- `verify_provenance.py` — recomputes the root from the working tree; prints attribution on match, diverged files on mismatch.
- `test_provenance.py` — asserts the lock verifies, is tamper-evident, and excludes mutable `results*.json`.

Root is bound into `../CITATION.cff` and echoed in `../NOTICE` / `../LICENSE`.

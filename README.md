# ihcei-ecosystem
The IHCEI Ecosystem is a Sovereign Operating System replacing standard AI with Centric and Ethical Intelligence. Built on the ADGE and TQG-CFE frameworks, it optimizes for Network Cognitive Development (C_{dev}) rather than profit. It features the Neural Ethical Reasoning Engine (NERE) to audit all decisions against the 10 Elements of Deen.

## Reproduce every test — one command

```bash
bash reproduce_all.sh
```

No keys, no network (needs `python3`+`pytest` and `node`≥18). Runs **all 23 test
suites** across NERE/IHCEI, HELM, Page Code, Echo, Agency Internet, the Novora
suite/PAGES, EI/EI-LLM, the **Hinton** and **Russell** tests, and the telemetry /
physics experiments. See **[REPRODUCE.md](REPRODUCE.md)** for the full map and how
to run any single component. CI runs it on every push (`.github/workflows/reproduce.yml`).

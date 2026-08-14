"""prox — command line interface.

    prox index ~/Documents -o home.prox.npz
    prox find  home.prox.npz "mtoto ana homa"
    prox near  home.prox.npz notes/clinic.txt
    prox stats home.prox.npz
"""

from __future__ import annotations

import argparse
import os
import sys

TEXT_SUFFIXES = {
    ".txt", ".md", ".rst", ".csv", ".tsv", ".json", ".yaml", ".yml", ".ini", ".cfg",
    ".py", ".js", ".ts", ".c", ".h", ".cpp", ".java", ".go", ".rs", ".rb", ".sh",
    ".html", ".xml", ".sql", ".org", ".tex",
}


def _walk(root, max_bytes, suffixes):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fn in sorted(filenames):
            if fn.startswith("."):
                continue
            if suffixes and os.path.splitext(fn)[1].lower() not in suffixes:
                continue
            p = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(p) > max_bytes:
                    continue
                with open(p, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
            except OSError:
                continue
            if text.strip():
                yield os.path.relpath(p, root), text


def cmd_index(args):
    import prox

    pairs = list(_walk(args.root, args.max_bytes, None if args.all else TEXT_SUFFIXES))
    if not pairs:
        sys.exit(f"no readable text files under {args.root}")
    names, texts = zip(*pairs)
    ix = prox.build(
        texts, ids=names, dim=args.dim, reach=args.reach,
        min_df=args.min_df, seed=args.seed, verbose=True,
    )
    ix.save(args.out)
    print(f"[prox] wrote {args.out} ({os.path.getsize(args.out)/1e6:.1f} MB on disk)")


def cmd_find(args):
    import prox

    ix = prox.ProxIndex.load(args.index)
    hits = ix.search(args.query, top_k=args.n)
    if not hits:
        print("no shared features with this index — nothing to rank.")
        print("that is an honest empty answer, not a ranking of noise.")
        return
    for rank, (name, dist, _) in enumerate(hits, 1):
        print(f"{rank:>3}. {dist:8.4f}  {name}")


def cmd_near(args):
    import prox

    ix = prox.ProxIndex.load(args.index)
    if args.item not in ix.ids:
        sys.exit(f"{args.item!r} is not in this index")
    for rank, (name, dist, _) in enumerate(ix.neighbors(ix.ids.index(args.item), args.n), 1):
        print(f"{rank:>3}. {dist:8.4f}  {name}")


def cmd_stats(args):
    import prox

    ix = prox.ProxIndex.load(args.index)
    for k in ("format", "n_items", "n_feats", "n_edges", "dim", "reach",
              "min_df", "couplings", "build_seconds"):
        print(f"{k:>15}: {ix.meta.get(k)}")
    print(f"{'in-memory':>15}: {ix.nbytes()/1e6:.1f} MB "
          f"({ix.nbytes()/max(ix.meta['n_items'],1):.0f} bytes/item)")


def main(argv=None):
    p = argparse.ArgumentParser(prog="prox", description="a proximity layer for everything")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("index", help="build an index from a directory")
    a.add_argument("root")
    a.add_argument("-o", "--out", default="index.prox.npz")
    a.add_argument("--dim", type=int, default=128)
    a.add_argument("--reach", type=float, default=1e-3)
    a.add_argument("--min-df", dest="min_df", type=int, default=2)
    a.add_argument("--seed", type=int, default=0)
    a.add_argument("--max-bytes", dest="max_bytes", type=int, default=1_000_000)
    a.add_argument("--all", action="store_true", help="index every file, not just known text types")
    a.set_defaults(func=cmd_index)

    b = sub.add_parser("find", help="rank items by proximity to a query")
    b.add_argument("index")
    b.add_argument("query")
    b.add_argument("-n", type=int, default=10)
    b.set_defaults(func=cmd_find)

    c = sub.add_parser("near", help="items nearest an existing item")
    c.add_argument("index")
    c.add_argument("item")
    c.add_argument("-n", type=int, default=10)
    c.set_defaults(func=cmd_near)

    d = sub.add_parser("stats", help="describe an index")
    d.add_argument("index")
    d.set_defaults(func=cmd_stats)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    main()

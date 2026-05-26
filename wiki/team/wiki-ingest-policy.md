# Wiki Ingest Policy

The ingest runner accepts packet manifests under changed raw packet roots and writes deterministic synthesis pages under `wiki/`.

Low-risk reference and meeting packets may be direct-commit candidates. Experiment, performance, model, feature, augmentation, supported, disputed, and superseded claims require bot PR review. Guard failures hard-fail and must not mutate `wiki/`.

Packets must keep raw evidence local to the packet root. Secret-like content, secret filenames, model weight files, path escapes, missing raw evidence, metric mismatches, wrong target routes, and packet size limit violations are blocked.

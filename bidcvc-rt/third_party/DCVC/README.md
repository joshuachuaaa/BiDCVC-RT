# third_party/DCVC

This directory is a placeholder for **vanilla DCVC-RT** source code.

## Add as a git submodule (recommended)

From the `bidcvc-rt/` repo root:

```bash
git submodule add <DCVC_REPO_URL> third_party/DCVC
git submodule update --init --recursive
```

## Notes

- Do not modify the DCVC source directly for BiDCVC-RT experiments in this scaffold.
- Implement all integration glue under `src/bidcvc/models/dcvc_adapter/`.


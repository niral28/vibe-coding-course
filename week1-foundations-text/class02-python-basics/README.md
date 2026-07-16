# FAQ:

## Error:

An cyptography error:
```bash
eror: command ['maturin', 'pep517', 'build-wheel', '-i', '/opt/anaconda3/envs/gset-vibes/bin/python3.10', '--compatibility', 'off'] returned non-zero exit status 1
      [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for cryptography
Failed to build cryptography
error: failed-wheel-build-for-install
```

Resolve by:

```bash
conda install -c conda-forge cryptography
```
"""Build the alpha-grid null tables (run once by the humans; the results are frozen data).

    python lab/unccd_alpha/build_nulls.py 2:800 3:300 ...   # dimension:n_max pairs
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nulls  # noqa: E402

OUT = Path(__file__).resolve().parent / "data" / "nulls"

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for spec in sys.argv[1:]:
        d, n_max = (int(x) for x in spec.split(":"))
        if (OUT / f"nn_d{d}.npz").exists():
            print(f"nn_d{d}.npz exists; skipped", flush=True)
            continue
        t = nulls.build(d, n_max)
        np.savez_compressed(OUT / f"nn_d{d}.npz", d=t["d"], n_max=t["n_max"], niter=t["niter"], seed=t["seed"],
                            alphas=t["alphas"], ave=t["ave"], med=t["med"])
        print(f"wrote nn_d{d}.npz (n_max {n_max})", flush=True)

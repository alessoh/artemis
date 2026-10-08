# Run 2: independent replication on the larger held-out problems

After run 2 finished, Claude re-ran the final solver (experiment_final_run2.py,
SHA-256 3406e1b80391) and the frozen PyVRP reference once each (seed 0) on the
eight scale problems, on a different and slower machine (the Claude workspace,
not the lab's sandbox), with the same frozen harness and time limits.

| Problem | Run 2 solver gap % | PyVRP default gap % |
|---|---|---|
| X-n627-k43 | 0.918 | 1.466 |
| X-n670-k130 | 3.450 | 2.628 |
| X-n716-k35 | 1.356 | 1.697 |
| X-n766-k71 | 1.513 | 1.683 |
| X-n801-k40 | 0.615 | 1.119 |
| X-n856-k95 | 0.310 | 0.572 |
| X-n916-k207 | 1.143 | 1.351 |
| X-n979-k58 | 1.057 | 1.837 |
| mean | 1.295 | 1.544 |

The run 2 solver was better on 7 of 8 problems and 0.25 points better on the
mean. The direction agrees with the lab's three-seed result (0.66 points,
8 of 8), but the margin is smaller on this slower machine, and X-n670-k130
(many short routes, about 5 customers per route) was lost here as it was by
run 1's solver. One seed on one machine; it supports, but does not by itself
establish, the lab's result.

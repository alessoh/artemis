# Preliminary probe: wave speeds in Lanyon's ideal MHD specifications

This folder backs the Artemis–Lanyon audit proposal of 31 October 2026 (`docs/Artemis_Lanyon_Audit_Proposal.docx`). It holds Claude's preliminary checks, made by hand before any Artemis run. Nothing here is pre-registered.

## Source examined
`lanyonai/IdealMHD`, commit `beeff1a` (27 Aug 2026, MIT licence), file `specifications/ideal_mhd_1d.rkt`. The C kernel `implementations/ideal_mhd_1d.c` computes the same expression.

The specification lists the eight wave speeds as follows:
- the Alfvén pair as `u ± vA`, with `vA = u - |B|/sqrt(rho)`, so the flow velocity is included in vA;
- the fast and slow pairs as `u ± sqrt(0.5*(vA^2 + cs^2 ± sqrt((vA^2+cs^2)^2 - 4 vA^2 cs^2)))`, which uses the total field where the textbook formula uses Bx.

The Lax-Friedrichs dissipation speed `amax` is the largest of these magnitudes over the left and right states. The 2D and 3D variants, and the divergence-cleaning (hyperbolic) variants, use the same construction with `vAx`/`vAy`.

## Scripts
- `check_mhd_wavespeeds.py`
  - Builds the exact Jacobian of the specification's own flux with SymPy and compares its eigenvalues with the listed speeds at random physical states.
  - Also compares the specification's `amax` with the true spectral radius.
  - Run as `python3 check_mhd_wavespeeds.py 20000`, seed 20261031.
- `briowu_probe.py`
  - A first-order Rusanov driver written by Claude, not Lanyon's, built on the specification's flux. It compares the specification's `amax` with the textbook fast speed on five standard Riemann problems.
  - The time step is set at CFL 0.9, from the speed the scheme itself uses.

## Results (`wavespeed_check_output.txt`, `shock_tube_output.txt`)
- The listed speeds differ from the true Jacobian eigenvalues in 40,000 of 40,000 states. The textbook fast speed matches the true spectral bound in all 40,000.
- At 52.1% of 20,000 random interfaces, the specification's `amax` is below the true fastest wave speed. The ratio is as low as 0.532.
- On the Brio–Wu left state, `amax` is 0.789 of the true value.
- Brio–Wu shifted by a uniform flow u = 2, which is physically the same problem seen from a moving frame:
  - with the specification's speed, pressure goes negative (minimum −3.56);
  - with the textbook speed, it stays positive (minimum 0.089).

## Caveats
- The formulas were transcribed by hand from the `.rkt` file. The Artemis program will parse the specifications directly.
- The driver is Claude's own, first order, with outflow boundaries.
- Lanyon's own simulation driver is not public.
- The Lean proofs were not rerun.

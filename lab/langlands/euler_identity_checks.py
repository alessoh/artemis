"""Numerical checks for "Euler's identity and the Langlands program".

Every identity marked "verified" in the paper is checked here. Run with

    pip install mpmath cypari2
    python euler_identity_checks.py

mpmath works at 40 significant digits; PARI/GP (through cypari2) supplies the
elliptic curve data. The script prints one line per check and a final count,
and exits with status 1 if any check fails.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from math import factorial

import mpmath as mp

mp.mp.dps = 40
TOL = mp.mpf(10) ** -25
RESULTS: list[tuple[str, bool, str]] = []
I_POWERS = (mp.mpc(1), mp.mpc(0, 1), mp.mpc(-1), mp.mpc(0, -1))   # exact powers of i


def record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'pass' if ok else 'FAIL'}] {name}{': ' + detail if detail else ''}")


def close(a, b, tol=TOL) -> bool:
    return abs(mp.mpc(a) - mp.mpc(b)) < tol


def primes(n: int) -> list[int]:
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(n + 1) if sieve[i]]


# ---------------------------------------------------------------- check 0
def check_euler() -> None:
    record("0a  e^{i pi} = -1", close(mp.exp(1j * mp.pi), -1))
    record("0b  e^{i pi/2} = i", close(mp.exp(1j * mp.pi / 2), 1j))
    record("0c  (e^{i pi/4})^4 = -1", close(mp.exp(1j * mp.pi / 4) ** 4, -1))


# ---------------------------------------------------------------- check 1
def bernoulli_fraction(n: int) -> Fraction:
    """Exact Bernoulli number B_n (B_1 = -1/2 convention) by the Akiyama-Tanigawa algorithm."""
    a = [Fraction(0)] * (n + 1)
    for m in range(n + 1):
        a[m] = Fraction(1, m + 1)
        for j in range(m, 0, -1):
            a[j - 1] = j * (a[j - 1] - a[j])
    return a[0] if n != 1 else Fraction(-1, 2)


def check_zeta_even() -> None:
    for k in range(1, 7):
        exact_frac = Fraction(-bernoulli_fraction(2 * k)) / (2 * factorial(2 * k))
        value = mp.zeta(2 * k) / (2j * mp.pi) ** (2 * k)
        ok = close(value, mp.mpf(exact_frac.numerator) / exact_frac.denominator)
        record(f"1.{k} zeta({2 * k})/(2 pi i)^{2 * k} = -B_{2 * k}/(2({2 * k})!)", ok, str(exact_frac))


# ---------------------------------------------------------------- check 2
def check_gauss_sums() -> None:
    odd = [p for p in primes(40) if p > 2][:10]
    for p in odd:
        g = mp.fsum(mp.exp(2j * mp.pi * mp.mpf(a * a % p) / p) for a in range(p))   # sum of (a/p) e(a/p) = sum e(a^2/p)
        predicted = I_POWERS[(((p - 1) // 2) ** 2) % 4] * mp.sqrt(p)
        record(f"2.{p} Gauss sum g_{p} = i^(((p-1)/2)^2) sqrt(p)", close(g, predicted, mp.mpf(10) ** -20))


# ---------------------------------------------------------------- check 3
def check_weil_index() -> None:
    # Regularised: int exp((i pi - eps) x^2) dx = sqrt(pi / (eps - i pi)); check the quadrature
    # against the closed form at eps = 1/2, then the eps -> 0 limit of the closed form.
    eps = mp.mpf(1) / 2
    numeric = mp.quad(lambda x: mp.exp((1j * mp.pi - eps) * x * x), mp.linspace(-12, 12, 49))
    record("3a  regularised Fresnel integral matches its closed form",
           close(numeric, mp.sqrt(mp.pi / (eps - 1j * mp.pi)), mp.mpf(10) ** -20))
    limit = mp.sqrt(mp.pi / (mp.mpf(10) ** -30 - 1j * mp.pi))
    record("3b  int_R e^{i pi x^2} dx = e^{i pi/4}", close(limit, mp.exp(1j * mp.pi / 4), mp.mpf(10) ** -20))


# ---------------------------------------------------------------- check 4
def check_landsberg_schaar() -> None:
    pairs = [(1, 1), (2, 3), (3, 5), (5, 7), (4, 9), (7, 11), (10, 13)]
    for p, q in pairs:
        lhs = mp.fsum(mp.exp(2j * mp.pi * mp.mpf(n * n * q % p) / p) for n in range(p)) / mp.sqrt(p)
        rhs = mp.exp(1j * mp.pi / 4) / mp.sqrt(2 * q) * mp.fsum(
            mp.exp(-1j * mp.pi * mp.mpf(n * n * p % (4 * q)) / (2 * q)) for n in range(2 * q))
        record(f"4.({p},{q}) Landsberg-Schaar", close(lhs, rhs, mp.mpf(10) ** -20))


# ---------------------------------------------------------------- check 5
def sigma(n: int, k: int) -> int:
    return sum(d ** k for d in range(1, n + 1) if n % d == 0)


def e6(tau, terms=80):
    q = mp.exp(2j * mp.pi * tau)
    return 1 - 504 * mp.fsum(sigma(n, 5) * q ** n for n in range(1, terms))


def delta(tau, terms=80):
    q = mp.exp(2j * mp.pi * tau)
    prod = mp.mpf(1)
    for n in range(1, terms):
        prod *= (1 - q ** n) ** 24
    return q * prod


def check_modular() -> None:
    t = mp.mpf("1.37")
    forms = [("E6", 6, e6), ("Delta", 12, delta), ("Delta*E6", 18, lambda z: delta(z) * e6(z))]
    for name, k, f in forms:
        lhs = f(1j / t)
        rhs = I_POWERS[k % 4] * t ** k * f(1j * t)
        record(f"5.{name} f(i/t) = i^k t^k f(it), k = {k}", close(lhs, rhs, mp.mpf(10) ** -18))
    record("5.E6(i) = 0", abs(e6(1j)) < mp.mpf(10) ** -18)


# ---------------------------------------------------------------- check 6
def check_root_numbers() -> None:
    try:
        import cypari2
    except ImportError:
        record("6   (-1)^rank = -w_N = a_N (needs cypari2)", False, "cypari2 not installed")
        return
    pari = cypari2.Pari()
    curves = {"11a1": ([0, -1, 1, -10, -20], 11, 0), "37a1": ([0, 0, 1, -1, 0], 37, 1),
              "43a1": ([0, 1, 1, 0, 0], 43, 1), "389a1": ([0, 1, 1, -2, 0], 389, 2),
              "5077a1": ([0, 0, 1, -7, 6], 5077, 3)}
    for label, (ai, n, rank) in curves.items():
        e = pari.ellinit(ai)
        conductor = int(pari.ellglobalred(e)[0])
        a_n = int(pari.ellap(e, n))
        w_n = int(pari.ellrootno(e, n))
        w = int(pari.ellrootno(e))
        analytic_rank = int(pari.ellanalyticrank(e)[0])
        ok = (conductor == n and analytic_rank == rank and (-1) ** rank == -w_n == a_n == w)
        record(f"6.{label} (-1)^rank = -w_N = a_N", ok,
               f"N = {conductor}, analytic rank {analytic_rank}, a_N = {a_n}, w_N = {w_n}")


# ---------------------------------------------------------------- check 7
def check_dwork() -> None:
    """Dwork's splitting function theta(x) = exp(pi (x - x^p)) at x = 1, with pi^(p-1) = -p.

    Elements of Q(pi) are vectors of p - 1 rational coefficients of 1, pi, ...,
    pi^(p-2). theta(1) = sum_n lambda_n with lambda_n the coefficient of x^n in
    exp(pi x) exp(-pi x^p); we truncate at x^TERMS.
    """
    TERMS = 60

    def mul(a, b, p):
        out = [Fraction(0)] * (p - 1)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    if y:
                        k = i + j
                        coeff = x * y
                        while k >= p - 1:            # pi^(p-1) = -p
                            k -= p - 1
                            coeff *= -p
                        out[k] += coeff
        return out

    def pi_power(n, p):
        v = [Fraction(0)] * (p - 1)
        v[0] = Fraction(1)
        base = [Fraction(0)] * (p - 1)
        base[1 % (p - 1)] = Fraction(1) if p > 2 else Fraction(-p)
        for _ in range(n):
            v = mul(v, base, p)
        return v

    def valuation(a, p):
        best = None
        for k, x in enumerate(a):
            if x:
                num, den = x.numerator, x.denominator
                vp = 0
                while num % p == 0:
                    num //= p
                    vp += 1
                while den % p == 0:
                    den //= p
                    vp -= 1
                v = (p - 1) * vp + k
                best = v if best is None else min(best, v)
        return best

    for p in (3, 5, 7):
        # lambda_n = sum_{a + p b = n} pi^a/a! * (-pi)^b/b!
        theta = [Fraction(0)] * (p - 1)
        for n in range(TERMS + 1):
            for b in range(n // p + 1):
                a = n - p * b
                coeff = Fraction((-1) ** b, factorial(a) * factorial(b))
                term = [c * coeff for c in pi_power(a + b, p)]
                theta = [x + y for x, y in zip(theta, term)]
        minus_one = theta.copy()
        minus_one[0] -= 1
        v1 = valuation(minus_one, p)
        power = [Fraction(1)] + [Fraction(0)] * (p - 2)
        for _ in range(p):
            power = mul(power, theta, p)
        power[0] -= 1
        vp = valuation(power, p)
        record(f"7.p={p} Dwork: v_pi(theta(1) - 1) = 1, theta(1)^p = 1 to high order",
               v1 == 1 and vp is not None and vp >= 20,
               f"v_pi(theta(1)-1) = {v1}, v_pi(theta(1)^p - 1) = {vp} with {TERMS} terms")


# ---------------------------------------------------------------- check 8
def check_gamma_fourier() -> None:
    for s in (mp.mpf("0.7"), mp.mpf("2.3")):
        integral = 2 * mp.quad(lambda x: mp.exp(-mp.pi * x * x) * x ** (s - 1), [0, mp.inf])
        record(f"8a.s={s} Gamma_R(s) = int e^(-pi x^2) |x|^s d*x",
               close(integral, mp.pi ** (-s / 2) * mp.gamma(s / 2), mp.mpf(10) ** -20))
    f = lambda x: x * mp.exp(-mp.pi * x * x)  # noqa: E731  odd Hermite function
    xi = mp.mpf("0.6")
    fourier = mp.quad(lambda x: f(x) * mp.exp(-2j * mp.pi * x * xi), [-mp.inf, 0, mp.inf])
    record("8b  Fourier eigenvalue of x e^{-pi x^2} is -i", close(fourier, -1j * f(xi), mp.mpf(10) ** -20))
    record("8c  F^2 = -1 on odd functions (F^2 f(x) = f(-x) = -f(x))", close((-1j) ** 2 * f(xi), f(-xi)))


# ---------------------------------------------------------------- check 9
def check_cm_sato_tate() -> None:
    try:
        import cypari2
    except ImportError:
        record("9   CM Sato-Tate (needs cypari2)", False, "cypari2 not installed")
        return
    pari = cypari2.Pari()
    for label, ai in (("y^2 = x^3 - x", [0, 0, 0, -1, 0]), ("y^2 = x^3 + 1", [0, 0, 0, 0, 1])):
        e = pari.ellinit(ai)
        conductor = int(pari.ellglobalred(e)[0])
        zero = total = 0
        m2 = m4 = mp.mpf(0)
        for p in primes(100000):
            if conductor % p == 0:
                continue
            a = int(pari.ellap(e, p))
            t = mp.mpf(a) / mp.sqrt(p)
            total += 1
            zero += a == 0
            m2 += t ** 2
            m4 += t ** 4
        frac, m2, m4 = zero / total, m2 / total, m4 / total
        # CM law: mass 1/2 at 0 plus 1/2 of the arcsine law on [-2, 2]: E t^2 = 1, E t^4 = 3
        # (the SU(2) law would give E t^4 = 2).
        ok = abs(frac - 0.5) < 0.01 and abs(m2 - 1) < 0.05 and abs(m4 - 3) < 0.15
        record(f"9.{label} CM Sato-Tate law", ok,
               f"{total} good primes < 10^5: a_p = 0 for {frac:.4f}, E t^2 = {mp.nstr(m2, 4)}, "
               f"E t^4 = {mp.nstr(m4, 4)} (CM: 0.5, 1, 3; SU(2): 0, 1, 2)")


def main() -> int:
    for check in (check_euler, check_zeta_even, check_gauss_sums, check_weil_index,
                  check_landsberg_schaar, check_modular, check_root_numbers, check_dwork,
                  check_gamma_fourier, check_cm_sato_tate):
        check()
    passed = sum(ok for _, ok, _ in RESULTS)
    print(f"\n{passed} of {len(RESULTS)} checks pass.")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())

"""Alpha falls with both the number of points and the square of the dimension: alpha = 240 / (n * d^2), always with the ascending radius search. Since n balls are each tested against CSR, n*alpha is the expected number of balls that reject CSR by chance alone; this holds that count at 240/d^2 (d=2: 60, d=5: 9.6, d=10: 2.4, d=20: 0.6), so a larger n gets a smaller per-ball alpha. Uses n and d."""


def alpha_formula(n, d):
    return 240 / (n * d ** 2), "ascend"

"""Starting rule: choose the alpha whose clustering has the largest mean silhouette.

For each alpha on the grid, UN-CCD is run with the ascending radius search
(the paper's Algorithm 4), and the alpha whose clustering reaches the largest
mean silhouette is chosen; ties go to the smaller alpha. This uses nothing but
the unlabelled data: the silhouette is the same internal criterion UN-CCD
already uses to choose the number of clusters.
"""


def choose(X, kit, seed):
    best_alpha, best_value = kit.alphas[0], -2.0
    for alpha in kit.alphas:
        value = kit.cluster(alpha, "ascend")["silhouette"]
        if value > best_value:
            best_alpha, best_value = alpha, value
    return {"alpha": best_alpha, "direction": "ascend"}

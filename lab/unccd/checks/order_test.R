# Row-order check on seeds: are the UN-CCD radii the same whatever the row order?
# Written by the independent fact-checking session; run from the repository root:
#   Rscript lab/unccd/checks/order_test.R
suppressPackageStartupMessages({library(jsonlite); library(mclust); library(cluster)})
vendor <- normalizePath("lab/unccd/vendor/ccd")
setwd(vendor)
source(file.path(vendor, "methods/clustering/UN-CCDs.R"))
src <- readLines(file.path(dirname(dirname(vendor)), "r/unccd_job.R"))
# take helper definitions only (eval_filtered, read_table, load_real)
start <- grep("^eval_filtered <- function", src); stop_ <- grep("^if \\(job\\$kind == \"real\"\\)", src)[1]-1
eval(parse(text = src[start:stop_]))
env <- load_real()
mat <- as.matrix(get("seeds", envir = env)); X <- mat[, -ncol(mat)]; storage.mode(X) <- "double"; Y <- mat[, ncol(mat)]
simul <- read_table(file.path(dirname(dirname(vendor)), "work/null_tables/nn_null_d7.csv"), "95")
R0 <- nnccd.radi(X, "lower", "descend", 3, 0.95, simul=simul, 1000)$R
for (p in c(1001, 1002, 1003)) {
  set.seed(p); idx <- sample(nrow(X))
  Rp <- nnccd.radi(X[idx,], "lower", "descend", 3, 0.95, simul=simul, 1000)$R
  back <- numeric(nrow(X)); back[idx] <- Rp
  cat("perm", p, "radii identical:", isTRUE(all.equal(back, R0, tolerance=0)), " n differ:", sum(back != R0), " max abs diff:", max(abs(back-R0)), "\n")
  lab <- UNCCD_clustering(datax=X[idx,], simul=simul, method="descend")$label
  cat("   ARI", adjustedRandIndex(lab, Y[idx]), "k", length(unique(lab)), "\n")
}

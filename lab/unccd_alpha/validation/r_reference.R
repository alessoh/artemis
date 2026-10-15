# Reference outputs from the authors' R code for validating the Python port.
#
# Run from the repository root after lab/unccd/prepare_data.py has fetched the
# authors' code and lab/unccd/null_tables.py has built the null tables:
#   Rscript lab/unccd_alpha/validation/r_reference.R <out_dir>
#
# For each case it writes one JSON file with the data (17 significant digits),
# the null-table entries used, and the authors' outputs: radii, Int.D, Int.R,
# labels, si and si.ind from UNCCD_clustering().

suppressPackageStartupMessages({ library(jsonlite); library(MASS); library(cluster); library(igraph) })
args <- commandArgs(trailingOnly = TRUE)
dir.create(args[1], recursive = TRUE, showWarnings = FALSE)
out_dir <- normalizePath(args[1])
root <- normalizePath(".")
vendor <- file.path(root, "lab/unccd/vendor/ccd")
tables <- file.path(root, "lab/unccd/work/null_tables")
setwd(vendor)
source(file.path(vendor, "methods/clustering/UN-CCDs.R"))

src <- readLines(file.path(root, "lab/unccd/r/unccd_job.R"))
start <- grep("^eval_filtered <- function", src)
stop_ <- grep('^if \\(job\\$kind == "real"\\)', src)[1] - 1
eval(parse(text = src[start:stop_]))
s2 <- grep("^sim_data <- function", src); e2 <- grep('^if \\(job\\$kind == "sim"\\)', src) - 1
eval(parse(text = src[s2:e2]))

table_for <- function(d, level) read_table(file.path(tables, sprintf("nn_null_d%d.csv", d)), level)

write_case <- function(name, X, Y, d_table, level, method) {
  simul <- table_for(d_table, level)
  n <- nrow(X)
  t0 <- proc.time()[["elapsed"]]
  g <- nnccd_clustering_quantile(X, low.num = 3, quantile = "lower", method = method,
                                 dom.method = "greedy2", simul = simul, niter = 1000)
  res <- UNCCD_clustering(datax = X, simul = simul, method = method)
  secs <- proc.time()[["elapsed"]] - t0
  r <- nnccd.radi(X, "lower", method, 3, 0.9, simul = simul, 1000)$R
  out <- list(name = name, method = method, level = level, d_table = d_table,
              X = unname(as.matrix(X)), Y = as.numeric(Y),
              env_ave = simul$average[1:n], env_med = simul$median[1:n],
              radii = r, int_d = g$Int.D, int_r = g$Int.R,
              labels = as.integer(res$label), si = res$si, si_ind = res$si.ind, r_seconds = secs)
  write(toJSON(out, digits = I(17), auto_unbox = TRUE), file.path(out_dir, paste0(name, ".json")))
  cat(name, "n", n, "seconds", round(secs, 1), "\n")
}

env <- load_real()
real <- list(iris = c(4, "90", "ascend"), seeds = c(7, "95", "descend"), user_knowledge = c(5, "95", "ascend"),
             wholesale = c(6, "95", "ascend"), asymmetric = c(2, "80", "ascend"), R15 = c(2, "85", "ascend"))
for (nm in names(real)) {
  mat <- as.matrix(get(nm, envir = env)); X <- mat[, -ncol(mat), drop = FALSE]; storage.mode(X) <- "double"
  cfg <- real[[nm]]
  write_case(paste0("real_", nm, "_", cfg[2], "_", cfg[3]), X, mat[, ncol(mat)], as.integer(cfg[1]), cfg[2], cfg[3])
  write_case(paste0("real_", nm, "_99_ascend"), X, mat[, ncol(mat)], as.integer(cfg[1]), "99", "ascend")
}

cache <- file.path(root, "lab/unccd/work/simdata")
sims <- list(
  list("Uniform", 2, 50, 5, "85", "ascend", 1:15),
  list("Gaussian", 2, 50, 3, "85", "ascend", 1:15),
  list("Uniform", 5, 200, 5, "95", "ascend", 1:5),
  list("Uniform", 20, 200, 3, "999", "descend", 1:6),
  list("Gaussian", 10, 200, 3, "999", "descend", 1:4),
  list("Uniform", 10, 200, 3, "95", "ascend", 1:3)
)
for (s in sims) {
  script <- sprintf("simulations/clustering/UN_CCDs/Simulations/%s/%dd/%dd_235clusters_n%d.R", s[[1]], s[[2]], s[[2]], s[[3]])
  sd <- sim_data(script, cache)
  cell <- sd$cap[[as.character(s[[4]])]]
  lvl <- s[[5]]
  for (r in s[[7]]) {
    write_case(sprintf("sim_%s_%dd_n%d_k%d_rep%d_%s_%s", s[[1]], s[[2]], s[[3]], s[[4]], r, lvl, s[[6]]),
               cell$data[[r]], cell$label, s[[2]], lvl, s[[6]])
  }
}

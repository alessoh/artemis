# Artemis Project 1: run one UN-CCD reproduction job with the authors' own code.
#
# Called by harness.py as:  Rscript unccd_job.R <job.json> <out.json>
#
# The authors' functions are sourced from their repository (lab/unccd/vendor/ccd)
# without modification. Two things are supplied from outside:
#   * the Monte Carlo null table (mean and median NND quantiles), built by
#     null_tables.py and validated against the authors' generator, because
#     their tables for these dimensions are not in their repository;
#   * the data, rebuilt by evaluating the authors' own loader
#     (data/clustering/Real_Data_Collection.R) and simulation drivers with only
#     the steps that cannot run here removed (setwd to a folder that does not
#     exist, packages that are not needed for the objects used, the parallel
#     clustering calls, and the printing of results).
#
# Job fields (JSON):
#   kind        "real" or "sim"
#   vendor      path to the authors' repository
#   table_csv   null table for the data's dimension (columns ave_<lvl>, med_<lvl>)
#   level       quantile label used by the authors' drivers ("80","85","90","95","99","999")
#   direction   "ascend" or "descend"
#   fun         "UNCCD_clustering" (Algorithm 4 of the paper)
#   real:  dataset, perm (0 = original row order, else a seed for a row shuffle)
#   sim:   script (path relative to vendor), ncls (2, 3 or 5), reps (vector of
#          1-based repetition indices), cache (folder for generated data)

suppressPackageStartupMessages({
  library(jsonlite); library(MASS); library(cluster); library(igraph); library(mclust)
})

args <- commandArgs(trailingOnly = TRUE)
job <- fromJSON(args[1])
out_path <- args[2]
vendor <- normalizePath(job$vendor)
setwd(vendor)  # here::here() resolves to the authors' repository root

source(file.path(vendor, "methods/clustering/UN-CCDs.R"))

# ---- helpers -----------------------------------------------------------------

# Evaluate an R file expression by expression, skipping any expression whose
# source text matches one of the patterns in `skip`, and replacing expressions
# matching names(replace) with the given code.
eval_filtered <- function(path, env, skip = character(0), replace = list()) {
  exprs <- parse(path, keep.source = TRUE)
  srcs <- vapply(attr(exprs, "srcref"), function(s) paste(as.character(s), collapse = "\n"), "")
  for (i in seq_along(exprs)) {
    txt <- srcs[i]
    hit <- FALSE
    for (pat in names(replace)) {
      if (grepl(pat, txt, perl = TRUE)) {
        eval(parse(text = replace[[pat]]), envir = env)
        hit <- TRUE
        break
      }
    }
    if (hit) next
    if (length(skip) && any(vapply(skip, function(p) grepl(p, txt, perl = TRUE), TRUE))) next
    eval(exprs[[i]], envir = env)
  }
  invisible(env)
}

read_table <- function(path, level) {
  tab <- read.csv(path, check.names = FALSE)
  ave <- tab[[paste0("ave_", level)]]
  med <- tab[[paste0("med_", level)]]
  if (is.null(ave) || is.null(med)) stop("level ", level, " not in ", path)
  # A table shorter than the data leaves NA past its end; the ascending search
  # then stops with an error if, and only if, its decision depends on a missing entry.
  list(average = ave, median = med)
}

run_unccd <- function(X, simul, direction) {
  t0 <- proc.time()[["elapsed"]]
  res <- UNCCD_clustering(datax = X, simul = simul, method = direction)
  list(res = res, seconds = proc.time()[["elapsed"]] - t0)
}

safe_ari <- function(a, b) as.numeric(adjustedRandIndex(a, b))

digest_labels <- function(lab) {
  # a short, order-sensitive fingerprint of a label vector (for determinism checks)
  v <- as.integer(factor(lab, levels = unique(lab)))
  sprintf("%08x", sum((v * seq_along(v)) %% 2147483647) %% 4294967296)
}

# ---- real data -----------------------------------------------------------------

load_real <- function() {
  env <- new.env(parent = globalenv())
  # dplyr::distinct and readxl::read_excel are what the loader needs
  suppressPackageStartupMessages({ library(dplyr); library(readxl) })
  owd <- getwd()
  setwd(file.path(vendor, "data/clustering"))
  on.exit(setwd(owd))
  eval_filtered(file.path(vendor, "data/clustering/Real_Data_Collection.R"), env,
                skip = c("^library\\(R\\.matlab\\)", "^library\\(foreign\\)", "^setwd\\(", "^anyNA\\("))
  env
}

if (job$kind == "real") {
  env <- load_real()
  mat <- get(job$dataset, envir = env)
  mat <- as.matrix(mat)
  X <- mat[, -ncol(mat), drop = FALSE]
  Y <- mat[, ncol(mat)]
  storage.mode(X) <- "double"
  if (job$perm > 0) {
    set.seed(job$perm)
    idx <- sample(nrow(X))
    X <- X[idx, , drop = FALSE]
    Y <- Y[idx]
  }
  simul <- read_table(job$table_csv, job$level)
  out <- tryCatch({
    r <- run_unccd(X, simul, job$direction)
    lab <- r$res$label
    sil <- if (length(unique(lab)) > 1) mean(silhouette(lab, dist(X))[, 3]) else NA_real_
    list(status = "ok", ari = safe_ari(lab, Y), sil = sil, k = length(unique(lab)),
         si = r$res$si, si_ind = r$res$si.ind, n = nrow(X), d = ncol(X),
         seconds = r$seconds, label_hash = digest_labels(lab))
  }, error = function(e) list(status = "error", message = conditionMessage(e), n = nrow(X), d = ncol(X)))
  out$job <- job
  write(toJSON(out, auto_unbox = TRUE, digits = NA, null = "null", na = "null"), out_path)
  quit(save = "no")
}

# ---- baselines on the real data --------------------------------------------------
# Settings are those of the authors' scripts in
# simulations/clustering/Algo_Compare_Clustering/*/Simulation/Real_Data/.
# K-means++ there calls ClusterR::KMeans_rcpp (one start, 100 iterations), which
# is not installable here; kmeanspp() below does the same: k-means++ seeding,
# then Lloyd iterations from those centres.

DBSCAN_EPS <- c(iris = 0.8, seeds = 0.9, user_knowledge = 1.5, wholesale = 1,
                asymmetric = 0.15, R15 = 0.35, D31 = 0.6)
TRUE_K <- c(iris = 3, seeds = 3, user_knowledge = 4, wholesale = 3,
            asymmetric = 5, R15 = 15, D31 = 31)

kmeanspp <- function(X, k, iter.max = 100) {
  n <- nrow(X)
  centers <- matrix(NA_real_, k, ncol(X))
  centers[1, ] <- X[sample.int(n, 1), ]
  d2 <- rowSums((X - matrix(centers[1, ], n, ncol(X), byrow = TRUE))^2)
  for (j in 2:k) {
    i <- sample.int(n, 1, prob = d2)
    centers[j, ] <- X[i, ]
    d2 <- pmin(d2, rowSums((X - matrix(centers[j, ], n, ncol(X), byrow = TRUE))^2))
  }
  stats::kmeans(X, centers = centers, iter.max = iter.max, algorithm = "Lloyd")$cluster
}

if (job$kind == "baseline") {
  env <- load_real()
  mat <- as.matrix(get(job$dataset, envir = env))
  X <- mat[, -ncol(mat), drop = FALSE]; storage.mode(X) <- "double"
  Y <- mat[, ncol(mat)]
  set.seed(job$seed)
  t0 <- proc.time()[["elapsed"]]
  out <- tryCatch({
    k <- TRUE_K[[job$dataset]]
    lab <- switch(job$method,
      dbscan = {
        suppressPackageStartupMessages(library(dbscan))
        dbscan::dbscan(X, DBSCAN_EPS[[job$dataset]], minPts = 5)$cluster
      },
      kmeanspp = kmeanspp(X, k),
      spectral = {
        suppressPackageStartupMessages(library(kernlab))
        as.integer(kernlab::specc(as.matrix(dist(X)), centers = k)@.Data)
      },
      louvain = {
        S <- exp(-as.matrix(dist(X))^2 / (2 * 2^2))
        g <- igraph::graph_from_adjacency_matrix(S, mode = "undirected", weighted = TRUE)
        as.integer(igraph::membership(igraph::cluster_louvain(g)))
      },
      stop("unknown method ", job$method))
    sil <- if (length(unique(lab)) > 1) mean(silhouette(lab, dist(X))[, 3]) else NA_real_
    # the authors' DBSCAN script counts clusters excluding the noise label 0
    kk <- if (job$method == "dbscan") length(unique(lab)) - 1 else length(unique(lab))
    list(status = "ok", ari = safe_ari(lab, Y), sil = sil, k = kk,
         seconds = proc.time()[["elapsed"]] - t0, n = nrow(X), d = ncol(X))
  }, error = function(e) list(status = "error", message = conditionMessage(e)))
  out$job <- job
  write(toJSON(out, auto_unbox = TRUE, digits = NA, null = "null", na = "null"), out_path)
  quit(save = "no")
}

# ---- simulations ---------------------------------------------------------------

# Regenerate the authors' simulated datasets for one driver script, in the same
# random-number stream: set.seed(2024), then the 2-, 3- and 5-cluster lists in order.
sim_data <- function(script, cache) {
  dir.create(cache, recursive = TRUE, showWarnings = FALSE)
  key <- gsub("[^A-Za-z0-9]+", "_", script)
  f <- file.path(cache, paste0(key, ".rds"))
  if (file.exists(f)) return(readRDS(f))
  gen <- new.env(parent = globalenv())
  eval_filtered(file.path(vendor, "R/general_functions/Uni-Gau_cls.R"), gen,
                skip = c("^library\\(spatstat\\)", "^library\\(hypercube\\)"))
  env <- new.env(parent = gen)
  env$.cap <- list()
  eval_filtered(file.path(vendor, script), env,
    skip = c("^source\\(", "^setwd\\(", "^library\\(", "makeCluster", "registerDoParallel",
             "stopCluster", "clustering_result", "^print\\(", "^t1 *=", "^t2 *=", "Sys\\.time",
             "^cores *=", "save\\.image", "load_quantile_table", "\\bt[12]\\b"),
    replace = list("^clustering_result *= *foreach" =
                     ".cap[[as.character(N)]] <- list(data = data_list, label = label_T)"))
  res <- list(cap = env$.cap, n = env$n, d = env$d, method = env$method)
  tmp <- paste0(f, ".tmp", Sys.getpid())
  saveRDS(res, tmp)
  file.rename(tmp, f)
  res
}


if (job$kind == "sim") {
  sd <- sim_data(job$script, job$cache)
  cell <- sd$cap[[as.character(job$ncls)]]
  if (is.null(cell)) stop("no captured data for ", job$ncls, " clusters in ", job$script)
  simul <- read_table(job$table_csv, job$level)
  rows <- lapply(job$reps, function(r) {
    X <- cell$data[[r]]
    tryCatch({
      rr <- run_unccd(X, simul, job$direction)
      list(rep = r, status = "ok", ari = safe_ari(rr$res$label, cell$label),
           sil = rr$res$si, k = rr$res$si.ind, seconds = rr$seconds)
    }, error = function(e) list(rep = r, status = "error", message = conditionMessage(e)))
  })
  out <- list(job = job, n = sd$n, d = sd$d, script_method = sd$method, rows = rows)
  write(toJSON(out, auto_unbox = TRUE, digits = NA, null = "null", na = "null"), out_path)
}

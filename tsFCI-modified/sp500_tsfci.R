data <- read.csv("~/Desktop/AP_causal_discovery/data/Cleaned_S_P_500_Data.csv")
# result <- realData_tsfci(data=data, sig=0.05, nrep=4, inclIE=FALSE, alg="tscfci", datatype="continuous", makeplot=FALSE)

time_execution <- function(data, lags) {
  start_time <- Sys.time()
  total_rows <- nrow(data)
  result <- realData_tsfci(data=data, sig=0.05, nrep=lags+1, inclIE=FALSE, alg="tscfci", datatype="continuous", makeplot=FALSE)
  end_time <- Sys.time()
  # execution_time <- end_time - start_time
  execution_time <- as.numeric(difftime(end_time, start_time, units = "secs"))
  return(execution_time)
}

record_time <- function(data, n, lags) {
  # n: maximum number of stocks, n is larger than 10
  # execution time is recorded in seconds
  results_df <- data.frame(num_stocks = integer(), execution_time = numeric())
  
  for (i in 10:n) {
    data_subset <- data[, 1:i]
    execution_time <- time_execution(data_subset, lags)
    results_df <- rbind(results_df, data.frame(num_stocks = i, execution_time = execution_time))
  }
  
  write.csv(results_df, file = "execution_times.csv", row.names = FALSE)
}
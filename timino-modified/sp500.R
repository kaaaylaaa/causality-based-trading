# d <- timino_dag(cbind(x,y,w), alpha = 0.05, max_lag = 2, model = traints_linear, indtest = indtestts_crosscov, output = TRUE)

data <- read.csv("~/Desktop/AP_causal_discovery/data/Cleaned_S_P_500_Data.csv")

# result <- timino_dag(data, alpha = 0.05, max_lag = 3, model = traints_linear, indtest = indtestts_crosscov, output = TRUE)

time_execution <- function(data, lags) {
  start_time <- Sys.time()
  total_rows <- nrow(data)
  result <- timino_dag(data, alpha = 0.05, max_lag = lags, model = traints_linear, indtest = indtestts_crosscov, output = TRUE)
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
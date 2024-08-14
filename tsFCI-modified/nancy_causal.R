source('start_up.R')
start_up()

data <- read.csv("Cleaned_nancy_data.csv")
for (lags in 1:6){
  print(lags)
  result <- realData_tsfci(data=data, sig=0.05, nrep=lags+1, inclIE=FALSE, alg="tscfci", datatype="continuous", makeplot=FALSE)
  temporal_names = c()
  for (i in 0:lags){
    for (name in colnames(data)){
      temporal_names <- c(temporal_names, paste(name,i, sep = "_"))
    }
  }
  colnames(result) = temporal_names
  output_filename <- paste0("./nancy_results/nancy_window_graph_tsfci_lag_", lags, ".csv")
  write.table(result, output_filename, col.names = temporal_names, row.names = temporal_names, sep = ",")
}

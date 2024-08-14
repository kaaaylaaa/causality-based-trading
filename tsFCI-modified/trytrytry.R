folder_path <- "~/Desktop/IC/AP/tsFCI/data/returns/selected"
n_lags <- 5
file_list <- list.files(path = folder_path, full.names = TRUE)

for (file in file_list) {
  data <- read.csv(file)
  result <- realData_tsfci(data=data, sig=0.05, nrep=n_lags, inclIE=FALSE, alg="tscfci", datatype="continuous", makeplot=FALSE)
  
  temporal_names = c()
  for (i in 1:n_lags){
    for (name in colnames(data)){
      temporal_names <- c(temporal_names, paste(name,i-1, sep = "_"))
    }
  }
  colnames(result) = temporal_names
  
  file_base_name <- basename(file)
  file_number <- sub("timeseries(\\d+)\\.csv", "\\1", file_base_name)
  output_file <- paste0("./results/result_", file_number, ".csv")
  write.table(result, output_file, col.names = temporal_names, row.names = temporal_names, sep = ",")
}

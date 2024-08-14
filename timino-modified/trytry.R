# data = read.csv("data/returns/selected/timeseries2.csv")
# d <- timino_dag(data, alpha = 0.05, max_lag = 5, model = traints_linear, indtest = indtestts_crosscov, output = TRUE)




folder_path <- "~/Desktop/IC/AP/codeTimino/data/returns/selected"

file_list <- list.files(path = folder_path, full.names = TRUE)

for (file in file_list) {
  data <- read.csv(file)
  result <- timino_dag(data, alpha = 0.05, max_lag = 5, model = traints_linear, indtest = indtestts_crosscov, output = TRUE)
  
  result[is.na(result)] <- 3
  
  for (j1 in 1:nrow(result)){
    for (j2 in 1:nrow(result)){
      if (result[j1,j2] == 1){
        result[j1,j2] <- 2
        
      }
    }
  }
  
  for (j1 in 1:nrow(result)){
    for (j2 in 1:nrow(result)){
      if (result[j1,j2] == 2){
        if (result[j2,j1] == 0){
          result[j2,j1] <- 1
        }
      }
      if (j1 == j2){
        result[j1,j2] <- 1
      }
    }
  }
  
  for (j1 in 1:nrow(result)){
    for (j2 in 1:nrow(result)){
      if (result[j1,j2] == 3){
        result[j1,j2] <- 2
        result[j2,j1] <- 2
      }
    }
  }
  
  file_base_name <- basename(file)
  file_number <- sub("timeseries(\\d+)\\.csv", "\\1", file_base_name)
  output_file <- paste0("./results/result_", file_number, ".csv")
  write.csv(result, file=output_file, row.names = FALSE)
}



























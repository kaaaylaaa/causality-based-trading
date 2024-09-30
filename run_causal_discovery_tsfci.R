args <- commandArgs(trailingOnly = TRUE)

if (length(args) != 4) {
  stop("Exactly four arguments must be supplied: 
       <input_file> <lag> <output_directory> <market>", call.=FALSE)
}

input_file <- args[1]
lag <- as.integer(args[2])
output_directory <- args[3]
market <- args[4]

original_dir <- getwd()
setwd("tsFCI-modified")

# output_directory <- "./tsfci_window_graphs"
if (!dir.exists(output_directory)) {
  dir.create(output_directory, recursive = TRUE)
}

source('start_up.R')
start_up()

data <- read.csv(input_file)
result <- realData_tsfci(data=data, sig=0.05, nrep=lag+1, inclIE=FALSE, alg="tscfci", datatype="continuous", makeplot=FALSE)
temporal_names = c()
for (i in 0:lag){
  for (name in colnames(data)){
    temporal_names <- c(temporal_names, paste(name,i, sep = "_"))
  }
}
colnames(result) = temporal_names

output_filename <- paste0(output_directory, "/", market, "_window_graph_tsfci_lag_", lag, ".csv")
write.table(result, output_filename, col.names = temporal_names, row.names = temporal_names, sep = ",")
setwd(original_dir)
# Run TIMINO for Pelosi datasets
# By Ruijie Tang

source("causal_discovery_timino.R")

run_timino("./data/pelosi-80.csv", 1, "./causal_graphs/pelosi80_graph_timino_lag_1.txt")
run_timino("./data/pelosi-80.csv", 2, "./causal_graphs/pelosi80_graph_timino_lag_2.txt")
run_timino("./data/pelosi-80.csv", 3, "./causal_graphs/pelosi80_graph_timino_lag_3.txt")
run_timino("./data/pelosi-80.csv", 4, "./causal_graphs/pelosi80_graph_timino_lag_4.txt")
run_timino("./data/pelosi-80.csv", 5, "./causal_graphs/pelosi80_graph_timino_lag_5.txt")
run_timino("./data/pelosi-80.csv", 6, "./causal_graphs/pelosi80_graph_timino_lag_6.txt")

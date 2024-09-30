# # make predictions
# for market in sp500 latest_sp500; do
#     for alg in varlingam pcmci; do
#         for lag in {1..3}; do
#             python predict.py data/${market}_return_80.csv causal_graphs/${market}_graph_${alg}_lag_${lag}.txt ${lag} ${market} ${alg}
#         done
#     done
# done

# for alg in varlingam pcmci; do
#     for lag in {1..6}; do
#         python predict.py data/csi300_return_80.csv causal_graphs/csi300_graph_${alg}_lag_${lag}.txt ${lag} csi300 ${alg}
#     done
# done

# for alg in varlingam pcmci timino tsfci; do
#     for lag in {1..6}; do
#         python predict.py data/pelosi_return_80.csv causal_graphs/pelosi_graph_${alg}_lag_${lag}.txt ${lag} pelosi ${alg}
#     done
# done

# # backtest
# for market in sp500 latest_sp500; do
#     for alg in varlingam pcmci; do
#         for lag in {1..3}; do
#             python backtest.py data/${market}_return_80.csv predictions/${market}_predictions_${alg}_lag_${lag}.csv ${lag} ${market} ${alg} return
#         done
#     done
# done

# for alg in varlingam pcmci; do
#     for lag in {1..6}; do
#         python backtest.py data/csi300_return_80.csv predictions/csi300_predictions_${alg}_lag_${lag}.csv ${lag} csi300 ${alg} return
#     done
# done

# for alg in varlingam pcmci timino tsfci; do
#     for lag in {1..6}; do
#         python backtest.py data/pelosi_return_80.csv predictions/pelosi_predictions_${alg}_lag_${lag}.csv ${lag} pelosi ${alg} return
#     done
# done

# plot

# causal graph
# save top 10 stocks with the most causes/effects/connections



# cause/effect distribution



# backtest plot
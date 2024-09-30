# generate causal graphs
# for i in {1..3}
# do
#     python causal_discovery_varlingam.py data/sp500_return_80.csv $i sp500 varlingam
#     python causal_discovery_varlingam.py data/latest_sp500_return_80.csv $i latest_sp500 varlingam
#     python -W ignore::SyntaxWarning causal_discovery_pcmci.py data/sp500_return_80.csv $i sp500 pcmci
#     python -W ignore::SyntaxWarning causal_discovery_pcmci.py data/latest_sp500_return_80.csv $i latest_sp500 pcmci
# done

# for i in {1..6}
# do
#     python causal_discovery_varlingam.py data/pelosi_return_80.csv $i pelosi varlingam
#     python causal_discovery_varlingam.py data/csi300_return_80.csv $i csi300 varlingam
#     python -W ignore::SyntaxWarning causal_discovery_pcmci.py data/pelosi_return_80.csv $i pelosi pcmci
#     python -W ignore::SyntaxWarning causal_discovery_pcmci.py data/csi300_return_80.csv $i csi300 pcmci
# done

# for i in {1..6}
# do
#     echo "Running pelosi lag $i timino"
#     output_file="./causal_graphs/pelosi_graph_timino_lag_${i}.txt"
#     Rscript run_causal_discovery_timino.R "./data/pelosi_return_80.csv" $i "$output_file"
# done

# for i in {1..6}
# do
#     echo "Running pelosi lag $i tsfci"
#     Rscript run_causal_discovery_tsfci.R "../data/pelosi_return_80.csv" $i "../tsfci_window_graphs" pelosi
#     python compress_tsfci_graph.py  tsfci_window_graphs/pelosi_window_graph_tsfci_lag_${i}.csv $i data/pelosi_return_80.csv pelosi
# done

# make predictions
for market in sp500 latest_sp500; do
    for alg in varlingam pcmci; do
        for lag in {1..3}; do
            python predict.py data/${market}_return_80.csv causal_graphs/${market}_graph_${alg}_lag_${lag}.txt ${lag} ${market} ${alg}
        done
    done
done

for alg in varlingam pcmci; do
    for lag in {1..6}; do
        python predict.py data/csi300_return_80.csv causal_graphs/csi300_graph_${alg}_lag_${lag}.txt ${lag} csi300 ${alg}
    done
done

for alg in varlingam pcmci timino tsfci; do
    for lag in {1..6}; do
        python predict.py data/pelosi_return_80.csv causal_graphs/pelosi_graph_${alg}_lag_${lag}.txt ${lag} pelosi ${alg}
    done
done

# backtest
for market in sp500 latest_sp500; do
    for alg in varlingam pcmci; do
        for lag in {1..3}; do
            python backtest.py data/${market}_return_80.csv predictions/${market}_predictions_${alg}_lag_${lag}.csv ${lag} ${market} ${alg} return
        done
    done
done

for alg in varlingam pcmci; do
    for lag in {1..6}; do
        python backtest.py data/csi300_return_80.csv predictions/csi300_predictions_${alg}_lag_${lag}.csv ${lag} csi300 ${alg} return
    done
done

for alg in varlingam pcmci timino tsfci; do
    for lag in {1..6}; do
        python backtest.py data/pelosi_return_80.csv predictions/pelosi_predictions_${alg}_lag_${lag}.csv ${lag} pelosi ${alg} return
    done
done

# plot

# causal graph
# save top 10 stocks with most causes/effects/connections
python draw_causal_graph.py causal_graphs/latest_sp500_summary_matrix_varlingam_lag_1.csv data/latest_sp500_return_80.csv 99.9 varlingam latest_sp500 1

# cause/effect distribution
python draw_cause_effect_distribution.py causal_graphs/latest_sp500_summary_matrix_varlingam_lag_1.csv 95 varlingam latest_sp500 1 5 10
python draw_cause_effect_distribution.py causal_graphs/latest_sp500_summary_matrix_varlingam_lag_1.csv 99 varlingam latest_sp500 1 2 5
python draw_cause_effect_distribution.py causal_graphs/latest_sp500_summary_matrix_varlingam_lag_1.csv 99.9 varlingam latest_sp500 1 1 1

# backtest plot
for market in sp500 latest_sp500; do
    for alg in varlingam pcmci; do
        for lag in {1..3}; do
            python draw_backtest_returns.py predictions/${market}_predictions_${alg}_lag_${lag}.csv backtesting/${market}_backtest_returns_${alg}_lag_${lag}.csv data/${market}_date.csv ${alg} ${market} ${lag} ^GSPC
        done
    done
done

for alg in varlingam pcmci; do
    for lag in {1..6}; do
        python draw_backtest_returns.py predictions/csi300_predictions_${alg}_lag_${lag}.csv backtesting/csi300_backtest_returns_${alg}_lag_${lag}.csv data/csi300_date.csv ${alg} csi300 ${lag} 000300.SS
    done
done

for alg in varlingam pcmci timino tsfci; do
    for lag in {1..6}; do
        python draw_backtest_returns.py predictions/pelosi_predictions_${alg}_lag_${lag}.csv backtesting/pelosi_backtest_returns_${alg}_lag_${lag}.csv data/pelosi_date.csv ${alg} pelosi ${lag} NANC
    done
done
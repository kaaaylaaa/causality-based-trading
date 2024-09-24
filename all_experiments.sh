for i in {1..3}
do
    python causal_discovery_varlingam.py data/sp500_return_80.csv $i sp500_return varlingam
    python causal_discovery_varlingam.py data/latest_sp500_return_80.csv $i latest_sp500_return varlingam
done
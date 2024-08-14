import networkx as nx

class GraphComparison:
    def __init__(self, ghat, oghat):
        self.ghat = ghat
        self.oghat = oghat

    def _process_graph(self, gtrue, method, operation):
        methods = {
            "all_oriented": lambda: (gtrue, self.ghat),
            "all_adjacent": lambda: (gtrue.to_undirected(), self.ghat.to_undirected()),
            "other_oriented": lambda: (gtrue, self.oghat),
            "other_adjacent": lambda: (gtrue.to_undirected(), self.oghat.to_undirected())
        }

        if method not in methods:
            raise AttributeError(f"Unknown method: {method}")

        g1, g2 = methods[method]()

        if operation == 'intersection':
            return nx.intersection(g1, g2)
        elif operation == 'difference_g2_g1':
            return nx.difference(g2, g1)
        elif operation == 'difference_g1_g2':
            return nx.difference(g1, g2)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def _tp(self, gtrue, method="all_oriented"):
        tp = self._process_graph(gtrue, method, 'intersection')
        return len(tp.edges)

    def _fp(self, gtrue, method="all_oriented"):
        fp = self._process_graph(gtrue, method, 'difference_g2_g1')
        return len(fp.edges)

    def _fn(self, gtrue, method="all_oriented"):
        fn = self._process_graph(gtrue, method, 'difference_g1_g2')
        return len(fn.edges)
    
    def _false_positive_rate(self, gtrue, method="all_oriented"):
        true_pos = self._tp(gtrue, method)
        false_pos = self._fp(gtrue, method)
        if false_pos == 0:
            return 0
        else:
            return false_pos / (true_pos + false_pos)

    def _precision(self, gtrue, method="all_oriented"):
        true_pos = self._tp(gtrue, method)
        false_pos = self._fp(gtrue, method)
        if true_pos == 0:
            return 0
        else:
            return true_pos / (true_pos + false_pos)

    def _recall(self, gtrue, method="all_oriented"):
        true_pos = self._tp(gtrue, method)
        false_neg = self._fn(gtrue, method)
        if true_pos == 0:
            return 0
        else:
            return true_pos / (true_pos + false_neg)

    def _f1(self, gtrue, method="all_oriented"):
        p = self._precision(gtrue, method)
        r = self._recall(gtrue, method)
        if (p == 0) and (r == 0):
            return 0
        else:
            return 2 * p * r / (p + r)
import numpy as np

from sklearn.base import BaseEstimator


class DecisionTree(BaseEstimator):

    def __init__(self, max_depth=np.inf, min_samples_split=2,
                 criterion='gini', debug=False):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.criterion = criterion
        self.criterions = {'gini': self._gini,
                           'entropy': self._entropy,
                           'variance': self._variance,
                           'mad_median': self._mad_median}
        self.type_task = 'class' if criterion == 'gini' or criterion == 'entropy' else 'reg'
        self.fun = self.criterions[self.criterion]
        self.uniq = None
        self.debug = debug
        self.tree = {}

    def fit(self, X, y):
        self.uniq = np.sort(np.unique(y))
        self.create_tree(X, y, self.tree, 0)
        return self

    def create_tree(self, X, y, link, depth):
        y_shape = y.shape[0]
        count_feature = X.shape[1]
        s0 = self.fun(y)
        if s0 == 0 or y_shape <= self.min_samples_split or depth == self.max_depth:
            if self.type_task == 'class':
                link['class'] = [round(np.int8(y == u).mean(), 3) for u in self.uniq]
            else:
                link['reg'] = y.mean()
        else:
            max_delta_s = 0
            max_feature = None
            max_num_feature = -1
            k = 0
            while k < count_feature:
                X = np.hstack((X, y.reshape((y_shape, 1))))
                X = np.array(sorted(X, key=lambda obj: obj[k]))
                X, y = X[:, :-1], X[:, -1]
                uniq_x = np.unique(X[:, k])
                for num_value, value in enumerate(uniq_x):
                    if y[num_value] == y[num_value - 1] or num_value == 0 or num_value == y_shape-1:
                        continue
                    s = self.Q(X, y, y_shape, k, value)
                    if s is not None:
                        delta_s = s0 - s
                        if delta_s >= max_delta_s:
                            max_feature = value
                            max_num_feature = k
                            max_delta_s = delta_s
                k += 1
            link[(max_num_feature, max_feature)] = [{}, {}]
            self.create_tree(X[X[:, max_num_feature] < max_feature],
                             y[X[:, max_num_feature] < max_feature],
                             link[(max_num_feature, max_feature)][0], depth + 1)
            self.create_tree(X[X[:, max_num_feature] >= max_feature],
                             y[X[:, max_num_feature] >= max_feature],
                             link[(max_num_feature, max_feature)][1], depth + 1)

    def Q(self, X, y, y_shape, i, t):
        left = y[X[:, i] < t]
        right = y[X[:, i] >= t]
        if left.size and right.size:
            return left.shape[0] * self.fun(left) / y_shape + \
                   right.shape[0] * self.fun(right) / y_shape
        return None

    def predict(self, X):
        answer = []
        for x in X:
            link = self.tree
            key = list(link.keys())[0]
            while key != self.type_task:
                enum, feature = key
                if x[enum] < feature:
                    link = link[key][0]
                else:
                    link = link[key][1]
                key = list(link.keys())[0]
            if self.type_task == 'class':
                answer.append(self.uniq[link['class'].index(max(link['class']))])
            else:
                answer.append(link['reg'])
        return np.array(answer)

    def predict_proba(self, X):
        answer = []
        for x in X:
            link = self.tree
            key = list(link.keys())[0]
            while key != self.type_task:
                enum, feature = key
                if x[enum] < feature:
                    link = link[key][0]
                else:
                    link = link[key][1]
                key = list(link.keys())[0]
            answer.append(link[self.type_task])
        return np.array(answer)

    def _entropy(self, y):
        s = 0
        for u in np.unique(y):
            p_i = np.int8(y == u).mean()
            s += p_i * np.log2(p_i)
        return -s

    def _gini(self, y):
        s = 0
        for u in np.unique(y):
            p_i = np.int8(y == u).mean()
            s += p_i ** 2
        return 1 - s

    @staticmethod
    def _variance(y):
        return np.var(y)

    @staticmethod
    def _mad_median(y):
        return np.mean(np.abs(y - np.median(y)))

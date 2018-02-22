import numpy as np
from matplotlib import pyplot as plt

from sklearn.base import BaseEstimator
from sklearn.datasets import make_classification, make_regression, load_digits, load_boston
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, mean_squared_error


class DecisionTree(BaseEstimator):

    def __init__(self, max_depth=np.inf, min_samples_split=2,
                 criterion='gini', debug=False):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.criterion = criterion
        self.criterions = {'gini': self._gini,
                           'entropy': self._entropy,
                           'var': self._variance,
                           'mad_median': self._mad_median}
        self.fun = self.criterions[self.criterion]
        self.uniq = None
        self.debug = debug
        self.tree = {}

    def fit(self, X, y):
        self.uniq = np.unique(y)
        self.create_tree(X, y, self.tree)

    def create_tree(self, X, y, link):

        print(X.shape, y.shape)
        s0 = self.fun(y)
        if s0 == 0 or y.size <= self.min_samples_split:
            if self.criterion == 'gini' or self.criterion == 'entropy':
                link['class'] = round(y.mean())
            else:
                link['class'] = y.mean()
        else:
            max_delta_s = 0
            max_feature = None
            max_num_feature = -1
            y_shape = y.shape[0]
            for x_num, x in enumerate(X):
                if y[x_num] == y[x_num - 1]:
                    continue
                for num_feature, feature in enumerate(x):
                    if num_feature == 0 or num_feature == (X.shape[1] - 1):
                        continue
                    s = self.Q(X, y, y_shape, num_feature, feature)
                    if s is not None:
                        delta_s = s0 - s
                        if delta_s > max_delta_s:
                            max_feature = feature
                            max_num_feature = num_feature
                            max_delta_s = delta_s
            link[(max_num_feature, max_feature)] = [{}, {}]
            self.create_tree(X[X[:, max_num_feature] < max_feature],
                             y[X[:, max_num_feature] < max_feature],
                             link[(max_num_feature, max_feature)][0])
            self.create_tree(X[X[:, max_num_feature] >= max_feature],
                             y[X[:, max_num_feature] >= max_feature],
                             link[(max_num_feature, max_feature)][1])

    def Q(self, X, y, y_shape, i, t):
        left = y[X[:, i] < t]
        right = y[X[:, i] >= t]
        if left.size and right.size:
            return left.shape[0] * self.fun(left) / y_shape + \
                   right.shape[0] * self.fun(right) / y_shape
        return None

    def predict(self, X):
        answer = []
        link = self.tree
        for x in X:
            key = link.keys()
            while key != 'class':
                enum, feature = key
                if x[enum] < feature:
                    link = link[0]
                else:
                    link = link[1]
                key = link.keys()
            answer.append(link['key'])
        return answer

    def predict_proba(self, X):
        pass

    def _entropy(self, y):
        s = 0
        for u in self.uniq:
            p_i = np.int8(y == u).mean()
            s += p_i * np.log(p_i, 2)
        return -s

    def _gini(self, y):
        s = 0
        for u in self.uniq:
            p_i = np.int8(y == u).mean()
            s += p_i ** 2
        return 1 - s

    @staticmethod
    def _variance(y):
        return np.std(y) ** 2

    @staticmethod
    def _mad_median(y):
        return np.sum(np.abs(y - np.median(y))) / y.size


tree = DecisionTree(criterion='gini')
X, y = load_digits(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=17)

tree.fit(X_train, y_train)
print(tree.tree)
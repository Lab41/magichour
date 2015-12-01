import numpy as np
from sklearn import svm
from sklearn.datasets import fetch_20newsgroups
from sklearn.svm import libsvm
import sys
from time import time
from functools import wraps

# Available from Github: https://github.com/timshenkao/StringKernelSVM
LIBSVM_IMPL = ['c_svc', 'nu_svc', 'one_class', 'epsilon_svr', 'nu_svr']


def caching():
    """
    Cache decorator. Arguments to the cached function must be hashable.
    """
    def decorate_func(func):
        cache = dict()
        # separating positional and keyword args
        kwarg_point = object()

        @wraps(func)
        def cache_value(*args, **kwargs):
            key = args
            if kwargs:
                key += (kwarg_point,) + tuple(sorted(kwargs.items()))
            if key in cache:
                result = cache[key]
            else:
                result = func(*args, **kwargs)
                cache[key] = result
            return result

        def cache_clear():
            """
            Clear the cache
            """
            cache.clear()

        # Clear the cache
        cache_value.cache_clear = cache_clear
        return cache_value
    return decorate_func


class StringKernelSVM(svm.SVC):
    """
    Implementation of string kernel from article:
    H. Lodhi, C. Saunders, J. Shawe-Taylor, N. Cristianini, and C. Watkins.
    Text classification using string kernels. Journal of Machine Learning Research, 2, 2002 .
    svm.SVC is a basic class from scikit-learn for SVM classification (in multiclass case, it uses one-vs-one approach)
    """
    def __init__(self, subseq_length=3, lambda_decay=0.5):
        """
        Constructor
        :param lambda_decay: lambda parameter for the algorithm
        :type  lambda_decay: float
        :param subseq_length: maximal subsequence length
        :type subseq_length: int
        """
        self.lambda_decay = lambda_decay
        self.subseq_length = subseq_length
        svm.SVC.__init__(self, kernel='precomputed')


    @caching()
    def _K(self, n, s, t):
        """
        K_n(s,t) in the original article; recursive function
        :param n: length of subsequence
        :type n: int
        :param s: document #1
        :type s: str
        :param t: document #2
        :type t: str
        :return: float value for similarity between s and t
        """
        if min(len(s), len(t)) < n:
            return 0
        else:
            part_sum = 0
            for j in range(1, len(t)):
                if t[j] == s[-1]:
                    #not t[:j-1] as in the article but t[:j] because of Python slicing rules!!!
                    part_sum += self._K1(n - 1, s[:-1], t[:j])
            result = self._K(n, s[:-1], t) + self.lambda_decay ** 2 * part_sum
            return result


    @caching()
    def _K1(self, n, s, t):
        """
        K'_n(s,t) in the original article; auxiliary intermediate function; recursive function
        :param n: length of subsequence
        :type n: int
        :param s: document #1
        :type s: str
        :param t: document #2
        :type t: str
        :return: intermediate float value
        """
        if n == 0:
            return 1
        elif min(len(s), len(t)) < n:
            return 0
        else:
            result = self._K2(n, s, t) + self.lambda_decay * self._K1(n, s[:-1], t)
            return result


    @caching()
    def _K2(self, n, s, t):
        """
        K''_n(s,t) in the original article; auxiliary intermediate function; recursive function
        :param n: length of subsequence
        :type n: int
        :param s: document #1
        :type s: str
        :param t: document #2
        :type t: str
        :return: intermediate float value
        """
        if n == 0:
            return 1
        elif min(len(s), len(t)) < n:
            return 0
        else:
            if s[-1] == t[-1]:
                return self.lambda_decay * (self._K2(n, s, t[:-1]) +
                                            self.lambda_decay * self._K1(n - 1, s[:-1], t[:-1]))
            else:
                return self.lambda_decay * self._K2(n, s, t[:-1])


    def _gram_matrix_element(self, s, t, sdkvalue1, sdkvalue2):
        """
        Helper function
        :param s: document #1
        :type s: str
        :param t: document #2
        :type t: str
        :param sdkvalue1: K(s,s) from the article
        :type sdkvalue1: float
        :param sdkvalue2: K(t,t) from the article
        :type sdkvalue2: float
        :return: value for the (i, j) element from Gram matrix
        """
        if s == t:
            return 1
        else:
            try:
                return self._K(self.subseq_length, s, t) / \
                       (sdkvalue1 * sdkvalue2) ** 0.5
            except ZeroDivisionError:
                print("Maximal subsequence length is less or equal to documents' minimal length."
                      "You should decrease it")
                sys.exit(2)


    def string_kernel(self, X1, X2):
        """
        String Kernel computation
        :param X1: list of documents (m rows, 1 column); each row is a single document (string)
        :type X1: list
        :param X2: list of documents (m rows, 1 column); each row is a single document (string)
        :type X2: list
        :return: Gram matrix for the given parameters
        """
        len_X1 = len(X1)
        len_X2 = len(X2)
        # numpy array of Gram matrix
        gram_matrix = np.zeros((len_X1, len_X2), dtype=np.float32)
        sim_docs_kernel_value = {}
        #when lists of documents are identical
        if X1 == X2:
        #store K(s,s) values in dictionary to avoid recalculations
            for i in range(len_X1):
                sim_docs_kernel_value[i] = self._K(self.subseq_length, X1[i], X1[i])
        #calculate Gram matrix
            for i in range(len_X1):
                for j in range(i, len_X2):
                    gram_matrix[i, j] = self._gram_matrix_element(X1[i], X2[j], sim_docs_kernel_value[i],
                                                                 sim_docs_kernel_value[j])
        #using symmetry
                    gram_matrix[j, i] = gram_matrix[i, j]
        #when lists of documents are not identical but of the same length
        elif len_X1 == len_X2:
            sim_docs_kernel_value[1] = {}
            sim_docs_kernel_value[2] = {}
        #store K(s,s) values in dictionary to avoid recalculations
            for i in range(len_X1):
                sim_docs_kernel_value[1][i] = self._K(self.subseq_length, X1[i], X1[i])
            for i in range(len_X2):
                sim_docs_kernel_value[2][i] = self._K(self.subseq_length, X2[i], X2[i])
        #calculate Gram matrix
            for i in range(len_X1):
                for j in range(i, len_X2):
                    gram_matrix[i, j] = self._gram_matrix_element(X1[i], X2[j], sim_docs_kernel_value[1][i],
                                                                 sim_docs_kernel_value[2][j])
        #using symmetry
                    gram_matrix[j, i] = gram_matrix[i, j]
        #when lists of documents are neither identical nor of the same length
        else:
            sim_docs_kernel_value[1] = {}
            sim_docs_kernel_value[2] = {}
            min_dimens = min(len_X1, len_X2)
        #store K(s,s) values in dictionary to avoid recalculations
            for i in range(len_X1):
                sim_docs_kernel_value[1][i] = self._K(self.subseq_length, X1[i], X1[i])
            for i in range(len_X2):
                sim_docs_kernel_value[2][i] = self._K(self.subseq_length, X2[i], X2[i])
        #calculate Gram matrix for square part of rectangle matrix
            for i in range(min_dimens):
                for j in range(i, min_dimens):
                    gram_matrix[i, j] = self._gram_matrix_element(X1[i], X2[j], sim_docs_kernel_value[1][i],
                                                                 sim_docs_kernel_value[2][j])
                    #using symmetry
                    gram_matrix[j, i] = gram_matrix[i, j]

        #if more rows than columns
            if len_X1 > len_X2:
                for i in range(min_dimens, len_X1):
                    for j in range(len_X2):
                        gram_matrix[i, j] = self._gram_matrix_element(X1[i], X2[j], sim_docs_kernel_value[1][i],
                                                                     sim_docs_kernel_value[2][j])
        #if more columns than rows
            else:
                for i in range(len_X1):
                    for j in range(min_dimens, len_X2):
                        gram_matrix[i, j] = self._gram_matrix_element(X1[i], X2[j], sim_docs_kernel_value[1][i],
                                                                     sim_docs_kernel_value[2][j])
        print sim_docs_kernel_value
        return gram_matrix


    def fit(self, X, Y):
        gram_matr = self.string_kernel(X, X)
        self.__X = X
        super(svm.SVC, self).fit(gram_matr, Y)


    def predict(self, X):
        svm_type = LIBSVM_IMPL.index(self.impl)
        if not self.__X:
            print('You should train the model first!!!')
            sys.exit(3)
        else:
            gram_matr_predict_new = self.string_kernel(X, self.__X)
            gram_matr_predict_new = np.asarray(gram_matr_predict_new, dtype=np.float64, order='C')
            return libsvm.predict(
                gram_matr_predict_new, self.support_, self.support_vectors_, self.n_support_,
                self.dual_coef_, self._intercept_,
                self._label, self.probA_, self.probB_,
                svm_type=svm_type,
                kernel=self.kernel, C=self.C, nu=self.nu,
                probability=self.probability, degree=self.degree,
                shrinking=self.shrinking, tol=self.tol, cache_size=self.cache_size,
                coef0=self.coef0, gamma=self._gamma, epsilon=self.epsilon)


if __name__ == '__main__':
    cur_f = __file__.split('/')[-1]
    if len(sys.argv) != 3:
        print >> sys.stderr, 'usage: ' + cur_f + ' <maximal subsequence length> <lambda (decay)>'
        sys.exit(1)
    else:
        subseq_length = int(sys.argv[1])
        lambda_decay = float(sys.argv[2])
    #The dataset is the 20 newsgroups dataset. It will be automatically downloaded, then cached.
        t_start = time()
        news = fetch_20newsgroups(subset='train')
        X_train = news.data[:10]
        Y_train = news.target[:10]
        print('Data fetched in %.3f seconds' % (time() - t_start))

        clf = StringKernelSVM(subseq_length=subseq_length, lambda_decay=lambda_decay)
        t_start = time()
        clf.fit(X_train, Y_train)
        print('Model trained in %.3f seconds' % (time() - t_start))

        t_start = time()
        result = clf.predict(news.data[10:14])
        print('New data predicted in %.3f seconds' % (time() - t_start))
        print result

"""General tests for all estimators."""
import copy
import importlib
import inspect

import pytest

from creme import base
from creme import dummy
from creme import compat
from creme import cluster
from creme import compose
from creme import ensemble
from creme import feature_extraction
from creme import feature_selection
from creme import imblearn
from creme import impute
from creme import linear_model
from creme import meta
from creme import multiclass
from creme import multioutput
from creme import naive_bayes
from creme import preprocessing
from creme import reco
from creme import stats
from creme import time_series
from creme import tree
from creme import utils
from creme.compat.sklearn import Creme2SKLBase
from creme.compat.sklearn import SKL2CremeBase


def get_all_estimators():

    ignored = (
        Creme2SKLBase,
        SKL2CremeBase,
        compat.PyTorch2CremeRegressor,
        compose.FuncTransformer,
        compose.Pipeline,
        ensemble.StackingBinaryClassifier,
        feature_extraction.Agg,
        feature_extraction.TargetAgg,
        feature_extraction.Differ,
        feature_selection.PoissonInclusion,
        imblearn.RandomOverSampler,
        imblearn.RandomUnderSampler,
        imblearn.RandomSampler,
        impute.PreviousImputer,
        impute.StatImputer,
        linear_model.FFMClassifier,
        linear_model.FFMRegressor,
        linear_model.FMClassifier,
        linear_model.FMRegressor,
        linear_model.HOFMClassifier,
        linear_model.HOFMRegressor,
        linear_model.SoftmaxRegression,
        meta.PredClipper,
        meta.TransformedTargetRegressor,
        multioutput.ClassifierChain,
        multioutput.RegressorChain,
        preprocessing.OneHotEncoder,
        reco.Baseline,
        reco.BiasedMF,
        reco.FunkMF,
        reco.RandomNormal,
        time_series.Detrender,
        time_series.GroupDetrender,
        time_series.SNARIMAX
    )

    def is_estimator(obj):
        return inspect.isclass(obj) and issubclass(obj, base.Estimator)

    for submodule in importlib.import_module('creme').__all__:

        if submodule == 'base':
            continue

        for _, obj in inspect.getmembers(importlib.import_module(f'creme.{submodule}'), is_estimator):

            if issubclass(obj, ignored):
                continue

            elif issubclass(obj, dummy.StatisticRegressor):
                inst = obj(statistic=stats.Mean())

            elif issubclass(obj, meta.BoxCoxRegressor):
                inst = obj(regressor=linear_model.LinearRegression())

            elif issubclass(obj, tree.RandomForestClassifier):
                inst = obj()

            elif issubclass(obj, ensemble.BaggingClassifier):
                inst = obj(linear_model.LogisticRegression())

            elif issubclass(obj, ensemble.BaggingRegressor):
                inst = obj(linear_model.LinearRegression())

            elif issubclass(obj, ensemble.AdaBoostClassifier):
                inst = obj(linear_model.LogisticRegression())

            elif issubclass(obj, ensemble.HedgeRegressor):
                inst = obj([
                    preprocessing.StandardScaler() | linear_model.LinearRegression(intercept_lr=.1),
                    preprocessing.StandardScaler() | linear_model.PARegressor(),
                ])

            elif issubclass(obj, feature_selection.SelectKBest):
                inst = obj(similarity=stats.PearsonCorrelation())

            elif issubclass(obj, linear_model.LinearRegression):
                inst = preprocessing.StandardScaler() | obj(intercept_lr=.1)

            elif issubclass(obj, linear_model.PARegressor):
                inst = preprocessing.StandardScaler() | obj()

            elif issubclass(obj, multiclass.OneVsRestClassifier):
                inst = obj(binary_classifier=linear_model.LogisticRegression())

            else:
                inst = obj()

            yield inst


@pytest.mark.parametrize('estimator, check', [
    pytest.param(
        copy.deepcopy(estimator),
        check,
        id=f'{estimator}:{check.__name__}'
    )
    for estimator in list(get_all_estimators()) + [
        feature_extraction.TFIDF(),
        linear_model.LogisticRegression(),
        preprocessing.StandardScaler() | linear_model.LinearRegression(),
        preprocessing.StandardScaler() | linear_model.PAClassifier(),
        preprocessing.StandardScaler() | multiclass.OneVsRestClassifier(linear_model.LogisticRegression()),
        preprocessing.StandardScaler() | multiclass.OneVsRestClassifier(linear_model.PAClassifier()),
        naive_bayes.GaussianNB(),
        preprocessing.StandardScaler(),
        cluster.KMeans(n_clusters=5, seed=42),
        preprocessing.MinMaxScaler(),
        preprocessing.MinMaxScaler() + preprocessing.StandardScaler(),
        preprocessing.PolynomialExtender(),
        feature_selection.VarianceThreshold(),
        feature_selection.SelectKBest(similarity=stats.PearsonCorrelation())
    ]
    for check in utils.estimator_checks.yield_checks(estimator)
])
def test_check_estimator(estimator, check):
    check(estimator)

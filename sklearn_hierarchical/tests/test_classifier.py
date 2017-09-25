"""
Unit-tests for the classifier interface.

"""
from hamcrest import (
    assert_that,
    calling,
    close_to,
    contains_inanyorder,
    equal_to,
    has_entries,
    has_item,
    is_,
    raises,
)
from networkx import DiGraph
from sklearn import svm
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.utils.estimator_checks import check_estimator

from sklearn_hierarchical.classifier import HierarchicalClassifier
from sklearn_hierarchical.constants import ROOT
from sklearn_hierarchical.tests.fixtures import make_classifier, make_classifier_and_data, make_digits_dataset
from sklearn_hierarchical.tests.matchers import matches_graph


RANDOM_STATE = 42


def test_estimator_inteface():
    """Run the scikit-learn estimator compatability test suite."""
    check_estimator(HierarchicalClassifier())


def test_parameter_validation():
    """Test parameter validation checks for consistent assignment."""
    test_cases = [
        dict(
            prediction_depth="nmlnp",
            stopping_criteria=None,
        ),
        dict(
            prediction_depth="nmlnp",
            stopping_criteria="not_a_float_or_a_callable",
        ),
        dict(
            prediction_depth="mlnp",
            stopping_criteria=123.4,
        ),
        dict(
            prediction_depth="some_invalid_prediction_depth_value",
        ),
        dict(
            algorithm="lcn",
            training_strategy=None,
        ),
        dict(
            algorithm="lcn",
            training_strategy="some_invalid_training_strategy",
        ),
        dict(
            algorithm="lcpn",
            training_strategy="exclusive",
        ),
        dict(
            algorithm="some_invalid_algorithm_value",
        ),
    ]

    for classifier_kwargs in test_cases:
        clf, (X, y) = make_classifier_and_data(**classifier_kwargs)
        assert_that(calling(clf.fit).with_args(X=X, y=y), raises(TypeError))


def test_fitted_attributes():
    """Test classifier attributes are set correctly after fitting."""
    n_classes = 10
    clf, (X, y) = make_classifier_and_data(n_classes=n_classes)

    clf.fit(X, y)

    assert_that(DiGraph(clf.class_hierarchy_), matches_graph(DiGraph(clf.class_hierarchy)))
    assert_that(clf.graph_, matches_graph(DiGraph(clf.class_hierarchy)))
    assert_that(clf.classes_, contains_inanyorder(*range(n_classes)))
    assert_that(clf.n_classes_, is_(equal_to(n_classes)))
    assert_that(
        clf.graph_.nodes[ROOT],
        has_entries(
            metafeatures=has_entries(
                num_samples=X.shape[0],
                num_targets=n_classes,
            ),
        ),
    )


def test_trivial_hierarchy_classification():
    """Test that a trivial hierarchy behaves as expected."""
    clf, (X, y) = make_classifier_and_data(n_classes=5)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=RANDOM_STATE,
    )

    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    assert_that(accuracy, is_(close_to(1., delta=0.05)))


def test_nontrivial_hierarchy_leaf_classification():
    """Test that a nontrivial hierarchy leaf classification behaves as expected
    under the default parameters.

    We build the following class hierarchy along with data from the handwritten digits dataset:

            <ROOT>
           /      \
          A        B
         / \      / \ \
        1   7    3   8  9

    """
    class_hierarchy = {
        ROOT: ["A", "B"],
        "A": [1, 7],
        "B": [3, 8, 9],
    }
    base_estimator = svm.SVC(
        gamma=0.001,
        kernel="rbf",
        probability=True
    )
    clf = make_classifier(
        base_estimator=base_estimator,
        class_hierarchy=class_hierarchy,
    )
    X, y = make_digits_dataset(
        targets=[1, 7, 3, 8, 9],
        as_str=False,
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
    )

    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    assert_that(accuracy, is_(close_to(1., delta=0.02)))


def test_nmlnp_strategy_with_float_stopping_criteria():
    # since NMLNP results in a mix of intermediate and lefa nodes,
    # make sure they are all of same dtype (str)
    class_hierarchy = {
        ROOT: ["A", "B"],
        "A": ["1", "5", "6", "7"],
        "B": ["2", "3", "4", "8", "9"],
    }
    base_estimator = svm.SVC(
        gamma=0.001,
        kernel="rbf",
        probability=True
    )
    clf = make_classifier(
        base_estimator=base_estimator,
        class_hierarchy=class_hierarchy,
        prediction_depth="nmlnp",
        stopping_criteria=0.9,
    )

    X, y = make_digits_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
    )

    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    assert_that(list(y_pred), has_item("B"))

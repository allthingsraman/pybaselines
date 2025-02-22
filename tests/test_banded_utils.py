# -*- coding: utf-8 -*-
"""Tests for pybaselines._banded_utils.

@author: Donald Erb
Created on Dec. 11, 2021

"""

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
from scipy.sparse import diags, identity, spdiags
from scipy.sparse.linalg import spsolve

from pybaselines import _banded_utils, _spline_utils

from .conftest import has_pentapy


@pytest.mark.parametrize('data_size', (10, 1001))
@pytest.mark.parametrize('lower_only', (True, False))
def test_diff_2_diags(data_size, lower_only):
    """Ensures the output of _diff_2_diags is the correct shape and values."""
    diagonal_data = _banded_utils._diff_2_diags(data_size, lower_only)

    diff_matrix = _banded_utils.difference_matrix(data_size, 2)
    diag_matrix = (diff_matrix.T @ diff_matrix).todia()
    actual_diagonal_data = diag_matrix.data[::-1]
    if lower_only:
        actual_diagonal_data = actual_diagonal_data[2:]

    assert_array_equal(diagonal_data, actual_diagonal_data)


@pytest.mark.parametrize('data_size', (10, 1001))
@pytest.mark.parametrize('lower_only', (True, False))
def test_diff_1_diags(data_size, lower_only):
    """Ensures the output of _diff_1_diags is the correct shape and values."""
    diagonal_data = _banded_utils._diff_1_diags(data_size, lower_only)

    diff_matrix = _banded_utils.difference_matrix(data_size, 1)
    diag_matrix = (diff_matrix.T @ diff_matrix).todia()
    actual_diagonal_data = diag_matrix.data[::-1]
    if lower_only:
        actual_diagonal_data = actual_diagonal_data[1:]

    assert_array_equal(diagonal_data, actual_diagonal_data)


@pytest.mark.parametrize('data_size', (10, 1001))
@pytest.mark.parametrize('lower_only', (True, False))
def test_diff_3_diags(data_size, lower_only):
    """Ensures the output of _diff_3_diags is the correct shape and values."""
    diagonal_data = _banded_utils._diff_3_diags(data_size, lower_only)

    diff_matrix = _banded_utils.difference_matrix(data_size, 3)
    diag_matrix = (diff_matrix.T @ diff_matrix).todia()
    actual_diagonal_data = diag_matrix.data[::-1]
    if lower_only:
        actual_diagonal_data = actual_diagonal_data[3:]

    assert_array_equal(diagonal_data, actual_diagonal_data)


@pytest.mark.parametrize('data_size', (10, 1001))
@pytest.mark.parametrize('diff_order', (0, 1, 2, 3, 4, 5))
@pytest.mark.parametrize('lower_only', (True, False))
@pytest.mark.parametrize('padding', (-1, 0, 1, 2))
def test_diff_penalty_diagonals(data_size, diff_order, lower_only, padding):
    """
    Ensures the penalty matrix (squared finite difference matrix) diagonals are correct.

    Also tests the condition for when `data_size` < 2 * `diff_order` + 1 to ensure
    the slower, sparse route is taken.

    """
    diagonal_data = _banded_utils.diff_penalty_diagonals(
        data_size, diff_order, lower_only, padding
    )

    diff_matrix = _banded_utils.difference_matrix(data_size, diff_order)
    diag_matrix = (diff_matrix.T @ diff_matrix).todia()
    actual_diagonal_data = diag_matrix.data[::-1]
    if lower_only:
        actual_diagonal_data = actual_diagonal_data[diff_order:]
    if padding > 0:
        pad_layers = np.repeat(np.zeros((1, data_size)), padding, axis=0)
        if lower_only:
            actual_diagonal_data = np.concatenate((actual_diagonal_data, pad_layers))
        else:
            actual_diagonal_data = np.concatenate((pad_layers, actual_diagonal_data, pad_layers))

    assert_array_equal(diagonal_data, actual_diagonal_data)


def test_diff_penalty_diagonals_order_neg():
    """Ensures penalty matrix fails for negative order."""
    with pytest.raises(ValueError):
        _banded_utils.diff_penalty_diagonals(10, -1)


def test_diff_penalty_diagonals_datasize_too_small():
    """Ensures penalty matrix fails for data size <= 0."""
    with pytest.raises(ValueError):
        _banded_utils.diff_penalty_diagonals(0)
    with pytest.raises(ValueError):
        _banded_utils.diff_penalty_diagonals(-1)


def test_shift_rows_2_diags():
    """Ensures rows are correctly shifted for a matrix with two off-diagonals on either side."""
    matrix = np.array([
        [1, 2, 9, 0, 0],
        [1, 2, 3, 4, 0],
        [1, 2, 3, 4, 5],
        [0, 1, 2, 3, 8],
        [0, 0, 1, 2, 3]
    ])
    expected = np.array([
        [0, 0, 1, 2, 9],
        [0, 1, 2, 3, 4],
        [1, 2, 3, 4, 5],
        [1, 2, 3, 8, 0],
        [1, 2, 3, 0, 0]
    ])
    output = _banded_utils._shift_rows(matrix, 2, 2)

    assert_array_equal(expected, output)
    # matrix should also be shifted since the changes are done in-place
    assert_array_equal(expected, matrix)


def test_shift_rows_1_diag():
    """Ensures rows are correctly shifted for a matrix with one off-diagonal on either side."""
    matrix = np.array([
        [1, 2, 3, 8, 0],
        [1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4],
    ])
    expected = np.array([
        [0, 1, 2, 3, 8],
        [1, 2, 3, 4, 5],
        [1, 2, 3, 4, 0],
    ])
    output = _banded_utils._shift_rows(matrix, 1, 1)

    assert_array_equal(expected, output)
    # matrix should also be shifted since the changes are done in-place
    assert_array_equal(expected, matrix)


def test_shift_rows_2_1_diags():
    """Tests shifting 2 upper diagonals and 1 lower diagonal."""
    matrix = np.array([
        [1, 2, 9, 0, 0],
        [1, 2, 3, 4, 0],
        [1, 2, 3, 4, 5],
        [0, 1, 2, 3, 8],
        [0, 0, 1, 2, 3]
    ])
    expected = np.array([
        [0, 0, 1, 2, 9],
        [0, 1, 2, 3, 4],
        [1, 2, 3, 4, 5],
        [0, 1, 2, 3, 8],
        [0, 1, 2, 3, 0]
    ])
    output = _banded_utils._shift_rows(matrix, 2, 1)

    assert_array_equal(expected, output)
    # matrix should also be shifted since the changes are done in-place
    assert_array_equal(expected, matrix)


def test_lower_to_full_simple():
    """Simple test for _lower_to_full."""
    lower = np.array([
        [1, 2, 3, 4],
        [5, 6, 7, 0],
        [8, 9, 0, 0]
    ])
    expected_full = np.array([
        [0, 0, 8, 9],
        [0, 5, 6, 7],
        [1, 2, 3, 4],
        [5, 6, 7, 0],
        [8, 9, 0, 0]
    ])

    output = _banded_utils._lower_to_full(lower)

    assert_array_equal(expected_full, output)


@pytest.mark.parametrize('num_knots', (100, 1000))
@pytest.mark.parametrize('spline_degree', (0, 1, 2, 3, 4, 5))
def test_lower_to_full(data_fixture, num_knots, spline_degree):
    """
    Ensures _lower_to_full correctly makes a full banded matrix from a lower banded matrix.

    Use ``B.T @ W @ B`` since most of the diagonals are different, so any issue in the
    calculation should show.

    """
    x, y = data_fixture
    # ensure x is a float
    x = x.astype(float, copy=False)
    # TODO replace with np.random.default_rng when min numpy version is >= 1.17
    weights = np.random.RandomState(0).normal(0.8, 0.05, x.size)
    weights = np.clip(weights, 0, 1)

    knots = _spline_utils._spline_knots(x, num_knots, spline_degree, True)
    basis = _spline_utils._spline_basis(x, knots, spline_degree)

    BTWB_full = (basis.T @ diags(weights, format='csr') @ basis).todia().data[::-1]
    BTWB_lower = BTWB_full[len(BTWB_full) // 2:]

    assert_allclose(_banded_utils._lower_to_full(BTWB_lower), BTWB_full, 1e-10, 1e-14)


@pytest.mark.parametrize('padding', (-1, 0, 1, 2))
@pytest.mark.parametrize('lower_only', (True, False))
def test_pad_diagonals(padding, lower_only):
    """Ensures padding is correctly applied to banded matrices."""
    array = np.array([
        [1, 2, 3, 4],
        [5, 6, 7, 0],
        [8, 9, 0, 0]
    ])
    output = _banded_utils._pad_diagonals(array, padding=padding, lower_only=lower_only)
    if padding < 1:
        expected_output = array
    else:
        layers = np.zeros((padding, array.shape[1]))
        if lower_only:
            expected_output = np.concatenate((array, layers))
        else:
            expected_output = np.concatenate((layers, array, layers))
    assert_array_equal(output, expected_output)


def test_add_diagonals_simple():
    """Basis example for _add_diagonals."""
    a = np.array([
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [1, 2, 3, 4]
    ])
    b = np.array([
        [1, 2, 3, 4],
        [5, 6, 7, 8]
    ])
    expected_output = np.array([
        [2, 4, 6, 8],
        [10, 12, 14, 16],
        [1, 2, 3, 4]
    ])
    output = _banded_utils._add_diagonals(a, b)

    assert_array_equal(output, expected_output)


@pytest.mark.parametrize('diff_order_1', (0, 1, 2, 3, 4))
@pytest.mark.parametrize('diff_order_2', (0, 1, 2, 3, 4))
@pytest.mark.parametrize('lower_only', (True, False))
def test_add_diagonals(diff_order_1, diff_order_2, lower_only):
    """Ensure _add_diagonals works for a broad range of matrices."""
    points = 100
    a = _banded_utils.diff_penalty_diagonals(points, diff_order_1, lower_only)
    b = _banded_utils.diff_penalty_diagonals(points, diff_order_2, lower_only)

    output = _banded_utils._add_diagonals(a, b, lower_only)

    a_offsets = np.arange(diff_order_1, -diff_order_1 - 1, -1)
    b_offsets = np.arange(diff_order_2, -diff_order_2 - 1, -1)
    a_matrix = spdiags(
        _banded_utils.diff_penalty_diagonals(points, diff_order_1, False),
        a_offsets, points, points, 'csr'
    )
    b_matrix = spdiags(
        _banded_utils.diff_penalty_diagonals(points, diff_order_2, False),
        b_offsets, points, points, 'csr'
    )
    expected_output = (a_matrix + b_matrix).todia().data[::-1]
    if lower_only:
        expected_output = expected_output[len(expected_output) // 2:]

    assert_allclose(output, expected_output, 0, 1e-10)


def test_add_diagonals_fails():
    """Ensure _add_diagonals properly raises errors."""
    a = np.array([
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [1, 2, 3, 4]
    ])
    b = np.array([
        [1, 2, 3, 4],
        [5, 6, 7, 8]
    ])

    # row mismatch is not a multiple of 2 when lower_only=False
    with pytest.raises(ValueError):
        _banded_utils._add_diagonals(a, b, lower_only=False)

    # mismatched number of columns
    with pytest.raises(ValueError):
        _banded_utils._add_diagonals(a[:, 1:], b)


@pytest.mark.parametrize('diff_order', (0, 1, 2, 3, 4, 5))
def test_difference_matrix(diff_order):
    """Tests common differential matrices."""
    diff_matrix = _banded_utils.difference_matrix(10, diff_order).toarray()
    numpy_diff = np.diff(np.eye(10), diff_order, axis=0)

    assert_array_equal(diff_matrix, numpy_diff)


def test_difference_matrix_order_2():
    """
    Tests the 2nd order differential matrix against the actual representation.

    The 2nd order differential matrix is most commonly used,
    so double-check that it is correct.
    """
    diff_matrix = _banded_utils.difference_matrix(8, 2).toarray()
    actual_matrix = np.array([
        [1, -2, 1, 0, 0, 0, 0, 0],
        [0, 1, -2, 1, 0, 0, 0, 0],
        [0, 0, 1, -2, 1, 0, 0, 0],
        [0, 0, 0, 1, -2, 1, 0, 0],
        [0, 0, 0, 0, 1, -2, 1, 0],
        [0, 0, 0, 0, 0, 1, -2, 1]
    ])

    assert_array_equal(diff_matrix, actual_matrix)


def test_difference_matrix_order_0():
    """
    Tests the 0th order differential matrix against the actual representation.

    The 0th order differential matrix should be the same as the identity matrix,
    so double-check that it is correct.
    """
    diff_matrix = _banded_utils.difference_matrix(10, 0).toarray()
    actual_matrix = identity(10).toarray()

    assert_array_equal(diff_matrix, actual_matrix)


def test_difference_matrix_order_neg():
    """Ensures differential matrix fails for negative order."""
    with pytest.raises(ValueError):
        _banded_utils.difference_matrix(10, diff_order=-2)


def test_difference_matrix_order_over():
    """
    Tests the (n + 1)th order differential matrix against the actual representation.

    If n is the number of data points and the difference order is greater than n,
    then differential matrix should have a shape of (0, n) with 0 stored elements,
    following a similar logic as np.diff.

    """
    diff_matrix = _banded_utils.difference_matrix(10, 11).toarray()
    actual_matrix = np.empty(shape=(0, 10))

    assert_array_equal(diff_matrix, actual_matrix)


def test_difference_matrix_size_neg():
    """Ensures differential matrix fails for negative data size."""
    with pytest.raises(ValueError):
        _banded_utils.difference_matrix(-1)


@pytest.mark.parametrize('form', ('dia', 'csc', 'csr'))
def test_difference_matrix_formats(form):
    """
    Ensures that the sparse format is correctly passed to the constructor.

    Tests both 0-order and 2-order, since 0-order uses a different constructor.
    """
    assert _banded_utils.difference_matrix(10, 2, form).format == form
    assert _banded_utils.difference_matrix(10, 0, form).format == form


def check_penalized_system(penalized_system, expected_penalty, lam, diff_order,
                           allow_lower, reverse_diags, padding, using_pentapy):
    """Tests a PenalizedSystem object with the expected values."""
    expected_padded_penalty = lam * _banded_utils._pad_diagonals(
        expected_penalty, padding, lower_only=allow_lower
    )

    assert_array_equal(penalized_system.original_diagonals, expected_penalty)
    assert_array_equal(penalized_system.penalty, expected_padded_penalty)
    assert penalized_system.reversed == reverse_diags
    assert penalized_system.lower == allow_lower
    assert penalized_system.diff_order == diff_order
    assert penalized_system.num_bands == diff_order + max(0, padding)
    assert penalized_system.using_pentapy == using_pentapy
    if allow_lower:
        assert penalized_system.main_diagonal_index == 0
    else:
        assert penalized_system.main_diagonal_index == diff_order + max(0, padding)


@pytest.mark.parametrize('diff_order', (1, 2, 3))
@pytest.mark.parametrize('allow_lower', (True, False))
@pytest.mark.parametrize('reverse_diags', (None, True, False))
def test_penalized_system_setup(diff_order, allow_lower, reverse_diags):
    """
    Tests the setup of a PenalizedSystem object.

    Also tests the `reset_diagonals` method of the object, which should try to
    reuse the diagonals whenever posible but will otherwise re-setup the object.

    Since `allow_pentapy` is set to False, the `lower` attribute of the
    PenalizedSystem will always equal the input `allow_lower` and the `reversed`
    attribute will be equal to the bool of the input `reverse_diags` input (ie. None
    will also be False).

    """
    data_size = 100
    lam = 5
    expected_penalty = _banded_utils.diff_penalty_diagonals(
        data_size, diff_order=diff_order, lower_only=allow_lower, padding=0
    )
    if reverse_diags:
        expected_penalty = expected_penalty[::-1]

    initial_system = _banded_utils.PenalizedSystem(
        data_size, lam=1, diff_order=0, allow_pentapy=False
    )

    for padding in range(-1, 3):
        penalized_system = _banded_utils.PenalizedSystem(
            data_size, lam=lam, diff_order=diff_order, allow_lower=allow_lower,
            reverse_diags=reverse_diags, allow_pentapy=False, padding=padding
        )
        check_penalized_system(
            penalized_system, expected_penalty, lam, diff_order, allow_lower,
            bool(reverse_diags), padding, False
        )
        # also check that the reset_diagonal method performs similarly
        initial_system.reset_diagonals(
            lam=lam, diff_order=diff_order, allow_lower=allow_lower,
            reverse_diags=reverse_diags, allow_pentapy=False, padding=padding
        )
        check_penalized_system(
            initial_system, expected_penalty, lam, diff_order, allow_lower,
            bool(reverse_diags), padding, False
        )


@has_pentapy
@pytest.mark.parametrize('diff_order', (1, 2, 3))
@pytest.mark.parametrize('allow_lower', (True, False))
@pytest.mark.parametrize('reverse_diags', (None, True, False))
def test_penalized_system_setup_pentapy(diff_order, allow_lower, reverse_diags):
    """
    Tests the setup of a PenalizedSystem object when `allow_pentapy` is True.

    Also tests the `reset_diagonals` method of the object, which should try to
    reuse the diagonals whenever posible but will otherwise re-setup the object.

    Since `allow_pentapy` is set to True, the `lower` attribute of the
    PenalizedSystem will equal the input `allow_lower` if `diff_order` is not 2, otherwise
    it will be False; the `reversed` attribute will be equal to the bool of the input
    `reverse_diags` input (ie. None will also be False) if `diff_order` is not 2, otherwise
    it will be True if `reverse_diags` is None or True.

    """
    data_size = 100
    lam = 5
    if diff_order == 2:  # will actually use pentapy
        actual_lower = False
        reversed_penalty = reverse_diags is not False
    else:
        actual_lower = allow_lower
        reversed_penalty = bool(reverse_diags)

    expected_penalty = _banded_utils.diff_penalty_diagonals(
        data_size, diff_order=diff_order, lower_only=actual_lower, padding=0
    )
    if reversed_penalty:
        expected_penalty = expected_penalty[::-1]

    initial_system = _banded_utils.PenalizedSystem(
        data_size, lam=1, diff_order=0, allow_pentapy=True
    )

    for padding in range(-1, 3):
        penalized_system = _banded_utils.PenalizedSystem(
            data_size, lam=lam, diff_order=diff_order, allow_lower=allow_lower,
            reverse_diags=reverse_diags, allow_pentapy=True, padding=padding
        )
        check_penalized_system(
            penalized_system, expected_penalty, lam, diff_order, actual_lower,
            reversed_penalty, padding, using_pentapy=diff_order == 2
        )
        # also check that the reset_diagonal method performs similarly
        initial_system.reset_diagonals(
            lam=lam, diff_order=diff_order, allow_lower=allow_lower,
            reverse_diags=reverse_diags, allow_pentapy=True, padding=padding
        )
        check_penalized_system(
            initial_system, expected_penalty, lam, diff_order, actual_lower,
            reversed_penalty, padding, using_pentapy=diff_order == 2
        )


@pytest.mark.parametrize('diff_order', (1, 2, 3))
@pytest.mark.parametrize('allow_lower', (True, False))
@pytest.mark.parametrize('allow_pentapy', (True, False))
def test_penalized_system_solve(data_fixture, diff_order, allow_lower, allow_pentapy):
    """
    Tests the solve method of a PenalizedSystem object.

    Solves the equation ``(I + lam * D.T @ D) x = y``, where `I` is the identity
    matrix, and ``D.T @ D`` is the penalty.

    """
    x, y = data_fixture
    data_size = len(y)
    lam = {1: 1e2, 2: 1e5, 3: 1e8}[diff_order]
    expected_penalty = _banded_utils.diff_penalty_diagonals(
        data_size, diff_order=diff_order, lower_only=False
    )
    sparse_penalty = spdiags(
        lam * expected_penalty, np.arange(diff_order, -(diff_order + 1), -1),
        data_size, data_size, 'csr'

    )
    expected_solution = spsolve(identity(data_size, format='csr') + sparse_penalty, y)

    penalized_system = _banded_utils.PenalizedSystem(
        data_size, lam=lam, diff_order=diff_order, allow_lower=allow_lower,
        reverse_diags=None, allow_pentapy=allow_pentapy
    )
    penalized_system.penalty[penalized_system.main_diagonal_index] += 1
    output = penalized_system.solve(penalized_system.penalty, y)

    assert_allclose(output, expected_solution, 1e-6, 1e-10)


@pytest.mark.parametrize('diff_order', (1, 2, 3))
@pytest.mark.parametrize('allow_lower', (True, False))
def test_penalized_system_add_penalty(diff_order, allow_lower):
    """
    Tests adding a penalty to a PenalizedSystem.

    Sets `allow_pentapy` to False so that the input `allow_lower` is always equal
    to the resulting `lower` attribute of the PenalizedSystem.

    """
    data_size = 100
    lam = 5
    expected_penalty = lam * _banded_utils.diff_penalty_diagonals(
        data_size, diff_order=diff_order, lower_only=allow_lower
    )

    # use even number of bands to ensure the matrix is symmetric when allow_lower is False
    for penalty_size in range(diff_order, diff_order + 5, 2):
        penalized_system = _banded_utils.PenalizedSystem(
            data_size, lam=lam, diff_order=diff_order, allow_lower=allow_lower,
            allow_pentapy=False
        )
        if allow_lower:
            additional_penalty = np.ones((penalty_size, data_size))
        else:
            additional_penalty = np.ones((2 * penalty_size + 1, data_size))
        output = penalized_system.add_penalty(additional_penalty)
        expected_output = _banded_utils._add_diagonals(
            expected_penalty, additional_penalty, lower_only=allow_lower
        )

        assert_allclose(output, expected_output)
        # should also modify the penalty attribute
        assert_allclose(penalized_system.penalty, expected_output)
        if allow_lower:
            expected_num_bands = max(diff_order, penalty_size - 1)
            expected_main_diag_index = 0
        else:
            expected_num_bands = max(diff_order, penalty_size)
            expected_main_diag_index = expected_num_bands
        assert penalized_system.num_bands == expected_num_bands
        assert penalized_system.main_diagonal_index == expected_main_diag_index


@pytest.mark.parametrize('allow_lower', (True, False))
@pytest.mark.parametrize('reverse_diags', (True, False))
def test_penalized_system_reverse_penalty(allow_lower, reverse_diags):
    """
    Ensures the reverse_penalty method performs as expected.

    Should raise an exception if the penalty is lower only, otherwise should
    work as expected. Using pentapy is set to False so that the penalized
    system's lower attribute is the same as the input allow_lower value.

    """
    penalized_system = _banded_utils.PenalizedSystem(
        10, allow_lower=allow_lower, reverse_diags=reverse_diags, allow_pentapy=False
    )
    if allow_lower:
        with pytest.raises(ValueError):
            penalized_system.reverse_penalty()
    else:
        original_diagonals = penalized_system.original_diagonals.copy()
        original_penalty = penalized_system.penalty.copy()
        original_reverse = penalized_system.reversed

        penalized_system.reverse_penalty()

        assert penalized_system.reversed == (not original_reverse)
        assert_array_equal(penalized_system.original_diagonals, original_diagonals[::-1])
        assert_array_equal(penalized_system.penalty, original_penalty[::-1])

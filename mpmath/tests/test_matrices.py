import pytest

from mpmath import (convert, diag, extend, eye, fp, hilbert, inf, inverse, iv,
                    j, matrix, mnorm, mp, mpc, mpf, mpi, norm, nstr, ones,
                    randmatrix, sqrt, swap_row, zeros, kron)

from functools import reduce


def test_matrix_basic():
    A1 = matrix(3)
    for i in range(3):
        A1[i,i] = 1
    assert A1 == eye(3)
    assert A1 == matrix(A1)
    A2 = matrix(3, 2)
    assert not A2._matrix__data
    A3 = matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    assert list(A3) == list(range(1, 10))
    A3[1,1] = 0
    assert (1, 1) not in A3._matrix__data
    A4 = matrix([[1, 2, 3], [4, 5, 6]])
    A5 = matrix([[6, -1], [3, 2], [0, -3]])
    assert A4 * A5 == matrix([[12, -6], [39, -12]])
    assert A1 * A3 == A3 * A1 == A3
    pytest.raises(ValueError, lambda: A2*A2)
    l = [[10, 20, 30], [40, 0, 60], [70, 80, 90]]
    A6 = matrix(l)
    assert A6.tolist() == l
    assert A6 == eval(repr(A6))
    A6 = fp.matrix(A6)
    assert A6 == eval(repr(A6))
    assert A6*1j == eval(repr(A6*1j))
    assert A3 * 10 == 10 * A3 == A6
    assert A2.rows == 3
    assert A2.cols == 2
    A3.rows = 2
    A3.cols = 2
    assert len(A3._matrix__data) == 3
    assert A4 + A4 == 2*A4
    pytest.raises(ValueError, lambda: A4 + A2)
    assert sum(A1 - A1) == 0
    A7 = matrix([[1, 2], [3, 4], [5, 6], [7, 8]])
    x = matrix([10, -10])
    assert A7*x == matrix([-10, -10, -10, -10])
    A8 = ones(5)
    assert sum((A8 + 1) - (2 - zeros(5))) == 0
    assert (1 + ones(4)) / 2 - 1 == zeros(4)
    assert eye(3)**10 == eye(3)
    pytest.raises(ValueError, lambda: A7**2)
    A9 = randmatrix(3)
    A10 = matrix(A9)
    A9[0,0] = -100
    assert A9 != A10
    assert nstr(A9)
    assert A9 != None  # issue 283
    pytest.raises(IndexError, lambda: zeros(1,1)[:, 1])  # issue 318
    pytest.raises(IndexError, lambda: zeros(1,1)[1, :])

def test_matmul():
    """
    Test the PEP465 "@" matrix multiplication syntax.
    """
    A4 = matrix([[1, 2, 3], [4, 5, 6]])
    A5 = matrix([[6, -1], [3, 2], [0, -3]])
    assert A4 @ A5 == A4 * A5

def test_matrix_slices():
    A = matrix([    [1, 2, 3],
                        [4, 5 ,6],
                        [7, 8 ,9]])
    V = matrix([1,2,3,4,5])

    # Get slice
    assert A[:,:] == A
    assert A[:,1] == matrix([[2],[5],[8]])
    assert A[2,:] == matrix([[7, 8 ,9]])
    assert A[1:3,1:3] == matrix([[5,6],[8,9]])
    assert A[0:2,0:2] == matrix([[1,2],[4,5]])  # issue 267
    assert A[:2,:2] == matrix([[1,2],[4,5]])
    assert V[2:4] == matrix([3,4])
    pytest.raises(IndexError, lambda: A[:,1:6])

    # Assign slice with matrix
    A1 = matrix(3)
    A1[:,:] = A
    assert A1[:,:] == matrix([[1, 2, 3],
                                        [4, 5 ,6],
                                        [7, 8 ,9]])
    A1[0,:] = matrix([[10, 11, 12]])
    assert A1 == matrix([ [10, 11, 12],
                                    [4, 5 ,6],
                                    [7, 8 ,9]])
    A1[:,2] = matrix([[13], [14], [15]])
    assert A1 == matrix([ [10, 11, 13],
                                    [4, 5 ,14],
                                    [7, 8 ,15]])
    A1[:2,:2] = matrix([[16, 17], [18 , 19]])
    assert A1 == matrix([ [16, 17, 13],
                                    [18, 19 ,14],
                                    [7, 8 ,15]])
    V[1:3] = 10
    assert V == matrix([1,10,10,4,5])
    with pytest.raises(ValueError):
        A1[2,:] = A[:,1]

    with pytest.raises(IndexError):
        A1[2,1:20] = A[:,:]

    # Assign slice with scalar
    A1[:,2] = 10
    assert A1 == matrix([ [16, 17, 10],
                                    [18, 19 ,10],
                                    [7, 8 ,10]])
    A1[:,:] = 40
    for x in A1:
        assert x == 40


def test_matrix_power():
    A = matrix([[1, 2], [3, 4]])
    assert A**2 == A*A
    assert A**3 == A*A*A
    assert A**-1 == inverse(A)
    assert A**-2 == inverse(A*A)

def test_matrix_transform():
    A = matrix([[1, 2], [3, 4], [5, 6]])
    assert A.T == A.transpose() == matrix([[1, 3, 5], [2, 4, 6]])
    swap_row(A, 1, 2)
    assert A == matrix([[1, 2], [5, 6], [3, 4]])
    l = [1, 2]
    swap_row(l, 0, 1)
    assert l == [2, 1]
    assert extend(eye(3), [1,2,3]) == matrix([[1,0,0,1],[0,1,0,2],[0,0,1,3]])

def test_matrix_conjugate():
    A = matrix([[1 + j, 0], [2, j]])
    assert A.conjugate() == matrix([[mpc(1, -1), 0], [2, mpc(0, -1)]])
    assert A.transpose_conj() == A.H == matrix([[mpc(1, -1), 2],
                                                [0, mpc(0, -1)]])

def test_matrix_creation():
    assert diag([1, 2, 3]) == matrix([[1, 0, 0], [0, 2, 0], [0, 0, 3]])
    A1 = ones(2, 3)
    assert A1.rows == 2 and A1.cols == 3
    for a in A1:
        assert a == 1
    A2 = zeros(3, 2)
    assert A2.rows == 3 and A2.cols == 2
    for a in A2:
        assert a == 0
    assert randmatrix(10) != randmatrix(10)
    one = mpf(1)
    assert hilbert(3) == matrix([[one, one/2, one/3],
                                 [one/2, one/3, one/4],
                                 [one/3, one/4, one/5]])

def test_norms():
    # matrix norms
    A = matrix([[1, -2], [-3, -1], [2, 1]])
    assert mnorm(A,1) == 6
    assert mnorm(A,inf) == 4
    assert mnorm(A,'F') == sqrt(20)
    # vector norms
    assert norm(-3) == 3
    x = [1, -2, 7, -12]
    assert norm(x, 1) == 22
    assert round(norm(x, 2), 10) == 14.0712472795
    assert round(norm(x, 10), 10) == 12.0054633727
    assert norm(x, inf) == 12

def test_vector():
    x = matrix([0, 1, 2, 3, 4])
    assert x == matrix([[0], [1], [2], [3], [4]])
    assert x[3] == 3
    assert len(x._matrix__data) == 4
    assert list(x) == list(range(5))
    x[0] = -10
    x[4] = 0
    assert x[0] == -10
    assert len(x) == len(x.T) == 5
    assert x.T*x == matrix([[114]])

def test_matrix_copy():
    A = ones(6)
    B = A.copy()
    C = +A
    assert A == B
    assert A == C
    B[0,0] = 0
    assert A != B
    C[0,0] = 42
    assert A != C

def test_matrix_numpy():
    numpy = pytest.importorskip("numpy")
    l = [[1, 2], [3, 4], [5, 6]]
    a = numpy.array(l)
    assert matrix(l) == matrix(a)

def test_interval_matrix_scalar_mult():
    """Multiplication of iv.matrix and any scalar type"""
    a = mpi(-1, 1)
    b = a + a * 2j
    c = mpf(42)
    d = c + c * 2j
    e = 1.234
    f = fp.convert(e)
    g = e + e * 3j
    h = fp.convert(g)
    M = iv.ones(1)
    for x in [a, b, c, d, e, f, g, h]:
        assert x * M == iv.matrix([x])
        assert M * x == iv.matrix([x])

@pytest.mark.xfail()
def test_interval_matrix_matrix_mult():
    """Multiplication of iv.matrix and other matrix types"""
    A = ones(1)
    B = fp.ones(1)
    M = iv.ones(1)
    for X in [A, B, M]:
        assert X * M == iv.matrix(X)
        assert X * M == X
        assert M * X == iv.matrix(X)
        assert M * X == X

def test_matrix_conversion_to_iv():
    # Test that matrices with foreign datatypes are properly converted
    for other_type_eye in [eye(3), fp.eye(3), iv.eye(3)]:
        A = iv.matrix(other_type_eye)
        B = iv.eye(3)
        assert type(A[0,0]) == type(B[0,0])
        assert A.tolist() == B.tolist()

def test_interval_matrix_mult_bug():
    # regression test for interval matrix multiplication:
    # result must be nonzero-width and contain the exact result
    x = convert('1.00000000000001') # note: this is implicitly rounded to some near mpf float value
    A = matrix([[x]])
    B = iv.matrix(A)
    C = iv.matrix([[x]])
    assert B == C
    B = B * B
    C = C * C
    assert B == C
    assert B[0, 0].delta > 1e-16
    assert B[0, 0].delta < 3e-16
    assert C[0, 0].delta > 1e-16
    assert C[0, 0].delta < 3e-16
    assert mp.mpf('1.00000000000001998401444325291756783368705994138804689654') in B[0, 0]
    assert mp.mpf('1.00000000000001998401444325291756783368705994138804689654') in C[0, 0]
    # the following caused an error before the bug was fixed
    assert iv.matrix(mp.eye(2)) * (iv.ones(2) + mpi(1, 2)) == iv.matrix([[mpi(2, 3), mpi(2, 3)], [mpi(2, 3), mpi(2, 3)]])

def test_matrix_kron():
    a = matrix(
        [[1, 2], 
         [3, 4]])
    b = matrix(
        [[5, 6], 
         [7, 8]])
    c = matrix(
        [[9, 10],
         [11, 12]])
    d = matrix([1, 10, 100])
    e = matrix([5, 6, 7])
    axb = matrix(
        [[5, 6, 10, 12],
        [7, 8, 14, 16],
        [15, 18, 20, 24],
        [21, 24, 28, 32]])
    bxc = matrix(
        [[45, 50, 54, 60],
         [55, 60, 66, 72],
         [63, 70, 72, 80],
         [77, 84, 88, 96]])
    axbxc = matrix(
        [[45, 50, 54, 60, 90, 100, 108, 120],
         [55, 60, 66, 72, 110, 120, 132, 144],
         [63, 70, 72, 80, 126, 140, 144, 160],
         [77, 84, 88, 96, 154, 168, 176, 192],
         [135, 150, 162, 180, 180, 200, 216, 240],
         [165, 180, 198, 216, 220, 240, 264, 288],
         [189, 210, 216, 240, 252, 280, 288, 320],
         [231, 252, 264, 288, 308, 336, 352, 384]])
    dxe = matrix(
        [[5],
         [6],
         [7],
         [50],
         [60],
         [70],
         [500],
         [600],
         [700]])
    assert kron(a) == a
    assert kron(b) == b
    assert kron(c) == c
    assert kron(d) == d
    assert kron(e) == e
    assert kron(a, b, c, d, e) == reduce(kron, [a, b, c, d, e])
    assert kron(a, b) == axb
    assert kron(b, c) == bxc
    assert kron(a, b, c) == axbxc == kron(kron(a, b), c) == kron(a, kron(b, c))
    assert kron(d, e) == dxe
    assert kron(ones(10, 9), ones(8, 7)) == ones(10 * 8, 9 * 7)
    assert kron(eye(4), eye(4), eye(4)) == eye(4 * 4 * 4)
    assert kron(zeros(5), d) == zeros(15, 5)
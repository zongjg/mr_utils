'''Iterative hard thresholding with variable encoding model, uses TV.
'''

import logging

import numpy as np

logging.basicConfig(format='%(levelname)s: %(message)s',
                    level=logging.DEBUG)

def IHT_TV(y, forward_fun, inverse_fun, k, mu=1, tol=1e-8,
           do_reordering=False, x=None, ignore_residual=False,
           disp=False, maxiter=500):
    r'''IHT for generic encoding model and TV constraint.

    Parameters
    ----------
    y : array_like
        Measured data, i.e., y = Ax.
    forward_fun : callable
        A, the forward transformation function.
    inverse_fun : callable
        A^H, the inverse transformation function.
    k : int
        Sparsity measure (number of nonzero coefficients expected).
    mu : float, optional
        Step size.
    tol : float, optional
        Stop when stopping criteria meets this threshold.
    do_reordering : bool, optional
        Reorder column-stacked true image.
    x : array_like, optional
        The true image we are trying to reconstruct.
    ignore_residual : bool, optional
        Whether or not to break out of loop if resid increases.
    disp : bool, optional
        Whether or not to display iteration info.
    maxiter : int, optional
        Maximum number of iterations.

    Returns
    -------
    x_hat : array_like
        Estimate of x.

    Notes
    -----
    Solves the problem:

    .. math::

        \min_x || y - Ax ||^2_2 \text{ s.t. } || \text{TV}(x) ||_0
        \leq k

    If `x=None`, then MSE will not be calculated.
    '''

    # Make sure we have a defined compare_mse and Table for printing
    if disp:
        from mr_utils.utils.printtable import Table

        if x is not None:
            from skimage.measure import compare_mse
            xabs = np.abs(x)
        else:
            compare_mse = lambda xx, yy: 0

    # Right now we are doing absolute values on updates
    x_hat = np.zeros(y.shape)
    r = y.copy()
    prev_stop_criteria = np.inf
    norm_y = np.linalg.norm(y)

    # Initialize display table
    if disp:
        table = Table(
            ['iter', 'norm', 'MSE'],
            [len(repr(maxiter)), 8, 8], ['d', 'e', 'e'])
        hdr = table.header()
        for line in hdr.split('\n'):
            logging.info(line)

    # Find perfect reordering (column-stacked-wise)
    if do_reordering:
        from mr_utils.utils.orderings import (col_stacked_order,
                                              inverse_permutation)
        reordering = col_stacked_order(x)
        inverse_reordering = inverse_permutation(reordering)

        # Find new sparsity measure
        if x is not None:
            k = np.sum(np.abs(np.diff(x.flatten()[reordering])) > 0)
        else:
            logging.warning(('Make sure sparsity level k is '
                             'adjusted for reordering!'))

    # Do the thing
    for ii in range(int(maxiter)):

        # Density compensation!!!!
        #

        # Take step
        # val = (x_hat + mu*np.abs(np.fft.ifft2(r))).flatten()
        val = (x_hat + mu*inverse_fun(r)).flatten()

        # Do the reordering
        if do_reordering:
            val = val[reordering]

        # Finite differences transformation
        first_samp = val[0] # save first sample for inverse transform
        fd = np.diff(val)

        # Hard thresholding
        fd[np.argsort(np.abs(fd))[:-1*k]] = 0

        # Inverse finite differences transformation
        res = np.hstack((first_samp, fd)).cumsum()
        if do_reordering:
            res = res[inverse_reordering]

        # Compute stopping criteria
        stop_criteria = np.linalg.norm(r)/norm_y

        # If the stop_criteria gets worse, get out of dodge
        if not ignore_residual and (
                stop_criteria > prev_stop_criteria):
            logging.warning('Residual increased! Not continuing!')
            break
        prev_stop_criteria = stop_criteria

        # Update x
        x_hat = res.reshape(x_hat.shape)

        # Show the people what they asked for
        if disp:
            logging.info(
                table.row([ii, stop_criteria,
                           compare_mse(xabs, x_hat)]))
        if stop_criteria < tol:
            break

        # update the residual
        r = y - forward_fun(x_hat)

    return x_hat

'''Fun little experiment for audio compression.

The idea is to use our reordering trick for sparse signals and apply
it to audio waveforms.  The new thing we're doing here is using
permutation ranks to be a sort of "key" that we can look the
permutation up with.  The reason we might want to use permutation
rank instead of the permutation is because it takes less storage --
instead of storing an integer for every sample of the waveform, store
an (potentially quite large but not as large as storing an integer
for every waveform) integer representing the permutation.  This means
we get some compression out of the deal, since we could transmit less
and still get the same audio quality.

The sad part is that permutation ranking and unranking goes by the
factorial of the length of the permutation -- even for the most
efficient algorithms. So we're restricted to very short block lengths
over which to reorder, and it might not be worth it for all the
trouble we had to go through to get the ranks in the first place and
the space we need to now take up storing many incredibly large
integers.

Maybe an idea to piggyback on other forms of compression?

Notes
-----
Finite differences (when you start dropping a lot of smaller
coefficients) gets square-wave-like with very noticable artifacts.
Perhaps low-pass filtering might help?

DCT seems to be very robust and does a great job, even when block
lengths are small (chunk_size=16).  We can beat the baseline of just
doing DCT and thresholding with appropriately chosen block size and
threshold.  The trick is getting enough of a gain to offset the extra
space required to store the permutation rank.

I've only tried db1 wavelets, don't work as well as DCT.
'''

from os.path import dirname

import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
from scipy.fftpack import dct, idct
from tqdm import tqdm
from skimage.measure import compare_mse

from mr_utils.utils.orderings import inverse_permutation
from mr_utils.cs import relaxed_ordinator
from mr_utils.utils import rank2pi, pi2rank
from mr_utils.test_data import load_test_data

if __name__ == '__main__':

    # Get some sample audio
    path = 'mr_utils/test_data/examples/music/'
    file = 'sample.wav'
    load_test_data(path, [file], do_return=False)
    filename = '%s/%s' % (path, file)
    rate, data = read(filename, mmap=True)
    orig_num_int16 = data.size

    # We're going to have to split this into chunks to make any sense.
    # These chunks should be small enough that we can compute the
    # rank of the permutations fairly easily.
    chunk_size = 16
    tol = 1000
    use_ordinator = False
    ranks1 = []
    ranks2 = []

    # Store coefficients like sparse vectors -- just locations and
    # values of nonzero elements
    chan1_idxs = []
    chan2_idxs = []
    chan1_vals = []
    chan2_vals = []

    # We'll need the first coefficients for finite differences recon
    chan1_firsts = []
    chan2_firsts = []

    # Choose sparsifying transform
    # DCT
    sparsify = lambda x: dct(x)
    unsparsify = lambda x: idct(x)

    # # wavelets...
    # import pywt
    # wvlt = 'db1'
    # sparsify = lambda x: np.concatenate(pywt.dwt(x, wvlt))
    # def unsparsify(x):
    #     '''Inverse wavelet transform.'''
    #     if np.mod(x.size, 2):
    #         x = np.concatenate((x, np.atleast_1d(x[0])))
    #     coeffs = np.split(x, 2, axis=0)
    #     return pywt.idwt(coeffs[0], coeffs[1], wvlt)

    # Try without chunking and ordering for a baseline
    no_ord_chan1 = sparsify(data[:, 0])
    no_ord_chan1 = no_ord_chan1[np.abs(no_ord_chan1) >= tol]
    no_ord_chan2 = sparsify(data[:, 1])
    no_ord_chan2 = no_ord_chan2[np.abs(no_ord_chan2) >= tol]
    comp_bit_required = (no_ord_chan1.size + no_ord_chan2.size)*16

    # Loop over the chunks, choose threshold of coefficients to throw
    # away
    for data0 in tqdm(np.array_split(
            data, int(data.shape[0]/chunk_size), axis=0),
                      leave=False):

        # Sort the data, both channels and get inverse permutation
        if use_ordinator:
            lam, k = .5, round(chunk_size/3)
            idx1 = relaxed_ordinator(data0[:, 0], lam, k, unsparsify)
            idx2 = relaxed_ordinator(data0[:, 1], lam, k, unsparsify)
        else:
            idx1, idx2 = np.argsort(data0, axis=0).T[:]

        idx1i = inverse_permutation(idx1)
        idx2i = inverse_permutation(idx2)

        # Now we need to do some heavy lifting -- find the ranks!
        ranks1.append(pi2rank(idx1i, method='rank1', iterative=False))
        ranks2.append(pi2rank(idx2i, method='rank1', iterative=False))

        # Do sparsifying transform
        chan1 = sparsify(data0[idx1, 0])
        chan2 = sparsify(data0[idx2, 1])
        # unsparsify(chan1)
        # chan1 = np.diff(data0[idx1, 0])
        # chan2 = np.diff(data0[idx2, 1])

        # Save first sample for later
        chan10 = data0[idx1[0], 0]
        chan20 = data0[idx2[0], 1]
        chan1_firsts.append(chan10)
        chan2_firsts.append(chan20)

        # Find nonzero coefficients and their locations
        chan1_idx = np.where(np.abs(chan1) >= tol)
        chan2_idx = np.where(np.abs(chan2) >= tol)
        chan1_val = chan1[chan1_idx]
        chan2_val = chan2[chan2_idx]
        chan1_idxs.append(chan1_idx)
        chan2_idxs.append(chan2_idx)
        chan1_vals.append(chan1_val)
        chan2_vals.append(chan2_val)

        # # Now reconstruct assuming we have the inverse permutation
        # # at our fingertips
        # recon1 = np.zeros(data0.shape[0]-1)
        # recon1[chan1_idx] = chan1_val
        # recon1 = np.concatenate(
        #     (np.atleast_1d(chan10), recon1)).cumsum()
        # recon1 = recon1[idx1i]
        # recon2 = np.zeros(data.shape[0]-1)
        # recon2[chan2_idx] = chan2_val
        # recon2 = np.concatenate(
        #     (np.atleast_1d(chan20), recon2)).cumsum()
        # recon2 = recon2[idx2i]
        # recon = np.stack((recon1, recon2)).T
        #
        # if not np.allclose(recon, data0):
        #     raise ValueError('We lost!')


    # After all is said and done, how much did it help?
    print('orig: %d, ordered: %d' % (data.shape[0], sum(
        [x.size for x in chan1_vals])))
    print('orig: %d, ordered: %d' % (data.shape[0], sum(
        [x.size for x in chan2_vals])))

    # Find out how many int16 we need for the coefficients
    compressed_num_int16 = sum([x.size for x in chan1_vals]) + sum(
        [x.size for x in chan2_vals])

    # Show an example rank that would need be stored for each chunk
    # print('example rank: %d' % ranks1[0])
    print('This is a %d digit number for every %d samples' % (
        len(str(ranks1[0])), chunk_size))
    total_nums = 2*len(ranks1)*len(str(ranks1[0]))
    places = 13*3 - 1 # how many place values for 128 bit int
    print('Total of about %d 128-bit ints' % round(total_nums/places))

    # Compute approx required space
    compressed_bits_required = round(
        total_nums/places)*128 + compressed_num_int16*16
    orig_bits_required = orig_num_int16*16
    print('Compression factor: %g' % (
        compressed_bits_required/orig_bits_required))
    print('Compared to baseline factor: %g' % (
        comp_bit_required/orig_bits_required))

    ii = 0
    recons = []
    for data0 in tqdm(np.array_split(
            data, int(data.shape[0]/chunk_size), 0),
                      leave=False, desc='Recon'):

        # Reconstruct from the ranks
        recon1 = np.zeros(data0.shape[0])
        recon1[chan1_idxs[ii]] = chan1_vals[ii]
        recon1 = unsparsify(recon1)
        # recon1 = np.concatenate(
        #     (np.atleast_1d(chan1_firsts[ii]), recon1)).cumsum()

        # Now we need the inverse permutation
        idx1i_pi = rank2pi(ranks1[ii], data0.shape[0], 'rank1')
        recon1 = recon1[idx1i_pi]

        # Same thing for other channel
        recon2 = np.zeros(data0.shape[0])
        recon2[chan2_idxs[ii]] = chan2_vals[ii]
        recon2 = unsparsify(recon2)
        # recon2 = np.concatenate(
        #     (np.atleast_1d(chan2_firsts[ii]), recon2)).cumsum()

        # Compute the inverse permutation from the ranking
        idx2i_pi = rank2pi(ranks2[ii], data0.shape[0], 'rank1')
        recon2 = recon2[idx2i_pi]
        recon = np.stack((recon1, recon2)).T

        # Make sure we still have a good recon
        # assert np.allclose(recon, data0)
        recons.append(recon)

        # To the next chunk!
        ii += 1

    # Concat all the chunks to get final recon
    recon = np.concatenate(recons)

    # Get MSE
    print('MSE: %e' % compare_mse(
        data/np.max(np.abs(data), axis=0), recon/np.max(
            np.abs(recon), axis=0)))

    # Take a gander
    print(data.shape, recon.shape)
    plt.plot(
        data/np.max(np.abs(data), axis=0) - recon/np.max(
            np.abs(recon), axis=0))
    plt.title('residual')
    plt.show()

    # Save the recon -- scale for no distortion
    recon /= np.max(np.max(recon))
    recon *= np.mean(np.mean(data))
    write(dirname(__file__) + '/sample_recon.wav', rate, recon)

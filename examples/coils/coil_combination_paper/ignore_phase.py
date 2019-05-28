'''Combine, ignoring phase.'''

import numpy as np
from sigpy.mri import birdcage_maps

from mr_utils.sim.ssfp import ssfp
from mr_utils.test_data.phantom import cylinder_2d
from mr_utils.recon.ssfp import gs_recon
from mr_utils.utils import sos
from mr_utils.coils.coil_combine import gcc, caldir
from mr_utils import view # pylint: disable=W0611

def get_coils(dims):
    '''Make coil sensitivities.'''
    return birdcage_maps(dims)

def get_df(dims, TR):
    '''Make off-res.'''
    _, df = np.meshgrid(
        np.linspace(-1/TR, 1/TR, dims[0]),
        np.linspace(-1/TR, 1/TR, dims[1]))
    return df

def PolyArea(x, y):
    '''Shoelace formula'''
    return 0.5*np.abs(
        np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

if __name__ == '__main__':

    find_max_intensity_coil = True
    noise_std = 0.05
    N = 64
    npcs = 4
    pcs = np.linspace(0, 2*np.pi, npcs, endpoint=False)
    ncoils = 5
    mps = get_coils(dims=(ncoils, N, N))
    TR = 3e-3
    alpha = np.deg2rad(30)
    df = get_df((N, N), TR)
    radius = .9
    PD, T1s, T2s = cylinder_2d(dims=(N, N), radius=radius)

    # Simulate the acquisition
    I = np.zeros((ncoils, npcs, N, N), dtype='complex')
    for cc in range(ncoils):
        rf = np.angle(mps[cc, ...])
        I[cc, ...] = np.abs(mps[cc, ...])*ssfp(
            T1s, T2s, TR, alpha, df, phase_cyc=pcs, M0=PD, phi_rf=rf)
    # view(I, montage_axis=0, movie_axis=1)

    if noise_std > 0:
        n_r = np.random.normal(0, noise_std/2, I.shape)
        n_i = np.random.normal(0, noise_std/2, I.shape)
        n = n_r + 1j*n_i
        I += n

    # lGS recon on each coil individually
    lGS = np.zeros((ncoils, N, N), dtype='complex')
    for cc in range(ncoils):
        lGS[cc, ...] = gs_recon(I[cc, ...], pc_axis=0)
    lGSsos = sos(lGS, axes=0)

    # Copy phase from brighest coil at that pixel.  We find this by
    # finding the largest ellipse
    if find_max_intensity_coil:
        phase = np.zeros((npcs, N, N), dtype='complex')
        for idx in np.ndindex((N, N)):
            xx, yy = idx[:]

            # Find out which coil is the brightest
            area = np.zeros(ncoils)
            for cc in range(ncoils):
                I0 = I[cc, :, xx, yy]
                area[cc] = PolyArea(I0.real, I0.imag)
                # area[cc] = np.mean(np.abs(I0))
            ind = np.argmax(area)
            phase[:, xx, yy] = np.angle(I[ind, :, xx, yy])
    else:
        # Copy phase from a single reference coil.  This way is
        # quicker!  There will be more error where the SNR of the
        # coil sensitivity is lower
        ref_coil = 0
        phase = np.angle(I[ref_coil, ...])

    # Take SOS recon across coils to be magnitude of phase-cycles
    I_sos_sub = sos(I, axes=0)

    # Now apply phase we found and do lGS to get band-reduced images
    I_sos_sub = I_sos_sub*np.exp(1j*phase)
    I_sos_sub = gs_recon(I_sos_sub, pc_axis=0)
    view(np.stack((
        lGSsos, I_sos_sub, 5*(lGSsos - np.abs(I_sos_sub)))))

    # Compare to SOS across both PC and coil dims
    I_sos = sos(I, axes=(0, 1))
    view(I_sos)

    # Try it with GCC -- it helps, but still get bad artifacts
    vcoils = 1
    I_gcc0 = np.zeros((vcoils, npcs, N, N), dtype='complex')
    for ii in range(npcs):
        I_gcc0[:, ii, ...] = gcc(I[:, ii, ...], vcoils, coil_axis=0)
    # view(I_gcc, montage_axis=0, movie_axis=1)

    I_gcc = np.zeros((vcoils, N, N), dtype='complex')
    I_gcc_sub = np.zeros((vcoils, N, N), dtype='complex')
    phase0 = phase.transpose((0, 2, 1)) # BART spits out transposed
    for vc in range(vcoils):
        val = np.abs(I_gcc0[vc, ...])*np.exp(1j*phase0)
        I_gcc_sub[vc, ...] = gs_recon(val, pc_axis=0)
        I_gcc[vc, ...] = gs_recon(I_gcc0[vc, ...], pc_axis=0)
    view(np.stack((
        I_gcc, I_gcc_sub)).reshape((-1, N, N)), montage_axis=0)

    # Try direct method
    I_caldir = np.zeros((npcs, N, N), dtype='complex')
    for ii in range(npcs):
        I_caldir[ii, ...] = caldir(I[:, ii, ...], coil_axis=0)
    # view(I_caldir)

    I_caldir_sub = np.abs(I_caldir)*np.exp(1j*phase0)
    I_caldir_sub = gs_recon(I_caldir_sub, pc_axis=0)
    I_caldir = gs_recon(I_caldir, pc_axis=0)
    view(np.stack((I_caldir, I_caldir_sub)))

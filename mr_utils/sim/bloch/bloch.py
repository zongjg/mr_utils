import numpy as np
from tqdm import trange
import matplotlib.pyplot as plt

def rotation(alpha,beta,gamma):

    ca = np.cos(alpha)
    cb = np.cos(beta)
    cg = np.cos(gamma)

    sa = np.sin(alpha)
    sb = np.sin(beta)
    sg = np.sin(gamma)

    rot = np.array([
        [ ca*cb*cg - sa*sg,-ca*cb*sg - sa*cg,ca*sb ],
        [ sa*cb*cg + ca*sg,-sa*cb*sg + ca*cg,sa*sb ],
        [ -sb*cg,sb*sg,cb ]
    ])

    return(rot)

def sim_loop(T1,T2,M0,Nt,h,alpha,beta,gamma,Bx=0,By=0,Bz=3,gyro=1):
    '''Loop implementation to verify matrix implementation.'''

    # Initalize spins at thermal equilibrium at first time point
    spins = np.zeros((Nt,3,) + M0.shape)
    spins[0,2,...] = M0

    # Aux variables to construct A matrix
    wx = gyro*Bx*np.ones(T1.shape)
    wy = gyro*By*np.ones(T1.shape)
    wz = gyro*Bz*np.ones(T1.shape)
    R1 = -1/T1
    R2 = -1/T2

    # Apply initial RF tip at each voxel
    R = rotation(alpha,beta,gamma)
    spins[0,...] = np.tensordot(R,spins[0,...],axes=1)

    # Do finite-difference simulation, using for loops over each voxel
    for tt in trange(1,Nt,leave=False,desc='Bloch sim'):
        for xx in range(T1.shape[0]):
            for yy in range(T1.shape[1]):
                for zz in range(T1.shape[2]):
                    A = np.array([
                        [  R2[xx,yy,zz], wz[xx,yy,zz],-wy[xx,yy,zz] ],
                        [ -wz[xx,yy,zz], R2[xx,yy,zz], wx[xx,yy,zz] ],
                        [  wy[xx,yy,zz],-wx[xx,yy,zz], R1[xx,yy,zz] ]
                    ])
                    spins[tt,:,xx,yy,zz] = A.dot(spins[tt-1,:,xx,yy,zz])*h + spins[tt-1,:,xx,yy,zz] + np.array([ 0,0,M0[xx,yy,zz]/T1[xx,yy,zz] ])*h

    # # Show results for first voxel
    # plt.plot(np.sqrt(np.sum(spins[:,0:2,0,0,0]**2,axis=1)))
    # plt.plot(spins[:,2,0,0,0])
    # plt.show()
    return(spins)

def sim(T1,T2,M0,Nt,h,alpha,beta,gamma,Bx=0,By=0,Bz=3,gyro=1):

    # Initalize spins at thermal equilibrium at first time point
    spins = np.zeros((Nt,3,) + M0.shape)
    spins[0,2,...] = M0

    # Aux variables to construct A matrix
    wx = gyro*Bx*np.ones(T1.shape)
    wy = gyro*By*np.ones(T1.shape)
    wz = gyro*Bz*np.ones(T1.shape)
    R1 = -1/T1
    R2 = -1/T2

    # Apply initial RF tip at each voxel
    R = rotation(alpha,beta,gamma)
    spins[0,...] = np.tensordot(R,spins[0,...],axes=1)

    # Calculate constant A
    A = np.array([
        [  R2, wz,-wy ],
        [ -wz, R2, wx ],
        [  wy,-wx, R1 ]
    ])

    # Do finite-difference simulation
    for tt in trange(1,Nt,leave=False,desc='Bloch sim'):
        spins[tt,...] = np.einsum('ijxyz,jxyz->ixyz',A,spins[tt-1,...])*h + spins[tt-1,...]
        spins[tt,2,...] += h*M0/T1

    return(spins)

def gre(T1,T2,M0,Nt,h,alpha,beta,gamma,TR,TE,Bx=0,By=0,Bz=3,gyro=1):
    '''Bloch simulation of spoiled GRE pulse sequence.'''

    # Initalize
    spins = np.zeros((3,) + M0.shape)
    spins[2,...] = M0

    # Initial tip
    R = rotation(alpha,beta,gamma)
    spins = np.tensordot(R,spins,axes=1)

    # Aux variables
    wx = gyro*Bx*np.ones(T1.shape)
    wy = gyro*By*np.ones(T1.shape)
    wz = gyro*Bz*np.ones(T1.shape)
    R1 = -1/T1
    R2 = -1/T2

    # Bloch equation matrix, A
    A = np.array([
        [  R2, wz,-wy ],
        [ -wz, R2, wx ],
        [  wy,-wx, R1 ]
    ])

    # Split into TRs
    num_TRs = int(Nt*h/TR)
    # print('num_TRs: %g' % num_TRs)

    # Split TRs into TEs
    num_before_TE = int(TE/TR*num_TRs)
    # print('num_before_TE: %g' % num_before_TE)

    num_iters_per_TR = np.around(Nt/num_TRs).astype(int)
    # print('Nt/num_TRs: %g' % num_iters_per_TR)

    # Do all TRs but the last one
    for tr in trange(num_TRs-1,leave=False,desc='GRE Bloch Sim'):

        # Relaxation
        for tt in range(num_iters_per_TR):
            spins += np.einsum('ijxyz,jxyz->ixyz',A,spins)*h
            spins[2,...] += h*M0/T1

        # Spoil
        spins[0:2,...] = 0

        # Next tip
        spins = np.tensordot(R,spins,axes=1)

    # Now readout at TE during last TR
    for tt in range(num_before_TE):
        # Relaxation
        spins += np.einsum('ijxyz,jxyz->ixyz',A,spins)*h
        spins[2,...] += h*M0/T1


    return(spins)

if __name__ == '__main__':
    pass

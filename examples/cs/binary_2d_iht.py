# Not sure if this works...

import numpy as np

import matplotlib.pyplot as plt
from mr_utils.sim.traj import radial
from mr_utils.cs import IHT, cosamp

if __name__ == '__main__':

    # We want a 2d signal, so let's make a binary smiley face

    N = 100
    smiley = np.zeros((N,N))

    # make circle for head
    radius = 0.75
    x,h = np.linspace(-1,1,N,retstep=True)
    X,Y = np.meshgrid(x,x)
    idx = np.sqrt(X**2 + Y**2) < radius
    smiley[idx] = 1

    # Make some eyes
    idx = X > radius*1/4
    idx &= X < radius*1/4 + .05
    idx |= X < -radius*1/4
    idx &= X > -radius*1/4 - .05
    idx &= Y > -radius*1/2
    idx &= Y < -radius*1/5
    smiley[idx] = 0

    # Make a mouth
    idx = X > -1/2*radius
    idx &= X < 1/2*radius
    idx &= Y > 1/2*radius
    idx &= Y < 1/2*radius + .05
    smiley[idx] = 0

    # Make sure it looks alright
    # plt.imshow(smiley)
    # plt.show()

    # Make sure it's sparse in finite differences
    smiley_fd = np.diff(smiley.flatten())
    k = np.sum(np.abs(smiley_fd) > 0)
    print('delta = %d/%d = %%%g' % (k,smiley_fd.size,k/smiley_fd.size*100))
    # plt.plot(smiley_fd)
    # plt.show()

    A = np.fft.fftshift(
        np.fft.fft(
                np.eye(N,N)
            )
        )
    print(A.shape)
    A = np.kron(A,A)

    # Create undersampling pattern, try golden angle
    num_spokes = 16
    samp = radial(smiley.shape,num_spokes,skinny=True)
    # samp = np.ones(samp.shape)
    # plt.imshow(samp)
    # plt.show()

    # Put smiley in kspace
    kspace = np.fft.fftshift(np.fft.fft2(smiley))
    # plt.imshow(np.log(np.abs(kspace)))
    # plt.show()

    # plt.plot(np.abs(A.dot(smiley.flatten())))
    # plt.plot(np.abs(kspace.flatten()))
    # plt.show()
    # assert np.allclose(A.dot(smiley.flatten()),kspace.flatten())

    # Sample kspace
    kspace_samp = samp*kspace
    # plt.imshow(np.log(np.abs(kspace_samp)))
    # plt.show()

    A = np.diag(samp.flatten()).dot(A)

    # plt.plot(np.abs(A.dot(smiley.flatten())))
    # plt.plot(np.abs(kspace_samp.flatten()))
    # plt.show()
    # assert np.allclose(A.dot(smiley.flatten()),kspace_samp.flatten())

    # Get aliased image space
    imspace = np.fft.ifft2(kspace_samp)
    # plt.imshow(np.abs(imspace))
    # plt.show()

    IFT = np.fft.fftshift(np.fft.ifft(np.eye(N)))
    A = np.kron(IFT,IFT).dot(A)

    # plt.imshow(np.abs(A.dot(smiley.flatten())).reshape(smiley.shape))
    # plt.show()
    # plt.plot(np.abs(A.dot(smiley.flatten())))
    # plt.plot(np.abs(imspace.flatten()))
    # plt.show()
    # assert np.allclose(A.dot(smiley.flatten()),imspace.flatten())

    # Try doing both fortran/c order, then average results from both?
    # y = np.diff(smiley.flatten())
    # y = np.diff(imspace.flatten())
    A = np.diff(A,axis=0)
    y = A.dot(smiley.flatten())
    plt.plot(np.abs(A.dot(smiley.flatten())))
    # plt.plot(np.abs(y))
    plt.show()

    # print(A.shape)
    # y = np.diff(imspace.flatten())

    # # Measurement matrix that satisfies y = Ax
    # n = 1500
    # print(n/smiley_fd.size*100)
    # A = np.random.randn(n,smiley_fd.size)
    # A /= np.sqrt(np.sum(A**2,axis=0))
    # y = np.dot(A,smiley_fd)
    #
    # # Do recon
    # x_hat = IHT(A,y,k=k,x=None,disp=True)
    print(k)
    x_hat = cosamp(A,y,k=k,x=smiley_fd,disp=True)
    print(x_hat.shape)
    #
    # Put everything back where it goes
    # if x_hat.size == N**2:
    recon = x_hat.cumsum().reshape(smiley.shape)
    # recon = x_hat.reshape(smiley.shape)
    # else:
    #     recon = np.hstack((smiley_fd[0],x_hat)).cumsum().reshape(smiley.shape)

    # Let's take a look
    plt.imshow(np.abs(recon))
    plt.show()

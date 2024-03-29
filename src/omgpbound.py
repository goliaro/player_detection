#!/usr/bin/python
from __future__ import division
import numpy as np
from covariance import *


def omgpboundA(loghyper, learn, covfunc, M, X, Y):
    """
    Computes the negative of the Marginalized Variational Bound (F) and its 
    derivatives wrt loghyper (dF).

    Parameters:
    loghyper: K hyperparameters, pZ, sn2 (M trajectories), logqZ
    learn: 'learnqZ', 'learnhyp', 'learnall'
    covfunc: Array of covariance functions. If it is a single one, it is shared.
    M: Number of trajectories
    X, Y, Xs: Inputs, outputs, test inputs

    (c) Miguel Lazaro-Gredilla 2010
    """

    # Initialize
    # [N, D] = X.shape
    [N, oD] = Y.shape

    logqZ = np.concatenate((np.zeros((N, 1)), np.reshape(loghyper[-N * (M - 1) : ], (M-1, N)).conj().transpose()), axis=1)
    logqZ = logqZ - np.matmul(np.matrix((np.max(logqZ, axis = 1))).conj().transpose(), np.ones((1, M)))
    logqZ = logqZ - np.matmul(np.log(np.exp(logqZ).sum(axis=1)), np.ones((1, M)))
    qZ = np.exp(logqZ)
    sn2 = np.matmul(np.ones((N, 1)), np.matrix((np.exp(2 * loghyper[-N * (M - 1) - M : -N * (M - 1)]))))
    logpZ = np.concatenate(([0], np.array(loghyper[-N * (M - 1) -2 * M + 1 : -N * (M - 1) - M])), axis=0).conj().transpose()
    logpZ = logpZ - np.max(logpZ)
    logpZ = logpZ - np.log(np.exp(logpZ).sum(axis=0))
    logpZ = np.ones((N, 1)) * logpZ
    sqB = np.sqrt(np.divide(qZ, sn2))
    dlogqZ = np.zeros((N, M))

    # Contribution of independent (modified) GPs
    F = 0
    dF = np.zeros((loghyper.shape))

    hypstart = 1
    covfunc_array = np.asarray(covfunc)
    cm = covfunc_array.item(0)

    if cm == 'covNoise':
        numhyp = 1
        K = covNoiseCM(loghyper[0 : numhyp], X)
    elif cm == 'covSEiso':
        numhyp = 2
        K = covSEisoCM(loghyper[0 : numhyp], X)
    else:
        raise Warning('Covariance type not (yet) supported')
        
    for m in range(M):
        if len(covfunc_array) > 1:
            cm = covfunc_array.item(m)
            if cm == 'covNoise':
                numhyp = 1
                K = covNoiseCM(loghyper[hypstart : hypstart + numhyp], X)
            elif cm == 'covSEiso':
                numhyp = 2
                K = covSEisoCM(loghyper[hypstart : hypstart + numhyp], X)
            else:
                raise Warning('Covariance type not (yet) supported')
        else:
            hypstart = 1

        R = (np.linalg.cholesky(np.eye(N) + np.multiply(K, np.matmul(sqB[:, m], sqB[:, m].conj().transpose())))).conj().transpose()
        sqBY = np.multiply(np.matmul(sqB[:, m], np.ones((1, oD))), Y)
        v = np.linalg.solve(R.conj().transpose(), sqBY)
        if not np.allclose(np.dot(R.conj().transpose(), v), sqBY):
            raise Warning(" linalg.solve not successful")
        F = F + 0.5 * np.power(v, 2).sum() + oD * np.log(np.diag(R)).sum(axis=0)

        # Compute derivatives
        diag_sqB = np.zeros((N, N))
        np.fill_diagonal(diag_sqB, sqB[:, m])
        U = np.linalg.solve(R.conj().transpose(), diag_sqB)
        if not np.allclose(np.dot(R.conj().transpose(), U), diag_sqB):
            raise Warning(" linalg.solve not successful")
        alpha = np.matmul(U.conj().transpose(), v)
        
        diagW = (np.power((Y - np.matmul(K, alpha)), 2).sum(axis=1) + oD * (np.diag(K) - np.power(np.matmul(U, K), 2).sum(axis=0).conj().transpose()))[:,0]
  
        
        if learn != 'learnqZ':
            W = oD * np.matmul(U.conj().transpose(), U) - np.matmul(alpha, alpha.conj().transpose())                # precompute for convenience

            
            for i in range(numhyp):
                if cm == 'covNoise':
                    dF[i + hypstart - 1] = dF[i + hypstart - 1] + np.multiply(W, covNoiseDERIV(loghyper[hypstart -1 : hypstart + numhyp - 1], X, i+1)).sum() / 2
                elif cm == 'covSEiso':
                    dF[i + hypstart - 1] = dF[i + hypstart - 1] + np.multiply(W, covSEisoDERIV(loghyper[hypstart -1 : hypstart + numhyp - 1], X, i+1)).sum() / 2

                else:
                    raise Warning('Covariance type not (yet) supported')

            dF[- N * (M - 1) - M + m] = diagW.conj().transpose() * qZ[:, m] * np.exp(-2 * loghyper[- N * (M - 1) - M + m]) * -2 / 2 # diagW * dB/dsn2
            
        if learn != 'learnhyp':
            dlogqZ[:, m] = (np.divide(diagW, sn2[:, m]) / 2).flatten('F')
        

        hypstart = hypstart + numhyp

    if (hypstart + 2 * M + N * (M - 1) - 2) != len(loghyper):
            raise Warning('Incorrect number of parameters')

    KLZ = np.multiply(qZ, (logqZ - logpZ)).sum() # KL Divergence from the posterior to the prior on Z
    F = F + oD / 2 * (np.multiply(qZ, np.log(2 * np.pi * sn2))).sum() + KLZ

    if learn != 'learnhyp':
        dKLZlogpz = (-qZ + np.exp(logpZ)).sum(axis=0).conj().transpose()
        dF[-N * (M - 1) -2 * M + 1 : -N * (M - 1) - M] = dKLZlogpz[1 : ].flatten('K')  # Derivative wrt pZ
        dlogqZ = dlogqZ + logqZ - logpZ + oD / 2 * np.log(2 * np.pi * sn2) # Derivative wrt qZ
        dlogqZ = np.multiply(qZ, (dlogqZ - np.matmul(np.multiply(qZ, dlogqZ).sum(axis=1), np.ones((1, M))))) # Derivative wrt actual hyperparam "beta" defnining qZ
        dlogqZ = dlogqZ[:, 1:]
        dF[-N * (M - 1) : ] = dlogqZ.flatten('K')
    
    if learn != 'learnqZ':
        dF[-N * (M - 1) - M : -N * (M - 1)] = dF[-N * (M - 1) - M : -N * (M - 1)].flatten('K') + (oD / 2 * ((qZ * 2).sum(axis=0)).conj().transpose()).flatten('K') #Derivative wrt sn2

    
    return [F, dF]

def omgpboundB(loghyper, learn, covfunc, M, X, Y, Xs):
    """
    Computes the negative of the Marginalized Variational Bound (F) and its 
    derivatives wrt loghyper (dF).

    Parameters:
    loghyper: K hyperparameters, pZ, sn2 (M trajectories), logqZ
    learn: 'learnqZ', 'learnhyp', 'learnall'
    covfunc: Array of covariance functions. If it is a single one, it is shared.
    M: Number of trajectories
    X, Y, Xs: Inputs, outputs, test inputs

    (c) Miguel Lazaro-Gredilla 2010
    """

    # Initialize
    # [N, D] = X.shape
    [N, oD] = Y.shape

    logqZ = np.concatenate((np.zeros((N, 1)), np.reshape(loghyper[-N * (M - 1) : ], (M-1, N)).conj().transpose()), axis=1)
    logqZ = logqZ - np.matmul(np.matrix((np.max(logqZ, axis = 1))).conj().transpose(), np.ones((1, M)))
    logqZ = logqZ - np.matmul(np.log(np.exp(logqZ).sum(axis=1)), np.ones((1, M)))
    qZ = np.exp(logqZ)
    sn2 = np.matmul(np.ones((N, 1)), np.matrix((np.exp(2 * loghyper[-N * (M - 1) - M : -N * (M - 1)]))))
    logpZ = np.concatenate(([0], np.array(loghyper[-N * (M - 1) -2 * M + 1 : -N * (M - 1) - M])), axis=0).conj().transpose()
    logpZ = logpZ - np.max(logpZ)
    logpZ = logpZ - np.log(np.exp(logpZ).sum(axis=0))
    logpZ = np.ones((N, 1)) * logpZ
    sqB = np.sqrt(np.divide(qZ, sn2))
    dlogqZ = np.zeros((N, M))

    # Contribution of independent (modified) GPs
    F = np.zeros((Xs.shape[0], oD, M))
    dF = np.zeros((Xs.shape[0], oD, M))

    hypstart = 1
    covfunc_array = np.asarray(covfunc)
    cm = covfunc_array.item(0)

    if cm == 'covNoise':
        numhyp = 1
        K = covNoiseCM(loghyper[0 : numhyp], X)
    elif cm == 'covSEiso':
        numhyp = 2
        K = covSEisoCM(loghyper[0 : numhyp], X)
    else:
        raise Warning('Covariance type not (yet) supported')
        
    for m in range(M):
        if len(covfunc_array) > 1:
            cm = covfunc_array.item(m)
            if cm == 'covNoise':
                numhyp = 1
                K = covNoiseCM(loghyper[hypstart : hypstart + numhyp], X)
            elif cm == 'covSEiso':
                numhyp = 2
                K = covSEisoCM(loghyper[hypstart : hypstart + numhyp], X)
            else:
                raise Warning('Covariance type not (yet) supported')
        else:
            hypstart = 1

        R = (np.linalg.cholesky(np.eye(N) + np.multiply(K, np.matmul(sqB[:, m], sqB[:, m].conj().transpose())))).conj().transpose()
        sqBY = np.multiply(np.matmul(sqB[:, m], np.ones((1, oD))), Y)
        v = np.linalg.solve(R.conj().transpose(), sqBY)
        if not np.allclose(np.dot(R.conj().transpose(), v), sqBY):
            raise Warning(" linalg.solve not successful")

        # Compute derivatives
        diag_sqB = np.zeros((N, N))
        np.fill_diagonal(diag_sqB, sqB[:, m])
        U = np.linalg.solve(R.conj().transpose(), diag_sqB)
        if not np.allclose(np.dot(R.conj().transpose(), U), diag_sqB):
            raise Warning(" linalg.solve not successful")
        alpha = np.matmul(U.conj().transpose(), v)
        
        if cm == 'covNoise':
            [Kss, Kfs] = covNoiseTSC(loghyper[hypstart-1: hypstart + numhyp - 1], X, Xs)
        elif cm == 'covSEiso':
            [Kss, Kfs] = covSEisoTSC(loghyper[hypstart-1: hypstart + numhyp - 1], X, Xs)
        else:
            raise Warning('Covariance type not (yet) supported')
        
        F[:,:, m] = np.matmul(Kfs.conj().transpose(), alpha)
        dF[:,:,m] = (sn2[0, m] + Kss - np.power(np.matmul(U, Kfs), 2).sum(axis=0).conj().transpose()) * np.ones((1, oD))
            
        
        hypstart = hypstart + numhyp

    if (hypstart + 2 * M + N * (M - 1) - 2) != len(loghyper):
            raise Warning('Incorrect number of parameters')
    
    return [F, dF]

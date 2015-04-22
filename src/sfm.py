from mpl_toolkits.mplot3d import Axes3D
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import sys

def g(a, b):
    g = np.zeros(6)
    g[0] = a[0] * b[0]
    g[1] = a[0] * b[1] + a[1] * b[0]
    g[2] = a[0] * b[2] + a[2] * b[0]
    g[3] = a[1] * b[1]
    g[4] = a[1] * b[2] + a[2] * b[1]
    g[5] = a[2] * b[2]
    return np.atleast_2d(g)

epsilon = 1e-12
focus = 200

if __name__ == '__main__':
    # Step 1: Create the D matrix
    with open(sys.argv[1] + "features.txt", 'r') as f:
        frames, features, points = [int(x) for x in f.readline().split()]
        frames = 50
        D = np.zeros((frames * 2, features+1))

        for i in range(points):
            frame, feature, x, y = f.readline().split()
            frame, feature = int(frame), int(feature)
            if frame < frames:
                x, y = float(x), float(y)

                D[frame, feature] = x
                D[frame+frames, feature] = y

    # Remove all zeros (features not tracked across frames)
    D[D == 0] = np.NaN
    D = np.ma.compress_cols(np.ma.masked_invalid(D))

    # Step 2: Create the D-tilde matrix
    #
    # The code subtracts the mean of each row from each element
    # in the rows. Atleast_2d allows us to transpose the numpy
    # vector that is the sum across the rows.
    D_tilde = D - np.atleast_2d(D.sum(axis=1)).T / D.shape[0]

    # Step 3: SVD
    U, W, V = np.linalg.svd(D_tilde)

    U3 = U[:, 0:3]
    W3 = np.identity(3) * W[0:3]
    V3 = V[0:3, :]

    # Step 4: Compute R* and S*
    R_star = np.dot(U3, np.sqrt(W3))
    S_star = np.dot(np.sqrt(W3), V3)

    # Step 5: Solve for Orthogonality
    c = np.concatenate([np.ones(2 * frames), np.zeros(frames)])
    G = g(R_star[0, :], R_star[0, :])

    for i in range(1, frames):
        G = np.concatenate([G, g(R_star[i], R_star[i])], axis = 0)
    for i in range(frames):
        G = np.concatenate([G, g(R_star[frames+i], R_star[frames+i])], axis = 0)
    for i in range(frames):
        G = np.concatenate([G, g(R_star[i], R_star[frames+i])], axis = 0)

    G_inv = np.linalg.pinv(G)
    I = np.dot(G_inv, c)

    L = np.array([[I[0], I[1], I[2]], [I[1], I[3], I[4]], [I[2], I[4], I[5]]])

    #Q = np.linalg.cholesky(L)

    # Alternative to Cholesky Decomposition
    UL, SigmaL, ULT = np.linalg.svd(L)
    for i in range(SigmaL.shape[0]):
        if SigmaL[i] < 0:
            SigmaL[i] = epsilon
    Q = np.dot(UL, np.sqrt(np.identity(3) * SigmaL))

    R = np.dot(R_star, Q)
    S = np.dot(Q.T, S_star)

    axis1 = np.cross(R[0, :], R[2, :])
    axis2 = np.cross(R[1, :], R[3, :])

    # Output the Ceres file
    with open(sys.argv[1] + "output-features.txt", 'w') as file:
        ceres_output = "{0} {1} {2}\n".format(2, D.shape[1], 2*D.shape[1])
        for i, row in enumerate(D.T):
            ceres_output += "{0} {1} {2} {3}\n".format(0, i, row[0], row[2])
            ceres_output += "{0} {1} {2} {3}\n".format(1, i, row[1], row[3])
        for i in range(2 * 9):
            if i == 6 or i == 15:
                ceres_output += "200\n"
            else:
                ceres_output += "0\n"
        for i in S.T:
            ceres_output += "{0}\n{1}\n{2}\n".format(i[0], i[1], i[2])
        file.write(ceres_output)

    with open('points.txt', 'w') as file:
        output = ""
        for i in S.T:
            output += "{0}, {1}, {2}\n".format(i[0], i[1], i[2])
        file.write(output)

    # Plot results
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(S[0, :], S[1, :], S[2, :])
    plt.show()

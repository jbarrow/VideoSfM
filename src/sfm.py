from mpl_toolkits.mplot3d import Axes3D
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

def g(a, b):
    g = np.zeros(6)
    g[0] = a[0] * b[0]
    g[1] = a[0] * b[1] + a[1] * b[0]
    g[2] = a[0] * b[2] + a[2] * b[0]
    g[3] = a[1] * b[1]
    g[4] = a[1] * b[2] + a[2] * b[1]
    g[5] = a[2] * b[2]
    return np.atleast_2d(g)

if __name__ == '__main__':
    # Step 1: Create the D matrix
    with open('../hotel-dense-output/features.txt') as f:
        frames, features, points = [int(x) for x in f.readline().split()]
        D = np.zeros((frames * 2, features+1))

        for i in range(points):
            frame, feature, x, y = f.readline().split()
            frame, feature = int(frame), int(feature)
            x, y = float(x), float(y)

            D[frame, feature] = x
            D[frame+frames, feature] = y

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
    Q = np.linalg.cholesky(L)

    R = np.dot(R_star, Q)
    S = np.dot(Q.T, S_star)

    # Plot results
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(S[0, :], S[1, :], S[2, :])
    plt.show()

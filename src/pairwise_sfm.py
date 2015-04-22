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

class Scene:
    def __init__(self, point_file):
        with open(point_file, 'r') as f:
            self._frames, self._features, points = \
                [int(x) for x in f.readline().split()]
            self._D = np.zeros((self._frames * 2, self._features+1))

            for i in range(points):
                frame, feature, x, y = f.readline().split()
                frame, feature = int(frame), int(feature)
                if frame < self._frames:
                    x, y = float(x), float(y)

                    self._D[frame, feature] = x
                    self._D[frame+self._frames, feature] = y

    def stereographic(self, frames):
        count = len(frames)
        frames = frames + [frame+self._frames for frame in frames]

        D = self._D[frames, :]
        zeros = np.sum(D == 0, 0) == 0

        indices = np.arange(self._features+1)
        indices = indices[zeros]
        D = D[:, zeros]

        D_tilde = D - np.atleast_2d(D.sum(axis=1)).T / D.shape[0]

        U, W, V = np.linalg.svd(D_tilde)

        U3 = U[:, 0:3]
        W3 = np.identity(3) * W[0:3]
        V3 = V[0:3, :]

        R_star = np.dot(U3, np.sqrt(W3))
        S_star = np.dot(np.sqrt(W3), V3)

        c = np.concatenate([np.ones(len(frames)), np.zeros(count)])
        G = g(R_star[0, :], R_star[0, :])

        for i in range(1, count):
            G = np.concatenate([G, g(R_star[i], R_star[i])], axis = 0)
        for i in range(count):
            G = np.concatenate([G, g(R_star[count+i], R_star[count+i])], axis = 0)
        for i in range(count):
            G = np.concatenate([G, g(R_star[i], R_star[count+i])], axis = 0)

        G_inv = np.linalg.pinv(G)
        I = np.dot(G_inv, c)

        L = np.array([[I[0], I[1], I[2]], [I[1], I[3], I[4]], [I[2], I[4], I[5]]])

        UL, SigmaL, ULT = np.linalg.svd(L)
        for i in range(SigmaL.shape[0]):
            if SigmaL[i] < 0:
                SigmaL[i] = epsilon
        Q = np.dot(UL, np.sqrt(np.identity(3) * SigmaL))

        R = np.dot(R_star, Q)
        S = np.dot(Q.T, S_star)

        return (S, indices)

    def compute_transformation(self, old_points, new_points, new_indices):
        correspondences = old_points[:, new_indices]
        unknown = new_points[:, np.sum(correspondences, axis=0) == 0]
        empty = new_indices[np.sum(correspondences, axis=0) == 0]
        new_points = new_points[:, np.sum(correspondences, axis=0) != 0]
        correspondences = correspondences[:, np.sum(correspondences, axis=0) != 0]
        dim, points = correspondences.shape

        A = np.zeros((points*dim, 12))
        y = np.zeros((points*3, 1))

        # We want to estimate the affine transformation matrix, so:
        for i, row in enumerate(new_points.T):
            A[3*i, 0:3] = row
            A[3*i, 3] = 1
            A[3*i+1, 4:7] = row
            A[3*i+1, 7] = 1
            A[3*i+2, 8:11] = row
            A[3*i+2, 11] = 1

        for i, row in enumerate(correspondences.T):
            y[3*i:3*(i+1), 0] = row.T

        m = np.linalg.lstsq(A, y)[0]

        # Construct our affine transformation matrix
        M = np.zeros((4, 4))
        M[0:3, :] = m.reshape((3, 4))
        M[3, 3] = 1

        unknown = np.concatenate([unknown, np.ones((1, unknown.shape[1]))])

        old_points[:, empty] = np.dot(M, unknown)[0:3, :]
        return old_points

    def sfm(self):
        points = np.zeros((3, self._features+1))
        i = 0

        while np.sum(points == 0) > 0 and i < self._frames - 1:
            new_points, indices = self.stereographic([i, i+1])
            if i == 0:
                points[:, indices] = new_points
            else:
                points = self.compute_transformation(points, new_points, indices)
            i += 1

        points = points[:, np.sum(points, axis=0) != 0]
            
        self.plot(points)

    def plot(self, points):
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(points[0, :], points[1, :], points[2, :])
            plt.show()

if __name__ == '__main__':
    scene = Scene(sys.argv[1])
    scene.sfm()

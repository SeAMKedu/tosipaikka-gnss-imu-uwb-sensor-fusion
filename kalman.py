import numpy as np

import config


class KalmanFilter:
    """
    Kalman filter that uses a constant velocity model.

    :param float x0: Initial X position.
    :param float y0: Initial Y position.
    :param float z0: Initial Z position.
    :param float dt: Time step in seconds.

    """

    def __init__(self, x0: float, y0: float, z0: float, dt: float) -> None:
        # State x. Constant velocity model: x = [x ẋ y ẏ z ż]ᵀ
        self.x = np.array([x0, 0, y0, 0, z0, 0]).T
        # State transition function F.
        self.F = np.array([
            [1, dt, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, dt, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, dt],
            [0, 0, 0, 0, 0, 1]
        ])
        # Covariance matrix P.
        self.P = np.eye(6) * 100
        # Process noice matrix Q.
        self.Q = np.eye(6) * config.KF_Q_VARIANCE
        # Measurement function H.
        self.H = np.eye(6)
        # Measurement noice matrix R.
        self.R = np.diag([
            np.power(config.KF_STD_POS, 2),
            np.power(config.KF_STD_ACC, 2),
            np.power(config.KF_STD_POS, 2),
            np.power(config.KF_STD_ACC, 2),
            np.power(config.KF_STD_POS, 2),
            np.power(config.KF_STD_ACC, 2)
        ])
        # Identity matrix I.
        self.I = np.eye(6)


    def predict(self):
        """Predict the state x and covariance matrix P."""
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q


    def update(self, z: np.ndarray):
        """Update the state x and covariance matrix P."""
        # System uncertainty.
        S = self.H @ self.P @ self.H.T + self.R
        # Kalman gain.
        K = self.P @ self.H.T @ np.linalg.inv(S)
        # Residual.
        y = z - self.H @ self.x
        # State update.
        self.x = self.x + K @ y
        # Covariance matrix update.
        I_KH = self.I - K @ self.H
        self.P = I_KH @ self.P @ I_KH.T + K @ self.R @ K.T

import abc
import math


__all__ = ['SquaredLoss', 'LogLoss','AbsoluteLoss']


class Loss(abc.ABC):

    @abc.abstractmethod
    def __call__(self, y_true, y_pred) -> float:
        """Returns the loss."""
        pass

    @abc.abstractmethod
    def gradient(self, y_true, y_pred) -> float:
        """Returns the gradient."""
        pass

class AbsoluteLoss(Loss):
    """Computes the absolute loss, also known as the mean absolute error or L1 loss.

    Mathematically, it is defined as

    $$L = \\frac{1}{n} \\sum_i^n |p_i - y_i|$$

    It's gradient w.r.t. to $p_i$ is

    $$\\frac{\\partial L}{\\partial p_i} = sgn(p_i - y_i) $$
    
    """
    def __call__(self,y_true,y_pred):
        return abs(y_pred - y_true)
    
    def gradient(self,y_true,y_pred):
        if y_pred - y_true > 0:
            return 1
        elif y_pred - y_true == 0:
            return 0
        return -1

class SquaredLoss(Loss):
    """Computes the squared loss, also known as the L2 loss.

    Mathematically, it is defined as

    .. math:: L = (p_i - y_i)^2

    It's gradient w.r.t. to $p_i$ is

    .. math:: \\frac{\\partial L}{\\partial p_i} = 2(p_i - y_i)

    """
    def __call__(self, y_true, y_pred):
        return (y_pred - y_true) ** 2

    def gradient(self, y_true, y_pred):
        return 2 * (y_pred - y_true)


class LogLoss(Loss):
    """Computes the logarithmic loss.

    Mathematically, it is defined as

    .. math:: L = -y_i log(p_i) + (1-y_i) log(1-p_i)

    It's gradient w.r.t. to $p_i$ is

    .. math:: \\frac{\\partial L}{\\partial y_i} = sign(p_i - y_i)

    """

    @staticmethod
    def _clip_proba(p):
        return max(min(p, 1 - 1e-15), 1e-15)

    def __call__(self, y_true, y_pred):
        y_pred = self._clip_proba(y_pred)
        return -(y_true * math.log(y_pred) + (1 - y_true) * math.log(1 - y_pred))

    def gradient(self, y_true, y_pred):
        return self._clip_proba(y_pred) - y_true

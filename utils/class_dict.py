import numpy as np


class AttrDict(dict):
    __setattr__ = dict.__setitem__

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class ConfigDict(AttrDict):
    def __init__(self):
        self.name: str = None  # 流场名称
        self.flow_type: str = None  # 流场类型
        self.expand_flow: int = 0  # 流场扩大范围
        self.scale_flow: int = 1  # 缩放流场速度
        self.width: int = 0  # 流场宽度
        self.height: int = 0  # 流场高度
        self.flow: np.ndarray = None  # 流场
        self.img_save_num: int = 0  # 数据集保存的PIV图像数量（PSV图像数量为该值-1）
        self.img_save_interval: int = 0  # 每两张保存图像之间的PIV图像间隔数
        self.piv_img_total: int = 0  # PIV图像迭代数量
        self.piv_interval: float = 0  # PIV图像生成间隔
        self.psv_interval: float = 0  # PSV图像叠加间隔
        self.psv_filter: int = 1  #  PSV叠加均值图像的亮度增益
        self.dt: float = 0  # 迭代间隔
        self.density: float = 0  # 粒子密度
        self.d: float = 0  # 粒子平均直径
        self.d_std: float = 0  # 粒子直径标准差
        self.l: float = 0  # 粒子平均亮度
        self.l_std: float = 0  # 粒子亮度标准差
        self.noise: int = 0  # 图像高斯噪声值
        self.blur: int = 0  # 图像高斯模糊值(奇数)


class PointsInfo(AttrDict):
    def __init__(self):
        self.x: np.ndarray = np.array([])
        self.y: np.ndarray = np.array([])
        self.d: np.ndarray = np.array([])
        self.l: np.ndarray = np.array([])
        self.vx: np.ndarray = np.array([])
        self.vy: np.ndarray = np.array([])

    def Offset_coordinate(self, dx: int, dy: int):
        self.x = self.x + dx
        self.y = self.y + dy
        return self

    def concate(self, points: "PointsInfo"):
        if points.x.size == 0:
            return

        self.x = np.concatenate((self.x, points.x))
        self.y = np.concatenate((self.y, points.y))
        self.vx = np.concatenate((self.vx, points.vx))
        self.vy = np.concatenate((self.vy, points.vy))
        self.d = np.concatenate((self.d, points.d))
        self.l = np.concatenate((self.l, points.l))

        return self

    def Delete_Points(self, mask: np.ndarray):
        self.x = self.x[mask]
        self.y = self.y[mask]
        self.vx = self.vx[mask]
        self.vy = self.vy[mask]
        self.d = self.d[mask]
        self.l = self.l[mask]

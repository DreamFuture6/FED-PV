import numpy as np
from utils.smoothn import smoothn


def Read_Flow(file_path, config):
    with open(file_path, "rb") as f:
        check = np.fromfile(f, dtype=np.float32, count=1)[0]

        if check != np.float32(202021.25):
            raise SystemExit("读取的文件头信息错误")

        o_width = np.fromfile(f, dtype=np.int32, count=1)[0]
        o_height = np.fromfile(f, dtype=np.int32, count=1)[0]

        data_size = o_width * o_height * 2

        data = np.fromfile(f, dtype=np.float32, count=data_size)

        data = data.reshape((o_height, o_width, 2)) * max(1, config.scale_flow)

    n_width, n_height, data = Expend_Flow(config.expand_flow, data)

    return n_width, n_height, data


def Expend_Flow(l, data):
    vx1 = np.pad(data[:, :, 0], pad_width=((l, l), (l, l)), mode="constant", constant_values=np.nan)
    vy1 = np.pad(data[:, :, 1], pad_width=((l, l), (l, l)), mode="constant", constant_values=np.nan)

    [w, h] = vx1.shape
    for i in range(w):
        for j in range(h):
            vx1[i, j] = vx1[min(max(i, l), w - l - 1), min(max(j, l), h - l - 1)]
            vy1[i, j] = vy1[min(max(i, l), w - l - 1), min(max(j, l), h - l - 1)]

    vx2 = smoothn(vx1, s=0.05, isrobust=True)[0]
    vy2 = smoothn(vy1, s=0.05, isrobust=True)[0]

    vx2[l:-l, l:-l] = data[:, :, 0]
    vy2[l:-l, l:-l] = data[:, :, 1]

    vx3 = smoothn(vx2, s=0.01, isrobust=True)[0]
    vy3 = smoothn(vy2, s=0.01, isrobust=True)[0]

    vx3[l:-l, l:-l] = data[:, :, 0]
    vy3[l:-l, l:-l] = data[:, :, 1]

    return w, h, np.stack((vx3, vy3), axis=-1)

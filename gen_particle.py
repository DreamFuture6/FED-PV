import numpy as np
import scipy.special as ss
import save_file as sf
import utils.progress_bar as pbar
import cv2
from utils.class_dict import *


def Random_Particle(width: int, height: int, config: ConfigDict):
    num = int(width * height * config.density + 0.5)

    points = PointsInfo()
    points.x = np.random.uniform(0, width, num)
    points.y = np.random.uniform(0, height, num)
    points.vx = np.zeros(num)
    points.vy = np.zeros(num)
    points.d = np.abs(np.random.randn(num) * config.d_std + config.d)
    points.l = np.abs(np.random.randn(num) * config.l_std + config.l)

    return points


def Particle_Init(config: ConfigDict):
    block_size = config.expand_flow // 2
    offset_mask = np.where(np.ones((config.width // block_size, config.height // block_size), dtype=bool))
    points = PointsInfo()
    for i in range(offset_mask[0].size):
        new_points = Random_Particle(block_size, block_size, config).Offset_coordinate(
            offset_mask[1][i] * block_size, offset_mask[0][i] * block_size
        )
        points.concate(new_points)
    return points


def Adjust_Particle(config: ConfigDict, points: PointsInfo, image: np.ndarray):
    mask = (points.x >= 0) & (points.y >= 0) & (points.x <= config.width - 1) & (points.y <= config.height - 1)
    points.Delete_Points(mask)

    block_size = config.expand_flow // 2
    sum_shape = (image.shape[0] // block_size, image.shape[1] // block_size, block_size, block_size)

    blocks_mean = np.lib.stride_tricks.as_strided(
        image[: image.shape[0] // 10 * 10, : image.shape[1] // 10 * 10],
        shape=sum_shape,
        strides=image.itemsize * np.array([image.shape[1] * block_size, block_size, image.shape[0], 1]),
    ).mean(axis=(2, 3))

    outer_mask = np.ones((sum_shape[0], sum_shape[1]), dtype=bool)
    outer_mask[1:-1, 1:-1] = False
    insert_area = np.where((blocks_mean <= 2) & outer_mask)

    is_opt = False
    expand_insert_area = block_size * config.flow.max() // 18000
    insert_points = PointsInfo()
    for i in range(insert_area[0].size):
        x_flag, y_flag = 0, 0
        if insert_area[0][i] == 0:
            x_flag = 1
            y_flag = -0.5
        elif insert_area[0][i] == insert_area[0][i].max():
            x_flag = -1
            y_flag = -0.5
        if insert_area[1][i] == 0:
            x_flag = -0.5
            y_flag = 1
        elif insert_area[1][i] == insert_area[1][i].max():
            x_flag = -0.5
            y_flag = -1
        new_points = Random_Particle(
            block_size + expand_insert_area, block_size + expand_insert_area, config
        ).Offset_coordinate(
            insert_area[1][i] * block_size + expand_insert_area * x_flag,
            insert_area[0][i] * block_size + expand_insert_area * y_flag,
        )
        is_opt = True
        insert_points.concate(new_points)
    points.concate(insert_points)

    return is_opt


def Bilinear_Interpolate(flow: np.ndarray, x: np.ndarray, y: np.ndarray):
    x1, y1 = np.floor(x).astype(int), np.floor(y).astype(int)
    x2, y2 = x1 + 1, y1 + 1

    x1 = np.clip(x1, 0, flow.shape[0] - 1)
    x2 = np.clip(x2, 0, flow.shape[0] - 1)
    y1 = np.clip(y1, 0, flow.shape[1] - 1)
    y2 = np.clip(y2, 0, flow.shape[1] - 1)

    v11 = flow[y1, x1]
    v12 = flow[y2, x1]
    v21 = flow[y1, x2]
    v22 = flow[y2, x2]

    w11 = (x2 - x) * (y2 - y)
    w12 = (x2 - x) * (y - y1)
    w21 = (x - x1) * (y2 - y)
    w22 = (x - x1) * (y - y1)

    v = w11[:, np.newaxis] * v11 + w12[:, np.newaxis] * v12 + w21[:, np.newaxis] * v21 + w22[:, np.newaxis] * v22

    return np.transpose(np.round(v, 7 if flow.dtype == np.float32 else 15))  # 保持与流场相同的精度


def Arc_Fitting(config: ConfigDict, points: PointsInfo):
    x0, y0 = points.x, points.y
    vx0, vy0 = points.vx, points.vy

    points.x = x0 + vx0 * config.dt
    points.y = y0 + vy0 * config.dt

    [points.vx, points.vy] = Bilinear_Interpolate(config.flow, points.x, points.y)


def Gen_Gray_Frame(config: ConfigDict, points: PointsInfo):
    image = np.zeros((config.height, config.width))
    xrange, yrange = np.meshgrid(np.arange(config.width), np.arange(config.height))

    for x, y, d, l in zip(points.x, points.y, points.d, points.l):
        x1 = int(min(max(0, x - 3 * d - 2), config.width - 6 * d - 3))
        y1 = int(min(max(0, y - 3 * d - 2), config.height - 6 * d - 3))
        x2 = x1 + int(6 * d + 3)
        y2 = y1 + int(6 * d + 3)

        lx = xrange[y1:y2, x1:x2] - x
        ly = yrange[y1:y2, x1:x2] - y

        b = d / np.sqrt(8)
        area = (
            (ss.erf((lx + 0.5) / b) - ss.erf((lx - 0.5) / b))
            * (ss.erf((ly + 0.5) / b) - ss.erf((ly - 0.5) / b))
            / (1.5 * (ss.erf(0.5 / b) - ss.erf(-0.5 / b)) ** 2)
        )

        image[y1:y2, x1:x2] = image[y1:y2, x1:x2] + area * l

    image = np.round(image * 255)

    return image


def Gen_Particle_Seq(config: ConfigDict):
    update_interval = config.expand_flow // 3 / np.max(config.flow)
    update_time = 0

    points = Particle_Init(config)
    [points.vx, points.vy] = Bilinear_Interpolate(config.flow, points.x, points.y)

    currNum, _pivdt, _psvdt, save_interval, save_index = 0, 0, 0, 0, 0

    PIV_image, PSV_image = None, np.zeros((config.height, config.width))
    start_save_img_tick = config.piv_img_total - int(config.img_save_num * config.img_save_interval + 0.5)

    pbar.Progress_Bar_Show(0, config)

    while True:

        Arc_Fitting(config, points)

        judge1 = _pivdt + config.dt / 2 >= config.piv_interval
        judge2 = _psvdt + config.dt / 2 >= config.psv_interval

        if judge1 or judge2:

            PIV_image = Gen_Gray_Frame(config, points)

            if update_time > update_interval:
                if Adjust_Particle(config, points, PIV_image):
                    update_time -= update_interval
                else:
                    update_time -= config.piv_interval

            if config.noise > 0:
                PIV_image += np.random.normal(0, config.noise, PIV_image.shape)
                PIV_image[PIV_image > 255] = 255
                PIV_image[PIV_image < 0] = 0
            if config.blur > 0:
                PIV_image = cv2.GaussianBlur(PIV_image, (config.blur, config.blur), 0)

        if judge1:

            _pivdt -= config.piv_interval
            sf.Add_Evt_Process_Data(config, PIV_img=PIV_image)

            if save_interval == config.img_save_interval - 1:

                if currNum >= start_save_img_tick:

                    sf.Save_Image(f"{config.name}-PIV-{save_index}", config, PIV_img=PIV_image)

                    if save_index != 0:
                        PSV_image = (PSV_image // config.img_save_interval) * config.psv_filter
                        PSV_image[PSV_image > 255] = 255
                        PSV_image[PSV_image < 0] = 0
                        sf.Save_Image(f"{config.name}-PSV-{save_index-1}", config, PSV_img=PSV_image)

                    PSV_image = np.zeros((config.height, config.width))
                    save_index += 1

                save_interval = 0
            else:
                save_interval += 1

            if currNum < config.piv_img_total - 1:
                currNum += 1
            else:
                break

        if judge2:
            _psvdt -= config.psv_interval
            PSV_image += PIV_image

        _pivdt += config.dt
        update_time += config.dt
        if currNum >= start_save_img_tick:
            _psvdt += config.dt

        pbar.Progress_Bar_Show(currNum + 1, config)

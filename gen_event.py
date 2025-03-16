import numpy as np


class EventList:
    def __init__(self, time, x, y, polarity):
        self.time = round(float(time), 8)
        self.x = int(x)
        self.y = int(y)
        self.polarity = int(polarity)


def gen_event(img_data):

    images = img_data + 5
    time_interval = 0.001 / 10

    images = np.log10(images)

    threshold = np.log10(1.25)

    height, width = images[0].shape
    event_list = []
    img_lux_ref = images[0].copy()
    img_time_ref = np.zeros((height, width))
    num = 0
    for i in range(1, 151):
        dl = images[i] - img_lux_ref
        for y in range(height):
            for x in range(width):
                if dl[y, x] >= threshold:
                    count = int(dl[y, x] // threshold)
                    line_k = (images[i][y, x] - images[i - 1][y, x]) / time_interval
                    for j in range(count):
                        if line_k == 0:
                            continue
                        if j == 0:
                            time_suppose = (
                                img_lux_ref[y, x] + threshold - images[i - 1][y, x]
                            ) / line_k + time_interval * (i - 1)
                        else:
                            time_suppose = threshold / line_k + img_time_ref[y, x]
                        event_list.append(EventList(time_suppose, x, y, 1))
                        img_lux_ref[y, x] = img_lux_ref[y, x] + threshold
                        img_time_ref[y, x] = time_suppose
                        num += 1
                if dl[y, x] <= -threshold:
                    count = int(-dl[y, x] // threshold)
                    line_k = (images[i][y, x] - images[i - 1][y, x]) / time_interval
                    for j in range(count):
                        if line_k == 0:
                            continue
                        if j == 0:
                            time_suppose = (
                                img_lux_ref[y, x] - threshold - images[i - 1][y, x]
                            ) / line_k + time_interval * (i - 1)
                        else:
                            time_suppose = -threshold / line_k + img_time_ref[y, x]
                        event_list.append(EventList(time_suppose, x, y, 0))
                        img_lux_ref[y, x] = img_lux_ref[y, x] - threshold
                        img_time_ref[y, x] = time_suppose
                        num += 1

    event_list.sort(key=lambda event0: event0.time)

    event_list = [
        EventList(event.time * 1e6, event.x, event.y, event.polarity)
        for event in event_list
    ]

    return event_list

import os
import cv2
import h5py
import numpy as np
import gen_event as ge
import matplotlib.pyplot as plt
from struct import pack
from utils.class_dict import *

PIV_data = None
dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
evt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evt")


def Build_Folder(flow_type: str):
    dir_name = os.path.join(dataset_path, flow_type)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def Save_Image(name: str, config: ConfigDict, PIV_img=None, PSV_img=None):
    if PIV_img is not None:
        cv2.imwrite(
            os.path.join(dataset_path, config.flow_type, f"{name}.png"),
            PIV_img[config.expand_flow : -config.expand_flow, config.expand_flow : -config.expand_flow],
        )
    if PSV_img is not None:
        cv2.imwrite(
            os.path.join(dataset_path, config.flow_type, f"{name}.png"),
            PSV_img[config.expand_flow : -config.expand_flow, config.expand_flow : -config.expand_flow],
        )


def Save_Flow_Info(config: ConfigDict):
    # np.savez(
    #     os.path.join(dataset_path, config.flow_type, f"{config.name}.npz"),
    #     flow=config.flow[config.expand_flow : -config.expand_flow, config.expand_flow : -config.expand_flow],
    # )

    data = config.flow[config.expand_flow : -config.expand_flow, config.expand_flow : -config.expand_flow]
    with open(os.path.join(dataset_path, config.flow_type, f"{config.name}.flo"), "wb") as f:
        np.array([202411.22], dtype=np.float32).tofile(f)
        np.array([data.shape[0]], dtype=np.uint32).tofile(f)
        np.array([data.shape[1]], dtype=np.uint32).tofile(f)
        np.array(data.flatten(), dtype=np.float32).tofile(f)


def Add_Evt_Process_Data(config: ConfigDict, PIV_img=None):
    global PIV_data
    if PIV_img is not None:
        PIV_img = PIV_img[config.expand_flow : -config.expand_flow, config.expand_flow : -config.expand_flow]
        if PIV_data is not None:
            PIV_data = np.append(PIV_data, [PIV_img], axis=0)
        else:
            PIV_data = np.array([PIV_img])


def Save_Evt_Data(config: ConfigDict):
    global PIV_data

    dir_name = os.path.join(evt_path, config.flow_type)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    event_list = ge.gen_event(PIV_data)
    evDict = {
        "t": np.array([event.time for event in event_list]),
        "x": np.array([event.x for event in event_list]),
        "y": np.array([event.y for event in event_list]),
        "p": np.array([event.polarity for event in event_list]),
        "time_stamp": 0,
        "image_size": [PIV_data[0].shape[0], PIV_data[0].shape[1]],
    }

    if True:
        start_time = 1000
        end_time = 2000

        event_image = np.ones((256, 256, 3), dtype=np.uint8) * 255

        filtered_events = [event for event in event_list if start_time <= event.time <= end_time]

        for event in filtered_events:
            if event.polarity == 1:
                event_image[event.y, event.x] = [255, 0, 0]
            else:
                event_image[event.y, event.x] = [0, 0, 255]

        plt.imshow(event_image)
        plt.title(f"Events from {start_time}s to {end_time}s")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.savefig(os.path.join(evt_path, config.flow_type, config.name.split(".")[0]) + ".png")

    if True:
        fnOUT = os.path.join(dataset_path, config.flow_type, config.name.split(".")[0]) + ".h5"
        t = np.round(evDict["t"]).astype(np.uint16)

        with h5py.File(fnOUT, "w") as file:
            events_group = file.create_group("events")
            events_group.create_dataset("p", data=evDict["p"], dtype=np.uint8)
            events_group.create_dataset("t", data=t, dtype=np.uint16)
            events_group.create_dataset("x", data=evDict["x"], dtype=np.uint8)
            events_group.create_dataset("y", data=evDict["y"], dtype=np.uint8)

            info_group = file.create_group("info")
            info_group.create_dataset("time_stamp", data=0, dtype=np.uint16)
            info_group.create_dataset("image_size", data=evDict["image_size"], dtype=np.uint16)

    if True:
        fnOUT = os.path.join(evt_path, config.flow_type, config.name.split(".")[0]) + ".evt"
        offset, duration = 0, 0

        t1 = offset
        t2 = t1 + duration
        t_max = evDict["t"].max() + 1
        if duration <= 0:
            t2 = t_max
        timIdx = np.where((evDict["t"] >= t1) & (evDict["t"] <= t2))
        evTime_OUT = evDict["t"][timIdx]
        packedData = (
            (evDict["x"][timIdx])
            | (evDict["y"][timIdx] << 16)
            | (evTime_OUT.astype(np.int64) << 33)
            | (evDict["p"][timIdx].astype(np.int64) << 32)
        )
        h, w = evDict["image_size"]
        duration = evTime_OUT.max() - t1
        header = pack(
            "4s3Q4L2Q",
            b"EVT3",
            64 + (evTime_OUT.size * 8),
            evTime_OUT.size,
            int(evDict["time_stamp"]),
            int(duration),
            64,
            w,
            h,
            0,
            0,
        )
        with open(fnOUT, "wb") as binary_file:
            nBytesWritten = binary_file.write(header)
            nBytesWritten2 = binary_file.write(packedData)
            binary_file.close()
            print(
                "Wrote %d events of duration %gms into EVT file with (%d+%d) bytes"
                % (evTime_OUT.size, (duration / 1000), nBytesWritten, nBytesWritten2)
            )

    PIV_data = None

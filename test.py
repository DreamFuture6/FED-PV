import numpy as np

if __name__ == "__main__":

    path = r"D:\Data\vscode\PIV\_Datasets\main\dataset\cylinder\cylinder_Re150_00001_flow.flo"

    with open(path, "rb") as f:
        check = np.fromfile(f, dtype=np.float32, count=1)[0]
        print(type(check),type(202411.22),check != 202411.22)

        if check != np.float32(202411.22):
            raise SystemExit("读取的文件头信息错误")

        o_width = np.fromfile(f, dtype=np.int32, count=1)[0]
        o_height = np.fromfile(f, dtype=np.int32, count=1)[0]

        data_size = o_width * o_height * 2

        data = np.fromfile(f, dtype=np.float32, count=data_size)

        data = data.reshape((o_height, o_width, 2))


from read_flow import Read_Flow
import gen_particle as gp
import save_file as sf
import utils.progress_bar as pbar
from utils.class_dict import *
from utils.progress_bar import *
import os


def gen_dataset(_path, _type):

    config = ConfigDict()
    config.name = os.path.splitext(os.path.basename(_path))[0]
    config.flow_type = _type
    config.expand_flow = 16
    config.scale_flow = 1200
    config.width, config.height, config.flow = Read_Flow(_path, config)
    config.img_save_num = 4
    config.piv_img_total = 150
    config.img_save_interval = 10
    config.piv_interval = 1e-4
    config.psv_interval = 1e-4
    config.psv_filter = 3
    config.dt = 2e-5
    config.density = 0.06
    config.d = 1.4
    config.d_std = 0.1
    config.l = 0.75
    config.l_std = 0.1
    config.noise = 0
    config.blur = 0

    sf.Save_Flow_Info(config)

    gp.Gen_Particle_Seq(config)

    sf.Save_Evt_Data(config)

    pbar.Next_Progress_Bar(config)


def main(path):

    dataset_path = []

    for i in os.scandir(path):
        if i.is_dir():
            for j in os.scandir(i.path):
                if j.is_file() and j.path.endswith(".flo"):
                    dataset_path.append(j.path)

    Init_Progress_Bar(len(dataset_path))

    for f in dataset_path:
        flow_type = os.path.basename(os.path.dirname(f))
        sf.Build_Folder(flow_type)
        gen_dataset(f, flow_type)


if __name__ == "__main__":

    main(os.path.join(os.path.dirname(os.path.abspath(__file__)), "flow_sets"))

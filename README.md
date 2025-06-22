# FED-PV: A large scale synthetic frame/event dataset for particle-based velocimetry.

## Description

This is code accompanying the dataset ~~and paper~~ by Xiang Feng, Fan Wu and Aoyu Zhang.

## Dataset Presentation

The following are the three flow fields in our dataset, which are (a) Cylinder, (b) JHTDB, and (c) Backstep.
![image](https://github.com/DreamFuture6/FED-PV/blob/main/FigDatasetShow.png?raw=true)


Each data item contains four grayscale particle images, 15 ms of event data, and the corresponding ground-truth motion field. For example:

> \cylinder\cylinder_Re150_00001_flow-PIV-0.png
> \cylinder\cylinder_Re150_00001_flow-PIV-1.png
> \cylinder\cylinder_Re150_00001_flow-PIV-2.png
> \cylinder\cylinder_Re150_00001_flow-PIV3.png
> \cylinder\cylinder_Re150_00001_flow.h5
> \cylinder\cylinder_Re150_00001_flow.flo

## Install

The dataset is publicly available on the OneDrive platform:

> URL: https://1drv.ms/f/c/b5123d043eaaea38/Esyx_kKJJaVNv3AgLJzcISEBGLji58gVUJqrTs4O9OAhog?e=161kuT
> Password: FEDPV666

## Directory structure

```
main   
├─ flow_sets
│  └─ [flow field name]   
│     └─ *.flo 
├─ dataset   
│  └─ [flow field name]   
│     └─ *.png, *.h5   
├─ evt   
│  └─ [flow field name] 
│     └─ *.pnd, *.evt   
├─ utils   
│  ├─ class_dict.py  
│  ├─ plot.py  
│  ├─ progress_bar.py  
│  └─ smoothn.py  
├─ gen_event.py  
├─ gen_particle.py   
├─ main_dataset.py
├─ read_flow.py 
└─ save_file.py   

```

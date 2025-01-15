import matplotlib.pyplot as plt
import numpy as np


def plot_flow(config):
    vx = config.flow[:, :, 0]
    vy = config.flow[:, :, 1]
    plt.subplot(121)
    plt.imshow(vx, interpolation="Nearest", vmin=np.min(vx), vmax=np.max(vx))
    plt.title("Flow Vx")
    plt.subplot(122)
    plt.imshow(vy, interpolation="Nearest", vmin=np.min(vy), vmax=np.max(vy))
    plt.title("Flow Vy")
    plt.show()

    xrange, yrange = np.meshgrid(np.arange(config.height / 10), np.arange(config.width / 10))
    plt.quiver(xrange, yrange, config.flow[::10, ::10, 0], config.flow[::10, ::10, 1], 5)
    plt.gca().invert_yaxis()
    plt.show()


def plot_grayimage(image, l):
    view_image = image[l:-l, l:-l]
    plt.figure()
    plt.imshow(view_image, vmax=255, vmin=0)
    plt.show()


# data第一维对应x轴参数，第二维为每个x值的数据集
def plot_boxplot(xlabel, ylabel, xnames, data):

    plt.boxplot(data, showfliers=False)
    plt.xticks([i for i in range(1, len(data) + 1)], xnames)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # plt.xlabel('Groups')
    # plt.legend(["Background free"])
    # plt.grid("on")

    plt.show()


# data第一维为数据对比数量，第二维为每个类型的数据集
def plot_histograms(xlabel, ylabel, data, datanames, bins: int = 30, showLegend: bool = True):

    for i in range(len(data)):
        plt.hist(data[i], histtype="stepfilled", bins=bins, alpha=0.6, density=True, label=datanames[i])

    if showLegend:
        plt.legend(loc="best")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


# xdata为所有点的x坐标列表，ydata为所有点的y坐标列表
def plot_scatter(xlabel, ylabel, xdata, ydata, show_distr: bool = False, color="cornflowerblue", style="s"):

    if show_distr:
        fig = plt.figure(figsize=(6, 6))
        grid = plt.GridSpec(4, 4, hspace=0.6, wspace=0.6)
        main_ax = fig.add_subplot(grid[:-1, 1:])
        y_hist = fig.add_subplot(grid[:-1, 0], xticklabels=[], yticklabels=[])
        x_hist = fig.add_subplot(grid[-1, 1:], xticklabels=[], yticklabels=[])

        main_ax.plot(xdata, ydata, "ok", markersize=3, alpha=0.3, mec="none")

        x_hist.hist(xdata, 40, histtype="stepfilled", orientation="vertical", color="gray")
        x_hist.invert_yaxis()
        x_hist.tick_params(bottom=False, top=False, left=False, right=False)
        x_hist.set_xticks([])
        x_hist.set_yticks([])

        y_hist.hist(ydata, 40, histtype="stepfilled", orientation="horizontal", color="gray")
        y_hist.invert_xaxis()
        y_hist.tick_params(bottom=False, top=False, left=False, right=False)
        y_hist.set_xticks([])
        y_hist.set_yticks([])

    else:
        plt.plot(
            xdata, ydata, alpha=0.6, ls="none", marker=style, markersize=3, mfc=color, mec="none"
        )  # marker标记：https://www.runoob.com/matplotlib/matplotlib-marker.html
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    plt.show()


# data第一维为数据对比数量，第二维对应x轴参数
def plot_bargraphs(xlabel, ylabel, xnames, data, datanames, showLegend: bool = True):

    num = len(data)
    x = np.arange(len(data[0]))
    width = 0.6 / num
    for i in range(num):
        plt.bar(x + width * i, data[i], width, color=f"C{i}", label=datanames[i])

    if showLegend:
        plt.legend(loc="best")
    plt.xticks(x + 0.3 * (num - 1) / num, labels=xnames)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


# xdata第一维为数据对比数量，第二维为所有点的x坐标列表
# ydata第一维为数据对比数量，第二维为所有点的y坐标列表
def plot_linechart(xlabel, ylabel, xdata, ydata, datanames, showLegend: bool = True):

    linestyles = ["solid", "dotted", "dashed", "dashdot"]
    markers = ["o", "^", "s", "x", "h", "*"]
    for i in range(len(ydata)):
        plt.plot(xdata[i], ydata[i], marker=markers[i % 5], linestyle=linestyles[i % 4], label=datanames[i])

    if showLegend:
        plt.legend(loc="best")  # frameon=False
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


if __name__ == "__main__":
    # plt.style.use('default') # 默认布局，下方和左侧有刻度线（朝外）
    # plt.style.use('classic') # 经典布局，四周都显示刻度线（朝内）
    # plt.style.use('Solarize_Light2') # 淡黄色背景，白色实线方格
    # plt.style.use('bmh') # 下方和左侧有刻度线，刻度线朝内，方格面板，格线是虚线
    # plt.style.use('dark_background') # 黑色背景，下方和左侧有刻度线（朝外）
    # plt.style.use('fivethirtyeight') # 无坐标轴线，无刻度，方格面板，绘图线条较粗
    # plt.style.use('ggplot') # 灰色方格面板，格线是白色实线
    # plt.style.use('grayscale') # 黑白图
    # plt.style.use('seaborn') # 无刻度线，白色实线方格面板（面板是浅色）
    # plt.style.use('seaborn-ticks') # 刻度线稍长

    group1 = np.random.normal(0, 1, 100)
    group2 = np.random.normal(2, 1.5, 100)
    group3 = np.random.normal(-1, 2, 100)
    plot_boxplot("", "Test", ["A", "B", "C"], [group1, group2, group3])

    data1 = []
    for a, b in ((10, 10), (4, 12), (50, 12)):
        data1.append(np.random.beta(a, b, size=1000))
    plot_histograms("", "Test", data1, ["A", "B", "C"])

    data2 = np.random.normal(loc=0.75, scale=0.25, size=(2, 1000))
    plot_scatter("X", "Y", data2[0], data2[1])
    plot_scatter("X", "Y", data2[0], data2[1], show_distr=True)

    plot_bargraphs("", "Y", ["A", "B", "C", "D", "E"], np.random.randint(5, 25, size=(3, 5)), ["1", "2", "3"])

    plot_linechart(
        "X",
        "Y",
        [[j for j in range(1, 11)] for i in range(3)],
        np.random.normal(loc=3, scale=5, size=(3, 10)),
        ["1", "2", "3"],
    )

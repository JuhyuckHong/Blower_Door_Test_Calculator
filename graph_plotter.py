import matplotlib.pyplot as plt

def plot_graph(results):
    # 데이터 설정
    x = range(10, 65)
    y, y_low, y_high = zip(*[results["volumetric flow rate"](i) for i in x])

    # 창 크기 고정 - 픽셀 단위
    width_px = 600  
    height_px = 500  
    dpi = 80  # 인치당 픽셀 (dots per inch)
    plt.figure(figsize=(width_px/dpi, height_px/dpi))

    # x 축 설정
    plt.xscale("log")
    plt.xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], [10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    plt.xlim(10, 100)

    # y 축 설정
    plt.yscale("log")
    plt.yticks([10, 100, 1000, 10000], [10, 100, 1000, 10000])
    plt.ylim(10, 10000)

    # 데이터 플롯
    x_values, y_values = zip(*results["measured values"])
    plt.scatter(x_values, y_values, label="measured", color='green', marker='x', zorder=10)
    plt.plot(x, y, label="derived", color='red', linewidth=1, alpha=0.9)
    plt.plot(x, y_low, label="lower CI", color='orange', linewidth=1, alpha=1)
    plt.plot(x, y_high, label="upper CI", color='blue', linewidth=1, alpha=1)

    # 보조선 추가
    plt.grid(True, which="both", linestyle="--", linewidth=1, color="gray", alpha=0.5)

    # 축 레이블 설정
    plt.xlabel('Measured pressure difference [Pa]')
    plt.ylabel('Measured volumetric flow rate [㎥/s]')

    # 제목 설정
    plt.title('Blower Door Test Result')

    # 범례 표시
    plt.legend(loc="upper left")

    # 그래프 보이기
    plt.show(block=False)
    plt.pause(20)
    plt.close()

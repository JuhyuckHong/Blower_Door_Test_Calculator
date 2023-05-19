import matplotlib.pyplot as plt
from matplotlib import font_manager
import matplotlib.ticker as ticker


def plot_graph(results):
    # 폰트 설정
    font_path = './NanumSquare_acL.ttf'
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    plt.rc('font', family=font_name)

    # 창 크기 고정 - 픽셀 단위
    width_px = 600  
    height_px = 500  
    dpi = 80  # 인치당 픽셀 (dots per inch)
    plt.figure(figsize=(width_px/dpi, height_px/dpi))

    # x 축 설정
    plt.xscale("log")
    plt.xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 
               [10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    plt.tick_params(axis='x', direction='in')
    plt.xlim(10, 100)

    # y 축 설정
    plt.yscale("log")
    plt.yticks([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
               [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
    plt.tick_params(axis='y', direction='in')
    plt.ylim(100, 1000)


    # 데이터 플롯
    # 측정값
    x_values, y_values = zip(*results["measured values"])
    # 계산값
    x = range(int(min(x_values) - 4), int(max(x_values) + 15))
    y, y_pi_l, y_pi_u, y_ci_l, y_ci_u = zip(*[results["volumetric flow rate"](i) for i in x])

    plt.scatter(x_values, y_values, label="measured", color='green', marker='x', zorder=10)
    plt.plot(x, y, label="derived", color='green', linewidth=1.5, alpha=1)
    plt.plot(x, y_pi_l, label="95% Prediction Band", color='red', linewidth=0.5, alpha=1, linestyle=':')
    plt.plot(x, y_pi_u, color='red', linewidth=1, alpha=1, linestyle=':')
    plt.plot(x, y_ci_l, label="95% Confidence Region", color='blue', linewidth=0.5, alpha=1, linestyle=':')
    plt.plot(x, y_ci_u, color='blue', linewidth=1, alpha=0.5, linestyle=':')
    # 예측구간 사이 영역 색칠
    plt.fill_between(x, y_pi_l, y_pi_u, color='red', alpha=0.1)
    # 신뢰구간 사이 영역 색칠
    plt.fill_between(x, y_ci_l, y_ci_u, color='blue', alpha=0.1)
    # 보조선 추가
    plt.grid(True, which="both", linestyle="--", linewidth=1, color="gray", alpha=0.5)
    # 축 레이블 설정
    plt.xlabel('내외부 압력차 [Pa]', labelpad=20)
    plt.ylabel('침기량\n(누기량)\n[㎥/s]', rotation='horizontal', labelpad=20, linespacing=2)
    # 제목 설정
    plt.title('기밀 시험 결과', fontsize=18, pad=20)
    # 그래프와 제목 사이 간격 조정
    plt.subplots_adjust(top=0.9, bottom=0.15, left=0.15)
    # 범례 표시
    plt.legend(loc="upper left")
    # 50 Pa 라인 그리기
    plt.axvline(x=50, color='green', linewidth=0.3, linestyle='-')
    plt.axhline(y=results["volumetric flow rate"](50)[0], color='green', linewidth=0.3, linestyle='-')
    # Mark Q50
    plt.plot(50, results["volumetric flow rate"](50)[0], 'ro', markersize=2, zorder=11)
    
    # Close-up subplot
    x_closeup_start = 47.5
    x_closeup_end = 52.5
    y_closeup_start = results["volumetric flow rate"](x_closeup_start)[0]
    y_closeup_end = results["volumetric flow rate"](x_closeup_end)[0]

    # 보조 플롯 위치, 크기 설정
    ax = plt.axes([0.6, 0.2, 0.25, 0.25])  # [left, bottom, width, height]    
    # 축 설정
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(x_closeup_start, x_closeup_end)
    ax.set_ylim(y_closeup_start, y_closeup_end)

    # Show only one y-axis tick label
    ax.set_xticks([x_closeup_start, 50, x_closeup_end], [x_closeup_start, 50, x_closeup_end])
    ax.set_yticks([results["volumetric flow rate"](x_closeup_start)[0], 
                   results["volumetric flow rate"](50)[0],
                   results["volumetric flow rate"](x_closeup_end)[0]], 
                  [f'{results["volumetric flow rate"](x_closeup_start)[0]:.0f}',
                   f'{results["volumetric flow rate"](50)[0]:.2f}',
                   f'{results["volumetric flow rate"](x_closeup_end)[0]:.0f}'])

    # 그리기
    ax.plot(x, y, label="derived", color='green', linewidth=1.5, alpha=1)
    ax.plot(x, y_pi_l, label="95% Prediction Band", color='red', linewidth=0.5, alpha=1, linestyle=':')
    ax.plot(x, y_pi_u, color='red', linewidth=1, alpha=1, linestyle=':')
    ax.plot(x, y_ci_l, label="95% Confidence Region", color='blue', linewidth=0.5, alpha=1, linestyle=':')
    ax.plot(x, y_ci_u, color='blue', linewidth=1, alpha=0.5, linestyle=':')
    ax.scatter(x_values, y_values, label="measured", color='green', marker='x', zorder=10)
    # 예측구간 사이 영역 색칠
    ax.fill_between(x, y_pi_l, y_pi_u, color='red', alpha=0.1)
    # 신뢰구간 사이 영역 색칠
    ax.fill_between(x, y_ci_l, y_ci_u, color='blue', alpha=0.1)

    # Inside the subplot section
    ax.yaxis.set_minor_locator(plt.NullLocator())
    ax.xaxis.set_minor_locator(plt.NullLocator())

    # Mark Q50
    ax.plot(50, results["volumetric flow rate"](50)[0], 'ro')
    # Add vertical line at y = results["volumetric flow rate"](50)[0]
    ax.axhline(y=results["volumetric flow rate"](50)[0], color='red', linewidth=0.5, linestyle='-')
    # Add vertical line at x = 50
    ax.axvline(x=50, color='red', linewidth=0.5, linestyle='-')

    # After plotting the zoomed-in region
    plt.axhspan(y_closeup_start, y_closeup_end, x_closeup_start, x_closeup_end, facecolor='none', edgecolor='black', linewidth=1)


    # 그래프 보이기
    plt.show(block=False)
    plt.pause(3600)


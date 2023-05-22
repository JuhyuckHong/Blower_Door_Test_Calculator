import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib import font_manager
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import matplotlib.patches as patches
from matplotlib.patches import ConnectionPatch
import numpy as np


def log_scale_value(start, end, percent):
    log_start = np.log10(start)
    log_end = np.log10(end)

    # 해당 퍼센티지에 대한 로그 스케일 값 계산
    log_value = log_start + (log_end - log_start) * (percent)

    # 로그 스케일 값을 원래 스케일로 변환
    value = 10 ** log_value

    return value


def plot_graph(results):
    # # 폰트 설정
    # font_path = './NanumSquare_acL.ttf'
    # font_name = font_manager.FontProperties(fname=font_path).get_name()
    # plt.rc('font', family=font_name)

    # # 창 크기 고정 - 픽셀 단위
    # width_px = 2400  
    # height_px = 1500  
    # dpi = 300  # 인치당 픽셀 (dots per inch)
    # #plt.figure(figsize=(width_px/dpi, height_px/dpi))

    # x 축 설정
    plt.xscale("log")
    plt.xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 
               [10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    plt.tick_params(axis='x', direction='in')
    x_lim_min = 10
    x_lim_max = 100
    plt.xlim(x_lim_min, x_lim_max)

    # y 축 설정
    plt.yscale("log")
    plt.yticks([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
               [100, 200, 300, 400, 500, 600, 700, 800, 900, '1,000'])
    plt.tick_params(axis='y', direction='in')
    y_lim_min = 100
    y_lim_max = 1000
    plt.ylim(y_lim_min, y_lim_max)

    # 데이터 플롯
    Pa_50 = 50
    Q50 = results["volumetric flow rate"](Pa_50)[0]
    # 측정값
    x_values, y_values = zip(*results["measured values"])
    # 계산값(ci=95%신뢰구간, pi=95%예측구간)
    x = range(int(min(x_values) - 4), int(max(x_values) + 15))
    y, y_ci_l, y_ci_u, y_pi_l, y_pi_u = zip(*[results["volumetric flow rate"](i) for i in x])

    # 그래프 그리기 옵션들
    scatter_params = {
        'label': "measured value",
        'color': (0.1, 0.1, 0.1, 0.5),
        'marker': 'x',
        'zorder': 10
    }

    derived_params = {
        'label': f"Q = {results['C at STP']:.2f}·ΔP^{results['n']:.2f}",
        'color': (1,0,0,0.8),
        'linewidth': 1.5,
        'alpha': 1,
        'zorder': 9
    }

    ci_params = {
        'color': 'green',
        'linewidth': 0.5,
        'alpha': 1,
        'linestyle': '-',
        'zorder': 8
    }

    pi_params = {
        'color': 'blue',
        'linewidth': 0.1,
        'alpha': 1,
        'linestyle': '-',
        'zorder': 8
    }

    fill_params_CI = {
        'color': 'green',
        'alpha': 0.2,
        'zorder': 8
    }

    fill_patch_CI = {
        'facecolor': 'green',
        'alpha': 0.2,
        'label': '95% Confidence Region',
        'zorder': 9
    }

    fill_params_PI = {
        'color': 'grey',
        'alpha': 0.1,
        'hatch': '\\',
        'zorder': 8
    }

    fill_patch_PI = {
        'color': 'grey',
        'hatch': '\\',
        'alpha': 0.1,
        'label': '95% Prediction Band',
        'zorder': 8
    }


    # 그래프 그리기
    plt.scatter(x_values, y_values, **scatter_params)
    plt.plot(x, y, **derived_params)
    plt.plot(x, y_pi_l, **pi_params)
    plt.plot(x, y_pi_u, **pi_params)
    plt.plot(x, y_ci_l, **ci_params)
    plt.plot(x, y_ci_u, **ci_params)
    plt.fill_between(x, y_pi_l, y_pi_u, **fill_params_PI)
    plt.fill_between(x, y_ci_l, y_ci_u, **fill_params_CI)

    # 보조선 추가
    plt.grid(True, which="both", linestyle="--", linewidth=1, color="gray", alpha=0.5)

    # 축 레이블 설정
    plt.xlabel('압력차 [Pa]', labelpad=15)
    plt.ylabel('침기량\n(누기량)\n[㎥/s]', rotation='horizontal', labelpad=20, linespacing=2)

    # 제목 설정
    plt.title('기밀 시험 결과', fontsize=18, pad=20)

    # 그래프와 제목 사이 간격 조정
    plt.subplots_adjust(top=0.9, bottom=0.15, left=0.15)
    
    # 기존 범례 가져오기
    handles, labels = plt.gca().get_legend_handles_labels()
    # 채우기(95% 신뢰, 예측) 범례 생성
    fill_ci = mpatches.Patch(**fill_patch_CI)
    handles.append(fill_ci)
    labels.append(fill_ci.get_label())    
    fill_pi = mpatches.Patch(**fill_patch_PI)
    handles.append(fill_pi)
    labels.append(fill_pi.get_label())

    # 범례 표시
    plt.legend(handles, labels, loc="upper left")

    # 50 Pa 라인 그리기
    plt.axvline(x=Pa_50, color='green', linewidth=0.3, linestyle='-')
    plt.axhline(y=Q50, color='green', linewidth=0.3, linestyle='-')
    # Mark Q50
    plt.plot(Pa_50, Q50, 'ro', markersize=2, zorder=11)
    
    # 확대 할 범위 계산 x=Q50값을 
    x_closeup_start = results['reverse vfra'](Q50)[1]
    x_closeup_end = results['reverse vfra'](Q50)[0]
    y_closeup_start = results["volumetric flow rate"](Pa_50)[1]
    y_closeup_end = results["volumetric flow rate"](Pa_50)[2]

    # 활대 플롯 위치, 크기 설정
    left = 0.58
    bottom = 0.2
    width = 0.25
    height = 0.10

    # 확대 플롯 위치 사각형 그리기
    rect = patches.Rectangle((x_closeup_start, y_closeup_start), 
                              x_closeup_end - x_closeup_start, 
                              y_closeup_end - y_closeup_start, 
                              linewidth=1, edgecolor='r', facecolor='none')
    plt.gca().add_patch(rect)

    # 확대 플롯 화살표 그리기
    ## 화살표 좌표값 계산
    x1 = log_scale_value(x_lim_min, x_lim_max, left + width/2 + 0.03)
    y1 = log_scale_value(y_lim_min, y_lim_max, (bottom + height)*1.45)
    x2 = (x_closeup_start + x_closeup_end)/2
    y2 = y_closeup_start
    ## 화살표 그리기
    plt.annotate('',  # 표시할 텍스트 
                xy=(x1, y1),  # 화살표 머리 위치
                xytext=(x2, y2),  # 화살표 꼬리 위치
                arrowprops=dict(facecolor='red',
                                edgecolor='red',
                                arrowstyle='->')
    )

    # 확대 플롯 위치
    ax = plt.axes([left, bottom, width, height]) 

    # 활대 플롯 축 설정
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(x_closeup_start, 
                x_closeup_end)
    ax.set_ylim(y_closeup_start - (Q50 - y_closeup_start)*0.1, 
                y_closeup_end + (y_closeup_end - Q50)*0.1)

    # 확대 플롯 틱
    ax.set_xticks([Pa_50], [""])
    ax.set_yticks([y_closeup_start, 
                   y_closeup_end], 
                  [f'{y_closeup_start:.0f}',
                   f'{y_closeup_end:.0f}'])

    # 확대 플롯 그리기
    ax.plot(x, y, **derived_params)
    ax.plot(x, y_pi_l, **ci_params)
    ax.plot(x, y_pi_u, **ci_params)
    ax.plot(x, y_ci_l, **pi_params)
    ax.plot(x, y_ci_u, **pi_params)
    ax.scatter(x_values, y_values, **scatter_params)
    
    # 예측구간 사이 영역 색칠
    ax.fill_between(x, y_pi_l, y_pi_u, **fill_params_PI)
    # 신뢰구간 사이 영역 색칠
    ax.fill_between(x, y_ci_l, y_ci_u, **fill_params_CI)

    # 자동생성 틱 삭제
    ax.yaxis.set_minor_locator(plt.NullLocator())
    ax.xaxis.set_minor_locator(plt.NullLocator())

    # 틱 설정
    ax.tick_params(axis='both', which='both', pad=5, labelcolor='red', direction='inout')
    ax.tick_params(axis='x', which='both', bottom=1, top=0, labelbottom=1, labeltop=0)
    ax.tick_params(axis='y', which='both', left=0, right=1, labelleft=0, labelright=1)
    
    # 축 설정
    ax.tick_params(axis='both', which='both', pad=5)
    ax.tick_params(axis='both', which='both', labelcolor='black')
    ax.tick_params(axis='both', which='both', width=1, length=5)

    ## 계산된 Q50과 95% 신뢰값 표시
    ### Q50
    marker_size = 50
    Pa_50_value = Pa_50
    offset_x = (x_closeup_end - Pa_50)/10
    offset_y = (y_closeup_end - Q50)/5    
    ax.scatter(Pa_50_value, Q50, s=marker_size, color='blue', marker=(5,1), zorder=11)
    ax.text(Pa_50_value + offset_x, Q50 - offset_y,
            f'{Q50:.2f}㎥/s',
            weight='bold',
            bbox=dict(facecolor=(0.9, 0.9, 0.7, 0.5), 
                      edgecolor=(0.5, 0.9, 0.5, 0.5), 
                      pad=0.1, 
                      boxstyle='round,pad=0.3'))
    ### 95% 신뢰값 Q50
    ax.scatter(Pa_50_value, y_closeup_end, color='blue', marker='_', s=marker_size, zorder=11)
    ax.scatter(Pa_50_value, y_closeup_start, color='blue', marker='_', s=marker_size, zorder=11)

    # x = 50 세로줄 긋기
    ax.axvline(x=Pa_50, color='red', linewidth=1, linestyle='--')

    # 레이블 배경 설정
    labels = ax.get_xticklabels() + ax.get_yticklabels()  # X와 Y 레이블 모두 가져오기
    plt.setp(labels, backgroundcolor=(1,1,1,0.7))  # 배경색을 흰색으로 설정

    # 그래프 보이기
    # plt.show(block=False)
    # from datetime import datetime
    # now = datetime.now().strftime("%d%m%Y-%H%M%S")
    # plt.savefig(f'test_results_{now}.png', dpi=300, bbox_inches='tight')
    # plt.pause(3600)

# 보고서 작성
def create_report(results, text):

    # 폰트 설정
    font_path = './NanumSquare_acL.ttf'
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    plt.rc('font', family=font_name)

    # 창 크기 고정 - 픽셀 단위
    width_px = 2481  
    height_px = 3507  
    dpi = 300  # 인치당 픽셀 (dots per inch)
    plt.figure(figsize=(width_px/dpi, height_px/dpi))

    # Gridspec을 사용하여 플롯과 텍스트 영역을 분할
    gs = GridSpec(2, 1, height_ratios=[1, 1])

    # 텍스트 영역
    plt.subplot(gs[0])
    plt.axis('off')
    plt.text(0.5, 0.5, text, ha='center', va='center', wrap=True)

    # 플롯 영역
    plt.subplot(gs[1])
    plot_graph(results)

    # 그래프 저장
    from datetime import datetime
    now = datetime.now().strftime("%d%m%Y-%H%M%S")
    plt.savefig(f'test_results_{now}.png', dpi=300, bbox_inches='tight')

    # 그래프 보이기
    plt.show()




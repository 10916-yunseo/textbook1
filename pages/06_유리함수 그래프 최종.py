import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# Streamlit 페이지 설정
st.set_page_config(
    page_title="유리함수 그래프 분석기",
    layout="wide"
)

st.title("➗ 유리함수 그래프 분석기")
st.markdown("유리함수 $y = \\frac{ax+b}{cx+d}$ 형태를 입력하고 분석해 보세요.")

# 사용자 입력
st.sidebar.header("함수 입력")
func_str = st.sidebar.text_input(
    "유리함수 $\\frac{ax+b}{cx+d}$ 를 입력하세요 (예: (2*x + 1)/(x - 3))",
    value="(2*x + 1)/(x - 3)"
)

# 그래프 범위 설정
st.sidebar.header("그래프 범위")
x_min = st.sidebar.number_input("x 축 최소값", value=-10.0, step=1.0)
x_max = st.sidebar.number_input("x 축 최대값", value=10.0, step=1.0)
y_min = st.sidebar.number_input("y 축 최소값", value=-10.0, step=1.0)
y_max = st.sidebar.number_input("y 축 최대값", value=10.0, step=1.0)

try:
    # 1. SymPy를 사용하여 함수 분석
    x = sp.Symbol('x')
    f_sym = sp.simplify(func_str)
    
    # 분자와 분모 추출
    (numer, denom), _ = sp.fraction(f_sym)

    # 2. 점근선 계산
    
    # 2-1. 수직 점근선 (분모 = 0이 되는 x값)
    vertical_asymptote = sp.solve(denom, x)
    
    # 2-2. 수평 점근선 (x -> inf)
    horizontal_asymptote = sp.limit(f_sym, x, sp.oo)
    
    # 3. 정의역 및 치역 계산
    
    # 정의역: 수직 점근선의 x값 제외
    domain = f"$\{x \mid x \\neq {vertical_asymptote[0]}}\}$" if vertical_asymptote else "$\{x \mid x는 모든 실수\}$"
    
    # 치역: 수평 점근선의 y값 제외 (일반적인 유리함수 형태 가정)
    range_set = f"$\{y \mid y \\neq {horizontal_asymptote}\}" if horizontal_asymptote.is_real and horizontal_asymptote != sp.oo else "$\{y \mid y는 모든 실수\}$"
    
    # 결과를 두 개의 컬럼으로 분할
    col1, col2 = st.columns(2)

    with col1:
        st.header("🔍 분석 결과")
        st.latex(f"f(x) = {sp.latex(f_sym)}")
        
        st.subheader("⭐ 점근선")
        if vertical_asymptote:
            st.write(f"**수직 점근선**: $x = {vertical_asymptote[0]}$")
        else:
            st.write("**수직 점근선**: 없음")
            
        if horizontal_asymptote.is_real and horizontal_asymptote != sp.oo:
            st.write(f"**수평 점근선**: $y = {horizontal_asymptote}$")
        else:
            st.write("**수평 점근선**: 없음 (혹은 사선/곡선 점근선)")

        st.subheader("📖 정의역 및 치역")
        st.write(f"**정의역**: {domain}")
        st.write(f"**치역**: {range_set}")
        
    with col2:
        st.header("📈 유리함수 그래프")
        
        # 4. 그래프 그리기 (Matplotlib)
        
        # 수치 함수 변환
        f_np = sp.lambdify(x, f_sym, 'numpy')
        
        # 그래프 데이터 생성
        x_vals = np.linspace(x_min, x_max, 500)
        y_vals = f_np(x_vals)

        # 수직 점근선 근처의 발산 처리
        if vertical_asymptote:
            va = float(vertical_asymptote[0])
            # 점근선 근처 값들을 NaN으로 처리하여 그래프가 끊기도록 함
            y_vals[np.abs(x_vals - va) < 0.1] = np.nan 

        # 그래프 그리기
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(x_vals, y_vals, label=f"${sp.latex(f_sym)}$", color='blue')
        
        # 점근선 표시
        if vertical_asymptote:
            ax.axvline(x=va, color='red', linestyle='--', label=f'VA: $x={va}$')
        
        if horizontal_asymptote.is_real and horizontal_asymptote != sp.oo:
            ha = float(horizontal_asymptote)
            ax.axhline(y=ha, color='green', linestyle='--', label=f'HA: $y={ha}$')

        # 축 설정 및 레이블
        ax.set_title(f"Graph of $f(x) = {sp.latex(f_sym)}$")
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend()

        # Streamlit에 그래프 표시
        st.pyplot(fig)

except Exception as e:
    st.error(f"함수 입력 오류 또는 계산 오류가 발생했습니다. 입력을 확인해 주세요: {e}")
    st.info("💡 **팁**: 입력은 Python/SymPy 문법을 따라야 합니다. 예: `(2*x + 1)/(x - 3)`. 곱셈은 `*`를 사용하세요.")

st.markdown("---")

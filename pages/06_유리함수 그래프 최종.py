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

# --- 사이드바 입력 ---
st.sidebar.header("함수 입력")
func_str = st.sidebar.text_input(
    "유리함수 $\\frac{ax+b}{cx+d}$ 를 입력하세요 (예: (2*x + 1)/(x - 3))",
    value="(2*x + 1)/(x - 3)"
)

st.sidebar.header("그래프 범위")
x_min = st.sidebar.number_input("x 축 최소값", value=-10.0, step=1.0)
x_max = st.sidebar.number_input("x 축 최대값", value=10.0, step=1.0)
y_min = st.sidebar.number_input("y 축 최소값", value=-10.0, step=1.0)
y_max = st.sidebar.number_input("y 축 최대값", value=10.0, step=1.0)
# --- 사이드바 입력 끝 ---


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
    
    # 3. 정의역 및 치역 계산 (수정된 부분)
    
    # 정의역 LaTeX 문자열 생성
    if vertical_asymptote:
        # SymPy 결과가 소수로 나올 수 있으므로, .evalf(3)로 소수점 3자리까지 표시
        va_val = vertical_asymptote[0].evalf(3)
        # st.markdown()을 사용하므로 LaTeX 이스케이프에 주의
        domain_latex = f"$\\{{x \\mid x \\neq {va_val}\}}$"
        va_float = float(va_val) # 그래프에 사용할 실수 값
    else:
        domain_latex = "모든 실수 $\\mathbb{R}$"
        va_float = None

    # 치역 LaTeX 문자열 생성
    if horizontal_asymptote.is_real and horizontal_asymptote != sp.oo:
        ha_val = horizontal_asymptote.evalf(3)
        range_latex = f"$\\{{y \\mid y \\neq {ha_val}\}}$"
        ha_float = float(ha_val) # 그래프에 사용할 실수 값
    else:
        range_latex = "모든 실수 $\\mathbb{R}$"
        ha_float = None
    
    # 4. 분석 결과 출력
    col1, col2 = st.columns(2)

    with col1:
        st.header("🔍 분석 결과")
        st.latex(f"f(x) = {sp.latex(f_sym)}")
        
        st.subheader("⭐ 점근선")
        if va_float is not None:
            st.write(f"**수직 점근선 (VA)**: $x = {va_val}$")
        else:
            st.write("**수직 점근선 (VA)**: 없음")
            
        if ha_float is not None:
            st.write(f"**수평 점근선 (HA)**: $y = {ha_val}$")
        else:
            st.write("**수평 점근선 (HA)**: 없음")

        st.subheader("📖 정의역 및 치역")
        st.markdown(f"**정의역**: {domain_latex}")
        st.markdown(f"**치역**: {range_latex}")
        
    # 5. 그래프 그리기
    with col2:
        st.header("📈 유리함수 그래프")
        
        # 수치 함수 변환
        f_np = sp.lambdify(x, f_sym, 'numpy')
        
        # 그래프 데이터 생성
        x_vals = np.linspace(x_min, x_max, 500)
        y_vals = f_np(x_vals)

        # 수직 점근선 근처의 발산 처리
        if va_float is not None:
            # 점근선 근처 값들을 NaN으로 처리하여 그래프가 끊기도록 함
            y_vals[np.abs(x_vals - va_float) < 0.05] = np.nan 

        # 그래프 그리기
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(x_vals, y_vals, label=f"${sp.latex(f_sym)}$", color='blue')
        
        # 점근선 표시
        if va_float is not None:
            ax.axvline(x=va_float, color='red', linestyle='--', label=f'VA: $x={va_val}$')
        
        if ha_float is not None:
            ax.axhline(y=ha_float, color='green', linestyle='--', label=f'HA: $y={ha_val}$')

        # 축 설정 및 레이블
        ax.set_title(f"Graph of $f(x) = {sp.latex(f_sym)}$")
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend()
        ax.axhline(0, color='gray', linewidth=0.5) # x축
        ax.axvline(0, color='gray', linewidth=0.5) # y축

        # Streamlit에 그래프 표시
        st.pyplot(fig)

except Exception as e:
    st.error("함수 입력 또는 계산에 문제가 발생했습니다. 입력을 확인하거나 분모가 항상 0이 되는 등의 특수한 경우가 아닌지 확인해 주세요.")
    st.info("💡 **팁**: 입력은 Python/SymPy 문법을 따라야 합니다. 예: `(2*x + 1)/(x - 3)`. 곱셈은 `*`를 사용하세요.")

st.markdown("---")
st.markdown("© 2025 Gemini AI Assistant")

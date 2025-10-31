import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# Streamlit 페이지 설정
st.set_page_config(
    page_title="유리함수 그래프 분석기 (안정화 버전)",
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
x_min = st.sidebar.number_input("x 축 최소값", value=-20.0, step=1.0)
x_max = st.sidebar.number_input("x 축 최대값", value=20.0, step=1.0)
y_min = st.sidebar.number_input("y 축 최소값", value=-50.0, step=1.0)
y_max = st.sidebar.number_input("y 축 최대값", value=50.0, step=1.0)
# --- 사이드바 입력 끝 ---

try:
    # 1. SymPy를 사용하여 함수 분석
    x = sp.Symbol('x')
    f_sym = sp.simplify(func_str)
    
    # --- ⭐ 핵심 수정 부분: sp.fraction() 결과를 직접 언팩킹합니다. ---
    # SymPy 튜플 언팩킹 오류를 피하기 위해 sp.fraction()을 호출하여 분자와 분모를 안전하게 추출
    # sp.fraction()은 (분자, 분모) 튜플을 반환합니다.
    numer, denom = sp.fraction(f_sym) 
    
    # 분모가 상수 0인 경우 처리
    if denom.is_constant() and denom == 0:
        st.error("입력하신 함수는 분모가 0이므로 수학적으로 정의할 수 없습니다.")
        st.stop()
    # ----------------------------------------------------------------

    # 2. 점근선 계산
    
    # 수직 점근선
    vertical_asymptote = sp.solve(denom, x)
    
    # 수평 점근선
    horizontal_asymptote = sp.limit(f_sym, x, sp.oo)
    
    # 3. 정의역 및 치역 계산 및 그래프에 사용할 실수 값 준비
    
    # 정의역 LaTeX 문자열 생성
    if vertical_asymptote:
        va_val = vertical_asymptote[0].evalf(3) 
        domain_latex = f"$\\{{x \\mid x \\neq {va_val}\}}$"
        va_float = float(va_val)
    else:
        domain_latex = "모든 실수 $\\mathbb{R}$"
        va_float = None

    # 치역 LaTeX 문자열 생성
    if horizontal_asymptote.is_real and horizontal_asymptote != sp.oo:
        ha_val = horizontal_asymptote.evalf(3)
        range_latex = f"$\\{{y \\mid y \\neq {ha_val}\}}$"
        ha_float = float(ha_val)
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
        ax.axhline(0, color='gray', linewidth=0.5) 
        ax.axvline(0, color='gray', linewidth=0.5) 

        # Streamlit에 그래프 표시
        st.pyplot(fig)

except Exception as e:
    st.error("❌ **함수 입력 또는 계산에 치명적인 오류가 발생했습니다.**")
    st.info("입력을 확인하거나, 분모가 0인 상수 함수 등 특수한 경우가 아닌지 확인해 주세요. 특히 **곱셈 기호(\*)**를 생략하지 않았는지 확인해 주세요.")
    
    st.subheader("🚨 디버깅 정보 (Traceback Error)")
    st.code(f"Error Type and Message: {type(e).__name__}: {e}")

st.markdown("---")

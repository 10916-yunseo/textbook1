import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import random

# --- 유틸리티 함수: 문제 데이터베이스 생성 ---
def generate_rational_function_problems(num_problems=30):
    """30개의 유리함수 문제 데이터베이스를 생성합니다."""
    problems = []
    COEF_RANGE = (-5, 5)
    x = sp.Symbol('x')

    while len(problems) < num_problems:
        a = random.choice([i for i in range(*COEF_RANGE) if i != 0])
        b = random.randint(*COEF_RANGE)
        c = random.choice([i for i in range(*COEF_RANGE) if i != 0])
        d = random.randint(*COEF_RANGE)

        # 수직 점근선이 정수 또는 간단한 분수가 되도록 조정
        if c != 0 and d % c != 0:
             d = c * random.choice([i for i in range(-5, 5) if i != 0])
        
        # 분모가 0이 아닌지 확인
        if c == 0 and d == 0: continue
        
        numer = a * x + b
        denom = c * x + d
        f_sym = sp.simplify(numer / denom)
        
        # 수직/수평 점근선 계산
        try:
            va_sol = sp.solve(denom, x)
            if not va_sol: continue
            
            va = va_sol[0]
            va_val_sympy = va.evalf(3)
            va_float = float(va_val_sympy)
            
            ha_sympy = sp.limit(f_sym, x, sp.oo)
            ha_val_sympy = ha_sympy.evalf(3)
            ha_float = float(ha_val_sympy)
            
        except Exception:
            continue

        solution_va = f"$x = {va_val_sympy}$"
        solution_ha = f"$y = {ha_val_sympy}$"
        
        explanation = f"""
        **1. 수직 점근선 ($\mathbf{{x}}$)**
        - 분모가 0이 되는 $x$ 값을 찾습니다. ${sp.latex(denom)} = 0$
        - $x = {va_val_sympy}$ 입니다. (정답: $\mathbf{{{solution_va}}}$)
        
        **2. 수평 점근선 ($\mathbf{{y}}$)**
        - 분자와 분모의 차수가 같으므로, 최고차항 계수의 비 $\\frac{{{a}}}{{{c}}}$를 구합니다.
        - $y = {ha_val_sympy}$ 입니다. (정답: $\mathbf{{{solution_ha}}}$)
        """

        problems.append({
            'id': len(problems) + 1,
            'function': f_sym,
            'function_str': f"({sp.latex(numer)})/({sp.latex(denom)})",
            'va_ans': solution_va,
            'ha_ans': solution_ha,
            'explanation': explanation,
            'va_val': va_float,
            'ha_val': ha_float,
        })
        
    return problems

# --- 유틸리티 함수: 그래프 그리기 ---
def plot_rational_function(f_sym, va_float, ha_float, va_val_str, ha_val_str, x_min, x_max, y_min, y_max):
    """Matplotlib을 사용하여 유리함수 그래프를 그립니다."""
    try:
        x = sp.Symbol('x')
        f_np = sp.lambdify(x, f_sym, 'numpy')
        
        # X 값 생성 시 점근선을 피하기 위해 두 영역으로 나눔 (그래프 안정화)
        x_vals = np.linspace(x_min, x_max, 500)
        
        if va_float is not None and x_min < va_float < x_max:
            # 점근선 근처 값들을 NaN 처리
            x_vals_1 = np.linspace(x_min, va_float - 0.01, 250)
            x_vals_2 = np.linspace(va_float + 0.01, x_max, 250)
            x_vals = np.concatenate([x_vals_1, x_vals_2])
        
        y_vals = f_np(x_vals)
        
        # Y 값 범위 초과 시 NaN 처리
        y_vals[y_vals > y_max * 1.5] = np.nan
        y_vals[y_vals < y_min * 1.5] = np.nan

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(x_vals, y_vals, label=f"${sp.latex(f_sym)}$", color='blue', linewidth=2)
        
        # 점근선 표시
        if va_float is not None:
            ax.axvline(x=va_float, color='red', linestyle='--', label=f'VA: $x={va_val_str}$')
        
        if ha_float is not None:
            ax.axhline(y=ha_float, color='green', linestyle='--', label=f'HA: $y={ha_val_str}$')

        ax.set_title(f"함수 그래프: $f(x) = {sp.latex(f_sym)}$")
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend()
        ax.axhline(0, color='gray', linewidth=0.5) 
        ax.axvline(0, color='gray', linewidth=0.5) 

        st.pyplot(fig)

    except Exception as e:
        st.error("📉 **그래프를 그리는 중 오류가 발생했습니다.**")
        st.warning("입력 함수, 또는 설정된 X, Y 범위가 계산하기 어렵거나 너무 좁을 수 있습니다.")
        st.info("X, Y 축 범위를 넓게 설정해 보세요.")
        # print(f"Graph Plot Error: {type(e).__name__}: {e}") # 디버깅용

# --- 탭 1: 그래프 분석기 (사용자 유리식 입력) ---
def graph_analyzer_tab():
    st.header("📊 사용자 유리식 그래프 분석기")
    st.markdown("분석을 원하는 유리식($x$에 대한 식)을 입력하고 그래프를 확인하세요. (예: `(2*x + 1)/(x - 3)` 또는 `x**2/(x+1)`)")
    
    # --- 사이드바 입력 ---
    with st.sidebar:
        st.header("그래프 분석기 설정")
        func_str = st.text_input(
            "유리식 $f(x)$ 입력",
            value="(2*x + 1)/(x - 3)",
            key="analyze_input"
        )
        st.subheader("그래프 범위")
        x_min = st.number_input("x 축 최소값", value=-10.0, step=1.0, key="a_xmin")
        x_max = st.number_input("x 축 최대값", value=10.0, step=1.0, key="a_xmax")
        y_min = st.number_input("y 축 최소값", value=-10.0, step=1.0, key="a_ymin")
        y_max = st.number_input("y 축 최대값", value=10.0, step=1.0, key="a_ymax")
    # --- 사이드바 입력 끝 ---

    if func_str:
        try:
            x = sp.Symbol('x')
            f_sym = sp.simplify(func_str)
            
            # 분자와 분모 추출
            numer, denom = sp.fraction(f_sym)

            # 2. 점근선 계산
            va_sol = sp.solve(denom, x)
            ha_sympy = sp.limit(f_sym, x, sp.oo)
            
            # 값 정리
            va_val = va_sol[0].evalf(3) if va_sol else None
            va_float = float(va_val) if va_val is not None else None
            va_str = str(va_val) if va_val is not None else "없음"
            
            ha_val = ha_sympy.evalf(3) if ha_sympy != sp.oo else None
            ha_float = float(ha_val) if ha_val is not None else None
            ha_str = str(ha_val) if ha_val is not None else "없음"

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🔍 분석 결과")
                st.latex(f"f(x) = {sp.latex(f_sym)}")
                
                st.markdown("#### ⭐ 점근선")
                st.write(f"**수직 점근선 (VA)**: $x = {va_str}$")
                st.write(f"**수평 점근선 (HA)**: $y = {ha_str}$")
                
                st.markdown("#### 📖 정의역 및 치역")
                domain_latex = f"$\\{{x \\mid x \\neq {va_str}\\}$" if va_val is not None else "모든 실수 $\\mathbb{R}$"
                range_latex = f"$\\{{y \\mid y \\neq {ha_str}\\}$" if ha_val is not None and ha_val != sp.oo else "모든 실수 $\\mathbb{R}$"
                st.markdown(f"**정의역**: {domain_latex}")
                st.markdown(f"**치역**: {range_latex}")
                
            with col2:
                st.subheader("📈 그래프 시각화")
                plot_rational_function(f_sym, va_float, ha_float, va_str, ha_str, x_min, x_max, y_min, y_max)
                
        except Exception as e:
            st.error("❌ **유리식 분석에 실패했습니다.**")
            st.warning("입력 형식이 잘못되었거나, 수식에 $x$가 포함되어 있지 않을 수 있습니다.")
            st.info("💡 팁: 곱셈은 `*`를 사용하고, 거듭제곱은 `**`를 사용하세요.")

# --- 탭 2: 유리함수 문제 풀이 ---
def quiz_tab():
    st.header("📝 유리함수 점근선 퀴즈")
    
    # 세션 상태 초기화 및 문제 로드
    if 'problems' not in st.session_state:
        st.session_state.problems = generate_rational_function_problems(30)
        st.session_state.current_index = 0
        st.session_state.attempts = [0] * 30 
        st.session_state.show_solution = [False] * 30 
        st.session_state.feedback_message = "" # 피드백 메시지 상태 추가

    total_problems = len(st.session_state.problems)
    current_index = st.session_state.current_index
    current_problem = st.session_state.problems[current_index]
    
    st.subheader(f"문제 {current_index + 1} / {total_problems}")

    # --- 문제 출제 ---
    st.markdown("다음 유리함수의 **수직 점근선**과 **수평 점근선**을 구하고 입력하세요.")
    st.latex(f"f(x) = {current_problem['function_str']}")
    
    # --- 문제 새로고침 및 이동 버튼 ---
    col_nav_1, col_nav_2, col_nav_3, col_nav_4 = st.columns([1, 1, 1, 3])

    def change_problem(direction):
        new_index = (current_index + direction) % total_problems
        st.session_state.current_index = new_index
        st.session_state.input_va_quiz = ""
        st.session_state.input_ha_quiz = ""
        st.session_state.feedback_message = ""
        st.rerun()
        
    def refresh_problem():
        new_index = random.randint(0, total_problems - 1)
        st.session_state.current_index = new_index
        st.session_state.input_va_quiz = ""
        st.session_state.input_ha_quiz = ""
        st.session_state.feedback_message = ""
        st.rerun()

    if col_nav_1.button("◀ 이전 문제", key="prev_btn"):
        change_problem(-1)

    if col_nav_2.button("▶ 다음 문제", key="next_btn"):
        change_problem(1)
        
    if col_nav_3.button("🔄 새로운 문제", key="refresh_btn"):
        refresh_problem()

    st.markdown("---")

    # --- 입력 및 채점 ---
    st.subheader("정답 입력")
    
    # 입력 필드 key를 사용하여 페이지 이동 시 값이 남아있지 않도록 처리
    user_va = st.text_input("수직 점근선 (예: x=3)", key="input_va_quiz")
    user_ha = st.text_input("수평 점근선 (예: y=2)", key="input_ha_quiz")

    if st.button("정답 확인 ✅", key="submit_btn"):
        
        # 정답 및 사용자 입력 클리닝 (공백 제거 및 소문자 통일)
        clean_user_va = user_va.lower().replace(" ", "")
        clean_user_ha = user_ha.lower().replace(" ", "")
        
        # 정답에서 LaTeX 기호 제거
        clean_ans_va = current_problem['va_ans'].strip('$').lower().replace(" ", "")
        clean_ans_ha = current_problem['ha_ans'].strip('$').lower().replace(" ", "")
        
        is_correct_va = clean_user_va == clean_ans_va
        is_correct_ha = clean_user_ha == clean_ans_ha
        is_all_correct = is_correct_va and is_correct_ha
        
        # 1. 시도 횟수 업데이트
        st.session_state.attempts[current_index] += 1
        current_attempts = st.session_state.attempts[current_index]

        # 2. 채점 로직 및 피드백 메시지 생성
        if is_all_correct:
            st.session_state.feedback_message = "🎉 **정답입니다!** 완벽하게 이해하셨네요."
            st.session_state.show_solution[current_index] = True
            
        else:
            if current_attempts < 2:
                st.session_state.feedback_message = f"오답입니다. 다시 한번 풀어보세요! (현재 시도 횟수: {current_attempts}회)"
                
                # 힌트 제공
                if not is_correct_va and not is_correct_ha:
                     st.session_state.feedback_message += "\n\n(수직 점근선과 수평 점근선 모두 틀렸습니다.)"
                elif not is_correct_va:
                     st.session_state.feedback_message += "\n\n(수직 점근선($x$)을 다시 확인해 보세요.)"
                elif not is_correct_ha:
                     st.session_state.feedback_message += "\n\n(수평 점근선($y$)을 다시 확인해 보세요.)"
                
            else:
                # 수정된 부분: 두 번 틀리면 풀이 표시 플래그 ON
                st.session_state.feedback_message = "😭 **오답입니다.** 두 번 틀리셨으므로 정답과 풀이를 보여드립니다."
                st.session_state.show_solution[current_index] = True
        
        # 채점 후 페이지 새로고침
        st.rerun() 
        
    # --- 피드백 메시지 표시 ---
    if st.session_state.feedback_message:
        if "정답입니다" in st.session_state.feedback_message:
            st.success(st.session_state.feedback_message)
        elif "오답입니다" in st.session_state.feedback_message:
            st.warning(st.session_state.feedback_message)
        else:
            st.info(st.session_state.feedback_message)

    # --- 정답 및 풀이 섹션 (맞추거나, 두 번 틀렸을 때만 표시) ---
    if st.session_state.show_solution[current_index] or st.session_state.attempts[current_index] >= 2:
        st.subheader("💡 정답 및 풀이")
        st.markdown(f"**정답: 수직 점근선**은 {current_problem['va_ans']}, **수평 점근선**은 {current_problem['ha_ans']} 입니다.")
        st.markdown("---")
        st.markdown("**상세 풀이:**")
        st.markdown(current_problem['explanation'])

    # --- 그래프 섹션 ---
    st.markdown("---")
    st.subheader("📈 문제의 유리함수 그래프")
    
    plot_rational_function(
        current_problem['function'], 
        current_problem['va_val'], 
        current_problem['ha_val'], 
        current_problem['va_ans'].strip('$').replace("x = ", ""), 
        current_problem['ha_ans'].strip('$').replace("y = ", ""),
        st.session_state.g_xmin_quiz, st.session_state.g_xmax_quiz, st.session_state.g_ymin_quiz, st.session_state.g_ymax_quiz
    )

# --- 메인 실행 함수 ---
def main():
    st.set_page_config(
        page_title="유리함수 마스터 앱",
        layout="wide"
    )

    # SessionState 초기화 (그래프 범위)
    if 'g_xmin_quiz' not in st.session_state:
        st.session_state.g_xmin_quiz = -10.0
        st.session_state.g_xmax_quiz = 10.0
        st.session_state.g_ymin_quiz = -10.0
        st.session_state.g_ymax_quiz = 10.0

    # 탭 생성
    tab1, tab2 = st.tabs(["📊 그래프 분석기", "📝 유리함수 문제 풀이"])
    
    with tab1:
        graph_analyzer_tab()
    
    with tab2:
        # 문제 풀이 탭 전용 사이드바 설정
        with st.sidebar:
            st.header("퀴즈 그래프 범위 설정")
            st.number_input("x 축 최소값", value=-10.0, step=1.0, key="g_xmin_quiz")
            st.number_input("x 축 최대값", value=10.0, step=1.0, key="g_xmax_quiz")
            st.number_input("y 축 최소값", value=-10.0, step=1.0, key="g_ymin_quiz")
            st.number_input("y 축 최대값", value=10.0, step=1.0, key="g_ymax_quiz")
        quiz_tab()

if __name__ == "__main__":
    main()

import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import random

# --- 1. 문제 데이터베이스 생성 함수 ---
def generate_rational_function_problems(num_problems=30):
    """30개의 유리함수 문제 데이터베이스를 생성합니다."""
    problems = []
    
    # 계수 범위 설정
    COEF_RANGE = (-5, 5)
    x = sp.Symbol('x')

    while len(problems) < num_problems:
        # ax + b / cx + d 형태의 계수 생성 (c=0, d=0, 점근선이 너무 복잡한 경우는 제외)
        a = random.choice([i for i in range(*COEF_RANGE) if i != 0])
        b = random.randint(*COEF_RANGE)
        c = random.choice([i for i in range(*COEF_RANGE) if i != 0])
        d = random.randint(*COEF_RANGE)

        # 점근선이 정수 또는 간단한 분수가 되도록 조정
        if d % c != 0:
             d = c * random.choice([i for i in range(-5, 5) if i != 0 and i * c + d != 0])
        
        # 함수 정의
        numer = a * x + b
        denom = c * x + d
        f_sym = sp.simplify(numer / denom)
        
        # 수직/수평 점근선 계산
        try:
            va_sol = sp.solve(denom, x)
            if not va_sol: continue
            
            va = va_sol[0]
            va_val_sympy = va.evalf(3)
            va_float = float(va_val_sympy) # 실수형으로 변환 (그래프용)
            
            ha_sympy = sp.limit(f_sym, x, sp.oo)
            ha_val_sympy = ha_sympy.evalf(3)
            ha_float = float(ha_val_sympy) # 실수형으로 변환 (그래프용)
            
        except Exception:
            continue # 계산 오류 시 해당 문제는 건너뛰기

        # 문제의 정답과 풀이
        solution_va = f"$x = {va_val_sympy}$"
        solution_ha = f"$y = {ha_val_sympy}$"
        
        explanation = f"""
        **1. 수직 점근선 ($\mathbf{{x}}$)**
        - 분모가 0이 되는 $x$ 값을 찾습니다. ${sp.latex(denom)} = 0$
        - $x = {va_val_sympy}$ 입니다. (정답: $\mathbf{{{solution_va}}}$)
        
        **2. 수평 점근선 ($\mathbf{{y}}$)**
        - 분자와 분모의 차수가 같으므로, 최고차항 계수의 비를 구합니다.
        - 최고차항 계수는 $x$의 계수 $\\frac{{{a}}}{{{c}}}$ 입니다.
        - $y = {ha_val_sympy}$ 입니다. (정답: $\mathbf{{{solution_ha}}}$)
        
        **3. 정의역 및 치역**
        - 정의역: $\\{{x \\mid x \\neq {va_val_sympy}\}}$
        - 치역: $\\{{y \\mid y \\neq {ha_val_sympy}\}}$
        """

        problem_data = {
            'id': len(problems) + 1,
            'function': f_sym,
            'function_str': f"({sp.latex(numer)})/({sp.latex(denom)})",
            'va_ans': solution_va,
            'ha_ans': solution_ha,
            'explanation': explanation,
            'va_val': va_float,  # 실수형으로 저장
            'ha_val': ha_float,  # 실수형으로 저장
            'va_str': str(va_val_sympy), # 문자열로 저장 (채점용)
            'ha_str': str(ha_val_sympy), # 문자열로 저장 (채점용)
        }
        problems.append(problem_data)
        
    return problems

# --- 2. 그래프 그리기 함수 ---
def plot_rational_function(f_sym, va_float, ha_float, va_val_str, ha_val_str, x_min, x_max, y_min, y_max):
    """Matplotlib을 사용하여 유리함수 그래프를 그립니다."""
    try:
        x = sp.Symbol('x')
        f_np = sp.lambdify(x, f_sym, 'numpy')
        
        # X 값 생성 시 점근선을 피하기 위해 두 영역으로 나눕니다. (그래프 안정화)
        if va_float is not None and x_min < va_float < x_max:
            # 점근선 근처를 넉넉하게 건너뜁니다.
            gap = 0.01 
            x_vals_1 = np.linspace(x_min, va_float - gap, 250)
            x_vals_2 = np.linspace(va_float + gap, x_max, 250)
            
            x_vals = np.concatenate([x_vals_1, x_vals_2])
            y_vals = f_np(x_vals)
            
        else:
            x_vals = np.linspace(x_min, x_max, 500)
            y_vals = f_np(x_vals)
            
        # 너무 큰 Y 값은 NaN 처리하여 그래프가 범위 밖으로 나가는 것을 막습니다.
        y_vals[y_vals > y_max * 2] = np.nan
        y_vals[y_vals < y_min * 2] = np.nan


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
        # 그래프 그리기가 실패했을 때 사용자에게 친절한 메시지를 표시
        st.error("📉 **그래프를 그리는 중 오류가 발생했습니다.**")
        st.warning(f"**원인**: 입력 함수 또는 설정된 X, Y 범위가 너무 좁거나 계산하기 어렵습니다.")
        st.info("X, Y 축 범위를 넓게 설정해 보세요.")
        # 디버깅을 위한 코드 (운영 환경에서는 주석 처리 권장)
        # st.code(f"Graph Plot Error: {type(e).__name__}: {e}") 

# --- 3. Streamlit 앱 메인 함수 ---
def main():
    st.title("🔢 유리함수 마스터 챌린지")
    st.markdown("점근선을 찾아보고, 그래프도 확인해 보세요!")

    # 세션 상태 초기화 및 문제 로드
    if 'problems' not in st.session_state:
        st.session_state.problems = generate_rational_function_problems(30)
        st.session_state.current_index = 0
        st.session_state.attempts = [0] * 30 
        st.session_state.show_solution = [False] * 30 

    total_problems = len(st.session_state.problems)
    current_index = st.session_state.current_index
    current_problem = st.session_state.problems[current_index]
    
    st.header(f"문제 {current_index + 1} / {total_problems}")

    # --- 문제 출제 ---
    st.markdown("다음 유리함수의 **수직 점근선**과 **수평 점근선**을 구하고 입력하세요.")
    st.latex(f"f(x) = {current_problem['function_str']}")
    
    # --- 문제 새로고침 및 이동 버튼 ---
    col_nav_1, col_nav_2, col_nav_3, col_nav_4 = st.columns([1, 1, 1, 3])

    if col_nav_1.button("◀ 이전 문제", key="prev_btn"):
        st.session_state.current_index = (current_index - 1) % total_problems
        # 페이지 이동 시 입력값 초기화
        st.session_state.input_va = "" 
        st.session_state.input_ha = ""
        st.rerun()

    if col_nav_2.button("▶ 다음 문제", key="next_btn"):
        st.session_state.current_index = (current_index + 1) % total_problems
        st.session_state.input_va = "" 
        st.session_state.input_ha = ""
        st.rerun()
        
    def refresh_problem():
        new_index = random.randint(0, total_problems - 1)
        st.session_state.current_index = new_index
        st.session_state.input_va = "" 
        st.session_state.input_ha = ""
        st.rerun()

    if col_nav_3.button("🔄 새로운 문제", key="refresh_btn"):
        refresh_problem()

    st.markdown("---")

    # --- 입력 및 채점 ---
    st.subheader("정답 입력")
    
    # 입력 필드 key를 사용하여 페이지 이동 시 값이 남아있지 않도록 처리
    user_va = st.text_input("수직 점근선 (예: x=3 또는 x=1/2)", key="input_va", value="")
    user_ha = st.text_input("수평 점근선 (예: y=2 또는 y=-0.5)", key="input_ha", value="")

    if st.button("정답 확인 ✅", key="submit_btn"):
        
        # SymPy 정답 문자열과 사용자의 입력 문자열을 비교합니다.
        # 공백 제거 및 소문자 통일 (x=3 vs x = 3, X=3 등 허용)
        clean_user_va = user_va.lower().replace(" ", "")
        clean_user_ha = user_ha.lower().replace(" ", "")
        
        # SymPy 정답은 x=... 형태로 저장되어 있으므로, 여기서도 x=... 형식으로 만듭니다.
        # 소수점 오류 방지를 위해 사용자의 입력값(문자열)을 SymPy로 처리하여 비교합니다.
        
        # 정답: $x=...$ 에서 x=... 부분만 추출
        clean_ans_va = current_problem['va_ans'].strip('$').lower().replace(" ", "")
        clean_ans_ha = current_problem['ha_ans'].strip('$').lower().replace(" ", "")
        
        is_correct_va = clean_user_va == clean_ans_va
        is_correct_ha = clean_user_ha == clean_ans_ha
        
        is_all_correct = is_correct_va and is_correct_ha
        
        st.session_state.attempts[current_index] += 1
        current_attempts = st.session_state.attempts[current_index]

        if is_all_correct:
            st.success("🎉 정답입니다! 완벽하게 이해하셨네요.")
            st.session_state.show_solution[current_index] = True
            
        else:
            if current_attempts < 2:
                st.warning(f"오답입니다. 다시 한번 풀어보세요! (현재 시도 횟수: {current_attempts}회)")
            else:
                # 수정된 부분: "정답과 풀이를 보여드릴게요" 대신 바로 정답 풀이 표시
                st.error("😭 오답입니다. 두 번 틀리셨으므로 **해당 문제의 정답과 풀이를** 바로 보여드립니다.")
                st.session_state.show_solution[current_index] = True
        
        # 채점 결과를 반영하기 위해 페이지 새로고침
        st.rerun() 

    # --- 정답 및 풀이 섹션 ---
    if st.session_state.show_solution[current_index] or st.session_state.attempts[current_index] >= 2:
        st.subheader("💡 정답 및 풀이")
        # 수정된 부분: 정답과 풀이 메시지를 명확하게 표시
        st.markdown(f"**정답: 수직 점근선**은 {current_problem['va_ans']}, **수평 점근선**은 {current_problem['ha_ans']} 입니다.")
        st.markdown("---")
        st.markdown("**상세 풀이:**")
        st.markdown(current_problem['explanation'])

    # --- 그래프 섹션 ---
    st.markdown("---")
    st.subheader("📈 문제의 유리함수 그래프")
    
    # 그래프 범위 설정은 사이드바에 있으므로 그래프 함수 호출만
    plot_rational_function(
        current_problem['function'], 
        current_problem['va_val'], 
        current_problem['ha_val'], 
        current_problem['va_ans'].strip('$').replace("x = ", ""), 
        current_problem['ha_ans'].strip('$').replace("y = ", ""),
        st.session_state.g_xmin, st.session_state.g_xmax, st.session_state.g_ymin, st.session_state.g_ymax
    )


if __name__ == "__main__":
    # 그래프 범위 입력을 위한 key 초기화 (SessionState 오류 방지)
    if 'g_xmin' not in st.session_state:
        st.session_state.g_xmin = -10.0
        st.session_state.g_xmax = 10.0
        st.session_state.g_ymin = -10.0
        st.session_state.g_ymax = 10.0

    # 입력창 초기값을 위해 key 초기화
    if 'input_va' not in st.session_state:
        st.session_state.input_va = ""
        st.session_state.input_ha = ""
        
    main()

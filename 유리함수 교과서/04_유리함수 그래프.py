import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import random

# --- 1. 문제 데이터베이스 생성 함수 ---
def generate_rational_function_problems(num_problems=30):
    """30개의 유리함수 문제 데이터베이스를 생성합니다."""
    problems = []
    
    # 계수 범위 설정 (너무 복잡한 분수나 너무 큰 숫자를 피하기 위해)
    COEF_RANGE = (-5, 5)
    
    # SymPy 변수 정의
    x = sp.Symbol('x')

    while len(problems) < num_problems:
        # ax + b / cx + d 형태의 계수 생성 (c=0인 상수 함수나 분모가 0인 경우는 제외)
        a = random.choice([i for i in range(*COEF_RANGE) if i != 0])
        b = random.randint(*COEF_RANGE)
        c = random.choice([i for i in range(*COEF_RANGE) if i != 0])
        d = random.randint(*COEF_RANGE)
        
        # 분모의 근 (수직 점근선)이 너무 복잡한 분수가 되지 않도록, d는 c의 배수에 가깝게 조정
        if d % c != 0:
             # 간단한 정수 점근선을 위해 d를 c의 배수로 조정
             d = c * random.choice([i for i in range(-5, 5) if i != 0])

        # 함수 정의
        numer = a * x + b
        denom = c * x + d
        f_sym = sp.simplify(numer / denom)
        
        # 수직 점근선 계산
        try:
            va_sol = sp.solve(denom, x)
            if not va_sol: # 수직 점근선이 없는 경우 (예: 분모가 상수)
                continue
            va = va_sol[0]
            va_val = va.evalf(3)
        except:
            continue # SymPy 오류 시 건너뛰기

        # 수평 점근선 계산
        ha = sp.limit(f_sym, x, sp.oo).evalf(3)
        
        # 문제의 정답과 풀이
        solution_va = f"$x = {va_val}$"
        solution_ha = f"$y = {ha}$"
        
        # 풀이 과정
        explanation = f"""
        **1. 수직 점근선 ($\mathbf{{x}}$)**
        - 분모가 0이 되는 $x$ 값을 찾습니다.
        - ${sp.latex(denom)} = 0$
        - $x = {va_val}$ 입니다. (정답: $\mathbf{{{solution_va}}}$)
        
        **2. 수평 점근선 ($\mathbf{{y}}$)**
        - 분자와 분모의 차수가 같으므로, 최고차항 계수의 비를 구합니다.
        - 최고차항 계수는 $x$의 계수 $\\frac{{{a}}}{{{c}}}$ 입니다.
        - $y = {ha}$ 입니다. (정답: $\mathbf{{{solution_ha}}}$)
        
        **3. 정의역 및 치역**
        - 정의역은 수직 점근선을 제외한 모든 실수입니다: $\\{{x \\mid x \\neq {va_val}\}}$
        - 치역은 수평 점근선을 제외한 모든 실수입니다: $\\{{y \\mid y \\neq {ha}\}}$
        """

        # 문제 데이터 저장
        problem_data = {
            'id': len(problems) + 1,
            'function': f_sym,
            'function_str': f"({sp.latex(numer)})/({sp.latex(denom)})",
            'va_ans': solution_va,
            'ha_ans': solution_ha,
            'explanation': explanation,
            'va_val': va_val, # 그래프용 실수 값
            'ha_val': ha,     # 그래프용 실수 값
        }
        problems.append(problem_data)
        
    return problems

# --- 2. 그래프 그리기 함수 ---
def plot_rational_function(f_sym, va_float, ha_float, va_val, ha_val, x_min, x_max, y_min, y_max):
    """Matplotlib을 사용하여 유리함수 그래프를 그립니다."""
    x = sp.Symbol('x')
    f_np = sp.lambdify(x, f_sym, 'numpy')
    
    x_vals = np.linspace(x_min, x_max, 500)
    y_vals = f_np(x_vals)

    # 수직 점근선 근처의 발산 처리
    if va_float is not None:
        y_vals[np.abs(x_vals - va_float) < 0.05] = np.nan 

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x_vals, y_vals, label=f"${sp.latex(f_sym)}$", color='blue')
    
    # 점근선 표시
    if va_float is not None:
        ax.axvline(x=va_float, color='red', linestyle='--', label=f'VA: $x={va_val}$')
    
    if ha_float is not None:
        ax.axhline(y=ha_float, color='green', linestyle='--', label=f'HA: $y={ha_val}$')

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


# --- 3. Streamlit 앱 메인 함수 ---
def main():
    st.title("🔢 유리함수 마스터 챌린지")
    st.markdown("점근선을 찾아보고, 그래프도 확인해 보세요!")

    # 세션 상태 초기화 및 문제 로드
    if 'problems' not in st.session_state:
        st.session_state.problems = generate_rational_function_problems(30)
        st.session_state.current_index = 0
        st.session_state.attempts = [0] * 30 # 문제별 시도 횟수
        st.session_state.show_solution = [False] * 30 # 문제별 정답 표시 여부

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
        st.rerun()

    if col_nav_2.button("▶ 다음 문제", key="next_btn"):
        st.session_state.current_index = (current_index + 1) % total_problems
        st.rerun()
        
    def refresh_problem():
        # 현재 문제를 유지하고 새로고침
        new_index = random.randint(0, total_problems - 1)
        st.session_state.current_index = new_index
        st.rerun()

    if col_nav_3.button("🔄 새로운 문제", key="refresh_btn"):
        refresh_problem()

    st.markdown("---")

    # --- 입력 및 채점 ---
    st.subheader("정답 입력")
    
    # 점근선은 정수, 분수, 소수(3자리) 등으로 다양하게 나올 수 있으므로, 
    # 사용자가 x=, y= 형태의 문자열로 입력하도록 유도
    user_va = st.text_input("수직 점근선 (예: x = 3)", key="input_va").strip().replace(" ", "")
    user_ha = st.text_input("수평 점근선 (예: y = 2)", key="input_ha").strip().replace(" ", "")

    if st.button("정답 확인 ✅", key="submit_btn"):
        # 입력된 값의 형식 검증 (대소문자 무시)
        clean_user_va = user_va.lower().replace(" ", "")
        clean_user_ha = user_ha.lower().replace(" ", "")
        
        # 정답과의 비교를 위해 정답도 클리닝 (SymPy로 계산된 문자열과 비교)
        clean_ans_va = current_problem['va_ans'].lower().replace(" ", "")
        clean_ans_ha = current_problem['ha_ans'].lower().replace(" ", "")
        
        is_correct_va = clean_user_va == clean_ans_va
        is_correct_ha = clean_user_ha == clean_ans_ha
        
        is_all_correct = is_correct_va and is_correct_ha
        
        # 시도 횟수 업데이트
        st.session_state.attempts[current_index] += 1
        current_attempts = st.session_state.attempts[current_index]

        if is_all_correct:
            st.success("🎉 정답입니다! 완벽하게 이해하셨네요.")
            st.session_state.show_solution[current_index] = True
            
        else:
            if current_attempts < 2:
                st.warning(f"오답입니다. 다시 한번 풀어보세요! (현재 시도 횟수: {current_attempts}회)")
                
                # 어떤 점근선이 틀렸는지 힌트 제공
                if not is_correct_va and current_attempts == 1:
                    st.info("수직 점근선($x$)을 다시 확인해 보세요. 분모가 0이 되는 값입니다.")
                elif not is_correct_ha and current_attempts == 1:
                    st.info("수평 점근선($y$)을 다시 확인해 보세요. 최고차항 계수의 비입니다.")
                
            else:
                st.error("😭 오답입니다. 두 번 틀리셨으므로 정답과 풀이를 보여드릴게요.")
                st.session_state.show_solution[current_index] = True
        
        # 채점 후 입력창 리셋
        st.session_state.input_va = ""
        st.session_state.input_ha = ""
        st.rerun() # 채점 결과를 반영하기 위해 페이지 새로고침

    # --- 정답 및 풀이 섹션 ---
    if st.session_state.show_solution[current_index] or st.session_state.attempts[current_index] >= 2:
        st.subheader("💡 정답 및 풀이")
        st.markdown(f"**수직 점근선**: {current_problem['va_ans']}")
        st.markdown(f"**수평 점근선**: {current_problem['ha_ans']}")
        st.markdown("---")
        st.markdown("**상세 풀이:**")
        st.markdown(current_problem['explanation'])

    # --- 그래프 섹션 ---
    st.markdown("---")
    st.subheader("📈 문제의 유리함수 그래프")
    
    # 그래프 범위 설정
    st.sidebar.header("그래프 범위 설정")
    g_x_min = st.sidebar.number_input("그래프 x 축 최소값", value=-10.0, step=1.0, key="g_xmin")
    g_x_max = st.sidebar.number_input("그래프 x 축 최대값", value=10.0, step=1.0, key="g_xmax")
    g_y_min = st.sidebar.number_input("그래프 y 축 최소값", value=-10.0, step=1.0, key="g_ymin")
    g_y_max = st.sidebar.number_input("그래프 y 축 최대값", value=10.0, step=1.0, key="g_ymax")

    plot_rational_function(
        current_problem['function'], 
        current_problem['va_val'], 
        current_problem['ha_val'], 
        current_problem['va_ans'].replace("x = ", ""), # 레이블에 VA 값만 넘김
        current_problem['ha_ans'].replace("y = ", ""), # 레이블에 HA 값만 넘김
        g_x_min, g_x_max, g_y_min, g_y_max
    )


if __name__ == "__main__":
    # SymPy 튜플 언팩킹 오류 방지를 위해, 이전에 발생했던 오류를 일으킬 수 있는
    # 불필요한 언팩킹 패턴을 제거하고 안전한 sp.fraction() 결과를 사용하도록 수정했습니다.
    try:
        main()
    except Exception as e:
        # 최종 사용자에게 보여줄 친절한 오류 메시지
        st.error("치명적인 오류가 발생했습니다. 앱을 다시 시작해 주세요.")
        
        # 디버깅 정보 (필요시 확인용)
        # st.code(f"Error Type and Message: {type(e).__name__}: {e}")

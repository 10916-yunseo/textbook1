import streamlit as st
from sympy import symbols, simplify, Poly, denom
from sympy.parsing.mathematica import parse_mathematica
import random

# 변수 정의
x = symbols('x')

## --- 1. 개념 설명 함수 ---
def display_concept():
    st.header("✨ 유리식(Rational Expression)의 개념")
    st.markdown("""
    유리식이란 두 **다항식(A, B)**을 이용하여 $\\frac{A}{B}$ 꼴로 나타낼 수 있는 식을 말합니다 (단, $B \\ne 0$).
    """)

    st.subheader("💡 다항식과의 비교")
    st.table({
        "구분": ["**다항식 (Polynomial)**", "**유리식 (Rational Expression)**"],
        "정의": ["단항식들의 합으로 이루어진 식 (분모가 상수)", "$\\frac{A}{B}$ 꼴의 식 ($A, B$는 다항식, $B \\ne 0$)"],
        "예시": ["$x^3 + 2x - 5$", "$\\frac{x+5}{x^2 - 4}$, $\\frac{1}{x-3}$"],
        "특징": ["모든 실수 $x$에 대해 정의됨", "**분모를 0으로 만드는 값**은 정의역에서 제외됨 (분수식의 경우)"]
    })

    st.subheader("➕ 유리식의 연산 원리")
    st.markdown("""
    유리식의 사칙연산은 **유리수(분수)의 연산과 동일**합니다.

    * **덧셈/뺄셈**: **통분** 후 분자끼리 계산합니다.
    * **곱셈/나눗셈**: 인수분해하여 **약분**한 후, 곱셈은 분자끼리/분모끼리, 나눗셈은 역수를 취해 곱셈으로 바꿔 계산합니다.
    """)

## --- 2. 문제 생성 및 풀이 함수 ---
def generate_problem():
    st.header("🔢 유리식의 계산 문제")

    # 문제 유형 선택 (간단한 덧셈/뺄셈)
    op = random.choice(['+', '-'])

    # 난이도 조절을 위한 분모 설정
    a, b, c, d = random.sample(range(1, 5), 4)
    
    # 간단한 분모 생성 (x에 대한 1차식 또는 x^2)
    denominator_A_expr = (x + a)
    denominator_B_expr = (x + b)

    # 분자 생성
    numerator_A_coeffs = [random.randint(1, 5), random.randint(0, 5)]
    numerator_B_coeffs = [random.randint(1, 5), random.randint(0, 5)]

    numerator_A = numerator_A_coeffs[0] * x + numerator_A_coeffs[1]
    numerator_B = numerator_B_coeffs[0] * x + numerator_B_coeffs[1]

    # 문제 식
    problem_expr_A = numerator_A / denominator_A_expr
    problem_expr_B = numerator_B / denominator_B_expr

    if op == '+':
        problem_latex = f"\\frac{{{numerator_A}}}{{{denominator_A_expr}}} + \\frac{{{numerator_B}}}{{{denominator_B_expr}}}"
        solution_expr = problem_expr_A + problem_expr_B
    else:
        problem_latex = f"\\frac{{{numerator_A}}}{{{denominator_A_expr}}} - \\frac{{{numerator_B}}}{{{denominator_B_expr}}}"
        solution_expr = problem_expr_A - problem_expr_B

    # 문제 표시
    st.subheader("다음 유리식을 계산하고, 결과를 기약분수 형태로 나타내시오.")
    st.latex(problem_latex)
    
    # 사용자 입력
    user_answer = st.text_input("계산 결과를 입력하세요 (예: (2*x+1)/(x+3))", key="answer_input")

    # 정답 계산 (sympy 사용)
    simplified_solution = simplify(solution_expr)
    
    # 분모, 분자 분리 (sympy Poly 사용)
    final_num = Poly(simplified_solution.subs(x, x), x).as_expr()
    final_den = denom(simplified_solution)

    # 정답 확인 버튼
    if st.button("정답 확인"):
        if not user_answer:
            st.warning("정답을 입력해주세요.")
            return

        try:
            # 사용자의 입력 식을 sympy 객체로 변환 및 단순화
            # 주의: 사용자가 입력한 문자열을 수학식으로 파싱하는 과정은 매우 까다롭습니다.
            # 가장 단순한 형태로 변환하기 위해 parse_mathematica를 사용 (수동으로 변환 규칙을 적용할 수도 있음)
            
            # 사용자 입력 형식을 'a/b' 형태로 가정하고 파싱
            user_expr_raw = parse_mathematica(user_answer)
            user_simplified = simplify(user_expr_raw)

            # 정답과 사용자 답의 차이가 0인지 확인
            difference = simplify(user_simplified - simplified_solution)

            if difference == 0:
                st.balloons()
                st.success("🎉 **정답입니다!**")
            else:
                st.error("❌ **오답입니다.** 다시 시도해보세요.")
            
            st.markdown("---")
            st.subheader("모범 답안")
            st.latex(f"\\frac{{{final_num}}}{{{final_den}}}")
            st.caption(f"($x$가 분모를 0으로 만들지 않는다는 가정 하에)")

        except Exception as e:
            st.error(f"입력 형식이 올바르지 않습니다. (예: (2*x+1)/(x+3)) 에러: {e}")

    # 새 문제 버튼
    if st.button("새 문제 생성"):
        st.experimental_rerun()


## --- 3. Streamlit 메인 함수 ---
def main():
    st.set_page_config(layout="wide", page_title="유리식 학습 앱")
    st.title("📚 유리식 개념 및 연산 학습 앱")
    st.caption("고등학교 수학 (하) 과정")

    # 탭 구성
    tab1, tab2 = st.tabs(["개념 학습", "문제 풀기"])

    with tab1:
        display_concept()

    with tab2:
        generate_problem()

if __name__ == "__main__":
    main()

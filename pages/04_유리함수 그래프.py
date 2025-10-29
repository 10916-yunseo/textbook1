import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import re # 정규 표현식 라이브러리 추가

# 페이지 설정
st.set_page_config(
    page_title="유리함수 그래프",
    layout="wide"
)

def preprocess_expression(expression):
    """
    사용자가 입력한 수학식을 Python이 해석할 수 있도록 전처리합니다.
    - '2x'를 '2*x'로, 'x^2'을 'x**2'로 변환합니다.
    """
    # 1. 'x' 앞에 숫자가 오거나 괄호가 오는 경우 '*' 추가 (예: 2x -> 2*x, 3(x) -> 3*(x))
    # 단, 'x'가 아닌 다른 변수나 함수 이름의 일부인 경우는 제외
    expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression)
    expression = re.sub(r'(\))([a-zA-Z])', r'\1*\2', expression)
    
    # 2. 거듭제곱 '^'를 Python의 '**'로 변환 (예: x^2 -> x**2)
    expression = expression.replace('^', '**')
    
    return expression

def plot_rational_function(numerator_str, denominator_str):
    """
    사용자 입력 문자열로부터 유리함수 그래프를 그립니다.
    """
    
    # 입력 식 전처리
    preprocessed_numerator = preprocess_expression(numerator_str)
    preprocessed_denominator = preprocess_expression(denominator_str)
    
    try:
        # x 값의 범위 설정
        x = np.linspace(-10, 10, 400)
        
        # 문자열을 파이썬 코드로 변환하여 함수 정의
        P = lambda x_val: eval(preprocessed_numerator, {"x": x_val, "np": np})
        Q = lambda x_val: eval(preprocessed_denominator, {"x": x_val, "np": np})
        
        # 함수 값 계산
        y = P(x) / Q(x)
        
        # 수직 점근선 찾기 (기존 로직 유지)
        asymptotes_x = []
        x_check = np.linspace(-10, 10, 2000)
        Q_check = Q(x_check)
        
        for i in range(len(Q_check) - 1):
            if np.sign(Q_check[i]) != np.sign(Q_check[i+1]) and np.abs(Q_check[i]) < 0.1:
                asymptotes_x.append(x_check[i])
        
        asymptotes_x = sorted(list(set(np.round(asymptotes_x, 2))))
        
        # 그래프 그리기
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 불연속점 처리 (점근선 근처의 극단적인 값들을 NaN으로 처리하여 끊어서 그림)
        y[np.abs(y) > 50] = np.nan 

        ax.plot(x, y, label=f'$y = \\frac{{{numerator_str}}}{{{denominator_str}}}$')
        
        # 수직 점근선 표시
        for x_a in asymptotes_x:
            ax.axvline(x=x_a, color='r', linestyle='--', label=f'점근선 x={x_a}' if x_a == asymptotes_x[0] else None)
        
        # 수평 점근선 (표시 로직은 간결화를 위해 생략하며, 필요시 복구 가능)
        
        ax.set_title(f'유리함수 그래프: $y = \\frac{{{numerator_str}}}{{{denominator_str}}}$')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.grid(True)
        ax.set_ylim(-10, 10) # y축 범위를 제한하여 보기 좋게 조정
        ax.legend()
        st.pyplot(fig)
        
        if asymptotes_x:
            st.info(f"**수직 점근선**: $x = {', '.join(map(str, asymptotes_x))}$ (분모가 0이 되는 값)")
        
    except Exception as e:
        # 오류 발생 시 사용자에게 친절하게 안내
        st.error(f"❌ 그래프를 그리는 데 오류가 발생했습니다. 다음 사항을 확인해 주세요:")
        st.markdown(f"""
        * **곱셈 기호**: `2x` 대신 `2*x`를 사용해 주세요. (자동 변환을 시도했으나 복잡한 식은 직접 입력해야 합니다.)
        * **거듭제곱**: $x^2$ 대신 `x**2`을 사용해 주세요.
        * **오류 내용**: `{e}`
        """)


# --- 앱 본문 시작 ---

st.title("📊 유리함수 그래프")
st.markdown("---")

## 📖 개념 이해: 유리함수란?
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 유리함수의 정의")
    st.markdown("""
    **유리함수(Rational Function)**는 함수 $y = f(x)$에서 
    $f(x)$가 **유리식**인 함수를 말합니다.
    
    쉽게 말해, 분모와 분자에 모두 다항식이 들어 있는 
    $$y = \\frac{P(x)}{Q(x)}$$
    꼴로 나타낼 수 있는 함수입니다. (단, $Q(x)$는 영다항식이 아님)
    """)

with col2:
    st.subheader("2. 정의역과 점근선")
    st.markdown("""
    유리함수의 정의역은 **분모를 0으로 만들지 않는** 실수 전체의 집합입니다.
    
    > **수직 점근선**: 분모 $Q(x)=0$이 되는 $x$ 값에서 발생합니다.
    > **수평 점근선**: $x$가 무한대로 갈 때 $y$가 수렴하는 값입니다 (분자와 분모의 차수 비교).
    """)

st.markdown("---")

## ✍️ 직접 그래프 그리기
st.subheader("4. 함수 식을 넣어 그래프 그려보기")
st.markdown("분자와 분모에 $x$에 대한 식을 입력하고 **Graph Plot** 버튼을 누르세요. \n**주의: 식은 자동 변환되지만, 복잡한 식은 `*`와 `**`를 직접 사용하는 것이 안전합니다.**")

with st.form("rational_function_form"):
    numerator_input = st.text_input("분자 (Numerator, P(x))", value="3")
    denominator_input = st.text_input("분모 (Denominator, Q(x))", value="x-2")
    
    # 예시 버튼
    st.markdown("**✨ 추천 예시 식**")
    st.code("y = 3 / (x - 2) + 1  ➡️ 분자: '3', 분모: 'x-2'")
    st.code("y = (2*x - 5) / (x - 3) ➡️ 분자: '2*x-5', 분모: 'x-3'")
    st.code("y = x / (x**2 + 1)   ➡️ 분자: 'x', 분모: 'x**2 + 1'")
    
    submitted = st.form_submit_button("Graph Plot")

if submitted:
    plot_rational_function(numerator_input, denominator_input)

st.markdown("---")

## ✅ 확인 퀴즈 (3문제)
st.subheader("5. 유리함수 그래프 확인 퀴즈")
st.markdown("개념을 정확히 이해했는지 확인해 봅시다.")

quiz_answers = {}

# 퀴즈 1
st.markdown("### 문제 1")
st.markdown("유리함수 $y = \\frac{1}{x-2} + 3$의 **수직 점근선**의 방정식은 무엇인가요?")
quiz_answers['q1'] = st.text_input("답변 1 (예: x=2)", key='q1')

# 퀴즈 2
st.markdown("### 문제 2")
st.markdown("함수 $y = \\frac{k}{x}$에서, 상수 $k$의 값이 양수($k>0$)일 때, 그래프가 지나는 사분면은 어디인가요? (정답을 모두 고르시오)")
quiz_answers['q2'] = st.multiselect("답변 2", ['제 1 사분면', '제 2 사분면', '제 3 사분면', '제 4 사분면'], key='q2')

# 퀴즈 3
st.markdown("### 문제 3")
st.markdown("유리함수 $y = \\frac{2x+1}{x-1}$을 표준형 $y = \\frac{k}{x-p} + q$ 꼴로 바꿨을 때, **수평 점근선**의 방정식은 무엇인가요?")
quiz_answers['q3'] = st.text_input("답변 3 (예: y=2)", key='q3')

if st.button("정답 확인"):
    st.markdown("---")
    st.subheader("🎉 퀴즈 결과")
    
    # 정답 채점
    score = 0
    
    # 문제 1 채점
    q1_correct = (quiz_answers['q1'].replace(' ', '').lower() in ['x=2', '2'])
    if q1_correct:
        st.success(f"**문제 1 정답**: **x=2** (정답)")
        score += 1
    else:
        st.error(f"**문제 1 정답**: **x=2** (오답)")

    # 문제 2 채점
    q2_correct_set = set(['제 1 사분면', '제 3 사분면'])
    q2_user_set = set(quiz_answers['q2'])
    if q2_user_set == q2_correct_set:
        st.success(f"**문제 2 정답**: **제 1 사분면, 제 3 사분면** (정답)")
        score += 1
    else:
        st.error(f"**문제 2 정답**: **제 1 사분면, 제 3 사분면** (오답)")
        
    # 문제 3 채점
    q3_correct = (quiz_answers['q3'].replace(' ', '').lower() in ['y=2', '2'])
    if q3_correct:
        st.success(f"**문제 3 정답**: **y=2** (정답) $\\rightarrow$ 분자/분모의 $x$ 계수 비 $\\frac{2}{1}=2$")
        score += 1
    else:
        st.error(f"**문제 3 정답**: **y=2** (오답) $\\rightarrow$ 분자/분모의 $x$ 계수 비 $\\frac{2}{1}=2$")
        
    st.markdown(f"### 총점: **{score} / 3**")
    if score == 3:
        st.balloons()
        st.markdown("**✨ 훌륭합니다! 유리함수의 핵심 개념을 모두 이해하셨습니다!**")

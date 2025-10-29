import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import re
import random

# --- 1. 전처리 및 그래프 함수 ---

def preprocess_expression(expression):
    """
    사용자가 입력한 수학식을 Python이 해석할 수 있도록 전처리합니다.
    - '2x'를 '2*x'로, 'x^2'을 'x**2'로 변환합니다.
    """
    expression = expression.replace(' ', '')
    expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression)
    expression = re.sub(r'(\))([a-zA-Z])', r'\1*\2', expression)
    expression = expression.replace('^', '**')
    
    return expression

def plot_rational_function(numerator_str, denominator_str):
    """사용자 입력 문자열로부터 유리함수 그래프를 그립니다."""
    
    preprocessed_numerator = preprocess_expression(numerator_str)
    preprocessed_denominator = preprocess_expression(denominator_str)
    
    try:
        x = np.linspace(-10, 10, 400)
        
        P = lambda x_val: eval(preprocessed_numerator, {"x": x_val, "np": np})
        Q = lambda x_val: eval(preprocessed_denominator, {"x": x_val, "np": np})
        
        y = P(x) / Q(x)
        
        # 수직 점근선 찾기 (분모가 0이 되는 지점 탐색)
        asymptotes_x = []
        x_check = np.linspace(-10, 10, 2000)
        Q_check = Q(x_check)
        
        for i in range(len(Q_check) - 1):
            if np.sign(Q_check[i]) != np.sign(Q_check[i+1]) and np.abs(Q_check[i]) < 0.1:
                asymptotes_x.append(x_check[i])
        
        asymptotes_x = sorted(list(set(np.round(asymptotes_x, 2))))
        
        fig, ax = plt.subplots(figsize=(8, 6))
        y[np.abs(y) > 50] = np.nan 

        ax.plot(x, y, label=f'$y = \\frac{{{numerator_str}}}{{{denominator_str}}}$')
        
        for x_a in asymptotes_x:
            ax.axvline(x=x_a, color='r', linestyle='--', label=f'점근선 x={x_a}' if x_a == asymptotes_x[0] else None)
        
        ax.set_title(f'유리함수 그래프: $y = \\frac{{{numerator_str}}}{{{denominator_str}}}$')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.grid(True)
        ax.set_ylim(-10, 10) 
        ax.legend()
        st.pyplot(fig)
        
        if asymptotes_x:
            st.info(f"**수직 점근선**: $x = {', '.join(map(str, asymptotes_x))}$ (분모가 0이 되는 값)")
        
    except Exception as e:
        st.error(f"❌ 그래프를 그리는 데 오류가 발생했습니다. 다음 사항을 확인해 주세요:")
        st.markdown(f"**오류 내용**: `{e}`")

# --- 2. 퀴즈 데이터 및 상태 관리 ---

QUIZ_DATA = [
    {
        "id": 1,
        "question": r"유리함수 $y = \frac{1}{x-2} + 3$의 **수직 점근선**과 **수평 점근선**의 교점 좌표는 무엇인가요? (예: (2, 3))",
        "answer": "(2, 3)",
        "explanation": r"**수직 점근선**: 분모가 0이 되는 $x=2$입니다. \n**수평 점근선**: 평행이동한 값 $y=3$입니다. \n따라서 교점은 $\mathbf{(2, 3)}$입니다.",
        "type": "text_input",
    },
    {
        "id": 2,
        "question": r"유리함수 $y = \frac{2x+1}{x-1}$을 표준형 $y = \frac{k}{x-p} + q$ 꼴로 바꿨을 때 $\mathbf{k+p+q}$의 값은 무엇인가요? (숫자만 입력)",
        "answer": "6",
        "explanation": r"표준형으로 변환하면: $y = \frac{2x+1}{x-1} = \frac{2(x-1) + 3}{x-1} = 2 + \frac{3}{x-1}$. \n따라서 $k=3, p=1, q=2$ 이므로 $k+p+q = 3+1+2=\mathbf{6}$입니다.",
        "type": "text_input",
    },
    {
        "id": 3,
        "question": r"유리함수 $y = \frac{-1}{x}$의 그래프에 대한 설명 중 **옳은 것**을 모두 고르시오.",
        "answer": set(['제 2 사분면과 제 4 사분면을 지난다', '원점에 대해 대칭이다', '수직 점근선은 y축이다']),
        "explanation": r"$y=\frac{k}{x}$에서 $k=-1$로 음수이므로, 그래프는 $\mathbf{제 2 사분면과 제 4 사분면}$을 지납니다. 또한 기본형이므로 $\mathbf{원점에 대해 대칭}$이며, 수직 점근선은 $x=0$, 즉 $\mathbf{y축}$입니다.",
        "type": "multiselect",
        "options": ['원점에 대해 대칭이다', '수직 점근선은 y축이다', '제 1 사분면과 제 3 사분면을 지난다', '제 2 사분면과 제 4 사분면을 지난다'],
    },
    {
        "id": 4,
        "question": r"함수 $y = \frac{x+1}{x-3}$의 그래프를 $x$축 방향으로 $-2$만큼, $y$축 방향으로 $2$만큼 평행이동한 후의 점근선의 교점 $(p, q)$는 무엇인가요? ($p, q$ 순서대로 콤마로 구분하여 입력, 예: 1, 2)",
        "answer": "1, 3",
        "explanation": r"주어진 함수 $y = \frac{x+1}{x-3} = 1 + \frac{4}{x-3}$ 의 점근선은 $x=3, y=1$ 입니다. \n평행이동 ($x$축: $-2$, $y$축: $2$) 후 새로운 점근선은 $x'=3+(-2)=1$, $y'=1+2=3$ 이 됩니다. \n따라서 교점은 $(1, 3)$ 이므로 $\mathbf{1, 3}$ 입니다.",
        "type": "text_input",
    }
]

def initialize_session_state():
    """세션 상태를 초기화합니다."""
    if 'current_quiz_index' not in st.session_state:
        st.session_state.current_quiz_index = random.randrange(len(QUIZ_DATA)) 
    if 'incorrect_attempts' not in st.session_state:
        st.session_state.incorrect_attempts = 0
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False
    if 'quiz_history' not in st.session_state:
        st.session_state.quiz_history = []
    # 사용자 입력값을 저장할 초기 상태 추가 (폼 밖으로 버튼을 빼면서 필요)
    if 'user_answer_value' not in st.session_state:
        st.session_state.user_answer_value = ''
    if 'user_answer_multi_value' not in st.session_state:
        st.session_state.user_answer_multi_value = []

def go_next_quiz():
    """다음 문제로 넘어가기 위해 상태를 리셋하고 새 문제를 설정합니다."""
    
    current_id = QUIZ_DATA[st.session_state.current_quiz_index]["id"]
    if current_id not in st.session_state.quiz_history:
        st.session_state.quiz_history.append(current_id)
        
    available_indices = [i for i, q in enumerate(QUIZ_DATA) if q["id"] not in st.session_state.quiz_history]
    
    if not available_indices:
        st.session_state.quiz_history = []
        new_idx = random.randrange(len(QUIZ_DATA))
    else:
        new_idx = random.choice(available_indices)

    st.session_state.current_quiz_index = new_idx
    st.session_state.incorrect_attempts = 0
    st.session_state.show_result = False
    
    # 사용자 입력값 리셋
    st.session_state.user_answer_value = ''
    st.session_state.user_answer_multi_value = []
    
    # 변경된 함수 사용: st.experimental_rerun() -> st.rerun()
    st.rerun() 

def check_answer(user_input, current_q):
    """사용자 답변을 확인하고 상태를 업데이트합니다."""
    
    is_correct = False
    correct_answer = current_q["answer"]
    
    if current_q["type"] == "text_input":
        user_clean = str(user_input).replace(' ', '').lower()
        answer_clean = str(correct_answer).replace(' ', '').lower()
        
        if ',' in answer_clean:
            user_clean_list = [s.strip() for s in user_clean.split(',')]
            answer_clean_list = [s.strip() for s in answer_clean.split(',')]
            is_correct = (user_clean_list == answer_clean_list)
        else:
            is_correct = (user_clean == answer_clean)
        
    elif current_q["type"] == "multiselect":
        user_set = set(user_input)
        answer_set = correct_answer
        is_correct = (user_set == answer_set)

    if is_correct:
        st.session_state.show_result = True
        st.session_state.is_last_attempt_correct = True
    else:
        st.session_state.incorrect_attempts += 1
        st.session_state.is_last_attempt_correct = False
        
        if st.session_state.incorrect_attempts >= 2:
            st.session_state.show_result = True
            st.session_state.is_last_attempt_correct = False

# --- 3. 앱 본문 레이아웃 ---

st.set_page_config(page_title="유리함수 그래프 및 퀴즈", layout="wide")
initialize_session_state()

st.title("📚 유리함수 그래프 교과서")
st.markdown("---")

## 📖 1. 유리함수의 정의와 개념
col1, col2 = st.columns(2)

with col1:
    st.subheader("1.1 유리함수의 정의")
    st.markdown("""
    **유리함수(Rational Function)**는 함수 $y = f(x)$에서 
    $f(x)$가 **유리식**인 함수를 말합니다.
    
    $$y = \\frac{P(x)}{Q(x)}$$
    꼴로 나타낼 수 있습니다. (단, $P(x), Q(x)$는 다항식이고, $Q(x)$는 영다항식이 아님)
    
    * **다항함수**: 분모 $Q(x)$가 상수인 경우입니다 (예: $y=2x-1$).
    * **분수함수**: 분모 $Q(x)$에 $x$가 포함된 경우이며, 일반적으로 유리함수라 하면 분수함수를 뜻합니다.
    """)

with col2:
    st.subheader("1.2 정의역과 점근선")
    st.markdown("""
    유리함수의 정의역은 특별한 언급이 없으면 **분모를 0으로 만들지 않는**
    실수 전체의 집합입니다.
    
    * **수직 점근선**: 분모 $Q(x)=0$이 되는 $x$ 값에서 발생합니다.
    * **수평 점근선**: $x$가 $\pm\infty$로 갈 때 $y$가 수렴하는 값입니다.
    
    ### 표준형 $y = \\frac{k}{x-p} + q$의 특징
    * **점근선**: $x = p$, $y = q$
    * **대칭의 중심**: 점 $(p, q)$에 대하여 대칭입니다.
    """)

st.markdown("---")

## ✍️ 2. 직접 그래프 그려보기
st.subheader("2. 함수 식을 넣어 그래프 그려보기")
st.markdown("분자와 분모에 $x$에 대한 식을 입력하고 **Graph Plot** 버튼을 누르세요. **(예: 분자 `3`, 분모 `x-2` 또는 분자 `2*x-5`, 분모 `x-3`)**")

with st.form("rational_function_form"):
    col_num, col_den = st.columns(2)
    with col_num:
        numerator_input = st.text_input("분자 (P(x))", value="3")
    with col_den:
        denominator_input = st.text_input("분모 (Q(x))", value="x-2")
    
    submitted = st.form_submit_button("Graph Plot")

if submitted:
    plot_rational_function(numerator_input, denominator_input)

st.markdown("---")

## ✅ 3. 유리함수 개념 확인 퀴즈
st.subheader("3. 유리함수 개념 확인 퀴즈")

current_q_index = st.session_state.current_quiz_index
current_q = QUIZ_DATA[current_q_index]

st.markdown(f"### ❓ 문제 {current_q['id']} (총 {len(QUIZ_DATA)}문제 중)")
st.markdown(current_q["question"])

# 사용자 입력 필드를 폼 외부로 꺼내서 버튼 충돌 방지
user_input_key = "current_user_input"

if current_q["type"] == "text_input":
    user_input = st.text_input("답변 입력", key=user_input_key, value=st.session_state.user_answer_value, placeholder=current_q.get("placeholder", ""), disabled=st.session_state.show_result)
    
elif current_q["type"] == "multiselect":
    user_input = st.multiselect("답변 선택 (하나 이상 선택 가능)", current_q["options"], key=user_input_key, default=st.session_state.user_answer_multi_value, disabled=st.session_state.show_result)


col_check, col_new = st.columns([1, 1])

# 버튼 클릭 핸들링을 위한 함수
def handle_check_answer():
    if current_q["type"] == "text_input":
        # 현재 입력된 텍스트 값을 세션 상태에 저장 후 체크 함수 호출
        check_answer(st.session_state[user_input_key], current_q)
    elif current_q["type"] == "multiselect":
        # 현재 선택된 멀티셀렉트 값을 세션 상태에 저장 후 체크 함수 호출
        check_answer(st.session_state[user_input_key], current_q)
    
with col_check:
    # 정답 확인 버튼. 클릭 시 handle_check_answer 호출
    st.button("정답 확인", on_click=handle_check_answer, disabled=st.session_state.show_result)
    
with col_new:
    # 랜덤 문제 가져오기 버튼. on_click 시 go_next_quiz 호출
    st.button("랜덤 문제 가져오기 🔄", on_click=go_next_quiz)


# 정답 확인 및 피드백 로직 (버튼 클릭 후 상태 변화에 따라 실행)
if st.session_state.show_result:
    
    if st.session_state.is_last_attempt_correct:
        st.success(f"✅ 정답입니다! (총 오답 횟수: {st.session_state.incorrect_attempts}회)")
    else:
        st.warning(f"⚠️ 오답 횟수 2회 초과로 정답을 공개합니다. 다음 문제로 넘어가세요.")
        
    # 정답 및 풀이 표시
    st.markdown("#### 정답 및 풀이")
    st.markdown(f"**정답**: **{current_q['answer']}**")
    st.info(current_q['explanation'])
    
    # 문제 해결 시 "다음 문제" 버튼 표시
    st.button("다음 문제 →", key="next_quiz_button", on_click=go_next_quiz)

# 오답 피드백 (정답 확인 버튼이 눌렸고, 결과가 아직 공개되지 않았을 때)
elif st.session_state.incorrect_attempts > 0 and not st.session_state.show_result:
    st.error(f"❌ 오답입니다. 다시 한 번 풀어보세요! (현재 오답 횟수: {st.session_state.incorrect_attempts}회)")

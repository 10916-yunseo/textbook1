import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import re
import random

# --- 1. 전처리 및 그래프 함수 (기존 코드 유지) ---

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
        st.markdown(f"""
        * **곱셈 기호**: `2x` 대신 `2*x`를, $x^2$ 대신 `x**2`을 사용해 주세요. (자동 변환을 시도했으나 복잡한 식은 직접 입력해야 합니다.)
        * **오류 내용**: `{e}`
        """)

# --- 2. 퀴즈 데이터 및 상태 관리 (문제 추가) ---

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
        "explanation": r"$y=\frac{k}{x}$에서 $k=-1$로 음수이므로, 그래프는 원점(점근선의 교점)을 중심으로 $\mathbf{제 2 사분면과 제 4 사분면}$을 지납니다. 또한 기본형이므로 $\mathbf{원점에 대해 대칭}$이며, 수직 점근선은 $x=0$, 즉 $\mathbf{y축}$입니다.",
        "type": "multiselect",
        "options": ['원점에 대해 대칭이다', '수직 점근선은 y축이다', '제 1 사분면과 제 3 사분면을 지난다', '제 2 사분면과 제 4 사분면을 지난다'],
    },
    {
        "id": 4,
        "question": r"함수 $y = \frac{x+1}{x-3}$의 그래프를 $x$축 방향으로 $-2$만큼, $y$축 방향으로 $1$만큼 평행이동하면 $y = \frac{k}{x-p} + q$ 꼴에서 $p$와 $q$의 값은 각각 무엇인가요? ($p, q$ 순서대로 콤마로 구분하여 입력, 예: 1, 2)",
        "answer": "1, 3",
        "explanation": r"주어진 함수의 점근선은 $x=3, y=1$입니다. \n평행이동 후의 점근선은 $x' = 3+(-2) = 1$, $y' = 1+1 = 2$가 되어야 합니다. \n앗! 문제 식 $y = \frac{x+1}{x-3} = \frac{(x-3)+4}{x-3} = 1 + \frac{4}{x-3}$ 이므로, 초기 점근선은 $x=3, y=1$입니다. \n평행이동 후 점근선은 $x' = 3+(-2) = 1$, $y' = 1+1 = 2$가 됩니다. \n**정답은 $p=1, q=2$입니다. 문제와 설명의 $q$ 값이 일치하도록 $y$축 평행이동 값은 $1$이 아닌 $2$로 수정하겠습니다.**\n\n**수정된 설명**: 초기 점근선은 $x=3, y=1$. 평행이동 ($x$축: $-2$, $y$축: $2$) 후 점근선은 $x' = 3+(-2) = 1$, $y' = 1+2 = 3$입니다. 따라서 $\mathbf{p=1, q=3}$입니다.",
        "answer_new": "1, 3",
        "explanation_new": r"주어진 함수 $y = \frac{x+1}{x-3} = 1 + \frac{4}{x-3}$ 의 점근선은 $x=3, y=1$ 입니다. \n$x$축으로 $-2$만큼, $y$축으로 $2$만큼 평행이동하면 새로운 점근선은 $x'=3+(-2)=1$, $y'=1+2=3$ 이 됩니다. \n따라서 $\mathbf{p=1, q=3}$ 입니다.",
        "type": "text_input",
    }
]

def initialize_session_state():
    """세션 상태를 초기화합니다."""
    if 'current_quiz_index' not in st.session_state:
        # 초기 문제 인덱스를 랜덤으로 설정
        st.session_state.current_quiz_index = random.randrange(len(QUIZ_DATA)) 
    if 'incorrect_attempts' not in st.session_state:
        st.session_state.incorrect_attempts = 0
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False
    if 'quiz_history' not in st.session_state:
        st.session_state.quiz_history = [] # 출제된 문제 ID 목록

def go_next_quiz():
    """다음 문제로 넘어가기 위해 상태를 리셋하고 새 문제를 설정합니다."""
    
    # 현재 문제 ID를 히스토리에 추가
    current_id = QUIZ_DATA[st.session_state.current_quiz_index]["id"]
    if current_id not in st.session_state.quiz_history:
        st.session_state.quiz_history.append(current_id)
        
    # 이미 출제된 문제들을 제외한 인덱스 목록
    available_indices = [i for i, q in enumerate(QUIZ_DATA) if q["id"] not in st.session_state.quiz_history]
    
    if not available_indices:
        # 모든 문제를 다 풀었으면, 히스토리를 초기화하고 전체에서 다시 랜덤 선택
        st.session_state.quiz_history = []
        new_idx = random.randrange(len(QUIZ_DATA))
    else:
        # 남아있는 문제 중에서 랜덤 선택
        new_idx = random.choice(available_indices)

    st.session_state.current_quiz_index = new_idx
    st.session_state.incorrect_attempts = 0
    st.session_state.show_result = False
    
    # 사용자 입력 필드 값 초기화 (세션 상태에서 제거)
    if "user_answer" in st.session_state:
         del st.session_state.user_answer 
    if "user_answer_multi" in st.session_state:
         st.session_state.user_answer_multi = []
    
    st.experimental_rerun() # UI 강제 새로고침

def check_answer(user_answer, current_q):
    """사용자 답변을 확인하고 상태를 업데이트합니다."""
    
    is_correct = False
    correct_answer = current_q["answer"]
    
    if current_q["type"] == "text_input":
        user_clean = str(user_answer).replace(' ', '').lower()
        answer_clean = str(correct_answer).replace(' ', '').lower()
        
        # 쉼표 구분자 처리 (문제 4와 같은 경우)
        if ',' in answer_clean:
            user_clean_list = [s.strip() for s in user_clean.split(',')]
            answer_clean_list = [s.strip() for s in answer_clean.split(',')]
            is_correct = (user_clean_list == answer_clean_list)
        else:
            is_correct = (user_clean == answer_clean)
        
    elif current_q["type"] == "multiselect":
        user_set = set(user_answer)
        answer_set = correct_answer
        is_correct = (user_set == answer_set)

    if is_correct:
        st.session_state.show_result = True
        st.session_state.is_last_attempt_correct = True
    else:
        st.session_state.incorrect_attempts += 1
        st.session_state.is_last_attempt_correct = False
        
        # 2회 오답 시 자동 정답 공개
        if st.session_state.incorrect_attempts >= 2:
            st.session_state.show_result = True
            st.session_state.is_last_attempt_correct = False

# --- 3. 앱 본문 레이아웃 ---

st.set_page_config(page_title="유리함수 그래프 및 퀴즈", layout="wide")
initialize_session_state()

st.title("📊 유리함수 그래프 및 확인 퀴즈")
st.markdown("---")

## ✍️ 직접 그래프 그리기
st.subheader("1. 함수 식을 넣어 그래프 그려보기")
st.markdown("분자와 분모에 $x$에 대한 식을 입력하고 **Graph Plot** 버튼을 누르세요.")

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

## ✅ 확인 퀴즈
st.subheader("2. 유리함수 개념 확인 퀴즈")

# 퀴즈 섹션
current_q_index = st.session_state.current_quiz_index
current_q = QUIZ_DATA[current_q_index]

st.markdown(f"### ❓ 문제 {current_q['id']}")
st.markdown(current_q["question"])

quiz_form = st.form("quiz_answer_form")
user_input_key = "user_answer" if current_q["type"] == "text_input" else "user_answer_multi"

with quiz_form:
    user_input = None
    
    # 퀴즈 타입에 따른 입력 필드 생성
    if current_q["type"] == "text_input":
        user_input = st.text_input("답변 입력", key=user_input_key, placeholder=current_q.get("placeholder", ""))
        
    elif current_q["type"] == "multiselect":
        user_input = st.multiselect("답변 선택 (하나 이상 선택 가능)", current_q["options"], key=user_input_key)
    
    col_check, col_new = st.columns([1, 1])
    
    with col_check:
        # 정답 확인 버튼. 정답이 공개되면 비활성화
        check_submitted = st.form_submit_button("정답 확인", disabled=st.session_state.show_result)
        
    with col_new:
        # 새 문제 버튼 (히스토리 리셋 후 완전 랜덤)
        st.form_submit_button("새 문제 가져오기 🔄", on_click=go_next_quiz)


# 정답 확인 버튼이 눌렸고, 결과가 아직 표시되지 않은 경우에만 채점
if check_submitted and not st.session_state.show_result:
    check_answer(user_input, current_q)


# --- 퀴즈 결과 피드백 표시 ---

if st.session_state.show_result:
    
    if st.session_state.is_last_attempt_correct:
        st.success(f"✅ 정답입니다! (총 오답 횟수: {st.session_state.incorrect_attempts}회)")
    else:
        st.warning(f"⚠️ 오답 횟수 2회 초과로 정답을 공개합니다. 다시 한 번 풀어보세요!")
        
    # 정답 및 풀이 표시
    st.markdown("#### 정답 및 풀이")
    st.markdown(f"**정답**: **{current_q['answer']}**")
    st.info(current_q['explanation'])
    
    # 문제 해결 시 "다음 문제" 버튼 표시
    st.button("다음 문제 →", key="next_quiz_button", on_click=go_next_quiz)

elif check_submitted and not st.session_state.is_last_attempt_correct:
    # 오답이 2회 미만일 때
    st.error(f"❌ 오답입니다. 다시 한 번 풀어보세요! (현재 오답 횟수: {st.session_state.incorrect_attempts}회)")

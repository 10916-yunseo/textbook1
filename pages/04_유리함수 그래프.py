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
        st.session_state.current

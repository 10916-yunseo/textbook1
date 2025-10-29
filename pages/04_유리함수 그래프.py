import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 페이지 설정
# st.set_page_config() 내에 page_title을 "유리함수 그래프"로 설정합니다.
st.set_page_config(
    page_title="유리함수 그래프",
    layout="wide"
)

def plot_rational_function(numerator_str, denominator_str):
    """
    사용자 입력 문자열로부터 유리함수 그래프를 그립니다.
    """
    try:
        # x 값의 범위 설정
        x = np.linspace(-10, 10, 400)
        
        # 문자열을 파이썬 코드로 변환하여 함수 정의
        # 람다 함수 내에서 'x'를 사용하여 계산
        
        # 분자 함수 (P(x))
        P = lambda x_val: eval(numerator_str, {"x": x_val, "np": np})
        # 분모 함수 (Q(x))
        Q = lambda x_val: eval(denominator_str, {"x": x_val, "np": np})
        
        # 함수 값 계산
        y = P(x) / Q(x)
        
        # 수직 점근선 찾기 (분모가 0이 되는 x 값)
        asymptotes_x = []
        x_check = np.linspace(-10, 10, 2000)
        Q_check = Q(x_check)
        
        # 분모가 0에 가까운 지점을 점근선으로 간주
        for i in range(len(Q_check) - 1):
            if np.sign(Q_check[i]) != np.sign(Q_check[i+1]) and np.abs(Q_check[i]) < 0.1:
                asymptotes_x.append(x_check[i])
        
        # 중복 제거 및 반올림
        asymptotes_x = sorted(list(set(np.round(asymptotes_x, 2))))
        
        # 그래프 그리기
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 불연속점 처리 (점근선 근처의 큰 값들을 NaN으로 처리하여 끊어서 그림)
        y[np.abs(y) > 50] = np.nan 

        ax.plot(x, y, label=f'$y = \\frac{{{numerator_str}}}{{{denominator_str}}}$')
        
        # 수직 점근선 표시
        for x_a in asymptotes_x:
            ax.axvline(x=x_a, color='r', linestyle='--', label=f'점근선 x={x_a}' if x_a == asymptotes_x[0] else None)
        
        # 수평 점근선 (간단한 경우만 처리)
        try:
            num_parts = numerator_str.replace(' ', '').split('x')
            den_parts = denominator_str.replace(' ', '').split('x')
            
            # y = (ax+b) / (cx+d) 형태일 때 y = a/c
            if len(num_parts) > 1 and len(den_parts) > 1:
                num_coeff = 1 if num_parts[0] == '' else float(num_parts[0])
                den_coeff = 1 if den_parts[0] == '' else float(den_parts[0])
                
                if den_coeff != 0:
                     horizontal_asymptote = num_coeff / den_coeff
                     ax.axhline(y=horizontal_asymptote, color='b', linestyle=':', label=f'점근선 y={horizontal_asymptote}')

            # 분모의 차수가 분자보다 클 경우 y = 0
            elif len(num_parts) == 1 and len(den_parts) > 1:
                ax.axhline(y=0, color='b', linestyle=':', label=f'점근선 y=0')

        except Exception:
            pass


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
        st.error(f"함수 식을 계산하는 중 오류가 발생했습니다. 올바른 형식인지 확인해 주세요. (예: `2*x+1`, `x-3`)")
        st.error(f"오류 내용: {e}")


# --- 앱 본문 시작 ---

# 앱 본문의 제목을 "유리함수 그래프"로 설정합니다.
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
    
    * **다항함수**: 분모가 상수인 경우 (예: $y = 2x+1$)
    * **분수함수**: 분모에 $x$가 포함된 경우 (예: $y = \\frac{1}{x-2}$)
    
    분수함수를 흔히 유리함수라고 부릅니다.
    """)

with col2:
    st.subheader("2. 정의역")
    st.markdown("""
    유리함수의 정의역은 특별한 언급이 없으면 **분모를 0으로 만들지 않는**
    실수 전체의 집합입니다.
    
    > **예시**: $y = \\frac{1}{x-3}$
    > 분모 $x-3 = 0$이 되는 $x=3$을 제외한
    > 모든 실수 집합 $\{x \mid x \\neq 3, x는 실수\}$가 정의역이 됩니다.
    
    이 제외된 지점에서 **수직 점근선**이 발생합니다.
    """)

st.markdown("---")

## 📉 그래프 개형
st.subheader("3. 유리함수의 기본형과 개형")
st.markdown("가장 기본적인 형태인 $y = \\frac{k}{x}$의 그래프를 통해 개형을 알아봅시다.")

st.markdown("""
* **점근선**: $x$축($y=0$)과 $y$축($x=0$)
* **대칭**: 원점 $(0, 0)$에 대하여 대칭입니다.
* **$|k|$ 값**: $|k|$가 커질수록 그래프는 원점으로부터 멀어집니다.

| $k$의 부호 | 그래프 위치 (사분면) |
| :---: | :---: |
| $k > 0$ | 제 1사분면과 제 3사분면 |
| $k < 0$ | 제 2사분면과 제 4사분면 |
""")

st.markdown("""
### 표준형 $y = \\frac{k}{x-p} + q$의 특징
$y = \\frac{k}{x}$의 그래프를 $x$축 방향으로 $p$만큼, $y$축 방향으로 $q$만큼 평행이동한 것입니다.
* **점근선**: $x = p$, $y = q$
* **대칭의 중심**: 점 $(p, q)$에 대하여 대칭입니다.
""")

st.markdown("---")

## ✍️ 직접 그래프 그리기
st.subheader("4. 함수 식을 넣어 그래프 그려보기")
st.markdown("분자와 분모에 $x$에 대한 식을 입력하고 **Graph Plot** 버튼을 누르세요. \n(예: 분자 `3`, 분모 `x-2` 또는 분자 `2*x+1`, 분모 `x-3`)")

with st.form("rational_function_form"):
    numerator_input = st.text_input("분자 (Numerator, P(x))", value="3")
    denominator_input = st.text_input("분모 (Denominator, Q(x))", value="x-2")
    
    # 예시 버튼
    st.markdown("**✨ 추천 예시 식**")
    st.code("y = 3 / (x - 2) + 1  ➡️ 분자: '3', 분모: 'x-2'")
    st.code("y = (2x - 5) / (x - 3) ➡️ 분자: '2*x-5', 분모: 'x-3'")
    st.code("y = x / (x**2 + 1)   ➡️ 분자: 'x', 분모: 'x**2 + 1'")
    
    submitted = st.form_submit_button("Graph Plot")

if submitted:
    # 폼 제출 시 그래프 그리기 함수 호출
    plot_rational_function(numerator_input, denominator_input)

# --- 외부 자료 첨부 ---

st.markdown("---")

st.markdown("점근선과 그래프 개형을 이해하는 데 도움이 될 만한 동영상 자료를 첨부합니다.")

st.markdown("[유리함수의 그래프 개형 쉽고 빠르게 그리기](https://www.youtube.com/watch?v=6ViHq7BSxtU)")

st.markdown("이 영상은 유리함수의 그래프를 쉽고 빠르게 그리는 방법을 보여주어 교과서 내용 보충에 도움이 될 수 있습니다.")

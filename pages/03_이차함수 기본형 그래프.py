import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# 페이지 제목 설정
st.title('이차함수 그래프 기본형($y=ax^2$) 분석하기 📈')

st.header('1. 계수 $a$ 값 설정')
# a 값 입력을 위한 슬라이더 (사용자가 직접 값을 변경하며 그래프 변화 관찰)
a = st.slider(
    '**$a$ 값 선택:**', 
    min_value=-5.0, 
    max_value=5.0, 
    value=1.0, 
    step=0.1,
    help="a의 값을 변경하면서 그래프의 모양 변화를 관찰해 보세요."
)

st.subheader(f'선택된 이차함수: $y = {a}x^2$')
st.markdown("---")

st.header('2. 그래프 시각화')

# x 범위 설정 및 y 값 계산
x = np.linspace(-5, 5, 400) # -5부터 5까지 400개의 x값 생성
y = a * x**2

# Matplotlib을 이용한 그래프 그리기
fig, ax = plt.subplots()

# 그래프 그리기
ax.plot(x, y, label=f'$y = {a}x^2$', color='blue')

# 축 및 제목 설정
ax.axhline(0, color='gray', linestyle='--', linewidth=0.5) # x축
ax.axvline(0, color='gray', linestyle='--', linewidth=0.5) # y축
ax.set_xlim(-5, 5)
ax.set_ylim(-15, 15)
ax.set_xlabel('$x$')
ax.set_ylabel('$y$')
ax.set_title('이차함수 $y=ax^2$ 그래프')
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend()
ax.set_aspect('equal', adjustable='box') # x, y 축 스케일 동일하게 설정

# Streamlit에 Matplotlib 그래프 표시
st.pyplot(fig)

st.markdown("---")

## 💡 학습 목표 및 귀납적 추론 유도
st.header('3. 학습 내용 확인 및 추론 유도')

if a > 0:
    st.info(f"**$a = {a}$ (양수)**: 그래프는 **아래로 볼록**합니다. 😃")
elif a < 0:
    st.info(f"**$a = {a}$ (음수)**: 그래프는 **위로 볼록**합니다. 😟")
else:
    st.warning("**$a = 0$**: 이 경우 $y=0$으로, $x$축과 일치하는 직선입니다.")

st.markdown(f"**$|a|$ 값**: **$|{a}| = {abs(a)}$**")

if abs(a) > 1:
    st.success(f"**$|a|$의 절댓값이 1보다 크면** (예: $|{a}|={abs(a)}$), 그래프의 폭이 $y=x^2$보다 **좁아집니다**.")
elif 0 < abs(a) < 1:
    st.success(f"**$|a|$의 절댓값이 1보다 작으면** (예: $|{a}|={abs(a)}$), 그래프의 폭이 $y=x^2$보다 **넓어집니다**.")
elif abs(a) == 1:
    st.success(f"**$|a|$의 절댓값이 1이면** (예: $|{a}|={abs(a)}$), 기본형 $y=x^2$과 폭이 같습니다.")

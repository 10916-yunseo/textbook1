import streamlit as st
import random

def generate_lotto_numbers():
    """1부터 45 중 중복 없이 6개의 로또 번호를 생성하고 정렬합니다."""
    # random.sample(범위, 개수)를 사용하여 중복 없는 6개의 숫자를 추출
    numbers = random.sample(range(1, 46), 6)
    # 번호를 오름차순으로 정렬
    numbers.sort()
    return numbers

## 메인 애플리케이션 ##

st.title("💰 스트림릿 로또 번호 생성기")
st.markdown("1부터 45 중 6개의 숫자를 무작위로 추천해 드립니다.")

# 1. 게임 수 입력 받기 (슬라이더 사용)
# min_value=1, max_value=10, value=1 (기본값)
game_count = st.slider(
    "몇 게임을 생성하시겠습니까? (1~10)",
    min_value=1,
    max_value=10,
    value=1
)

st.write(f"선택된 게임 수: **{game_count}**")

# 2. 생성 버튼
if st.button("✨ 로또 번호 생성"):
    st.subheader("🎉 이번 주 로또 추천 번호!")
    
    # 3. 입력된 게임 수만큼 번호 생성 및 출력
    for i in range(game_count):
        # 로또 번호 생성 함수 호출
        lotto_set = generate_lotto_numbers()
        
        # 번호를 쉼표로 구분된 문자열로 변환하여 출력
        # f-string과 markdown을 사용해 결과를 보기 좋게 표시
        st.markdown(f"**게임 {i+1}:** `{' '.join(map(str, lotto_set))}`")
    
    st.balloons() # 번호 생성 시 축하 풍선 효과

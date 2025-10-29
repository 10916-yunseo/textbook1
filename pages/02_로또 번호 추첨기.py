import streamlit as st
import random
from collections import Counter

# 1. 앱 기본 설정
st.set_page_config(
    page_title="🍀 로또 번호 추천기",
    layout="centered"
)

st.title("🍀 로또 번호 추천기 (1-45, 6개)")
st.caption("원하는 세트 수만큼 로또 번호를 추천받고 최근 당첨 번호와 비교해 보세요!")

# 2. 최근 1등 당첨 번호 (검색 결과 기준, 1195회)
# 검색 결과: 1195회 로또 당첨번호 '3, 15, 27, 33, 34, 36'
RECENT_WINNING_NUMBERS = {3, 15, 27, 33, 34, 36}

# 3. 로또 번호 생성 함수
def generate_lotto_numbers():
    """1부터 45 사이의 겹치지 않는 6개의 숫자를 오름차순으로 생성"""
    # random.sample: 주어진 범위(range(1, 46))에서 지정된 개수(6)만큼 중복 없이 무작위로 추출
    numbers = random.sample(range(1, 46), 6)
    numbers.sort()
    return numbers

# 4. 번호 비교 함수
def compare_with_winning(generated_numbers, winning_numbers):
    """생성된 번호와 당첨 번호를 비교하여 일치하는 개수를 반환"""
    # 두 집합(set)의 교집합(intersection)을 구하고 그 크기(len)를 계산
    match_count = len(set(generated_numbers) & winning_numbers)
    return match_count

# 5. 사용자 입력 (몇 세트 생성할지)
st.subheader("몇 세트를 생성하시겠어요?")
# min_value=1, max_value=20 으로 설정하여 1~20 사이의 숫자를 직접 입력하도록 변경
num_sets = st.number_input(
    "로또 번호 세트 수 (1 ~ 20):",
    min_value=1,
    max_value=20,
    value=5, # 기본값 5로 설정
    step=1,
    help="1세트부터 최대 20세트까지 숫자를 직접 입력할 수 있습니다."
)

# 6. 생성 버튼
if st.button("✨ 번호 생성하기", type="primary"):
    # 입력된 세트 수가 유효한지 다시 한번 확인
    if 1 <= num_sets <= 20:
        st.divider()
        st.subheader(f"🔮 로또 번호 추천 결과 ({num_sets} 세트)")
        
        results = []
        
        # 입력된 세트 수만큼 번호 생성 및 비교
        for i in range(1, num_sets + 1):
            lotto_set = generate_lotto_numbers()
            match_count = compare_with_winning(lotto_set, RECENT_WINNING_NUMBERS)
            
            # 결과를 저장 (비교를 위해 set 형태로도 저장)
            results.append({
                "set_num": i,
                "numbers": lotto_set,
                "match_count": match_count
            })
            
            # 결과 출력 포맷 설정
            numbers_str = ", ".join(map(str, lotto_set))
            comparison_emoji = "🎉" if match_count >= 3 else ("😊" if match_count > 0 else "🧐")
            
            # 번호와 일치 개수 출력
            st.markdown(
                f"**✅ 세트 {i}:** **`{numbers_str}`**"
            )
            st.info(f"{comparison_emoji} 최근 당첨 번호와 **{match_count}개** 일치합니다.")

        st.divider()

        # 7. 최근 당첨 번호 정보 표시 및 비교 요약
        st.subheader("📊 최근 당첨 번호 비교 정보")

        # 최근 당첨 번호 표시
        winning_str = ", ".join(map(str, sorted(list(RECENT_WINNING_NUMBERS))))
        st.markdown(
            f"**🏆 최근 1등 당첨 번호 (1195회 기준):** **`{winning_str}`**"
        )

        # 일치 개수 요약
        all_match_counts = [res['match_count'] for res in results]
        count_summary = Counter(all_match_counts)

        st.markdown("### 일치 개수 요약")
        
        # 생성된 모든 세트의 최대 일치 개수 찾기
        max_match = max(all_match_counts)
        
        if max_match == 6:
            st.balloons()
            st.success("🎉 **축하합니다! 6개 모두 일치하는 조합이 나왔습니다!** 🥳")
        elif max_match >= 3:
            st.success(f"✨ **최대 {max_match}개** 일치하는 조합이 나왔습니다!")
        else:
            st.warning("다음 기회를 노려보세요!")

        # 일치 개수별 세트 수 표시
        summary_table = {
            "일치 개수": [i for i in range(7)],
            "세트 수": [count_summary.get(i, 0) for i in range(7)]
        }
        
        st.table(summary_table)

        st.caption("참고: 실제 로또 1등은 6개 숫자 모두 일치해야 합니다.")
    else:
        st.error("세트 수는 1부터 20 사이의 숫자로 입력해야 합니다.")

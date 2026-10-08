import streamlit as st
from datetime import datetime, timedelta
import calendar
import json
import os

# 페이지 설정
st.set_page_config(page_title="공부계획서", layout="centered")

# 스타일 추가
st.markdown("""
<style>
    .calendar-day-btn {
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        transition: all 0.2s;
    }
    .checklist-container {
        padding: 20px;
        background-color: #f5f5f5;
        border-radius: 10px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ===== JSON 데이터 관리 =====
DATA_FILE = "study_data.json"

def load_data():
    """JSON 파일에서 데이터 로드"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}, "data": {}}

def save_data(data):
    """데이터를 JSON 파일에 저장"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def user_exists(username):
    """사용자 존재 확인"""
    data = load_data()
    return username in data["users"]

def verify_password(username, password):
    """비밀번호 확인"""
    data = load_data()
    if username in data["users"]:
        return data["users"][username] == password
    return False

def create_user(username, password):
    """새 사용자 생성"""
    data = load_data()
    if username not in data["users"]:
        data["users"][username] = password
        data["data"][username] = {}
        save_data(data)
        return True
    return False

def get_user_checklists(username):
    """사용자의 모든 체크리스트 조회"""
    data = load_data()
    return data.get("data", {}).get(username, {})

def save_user_checklists(username, checklists):
    """사용자의 체크리스트 저장"""
    data = load_data()
    if "data" not in data:
        data["data"] = {}
    data["data"][username] = checklists
    save_data(data)

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = None
if 'current_month' not in st.session_state:
    st.session_state.current_month = datetime.now().date().replace(day=1)
if 'new_item_input' not in st.session_state:
    st.session_state.new_item_input = ""
if 'show_date_picker' not in st.session_state:
    st.session_state.show_date_picker = False

# ===== 로그인되지 않은 상태 =====
if not st.session_state.logged_in:
    st.markdown("# 📚 공부계획서")
    st.markdown("---")

    tab1, tab2 = st.tabs(["로그인", "회원가입"])

    with tab1:
        st.markdown("## 로그인")

        login_username = st.text_input("닉네임", key="login_username")
        login_password = st.text_input("비밀번호", type="password", key="login_password")

        if st.button("로그인", use_container_width=True):
            if not login_username or not login_password:
                st.error("닉네임과 비밀번호를 입력하세요")
            elif verify_password(login_username, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success("로그인 성공! 🎉")
                st.rerun()
            else:
                st.error("닉네임 또는 비밀번호가 잘못되었습니다")

    with tab2:
        st.markdown("## 회원가입")

        signup_username = st.text_input("닉네임", key="signup_username")
        signup_password = st.text_input("비밀번호", type="password", key="signup_password")
        signup_password_confirm = st.text_input("비밀번호 확인", type="password", key="signup_password_confirm")

        if st.button("회원가입", use_container_width=True):
            if not signup_username or not signup_password:
                st.error("닉네임과 비밀번호를 입력하세요")
            elif signup_password != signup_password_confirm:
                st.error("비밀번호가 일치하지 않습니다")
            elif user_exists(signup_username):
                st.error("이미 존재하는 닉네임입니다")
            elif len(signup_password) < 4:
                st.error("비밀번호는 4자 이상이어야 합니다")
            else:
                if create_user(signup_username, signup_password):
                    st.session_state.logged_in = True
                    st.session_state.username = signup_username
                    st.success("회원가입 성공! 로그인되었습니다 🎉")
                    st.rerun()
                else:
                    st.error("회원가입에 실패했습니다")

# ===== 로그인된 상태 =====
else:
    # 로그아웃 버튼 (우상단)
    col_empty, col_logout = st.columns([8, 2])
    with col_logout:
        if st.button("로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.selected_date = None
            st.rerun()

    st.markdown(f"# 📚 {st.session_state.username}의 공부계획서")
    st.markdown("---")

    # 사용자 데이터 로드
    user_checklists = get_user_checklists(st.session_state.username)

    # 날짜를 선택했는지 확인
    if st.session_state.selected_date is None:
        # 달력만 표시
        today = datetime.now().date()
        st.markdown(f"## 📅 오늘: {today} | 날짜를 선택하세요")

        # 오늘 날짜 버튼 스타일 (한 번만 추가)
        st.markdown("""
        <style>
            .red-border-today {
                border: 3px solid red !important;
                box-shadow: 0 0 0 3px red !important;
            }
        </style>
        """, unsafe_allow_html=True)

        # 월 네비게이션
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            if st.button("◀ 이전"):
                st.session_state.current_month = st.session_state.current_month.replace(day=1) - timedelta(days=1)
                st.session_state.current_month = st.session_state.current_month.replace(day=1)
                st.rerun()
        with nav_col2:
            if st.button(f"{st.session_state.current_month.year}년 {st.session_state.current_month.month}월 🔽", use_container_width=True):
                st.session_state.show_date_picker = not st.session_state.show_date_picker
                st.rerun()
        with nav_col3:
            if st.button("다음 ▶"):
                st.session_state.current_month = st.session_state.current_month.replace(day=28) + timedelta(days=4)
                st.session_state.current_month = st.session_state.current_month.replace(day=1)
                st.rerun()

        # 년/월 선택기
        if st.session_state.show_date_picker:
            st.markdown("---")
            picker_col1, picker_col2 = st.columns(2)
            with picker_col1:
                year = st.number_input("년도", min_value=2000, max_value=2100, value=st.session_state.current_month.year)
            with picker_col2:
                month = st.selectbox("월", list(range(1, 13)), index=st.session_state.current_month.month - 1)

            pick_col1, pick_col2 = st.columns(2)
            with pick_col1:
                if st.button("확인", use_container_width=True):
                    st.session_state.current_month = datetime(year, month, 1).date()
                    st.session_state.show_date_picker = False
                    st.rerun()
            with pick_col2:
                if st.button("취소", use_container_width=True):
                    st.session_state.show_date_picker = False
                    st.rerun()
            st.markdown("---")

        # 달력 표시
        year = st.session_state.current_month.year
        month = st.session_state.current_month.month

        # 요일 헤더
        day_names = ["월", "화", "수", "목", "금", "토", "일"]
        cols = st.columns(7)
        for i, day_name in enumerate(day_names):
            with cols[i]:
                st.markdown(f"<div style='text-align: center; font-weight: bold;'>{day_name}</div>", unsafe_allow_html=True)

        # 날짜 버튼
        cal = calendar.monthcalendar(year, month)
        today = datetime.now().date()

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.write("")
                    else:
                        date = datetime(year, month, day).date()
                        date_str = str(date)
                        checklist = user_checklists.get(date_str, [])

                        # 모든 할일이 완료되었는지 확인
                        is_all_completed = len(checklist) > 0 and all(item["completed"] for item in checklist)

                        # 날짜 표시 (완료되면 폭죽 이모지)
                        if is_all_completed:
                            button_text = f"🎉 {day}"
                        else:
                            button_text = str(day)

                        if st.button(
                            button_text,
                            key=f"day_{day}_{month}_{year}",
                            use_container_width=True,
                        ):
                            st.session_state.selected_date = date
                            st.rerun()

        # 오늘 날짜 숫자를 빨간색으로 표시
        st.markdown(f"""
        <script>
        setTimeout(() => {{
            const buttons = document.querySelectorAll('button');
            buttons.forEach(btn => {{
                const text = btn.textContent.trim();
                if (text == '{today.day}' || text.includes('{today.day}')) {{
                    btn.style.color = 'red';
                    btn.style.fontWeight = 'bold';
                }}
            }});
        }}, 50);
        </script>
        """, unsafe_allow_html=True)

    else:
        # 선택된 날짜의 체크리스트 표시
        selected_date_str = str(st.session_state.selected_date)

        # 상단: 선택된 날짜와 뒤로가기 버튼
        col_back, col_title = st.columns([1, 4])
        with col_back:
            if st.button("◀ 뒤로", use_container_width=True):
                st.session_state.selected_date = None
                st.rerun()
        with col_title:
            st.markdown(f"## 📝 {st.session_state.selected_date}의 할일")

        st.markdown("---")

        # 새 할일 추가 함수
        def add_new_item():
            if st.session_state.new_item_input.strip():
                if selected_date_str not in user_checklists:
                    user_checklists[selected_date_str] = []

                user_checklists[selected_date_str].append({
                    "text": st.session_state.new_item_input,
                    "completed": False
                })
                save_user_checklists(st.session_state.username, user_checklists)
                st.session_state.new_item_input = ""

        # 새 할일 추가
        col_input, col_add = st.columns([4, 1])
        with col_input:
            st.text_input("할 일 추가", key="new_item_input", placeholder="예: 수학 문제 10개 풀기", label_visibility="collapsed", on_change=add_new_item)
        with col_add:
            if st.button("추가", use_container_width=True):
                add_new_item()

        st.markdown("---")

        # 체크리스트 표시
        checklist = user_checklists.get(selected_date_str, [])

        if checklist:
            st.markdown("### ✓ 체크리스트")

            # 테이블 헤더
            header_col1, header_col2, header_col3 = st.columns([4, 1, 1])
            with header_col1:
                st.markdown("**할일**")
            with header_col2:
                st.markdown("**완료**")
            with header_col3:
                st.markdown("**삭제**")
            st.markdown("---")

            for idx, item in enumerate(checklist):
                col_text, col_checkbox, col_delete = st.columns([4, 1, 1])

                with col_text:
                    # 할 일 텍스트
                    text_style = "text-decoration: line-through; opacity: 0.6; vertical-align: middle;" if item["completed"] else "vertical-align: middle;"
                    st.markdown(f"<span style='{text_style}'>{item['text']}</span>", unsafe_allow_html=True)

                with col_checkbox:
                    # 체크박스
                    completed = st.checkbox(
                        label="",
                        value=item["completed"],
                        key=f"check_{idx}_{selected_date_str}",
                    )

                    # 체크 상태 업데이트
                    if completed != item["completed"]:
                        user_checklists[selected_date_str][idx]["completed"] = completed
                        save_user_checklists(st.session_state.username, user_checklists)
                        st.rerun()

                with col_delete:
                    if st.button("❌", key=f"delete_{idx}_{selected_date_str}", use_container_width=True):
                        user_checklists[selected_date_str].pop(idx)
                        # 할일이 모두 삭제되면 날짜도 제거
                        if len(user_checklists[selected_date_str]) == 0:
                            del user_checklists[selected_date_str]
                        save_user_checklists(st.session_state.username, user_checklists)
                        st.rerun()

            # 진행률 표시
            st.markdown("---")
            total = len(checklist)
            completed = sum(1 for item in checklist if item["completed"])
            progress = completed / total if total > 0 else 0

            st.progress(progress)
            st.caption(f"완료율: {completed}/{total} ({int(progress*100)}%)")
        else:
            st.info("할 일을 추가하세요!")

    # 사이드바: 통계
    with st.sidebar:
        st.header("📊 통계")

        # 등록된 날짜 통계
        total_dates = len(user_checklists)
        st.metric("등록된 날짜", total_dates)

        # 최근 할일 목록
        if user_checklists:
            st.markdown("---")
            st.subheader("📋 최근 활동")

            recent_dates = sorted(user_checklists.keys(), reverse=True)[:5]
            for date in recent_dates:
                checklist = user_checklists[date]
                with st.expander(f"📅 {date}"):
                    completed = sum(1 for item in checklist if item["completed"])
                    st.write(f"**할일:** {completed}/{len(checklist)} 완료")

                    # 항목 미리보기
                    for item in checklist[:3]:
                        status = "✅" if item["completed"] else "⭕"
                        st.caption(f"{status} {item['text'][:30]}")

                    if len(checklist) > 3:
                        st.caption(f"외 {len(checklist) - 3}개 더...")

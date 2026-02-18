# 🎯 Cursor에서 디지털 트윈 서베이 시스템 사용하기

## 📦 1. 프로젝트 설정

### 1.1. Cursor에서 프로젝트 열기

```bash
# 터미널에서 프로젝트 폴더로 이동
cd /path/to/digital-twin-survey

# Cursor로 열기
cursor .
```

### 1.2. Python 가상환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## 🔑 2. API 키 설정

### 방법 1: .env 파일 사용 (권장)

프로젝트 루트에 `.env` 파일을 생성:

```bash
# .env 파일 생성
touch .env
```

`.env` 파일 내용:
```
ANTHROPIC_API_KEY=your_api_key_here
```

### 방법 2: 환경변수 직접 설정

```bash
# macOS/Linux
export ANTHROPIC_API_KEY='your_api_key_here'

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY='your_api_key_here'

# Windows (CMD)
set ANTHROPIC_API_KEY=your_api_key_here
```

## 🚀 3. 실행하기

### 3.1. Streamlit GUI 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열리고 `http://localhost:8501`에서 앱이 실행됩니다.

### 3.2. Cursor의 통합 터미널에서 실행

1. Cursor에서 `Ctrl/Cmd + J` 눌러 터미널 열기
2. 위의 명령어 입력

## 💡 4. Cursor AI와 함께 작업하기

### 4.1. Cursor Chat 활용

`Ctrl/Cmd + K` 또는 `Ctrl/Cmd + L`로 Cursor AI와 대화:

**예시 프롬프트:**

```
"커스텀 질문 템플릿을 추가하고 싶어. QuestionTemplate 클래스에 
'customer_satisfaction' 카테고리를 추가해줘"

"서베이 결과를 시각화하는 차트를 추가해줘. Plotly를 사용해서"

"페르소나 필터링 기능을 개선해서 나이, 성별, 지역으로 
필터링할 수 있게 해줘"

"app.py에 새로운 탭을 추가해서 과거 결과를 불러올 수 있게 해줘"
```

### 4.2. 인라인 코드 수정

- 코드를 선택하고 `Ctrl/Cmd + K`
- 원하는 수정사항을 자연어로 설명

**예시:**
```python
# 이 함수를 선택하고 Ctrl/Cmd + K
def create_persona_prompt(self, persona_data: Dict[str, Any]) -> str:
    # ...
```

프롬프트: "이 함수에 에러 핸들링을 추가하고 로깅 기능을 넣어줘"

### 4.3. 코드 생성

새 파일이나 함수가 필요할 때:

1. 빈 공간에서 `Ctrl/Cmd + K`
2. 원하는 기능 설명

**예시:**
```
"시각화를 위한 visualization.py 파일을 만들어줘. 
Plotly로 서베이 결과를 차트로 보여주는 함수들을 포함해야 해"
```

## 🛠️ 5. 커스터마이징 가이드

### 5.1. 새로운 질문 카테고리 추가

`digital_twin_survey_system.py`의 `QuestionTemplate` 클래스 수정:

```python
SURVEY_QUESTIONS = {
    # 기존 카테고리...
    
    "your_new_category": [
        "새로운 질문 1",
        "새로운 질문 2",
        "새로운 질문 3",
    ],
}
```

### 5.2. GUI 테마 변경

`app.py`의 CSS 부분 수정:

```python
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
    }
    .stButton>button {
        background-color: #YOUR_COLOR;
    }
</style>
""", unsafe_allow_html=True)
```

### 5.3. 결과 내보내기 형식 추가

`app.py`의 "결과 분석" 탭에서 다운로드 버튼 추가:

```python
# Excel 다운로드 예시
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    survey_df.to_excel(writer, index=False, sheet_name='Results')

st.download_button(
    label="📥 Excel 다운로드",
    data=excel_buffer.getvalue(),
    file_name=f"results_{datetime.now().strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.ms-excel"
)
```

## 📁 6. 프로젝트 구조

```
digital-twin-survey/
├── app.py                          # Streamlit GUI 메인 앱
├── digital_twin_survey_system.py   # 백엔드 로직
├── requirements.txt                # 의존성
├── .env                           # API 키 (Git에 커밋하지 마세요!)
├── .cursorrules                   # Cursor AI 설정
├── README.md                      # 전체 프로젝트 문서
├── README_CURSOR.md              # 이 파일
└── .gitignore                    # Git 제외 파일
```

## 🔥 7. 자주 사용하는 Cursor 단축키

| 단축키 | 기능 |
|--------|------|
| `Ctrl/Cmd + K` | 인라인 AI 편집 |
| `Ctrl/Cmd + L` | AI 채팅 열기 |
| `Ctrl/Cmd + I` | 터미널에서 AI 명령 |
| `Ctrl + Shift + P` | 명령 팔레트 |
| `Ctrl/Cmd + J` | 터미널 토글 |
| `Ctrl/Cmd + B` | 사이드바 토글 |

## 🐛 8. 문제 해결

### 8.1. 모듈을 찾을 수 없음

```bash
# 가상환경이 활성화되어 있는지 확인
which python  # macOS/Linux
where python  # Windows

# 의존성 재설치
pip install -r requirements.txt --force-reinstall
```

### 8.2. Streamlit 실행 오류

```bash
# Streamlit 캐시 삭제
streamlit cache clear

# 포트가 이미 사용 중인 경우
streamlit run app.py --server.port 8502
```

### 8.3. API 키 오류

```bash
# .env 파일 확인
cat .env

# 환경변수 확인
echo $ANTHROPIC_API_KEY  # macOS/Linux
echo %ANTHROPIC_API_KEY%  # Windows
```

## 🎨 9. 추천 확장 기능 (Cursor/VS Code)

Cursor에서 다음 확장 기능 설치:

1. **Python** (Microsoft)
2. **Pylance** (Microsoft)
3. **Jupyter** (Microsoft)
4. **Python Docstring Generator**
5. **Better Comments**

## 💪 10. 고급 활용법

### 10.1. 실시간 코드 리뷰

코드 블록을 선택하고 Cursor AI에게:
```
"이 코드를 리뷰해주고 개선점을 제안해줘"
```

### 10.2. 테스트 코드 생성

함수를 선택하고:
```
"이 함수에 대한 pytest 테스트 케이스를 작성해줘"
```

### 10.3. 문서화 자동 생성

함수나 클래스를 선택하고:
```
"이 코드에 대한 docstring을 추가해줘. Google 스타일로"
```

## 🔄 11. Git 연동

### 11.1. .gitignore 설정

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
env/

# 환경 변수
.env

# Streamlit
.streamlit/

# 결과 파일
*.json
*.csv
*.xlsx

# IDE
.vscode/
.idea/
```

### 11.2. Git 커밋

```bash
git add .
git commit -m "feat: 디지털 트윈 서베이 시스템 초기 구현"
git push
```

## 📚 12. 학습 자료

- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [Anthropic API 문서](https://docs.anthropic.com/)
- [Twin-2K-500 데이터셋](https://huggingface.co/datasets/LLM-Digital-Twin/Twin-2K-500)
- [Cursor 공식 문서](https://cursor.sh/docs)

## 💬 13. Cursor AI에게 물어볼 만한 것들

1. **버그 수정**: "이 에러가 왜 발생하는지 설명하고 수정해줘"
2. **기능 추가**: "결과를 PDF로 내보내는 기능을 추가해줘"
3. **성능 최적화**: "이 함수의 성능을 개선할 방법을 제안해줘"
4. **코드 리팩토링**: "이 코드를 더 깔끔하게 정리해줘"
5. **설명**: "이 코드가 어떻게 동작하는지 단계별로 설명해줘"

## 🎯 14. 다음 단계

1. ✅ 기본 기능 테스트
2. 📊 결과 시각화 추가
3. 🎨 UI/UX 개선
4. 🔒 에러 핸들링 강화
5. 📈 대시보드 기능 추가
6. 🌐 배포 (Streamlit Cloud)

---

**Happy Coding with Cursor! 🚀**

궁금한 점이 있으면 Cursor AI에게 물어보세요!

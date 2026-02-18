# ⚡ 퀵스타트 가이드

5분 안에 시작하세요!

## 🎯 1단계: Cursor에서 열기 (30초)

```bash
# 터미널에서 프로젝트 폴더로 이동
cd /path/to/your/project

# Cursor로 열기
cursor .
```

또는 Cursor에서 `File > Open Folder`로 프로젝트 폴더 선택

## 🔑 2단계: API 키 설정 (1분)

### 방법 1: 간단한 방법

1. `.env.example` 파일을 `.env`로 복사
2. `.env` 파일 열기
3. `your_anthropic_api_key_here`를 실제 API 키로 교체

```bash
# macOS/Linux
cp .env.example .env
nano .env  # 또는 code .env

# Windows (PowerShell)
Copy-Item .env.example .env
notepad .env  # 또는 code .env
```

### API 키 받기
- [Anthropic Console](https://console.anthropic.com/)에서 가입
- API Keys 메뉴에서 새 키 생성
- 키 복사

## 🚀 3단계: 실행 (1분)

### macOS/Linux
```bash
./run.sh
```

### Windows
```cmd
run.bat
```

또는 **Cursor 통합 터미널**에서 (`Ctrl/Cmd + J`):
```bash
streamlit run app.py
```

## ✅ 4단계: 사용하기 (2분)

1. 브라우저가 자동으로 열림 (`http://localhost:8501`)
2. 왼쪽 사이드바에서 "🚀 시스템 초기화" 버튼 클릭
3. "👥 페르소나 선택" 탭에서 샘플링
4. "📋 서베이" 탭에서 서베이 실행
5. "📊 결과 분석" 탭에서 결과 확인 및 다운로드

## 🎨 Cursor에서 커스터마이징하기

### 1. 질문 추가하기

`Ctrl/Cmd + P` → `digital_twin_survey_system.py` 입력

`Ctrl/Cmd + F` → `SURVEY_QUESTIONS` 검색

`Ctrl/Cmd + K`로 Cursor AI에게:
```
"여기에 'tech_adoption' 카테고리를 추가해줘. 
기술 수용도에 대한 5개 질문을 포함해야 해"
```

### 2. UI 색상 변경

`app.py` 열기 → CSS 부분 찾기

`Ctrl/Cmd + K`로 Cursor AI에게:
```
"이 CSS를 파란색 계열에서 초록색 계열로 바꿔줘"
```

### 3. 차트 추가

결과 분석 탭 선택 → `Ctrl/Cmd + K`:
```
"여기에 Plotly를 사용한 막대 그래프를 추가해줘. 
감성 분석 결과를 시각화해야 해"
```

## 💡 자주 사용하는 Cursor 명령

### 코드 선택 후:

| 하고 싶은 것 | 단축키 | 명령 예시 |
|------------|--------|----------|
| 수정하기 | `Ctrl/Cmd + K` | "이 함수에 에러 핸들링 추가해줘" |
| 설명듣기 | `Ctrl/Cmd + L` | "이 코드가 어떻게 동작하는지 설명해줘" |
| 개선하기 | `Ctrl/Cmd + K` | "이 코드를 더 효율적으로 만들어줘" |
| 테스트 작성 | `Ctrl/Cmd + K` | "이 함수의 테스트 코드 작성해줘" |

### 새 기능 추가:

파일 열고 빈 공간에서 `Ctrl/Cmd + K`:
```
"서베이 결과를 Excel로 내보내는 함수를 만들어줘"
```

## 🔧 문제 해결

### "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### "API Error"

`.env` 파일에 API 키가 올바르게 입력되었는지 확인:
```bash
cat .env  # macOS/Linux
type .env  # Windows
```

### 포트가 이미 사용 중

```bash
streamlit run app.py --server.port 8502
```

### Streamlit 캐시 오류

```bash
streamlit cache clear
```

## 📚 다음 단계

1. ✅ [README_CURSOR.md](README_CURSOR.md) - 상세 가이드
2. 📖 [README.md](README.md) - 전체 문서
3. 🎓 Cursor AI에게 물어보기: "이 프로젝트에서 뭘 할 수 있어?"

## 🎯 빠른 예시

### 예시 1: 커스텀 서베이 만들기

1. 서베이 탭으로 이동
2. "커스텀 질문 사용" 체크
3. 질문 입력:
   ```
   우리 제품의 가장 좋은 점은?
   개선이 필요한 부분은?
   경쟁사와 비교했을 때 어떤가요?
   ```
4. "▶️ 서베이 실행" 클릭

### 예시 2: 특정 타겟 조사

```python
# Cursor AI에게: "25-35세 여성 페르소나만 필터링하는 코드 추가해줘"
```

### 예시 3: 결과 시각화

```python
# 결과 분석 탭에서 Cursor AI에게:
"Plotly로 서베이 결과를 파이 차트로 보여주는 코드 추가해줘"
```

## 🆘 도움말

### Cursor AI에게 물어보기

프로젝트에 대해 궁금한 게 있으면 `Ctrl/Cmd + L`로 채팅 열고:

```
"이 프로젝트의 구조를 설명해줘"
"서베이 결과를 PDF로 저장하려면?"
"새로운 실험 타입을 추가하려면 어떻게 해야 해?"
"에러가 발생했어. 해결 방법 알려줘"
```

---

**🎉 준비 완료! 이제 디지털 트윈 서베이를 시작하세요!**

문제가 생기면 Cursor AI가 도와줄 거예요! 💪

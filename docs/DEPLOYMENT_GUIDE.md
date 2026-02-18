# 배포 가이드 (Deployment Guide)

## 🔒 보안 사항 체크리스트

### ✅ 완료된 보안 개선 사항

1. **API 키 보안**
   - ✅ 하드코딩된 API 키 제거
   - ✅ 환경 변수로 관리 (`OPENAI_API_KEY`)

2. **인증 정보 보안**
   - ✅ 하드코딩된 비밀번호 제거
   - ✅ 환경 변수로 관리
     - `AUTH_USER_ID`
     - `AUTH_USER_PW`
     - `AUTH_ADMIN_ID`
     - `AUTH_ADMIN_PW`

### ⚠️ 추가로 개선해야 할 사항

1. **Rate Limiting**
   - API 호출 빈도 제한 필요
   - 악의적인 공격 방지

2. **Session Security**
   - 세션 타임아웃 설정
   - CSRF 보호 강화

3. **Logging & Monitoring**
   - 에러 로깅 강화
   - 모니터링 도구 연동

4. **Data Privacy**
   - 사용자 데이터 암호화
   - 개인정보 보호 정책 명시

## 🚀 Railway 배포 절차

### 1. Railway 설정

1. Railway에 접속: https://railway.app
2. "New Project" 클릭
3. "Deploy from GitHub repo" 선택
4. `digital-twin-survey` 리포지토리 선택

### 2. 환경 변수 설정

Railway 프로젝트 설정에서 다음 환경 변수를 추가하세요:

```
OPENAI_API_KEY=your_openai_api_key_here
AUTH_USER_ID=your_user_id
AUTH_USER_PW=your_secure_password_here
AUTH_ADMIN_ID=your_admin_id
AUTH_ADMIN_PW=your_admin_password_here
```

### 3. 자동 배포

- GitHub에 푸시하면 자동으로 배포됩니다
- 배포 URL은 Railway 대시보드에서 확인할 수 있습니다

## 📝 추가 권장 사항

### 1. HTTPS 설정
- Railway는 기본적으로 HTTPS를 제공합니다
- 커스텀 도메인 사용 시 SSL 인증서 설정

### 2. Database 설정
- 장기간 로그 저장을 위해 PostgreSQL 등 DB 연동 고려

### 3. Caching
- Redis 등을 사용한 캐싱으로 성능 향상

### 4. Backup
- 정기적인 데이터 백업 설정

## 🔧 문제 해결

### 배포 실패 시

1. 로그 확인: Railway 대시보드에서 배포 로그 확인
2. 환경 변수 확인: 모든 필수 환경 변수가 설정되었는지 확인
3. 의존성 확인: `requirements.txt`에 모든 필요한 패키지가 포함되어 있는지 확인

### 오류 메시지

- "OPENAI_API_KEY 환경 변수가 설정되지 않았습니다"
  → Railway 환경 변수에 `OPENAI_API_KEY` 추가
  
- "ModuleNotFoundError"
  → `requirements.txt`에 해당 모듈 추가

## 📧 문의

문제가 발생하면 GitHub Issues를 통해 문의해 주세요.


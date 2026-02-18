"""
설문조사 시스템
디지털 트윈들에게 구조화된 설문을 진행하고 1-7 척도 응답을 수집합니다.
"""

import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box
from src.dataset_loader import Persona
from src.ai_agent import AIAgent


class SurveyQuestion:
    """설문 질문 클래스"""
    
    def __init__(
        self,
        question_id: str,
        text: str,
        scale_description: str = "1(전혀 동의하지 않음) ~ 7(매우 동의함)",
        category: Optional[str] = None
    ):
        self.question_id = question_id
        self.text = text
        self.scale_description = scale_description
        self.category = category
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "text": self.text,
            "scale_description": self.scale_description,
            "category": self.category
        }


class Survey:
    """설문조사 클래스"""
    
    def __init__(self, title: str, description: str = ""):
        self.title = title
        self.description = description
        self.questions: List[SurveyQuestion] = []
        self.created_at = datetime.now().isoformat()
    
    def add_question(
        self,
        text: str,
        question_id: Optional[str] = None,
        scale_description: str = "1(전혀 동의하지 않음) ~ 7(매우 동의함)",
        category: Optional[str] = None
    ) -> None:
        """설문 질문을 추가합니다."""
        if question_id is None:
            question_id = f"Q{len(self.questions) + 1}"
        
        question = SurveyQuestion(question_id, text, scale_description, category)
        self.questions.append(question)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at,
            "questions": [q.to_dict() for q in self.questions]
        }


class SurveySystem:
    """설문조사 시스템"""
    
    def __init__(self, ai_agent: AIAgent):
        self.ai_agent = ai_agent
        self.console = Console()
        self.survey: Optional[Survey] = None
        self.responses: List[Dict[str, Any]] = []
    
    def create_survey_wizard(self) -> Survey:
        """대화형 설문조사 생성 마법사"""
        self.console.print("\n[bold cyan]═══ 설문조사 생성 ═══[/bold cyan]\n")
        
        title = Prompt.ask("[bold]설문조사 제목[/bold]")
        description = Prompt.ask("[bold]설명[/bold] (선택사항, Enter로 건너뛰기)", default="")
        
        survey = Survey(title, description)
        
        self.console.print("\n[bold]질문 추가[/bold]")
        self.console.print("[dim]각 질문은 1-7 척도로 응답받습니다.[/dim]\n")
        
        question_num = 1
        while True:
            self.console.print(f"[cyan]질문 {question_num}[/cyan]")
            
            question_text = Prompt.ask("질문 내용 (완료하려면 Enter)", default="")
            
            if not question_text:
                if question_num == 1:
                    self.console.print("[yellow]⚠ 최소 1개의 질문이 필요합니다.[/yellow]")
                    continue
                break
            
            # 척도 설명 커스터마이징
            use_default_scale = Confirm.ask(
                "기본 척도(1=전혀 동의하지 않음, 7=매우 동의함) 사용?",
                default=True
            )
            
            if use_default_scale:
                scale_description = "1(전혀 동의하지 않음) ~ 7(매우 동의함)"
            else:
                scale_description = Prompt.ask("척도 설명")
            
            # 카테고리 (선택사항)
            category = Prompt.ask("카테고리 (선택사항)", default="")
            
            survey.add_question(
                text=question_text,
                scale_description=scale_description,
                category=category if category else None
            )
            
            self.console.print(f"[green]✓ 질문 {question_num} 추가됨[/green]\n")
            question_num += 1
        
        self.survey = survey
        
        # 설문 요약 표시
        self._show_survey_summary(survey)
        
        return survey
    
    def load_survey_from_file(self, filepath: str) -> Survey:
        """파일에서 설문조사를 로드합니다."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        survey = Survey(data['title'], data.get('description', ''))
        
        for q_data in data['questions']:
            survey.add_question(
                text=q_data['text'],
                question_id=q_data.get('question_id'),
                scale_description=q_data.get('scale_description', "1(전혀 동의하지 않음) ~ 7(매우 동의함)"),
                category=q_data.get('category')
            )
        
        self.survey = survey
        self.console.print(f"[green]✓ 설문조사 로드 완료: {survey.title}[/green]")
        self._show_survey_summary(survey)
        
        return survey
    
    def save_survey_template(self, filepath: str) -> None:
        """설문조사 템플릿을 파일로 저장합니다."""
        if not self.survey:
            self.console.print("[red]✗ 저장할 설문조사가 없습니다.[/red]")
            return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.survey.to_dict(), f, ensure_ascii=False, indent=2)
        
        self.console.print(f"[green]✓ 설문조사 템플릿 저장됨: {filepath}[/green]")
    
    def _show_survey_summary(self, survey: Survey) -> None:
        """설문조사 요약을 표시합니다."""
        self.console.print(f"\n[bold]설문조사: {survey.title}[/bold]")
        if survey.description:
            self.console.print(f"[dim]{survey.description}[/dim]")
        self.console.print(f"\n총 {len(survey.questions)}개의 질문\n")
        
        for i, q in enumerate(survey.questions, 1):
            self.console.print(f"[cyan]{i}. {q.text}[/cyan]")
            self.console.print(f"   척도: {q.scale_description}")
            if q.category:
                self.console.print(f"   카테고리: {q.category}")
            self.console.print()
    
    def conduct_survey(
        self,
        personas: List[Persona],
        survey: Optional[Survey] = None,
        delay: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        설문조사를 진행합니다.
        
        Args:
            personas: 응답할 페르소나 리스트
            survey: 설문조사 객체 (None인 경우 self.survey 사용)
            delay: 각 API 호출 사이의 지연 시간 (초)
        
        Returns:
            응답 결과 리스트
        """
        if survey is None:
            survey = self.survey
        
        if not survey:
            self.console.print("[red]✗ 설문조사가 설정되지 않았습니다.[/red]")
            return []
        
        self.console.print(f"\n[bold cyan]═══ 설문조사 진행: {survey.title} ═══[/bold cyan]\n")
        self.console.print(f"[green]응답자: {len(personas)}명[/green]")
        self.console.print(f"[green]질문: {len(survey.questions)}개[/green]")
        self.console.print(f"[green]총 응답: {len(personas) * len(survey.questions)}개[/green]\n")
        
        responses = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            total_tasks = len(personas) * len(survey.questions)
            task = progress.add_task("[cyan]설문 진행 중...", total=total_tasks)
            
            for persona_idx, persona in enumerate(personas, 1):
                for question in survey.questions:
                    progress.update(
                        task,
                        description=f"[cyan]응답자 {persona_idx}/{len(personas)} | {question.question_id}"
                    )
                    
                    # AI 에이전트로 응답 생성
                    response = self.ai_agent.respond_to_survey_question(
                        persona,
                        question.text,
                        question.scale_description
                    )
                    
                    # 응답에 추가 정보 포함
                    response.update({
                        "survey_title": survey.title,
                        "question_id": question.question_id,
                        "category": question.category,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    responses.append(response)
                    
                    progress.advance(task)
                    
                    # API 레이트 리밋 방지를 위한 지연
                    if delay > 0:
                        time.sleep(delay)
        
        self.responses = responses
        
        self.console.print(f"\n[bold green]✓ 설문조사 완료![/bold green]")
        self.console.print(f"[green]총 {len(responses)}개의 응답 수집됨[/green]\n")
        
        # 간단한 통계 표시
        self._show_response_statistics(responses)
        
        return responses
    
    def _show_response_statistics(self, responses: List[Dict[str, Any]]) -> None:
        """응답 통계를 표시합니다."""
        if not responses:
            return
        
        # 질문별 평균 점수 계산
        question_stats = {}
        
        for response in responses:
            qid = response.get('question_id', 'Unknown')
            score = response.get('score')
            
            if qid not in question_stats:
                question_stats[qid] = {
                    'scores': [],
                    'question': response.get('question', ''),
                    'errors': 0
                }
            
            if score is not None:
                question_stats[qid]['scores'].append(score)
            else:
                question_stats[qid]['errors'] += 1
        
        # 통계 테이블 생성
        table = Table(title="설문 응답 통계", box=box.ROUNDED)
        table.add_column("질문 ID", style="cyan")
        table.add_column("평균 점수", style="green", justify="right")
        table.add_column("응답 수", style="yellow", justify="right")
        table.add_column("오류", style="red", justify="right")
        
        for qid, stats in question_stats.items():
            scores = stats['scores']
            avg_score = sum(scores) / len(scores) if scores else 0
            
            table.add_row(
                qid,
                f"{avg_score:.2f}",
                str(len(scores)),
                str(stats['errors']) if stats['errors'] > 0 else "-"
            )
        
        self.console.print(table)
        self.console.print()
    
    def get_responses(self) -> List[Dict[str, Any]]:
        """수집된 응답을 반환합니다."""
        return self.responses
    
    def export_responses(self, filepath: str) -> None:
        """응답을 JSON 파일로 내보냅니다."""
        if not self.responses:
            self.console.print("[yellow]⚠ 내보낼 응답이 없습니다.[/yellow]")
            return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.responses, f, ensure_ascii=False, indent=2)
        
        self.console.print(f"[green]✓ 응답 저장됨: {filepath}[/green]")


if __name__ == "__main__":
    # 테스트 코드
    from src.dataset_loader import DatasetLoader, Persona
    
    # 테스트용 페르소나
    test_personas = [
        Persona(id="1", data={"age": 25, "occupation": "student"}),
        Persona(id="2", data={"age": 35, "occupation": "teacher"}),
    ]
    
    # AI 에이전트 (API 키 필요)
    try:
        agent = AIAgent()
        system = SurveySystem(agent)
        
        # 설문 생성
        survey = system.create_survey_wizard()
        
        # 설문 진행
        if Confirm.ask("\n설문조사를 진행하시겠습니까?"):
            responses = system.conduct_survey(test_personas, survey)
    
    except ValueError as e:
        print(f"Error: {e}")


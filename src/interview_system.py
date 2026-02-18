"""
인터뷰 시스템
디지털 트윈들에게 개방형 질문을 하고 자유로운 응답을 수집합니다.
"""

import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from src.dataset_loader import Persona
from src.ai_agent import AIAgent


class InterviewQuestion:
    """인터뷰 질문 클래스"""
    
    def __init__(
        self,
        question_id: str,
        text: str,
        category: Optional[str] = None,
        context: Optional[str] = None
    ):
        self.question_id = question_id
        self.text = text
        self.category = category
        self.context = context
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "text": self.text,
            "category": self.category,
            "context": self.context
        }


class InterviewGuide:
    """인터뷰 가이드 클래스"""
    
    def __init__(self, title: str, description: str = ""):
        self.title = title
        self.description = description
        self.questions: List[InterviewQuestion] = []
        self.created_at = datetime.now().isoformat()
    
    def add_question(
        self,
        text: str,
        question_id: Optional[str] = None,
        category: Optional[str] = None,
        context: Optional[str] = None
    ) -> None:
        """인터뷰 질문을 추가합니다."""
        if question_id is None:
            question_id = f"IQ{len(self.questions) + 1}"
        
        question = InterviewQuestion(question_id, text, category, context)
        self.questions.append(question)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at,
            "questions": [q.to_dict() for q in self.questions]
        }


class InterviewSystem:
    """인터뷰 시스템"""
    
    def __init__(self, ai_agent: AIAgent):
        self.ai_agent = ai_agent
        self.console = Console()
        self.interview_guide: Optional[InterviewGuide] = None
        self.interviews: List[Dict[str, Any]] = []
    
    def create_interview_guide_wizard(self) -> InterviewGuide:
        """대화형 인터뷰 가이드 생성 마법사"""
        self.console.print("\n[bold cyan]═══ 인터뷰 가이드 생성 ═══[/bold cyan]\n")
        
        title = Prompt.ask("[bold]인터뷰 제목[/bold]")
        description = Prompt.ask("[bold]설명[/bold] (선택사항, Enter로 건너뛰기)", default="")
        
        guide = InterviewGuide(title, description)
        
        self.console.print("\n[bold]질문 추가[/bold]")
        self.console.print("[dim]개방형 질문으로 구성됩니다.[/dim]\n")
        
        question_num = 1
        while True:
            self.console.print(f"[cyan]질문 {question_num}[/cyan]")
            
            question_text = Prompt.ask("질문 내용 (완료하려면 Enter)", default="")
            
            if not question_text:
                if question_num == 1:
                    self.console.print("[yellow]⚠ 최소 1개의 질문이 필요합니다.[/yellow]")
                    continue
                break
            
            # 카테고리 (선택사항)
            category = Prompt.ask("카테고리 (선택사항)", default="")
            
            # 컨텍스트 (선택사항)
            add_context = Confirm.ask("추가 컨텍스트를 제공하시겠습니까?", default=False)
            context = None
            if add_context:
                context = Prompt.ask("컨텍스트")
            
            guide.add_question(
                text=question_text,
                category=category if category else None,
                context=context
            )
            
            self.console.print(f"[green]✓ 질문 {question_num} 추가됨[/green]\n")
            question_num += 1
        
        self.interview_guide = guide
        
        # 가이드 요약 표시
        self._show_guide_summary(guide)
        
        return guide
    
    def load_guide_from_file(self, filepath: str) -> InterviewGuide:
        """파일에서 인터뷰 가이드를 로드합니다."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        guide = InterviewGuide(data['title'], data.get('description', ''))
        
        for q_data in data['questions']:
            guide.add_question(
                text=q_data['text'],
                question_id=q_data.get('question_id'),
                category=q_data.get('category'),
                context=q_data.get('context')
            )
        
        self.interview_guide = guide
        self.console.print(f"[green]✓ 인터뷰 가이드 로드 완료: {guide.title}[/green]")
        self._show_guide_summary(guide)
        
        return guide
    
    def save_guide_template(self, filepath: str) -> None:
        """인터뷰 가이드를 파일로 저장합니다."""
        if not self.interview_guide:
            self.console.print("[red]✗ 저장할 인터뷰 가이드가 없습니다.[/red]")
            return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.interview_guide.to_dict(), f, ensure_ascii=False, indent=2)
        
        self.console.print(f"[green]✓ 인터뷰 가이드 저장됨: {filepath}[/green]")
    
    def _show_guide_summary(self, guide: InterviewGuide) -> None:
        """인터뷰 가이드 요약을 표시합니다."""
        self.console.print(f"\n[bold]인터뷰: {guide.title}[/bold]")
        if guide.description:
            self.console.print(f"[dim]{guide.description}[/dim]")
        self.console.print(f"\n총 {len(guide.questions)}개의 질문\n")
        
        for i, q in enumerate(guide.questions, 1):
            self.console.print(f"[cyan]{i}. {q.text}[/cyan]")
            if q.category:
                self.console.print(f"   카테고리: {q.category}")
            if q.context:
                self.console.print(f"   컨텍스트: {q.context}")
            self.console.print()
    
    def conduct_interviews(
        self,
        personas: List[Persona],
        guide: Optional[InterviewGuide] = None,
        delay: float = 0.5,
        show_responses: bool = False
    ) -> List[Dict[str, Any]]:
        """
        인터뷰를 진행합니다.
        
        Args:
            personas: 인터뷰할 페르소나 리스트
            guide: 인터뷰 가이드 (None인 경우 self.interview_guide 사용)
            delay: 각 API 호출 사이의 지연 시간 (초)
            show_responses: 실시간으로 응답을 표시할지 여부
        
        Returns:
            인터뷰 결과 리스트
        """
        if guide is None:
            guide = self.interview_guide
        
        if not guide:
            self.console.print("[red]✗ 인터뷰 가이드가 설정되지 않았습니다.[/red]")
            return []
        
        self.console.print(f"\n[bold cyan]═══ 인터뷰 진행: {guide.title} ═══[/bold cyan]\n")
        self.console.print(f"[green]인터뷰 대상: {len(personas)}명[/green]")
        self.console.print(f"[green]질문: {len(guide.questions)}개[/green]\n")
        
        interviews = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            total_tasks = len(personas) * len(guide.questions)
            task = progress.add_task("[cyan]인터뷰 진행 중...", total=total_tasks)
            
            for persona_idx, persona in enumerate(personas, 1):
                interview_data = {
                    "persona_id": persona.id,
                    "interview_title": guide.title,
                    "timestamp": datetime.now().isoformat(),
                    "responses": []
                }
                
                for question in guide.questions:
                    progress.update(
                        task,
                        description=f"[cyan]인터뷰 {persona_idx}/{len(personas)} | {question.question_id}"
                    )
                    
                    # AI 에이전트로 응답 생성
                    response = self.ai_agent.respond_to_interview_question(
                        persona,
                        question.text,
                        question.context
                    )
                    
                    # 응답에 추가 정보 포함
                    response.update({
                        "question_id": question.question_id,
                        "category": question.category,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    interview_data["responses"].append(response)
                    
                    progress.advance(task)
                    
                    # API 레이트 리밋 방지를 위한 지연
                    if delay > 0:
                        time.sleep(delay)
                
                interviews.append(interview_data)
        
        self.interviews = interviews
        
        self.console.print(f"\n[bold green]✓ 인터뷰 완료![/bold green]")
        self.console.print(f"[green]총 {len(interviews)}개의 인터뷰 완료[/green]\n")
        
        # 실시간 응답 표시
        if show_responses:
            self._show_interview_responses(interviews)
        
        return interviews
    
    def conduct_single_interview(
        self,
        persona: Persona,
        guide: Optional[InterviewGuide] = None,
        interactive: bool = True
    ) -> Dict[str, Any]:
        """
        단일 페르소나와 인터뷰를 진행합니다 (대화형 모드).
        
        Args:
            persona: 인터뷰할 페르소나
            guide: 인터뷰 가이드
            interactive: 대화형 모드 여부
        
        Returns:
            인터뷰 결과
        """
        if guide is None:
            guide = self.interview_guide
        
        if not guide:
            self.console.print("[red]✗ 인터뷰 가이드가 설정되지 않았습니다.[/red]")
            return {}
        
        self.console.print(f"\n[bold cyan]═══ 인터뷰: {guide.title} ═══[/bold cyan]\n")
        self.console.print(Panel(
            persona.get_summary(),
            title=f"[bold]인터뷰 대상 (ID: {persona.id})[/bold]",
            border_style="cyan"
        ))
        self.console.print()
        
        interview_data = {
            "persona_id": persona.id,
            "interview_title": guide.title,
            "timestamp": datetime.now().isoformat(),
            "responses": []
        }
        
        conversation_history = []
        
        for i, question in enumerate(guide.questions, 1):
            self.console.print(f"\n[bold cyan]질문 {i}/{len(guide.questions)}[/bold cyan]")
            self.console.print(f"[yellow]{question.text}[/yellow]\n")
            
            # AI 응답 생성
            response = self.ai_agent.respond_to_interview_question(
                persona,
                question.text,
                question.context
            )
            
            # 응답 표시
            if response.get('response'):
                self.console.print(Panel(
                    response['response'],
                    title="[bold green]응답[/bold green]",
                    border_style="green"
                ))
            elif response.get('error'):
                self.console.print(f"[red]✗ 오류: {response['error']}[/red]")
            
            response.update({
                "question_id": question.question_id,
                "category": question.category,
                "timestamp": datetime.now().isoformat()
            })
            
            interview_data["responses"].append(response)
            conversation_history.append({
                "question": question.text,
                "answer": response.get('response', '')
            })
            
            # 대화형 모드: 후속 질문 옵션
            if interactive and i < len(guide.questions):
                self.console.print()
                
                if Confirm.ask("후속 질문을 하시겠습니까?", default=False):
                    follow_up = Prompt.ask("[bold]후속 질문[/bold]")
                    
                    self.console.print()
                    follow_up_response = self.ai_agent.conduct_follow_up(
                        persona,
                        conversation_history,
                        follow_up
                    )
                    
                    if follow_up_response.get('response'):
                        self.console.print(Panel(
                            follow_up_response['response'],
                            title="[bold green]응답[/bold green]",
                            border_style="green"
                        ))
                    
                    # 후속 질문도 기록
                    follow_up_response.update({
                        "question_id": f"{question.question_id}_followup",
                        "category": "follow_up",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    interview_data["responses"].append(follow_up_response)
                    conversation_history.append({
                        "question": follow_up,
                        "answer": follow_up_response.get('response', '')
                    })
        
        self.console.print(f"\n[bold green]✓ 인터뷰 완료[/bold green]\n")
        
        return interview_data
    
    def _show_interview_responses(self, interviews: List[Dict[str, Any]]) -> None:
        """인터뷰 응답을 표시합니다."""
        self.console.print("\n[bold cyan]═══ 인터뷰 응답 샘플 ═══[/bold cyan]\n")
        
        # 첫 번째 인터뷰만 표시 (샘플)
        if interviews:
            interview = interviews[0]
            self.console.print(f"[bold]응답자 ID: {interview['persona_id']}[/bold]\n")
            
            for resp in interview['responses']:
                if resp.get('response'):
                    self.console.print(Panel(
                        f"[cyan]Q: {resp['question']}[/cyan]\n\n{resp['response']}",
                        border_style="green"
                    ))
                    self.console.print()
            
            if len(interviews) > 1:
                self.console.print(f"[dim]... 외 {len(interviews) - 1}개의 인터뷰[/dim]\n")
    
    def get_interviews(self) -> List[Dict[str, Any]]:
        """수집된 인터뷰를 반환합니다."""
        return self.interviews
    
    def export_interviews(self, filepath: str) -> None:
        """인터뷰를 JSON 파일로 내보냅니다."""
        if not self.interviews:
            self.console.print("[yellow]⚠ 내보낼 인터뷰가 없습니다.[/yellow]")
            return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.interviews, f, ensure_ascii=False, indent=2)
        
        self.console.print(f"[green]✓ 인터뷰 저장됨: {filepath}[/green]")
    
    def export_to_text(self, filepath: str) -> None:
        """인터뷰를 읽기 쉬운 텍스트 형식으로 내보냅니다."""
        if not self.interviews:
            self.console.print("[yellow]⚠ 내보낼 인터뷰가 없습니다.[/yellow]")
            return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"인터뷰 인터뷰록\n")
            f.write(f"{'='*80}\n\n")
            
            for interview in self.interviews:
                f.write(f"응답자 ID: {interview['persona_id']}\n")
                f.write(f"인터뷰: {interview['interview_title']}\n")
                f.write(f"일시: {interview['timestamp']}\n")
                f.write(f"{'-'*80}\n\n")
                
                for resp in interview['responses']:
                    f.write(f"Q: {resp['question']}\n\n")
                    f.write(f"A: {resp.get('response', '[응답 없음]')}\n\n")
                    if resp.get('category'):
                        f.write(f"   (카테고리: {resp['category']})\n\n")
                    f.write(f"{'-'*40}\n\n")
                
                f.write(f"\n{'='*80}\n\n")
        
        self.console.print(f"[green]✓ 인터뷰 인터뷰록 저장됨: {filepath}[/green]")


if __name__ == "__main__":
    # 테스트 코드
    from src.dataset_loader import Persona
    
    test_persona = Persona(
        id="test_1",
        data={"age": 30, "occupation": "designer", "interests": "art, technology"}
    )
    
    try:
        agent = AIAgent()
        system = InterviewSystem(agent)
        
        # 인터뷰 가이드 생성
        guide = system.create_interview_guide_wizard()
        
        # 인터뷰 진행
        if Confirm.ask("\n인터뷰를 진행하시겠습니까?"):
            interview = system.conduct_single_interview(test_persona, guide)
    
    except ValueError as e:
        print(f"Error: {e}")


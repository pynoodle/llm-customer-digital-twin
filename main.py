"""
디지털 트윈 설문조사 및 인터뷰 시스템
메인 프로그램 및 CLI 인터페이스

Hugging Face Twin-2K-500 데이터셋을 활용하여
AI 기반 설문조사와 인터뷰를 진행합니다.
"""

import sys
import os
from typing import List, Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import box

from src.dataset_loader import DatasetLoader, Persona
from src.persona_selector import PersonaSelector
from src.ai_agent import AIAgent
from src.survey_system import SurveySystem, Survey
from src.interview_system import InterviewSystem, InterviewGuide
from src.results_manager import ResultsManager


class DigitalTwinResearchSystem:
    """디지털 트윈 연구 시스템 메인 클래스"""
    
    def __init__(self):
        self.console = Console()
        self.loader = DatasetLoader()
        self.ai_agent = None
        self.selected_personas: List[Persona] = []
        self.results_manager = ResultsManager()
    
    def welcome(self) -> None:
        """환영 메시지를 표시합니다."""
        welcome_text = """
[bold cyan]디지털 트윈 설문조사 & 인터뷰 시스템[/bold cyan]

이 시스템은 Hugging Face의 Twin-2K-500 데이터셋을 활용하여
AI 기반 디지털 트윈과 설문조사 및 인터뷰를 진행합니다.

[bold]주요 기능:[/bold]
• 📊 구조화된 설문조사 (1-7점 리커트 척도)
• 💬 개방형 인터뷰 (자유 응답)
• 🎯 응답자 선택 및 필터링
• 📁 결과 저장 및 분석

[dim]Powered by ChatGPT API[/dim]
        """
        
        self.console.print(Panel(
            welcome_text,
            box=box.DOUBLE,
            border_style="cyan"
        ))
        self.console.print()
    
    def initialize(self) -> bool:
        """시스템을 초기화합니다."""
        self.console.print("[bold]시스템 초기화 중...[/bold]\n")
        
        # 1. 데이터셋 로드
        try:
            self.console.print("[cyan]1/2 데이터셋 로딩...[/cyan]")
            self.loader.load()
            self.console.print("[green]✓ 데이터셋 로드 완료[/green]\n")
        except Exception as e:
            self.console.print(f"[red]✗ 데이터셋 로드 실패: {e}[/red]")
            return False
        
        # 2. AI 에이전트 초기화
        try:
            self.console.print("[cyan]2/2 AI 에이전트 초기화...[/cyan]")
            self.ai_agent = AIAgent()
            self.console.print("[green]✓ AI 에이전트 초기화 완료[/green]\n")
        except ValueError as e:
            self.console.print(f"[red]✗ AI 에이전트 초기화 실패: {e}[/red]")
            self.console.print("\n[yellow]OpenAI API 키를 설정해주세요:[/yellow]")
            self.console.print("1. 프로젝트 루트에 .env 파일을 생성")
            self.console.print("2. OPENAI_API_KEY=your_api_key_here 입력")
            return False
        except Exception as e:
            self.console.print(f"[red]✗ 초기화 실패: {e}[/red]")
            return False
        
        self.console.print("[bold green]✓ 시스템 초기화 완료![/bold green]\n")
        return True
    
    def select_personas(self) -> bool:
        """응답자를 선택합니다."""
        selector = PersonaSelector(self.loader)
        self.selected_personas = selector.run_selection_wizard()
        
        if not self.selected_personas:
            self.console.print("[red]✗ 응답자가 선택되지 않았습니다.[/red]")
            return False
        
        selector.show_selection_summary()
        return True
    
    def conduct_survey(self) -> None:
        """설문조사를 진행합니다."""
        if not self.selected_personas:
            self.console.print("[red]✗ 먼저 응답자를 선택해주세요.[/red]")
            return
        
        survey_system = SurveySystem(self.ai_agent)
        
        # 설문조사 생성 또는 로드
        self.console.print("\n[bold]설문조사 준비[/bold]")
        self.console.print("1. 새 설문조사 만들기")
        self.console.print("2. 파일에서 불러오기")
        
        choice = Prompt.ask("선택", choices=["1", "2"], default="1")
        
        if choice == "1":
            survey = survey_system.create_survey_wizard()
        else:
            filepath = Prompt.ask("설문조사 파일 경로")
            try:
                survey = survey_system.load_survey_from_file(filepath)
            except Exception as e:
                self.console.print(f"[red]✗ 파일 로드 실패: {e}[/red]")
                return
        
        # 설문조사 진행 확인
        if not Confirm.ask(f"\n{len(self.selected_personas)}명의 응답자에게 설문조사를 진행하시겠습니까?", default=True):
            return
        
        # API 지연 시간 설정
        delay = float(Prompt.ask("API 호출 사이 지연 시간(초)", default="0.5"))
        
        # 설문조사 진행
        responses = survey_system.conduct_survey(
            self.selected_personas,
            survey,
            delay=delay
        )
        
        # 결과 저장
        if responses and Confirm.ask("\n결과를 저장하시겠습니까?", default=True):
            self.results_manager.save_survey_results(responses)
            self.results_manager.show_survey_analysis(responses)
    
    def conduct_interview(self) -> None:
        """인터뷰를 진행합니다."""
        if not self.selected_personas:
            self.console.print("[red]✗ 먼저 응답자를 선택해주세요.[/red]")
            return
        
        interview_system = InterviewSystem(self.ai_agent)
        
        # 인터뷰 가이드 생성 또는 로드
        self.console.print("\n[bold]인터뷰 준비[/bold]")
        self.console.print("1. 새 인터뷰 가이드 만들기")
        self.console.print("2. 파일에서 불러오기")
        
        choice = Prompt.ask("선택", choices=["1", "2"], default="1")
        
        if choice == "1":
            guide = interview_system.create_interview_guide_wizard()
        else:
            filepath = Prompt.ask("인터뷰 가이드 파일 경로")
            try:
                guide = interview_system.load_guide_from_file(filepath)
            except Exception as e:
                self.console.print(f"[red]✗ 파일 로드 실패: {e}[/red]")
                return
        
        # 인터뷰 모드 선택
        self.console.print("\n[bold]인터뷰 모드 선택[/bold]")
        self.console.print("1. 배치 모드 (모든 응답자에게 자동 진행)")
        self.console.print("2. 대화형 모드 (한 명씩 인터뷰, 후속 질문 가능)")
        
        mode = Prompt.ask("선택", choices=["1", "2"], default="1")
        
        if mode == "1":
            # 배치 모드
            if not Confirm.ask(f"\n{len(self.selected_personas)}명의 응답자와 인터뷰를 진행하시겠습니까?", default=True):
                return
            
            delay = float(Prompt.ask("API 호출 사이 지연 시간(초)", default="0.5"))
            show_responses = Confirm.ask("진행 중 응답을 표시하시겠습니까?", default=False)
            
            interviews = interview_system.conduct_interviews(
                self.selected_personas,
                guide,
                delay=delay,
                show_responses=show_responses
            )
            
            # 결과 저장
            if interviews and Confirm.ask("\n결과를 저장하시겠습니까?", default=True):
                self.results_manager.save_interview_results(interviews)
        
        else:
            # 대화형 모드
            for i, persona in enumerate(self.selected_personas, 1):
                self.console.print(f"\n[bold cyan]═══ 인터뷰 {i}/{len(self.selected_personas)} ═══[/bold cyan]")
                
                interview = interview_system.conduct_single_interview(
                    persona,
                    guide,
                    interactive=True
                )
                
                # 개별 저장 옵션
                if i < len(self.selected_personas):
                    if not Confirm.ask("\n다음 인터뷰를 계속하시겠습니까?", default=True):
                        break
            
            # 전체 결과 저장
            interviews = interview_system.get_interviews()
            if interviews and Confirm.ask("\n모든 인터뷰 결과를 저장하시겠습니까?", default=True):
                self.results_manager.save_interview_results(interviews)
    
    def main_menu(self) -> None:
        """메인 메뉴를 표시하고 사용자 선택을 처리합니다."""
        while True:
            self.console.print("\n[bold cyan]═══ 메인 메뉴 ═══[/bold cyan]\n")
            self.console.print("1. 응답자 선택")
            self.console.print("2. 설문조사 진행")
            self.console.print("3. 인터뷰 진행")
            self.console.print("4. 결과 관리")
            self.console.print("5. 종료")
            
            choice = Prompt.ask("\n메뉴 선택", choices=["1", "2", "3", "4", "5"], default="1")
            
            if choice == "1":
                self.select_personas()
            
            elif choice == "2":
                self.conduct_survey()
            
            elif choice == "3":
                self.conduct_interview()
            
            elif choice == "4":
                self.results_menu()
            
            elif choice == "5":
                self.console.print("\n[bold green]시스템을 종료합니다. 감사합니다![/bold green]\n")
                break
    
    def results_menu(self) -> None:
        """결과 관리 메뉴"""
        self.console.print("\n[bold cyan]═══ 결과 관리 ═══[/bold cyan]\n")
        self.console.print("1. 설문조사 결과 분석")
        self.console.print("2. 인터뷰 결과 보기")
        self.console.print("3. Excel로 내보내기")
        self.console.print("4. 돌아가기")
        
        choice = Prompt.ask("\n선택", choices=["1", "2", "3", "4"], default="4")
        
        if choice == "1":
            filepath = Prompt.ask("설문조사 결과 파일 경로 (JSON)")
            try:
                import json
                with open(filepath, 'r', encoding='utf-8') as f:
                    responses = json.load(f)
                self.results_manager.show_survey_analysis(responses)
            except Exception as e:
                self.console.print(f"[red]✗ 파일 로드 실패: {e}[/red]")
        
        elif choice == "2":
            filepath = Prompt.ask("인터뷰 결과 파일 경로 (JSON)")
            try:
                import json
                with open(filepath, 'r', encoding='utf-8') as f:
                    interviews = json.load(f)
                self.console.print(f"\n[green]총 {len(interviews)}개의 인터뷰가 있습니다.[/green]")
                # 첫 번째 인터뷰 표시
                if interviews and Confirm.ask("첫 번째 인터뷰를 표시하시겠습니까?", default=True):
                    interview = interviews[0]
                    self.console.print(f"\n[bold]응답자 ID: {interview['persona_id']}[/bold]\n")
                    for resp in interview.get('responses', [])[:3]:  # 처음 3개만
                        self.console.print(Panel(
                            f"[cyan]Q: {resp['question']}[/cyan]\n\n{resp.get('response', '[응답 없음]')}",
                            border_style="green"
                        ))
            except Exception as e:
                self.console.print(f"[red]✗ 파일 로드 실패: {e}[/red]")
        
        elif choice == "3":
            survey_path = Prompt.ask("설문조사 결과 파일 (선택사항, Enter로 건너뛰기)", default="")
            interview_path = Prompt.ask("인터뷰 결과 파일 (선택사항, Enter로 건너뛰기)", default="")
            
            import json
            survey_data = None
            interview_data = None
            
            try:
                if survey_path:
                    with open(survey_path, 'r', encoding='utf-8') as f:
                        survey_data = json.load(f)
                
                if interview_path:
                    with open(interview_path, 'r', encoding='utf-8') as f:
                        interview_data = json.load(f)
                
                if survey_data or interview_data:
                    self.results_manager.export_to_excel(survey_data, interview_data)
                else:
                    self.console.print("[yellow]⚠ 내보낼 데이터가 없습니다.[/yellow]")
            
            except Exception as e:
                self.console.print(f"[red]✗ 내보내기 실패: {e}[/red]")
    
    def run(self) -> None:
        """시스템을 실행합니다."""
        self.welcome()
        
        if not self.initialize():
            self.console.print("\n[red]시스템 초기화에 실패했습니다.[/red]")
            return
        
        self.main_menu()


def main():
    """메인 함수"""
    try:
        system = DigitalTwinResearchSystem()
        system.run()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n\n[yellow]사용자에 의해 중단되었습니다.[/yellow]\n")
        sys.exit(0)
    except Exception as e:
        console = Console()
        console.print(f"\n[red]예상치 못한 오류가 발생했습니다: {e}[/red]\n")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()


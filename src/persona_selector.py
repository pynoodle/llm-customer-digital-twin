"""
응답자 선택 및 필터링 시스템
연구자가 설문조사나 인터뷰를 진행할 페르소나를 선택할 수 있도록 합니다.
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import box
from src.dataset_loader import DatasetLoader, Persona


class PersonaSelector:
    """페르소나 선택 인터페이스"""
    
    def __init__(self, loader: DatasetLoader):
        self.loader = loader
        self.console = Console()
        self.selected_personas: List[Persona] = []
    
    def run_selection_wizard(self) -> List[Persona]:
        """
        대화형 페르소나 선택 마법사를 실행합니다.
        
        Returns:
            선택된 페르소나 리스트
        """
        self.console.print("\n[bold cyan]═══ 응답자 선택 시스템 ═══[/bold cyan]\n")
        
        # 전체 페르소나 수 표시
        total = len(self.loader.get_all_personas())
        self.console.print(f"[green]데이터셋에 총 {total}명의 디지털 트윈이 있습니다.[/green]\n")
        
        # 선택 방법 선택
        self.console.print("[bold]응답자를 어떻게 선택하시겠습니까?[/bold]")
        self.console.print("1. 전체 선택")
        self.console.print("2. 무작위 샘플 추출")
        self.console.print("3. 조건 필터링")
        self.console.print("4. ID로 직접 선택")
        
        choice = Prompt.ask("\n선택", choices=["1", "2", "3", "4"], default="2")
        
        if choice == "1":
            return self._select_all()
        elif choice == "2":
            return self._select_random()
        elif choice == "3":
            return self._select_by_filters()
        elif choice == "4":
            return self._select_by_ids()
        
        return []
    
    def _select_all(self) -> List[Persona]:
        """전체 페르소나를 선택합니다."""
        personas = self.loader.get_all_personas()
        
        confirm = Confirm.ask(
            f"\n전체 {len(personas)}명을 선택하시겠습니까? (처리 시간이 오래 걸릴 수 있습니다)",
            default=False
        )
        
        if confirm:
            self.selected_personas = personas
            self.console.print(f"[green]✓ {len(personas)}명의 응답자가 선택되었습니다.[/green]\n")
            return personas
        else:
            return self.run_selection_wizard()
    
    def _select_random(self) -> List[Persona]:
        """무작위 샘플을 추출합니다."""
        total = len(self.loader.get_all_personas())
        
        sample_size = Prompt.ask(
            f"\n샘플 크기를 입력하세요 (1-{total})",
            default="50"
        )
        
        try:
            n = int(sample_size)
            if n < 1 or n > total:
                self.console.print(f"[red]✗ 1에서 {total} 사이의 숫자를 입력해주세요.[/red]")
                return self._select_random()
            
            personas = self.loader.get_random_sample(n)
            self.selected_personas = personas
            
            self.console.print(f"[green]✓ {len(personas)}명의 응답자가 무작위로 선택되었습니다.[/green]\n")
            
            # 미리보기 표시
            if Confirm.ask("선택된 응답자 미리보기를 보시겠습니까?", default=True):
                self._show_preview(personas[:5])
            
            return personas
            
        except ValueError:
            self.console.print("[red]✗ 유효한 숫자를 입력해주세요.[/red]")
            return self._select_random()
    
    def _select_by_filters(self) -> List[Persona]:
        """조건 필터링으로 페르소나를 선택합니다."""
        self.console.print("\n[bold]필터링 조건 설정[/bold]")
        
        # 사용 가능한 필드 표시
        fields = self.loader.get_available_fields()
        
        self.console.print("\n[cyan]사용 가능한 필드:[/cyan]")
        for i, field in enumerate(fields, 1):
            self.console.print(f"  {i}. {field}")
        
        filters = {}
        
        while True:
            self.console.print("\n[bold]필터 추가 (완료하려면 Enter를 누르세요)[/bold]")
            
            field_name = Prompt.ask("필드 이름", default="")
            
            if not field_name:
                break
            
            if field_name not in fields:
                self.console.print(f"[yellow]⚠ '{field_name}'는 유효한 필드가 아닙니다.[/yellow]")
                continue
            
            # 해당 필드의 고유 값 표시
            unique_values = self.loader.get_field_unique_values(field_name)
            
            if unique_values and len(unique_values) < 50:
                self.console.print(f"\n[cyan]'{field_name}'의 가능한 값:[/cyan]")
                for value in unique_values[:20]:  # 최대 20개만 표시
                    self.console.print(f"  - {value}")
                if len(unique_values) > 20:
                    self.console.print(f"  ... 외 {len(unique_values) - 20}개")
            
            filter_value = Prompt.ask(f"{field_name} 값")
            filters[field_name] = filter_value
            
            self.console.print(f"[green]✓ 필터 추가됨: {field_name} = {filter_value}[/green]")
        
        if not filters:
            self.console.print("[yellow]⚠ 필터가 설정되지 않았습니다. 전체 선택으로 진행합니다.[/yellow]")
            return self._select_all()
        
        # 필터 적용
        self.console.print(f"\n[cyan]필터 적용 중...[/cyan]")
        personas = self.loader.search_personas(filters)
        
        self.console.print(f"[green]✓ {len(personas)}명의 응답자가 필터링되었습니다.[/green]\n")
        
        if len(personas) == 0:
            self.console.print("[red]✗ 조건에 맞는 응답자가 없습니다.[/red]")
            if Confirm.ask("다시 시도하시겠습니까?", default=True):
                return self._select_by_filters()
            else:
                return []
        
        # 미리보기
        if Confirm.ask("선택된 응답자 미리보기를 보시겠습니까?", default=True):
            self._show_preview(personas[:5])
        
        self.selected_personas = personas
        return personas
    
    def _select_by_ids(self) -> List[Persona]:
        """ID로 직접 페르소나를 선택합니다."""
        self.console.print("\n[bold]ID로 직접 선택[/bold]")
        self.console.print("쉼표로 구분된 ID를 입력하세요 (예: 1,2,3,4,5)")
        
        id_input = Prompt.ask("\nIDs")
        
        try:
            ids = [id.strip() for id in id_input.split(",")]
            personas = []
            
            for pid in ids:
                persona = self.loader.get_persona_by_id(pid)
                if persona:
                    personas.append(persona)
                else:
                    self.console.print(f"[yellow]⚠ ID '{pid}'를 찾을 수 없습니다.[/yellow]")
            
            if not personas:
                self.console.print("[red]✗ 선택된 응답자가 없습니다.[/red]")
                if Confirm.ask("다시 시도하시겠습니까?", default=True):
                    return self._select_by_ids()
                else:
                    return []
            
            self.console.print(f"[green]✓ {len(personas)}명의 응답자가 선택되었습니다.[/green]\n")
            
            # 미리보기
            if Confirm.ask("선택된 응답자 미리보기를 보시겠습니까?", default=True):
                self._show_preview(personas)
            
            self.selected_personas = personas
            return personas
            
        except Exception as e:
            self.console.print(f"[red]✗ 오류 발생: {e}[/red]")
            if Confirm.ask("다시 시도하시겠습니까?", default=True):
                return self._select_by_ids()
            else:
                return []
    
    def _show_preview(self, personas: List[Persona]) -> None:
        """선택된 페르소나의 미리보기를 표시합니다."""
        self.console.print("\n[bold cyan]═══ 응답자 미리보기 ═══[/bold cyan]\n")
        
        for i, persona in enumerate(personas, 1):
            panel_content = persona.get_summary()
            
            self.console.print(
                Panel(
                    panel_content,
                    title=f"[bold]응답자 #{persona.id}[/bold]",
                    border_style="cyan",
                    box=box.ROUNDED
                )
            )
            self.console.print()
        
        if len(personas) < len(self.selected_personas):
            remaining = len(self.selected_personas) - len(personas)
            self.console.print(f"[dim]... 외 {remaining}명의 응답자[/dim]\n")
    
    def get_selected_personas(self) -> List[Persona]:
        """선택된 페르소나를 반환합니다."""
        return self.selected_personas
    
    def show_selection_summary(self) -> None:
        """선택 요약을 표시합니다."""
        if not self.selected_personas:
            self.console.print("[yellow]선택된 응답자가 없습니다.[/yellow]")
            return
        
        table = Table(title="선택된 응답자 요약", box=box.ROUNDED)
        table.add_column("항목", style="cyan")
        table.add_column("값", style="green")
        
        table.add_row("총 응답자 수", str(len(self.selected_personas)))
        table.add_row("첫 번째 ID", self.selected_personas[0].id)
        table.add_row("마지막 ID", self.selected_personas[-1].id)
        
        self.console.print()
        self.console.print(table)
        self.console.print()


if __name__ == "__main__":
    # 테스트 코드
    loader = DatasetLoader()
    loader.load()
    
    selector = PersonaSelector(loader)
    selected = selector.run_selection_wizard()
    
    print(f"\nSelected {len(selected)} personas")


"""
결과 저장 및 내보내기 관리 모듈
설문조사 및 인터뷰 결과를 다양한 형식으로 저장하고 분석합니다.
"""

import json
import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich import box


class ResultsManager:
    """결과 관리 시스템"""
    
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.console = Console()
    
    def save_survey_results(
        self,
        responses: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> Dict[str, str]:
        """
        설문조사 결과를 여러 형식으로 저장합니다.
        
        Args:
            responses: 설문조사 응답 리스트
            filename: 파일명 (없으면 자동 생성)
        
        Returns:
            저장된 파일 경로들
        """
        if not responses:
            self.console.print("[yellow]⚠ 저장할 결과가 없습니다.[/yellow]")
            return {}
        
        # 파일명 생성
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            survey_title = responses[0].get('survey_title', 'survey')
            safe_title = "".join(c for c in survey_title if c.isalnum() or c in (' ', '_')).strip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}_{timestamp}"
        
        saved_files = {}
        
        # JSON 형식 저장
        json_path = self.output_dir / f"{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)
        saved_files['json'] = str(json_path)
        
        # CSV 형식 저장
        csv_path = self.output_dir / f"{filename}.csv"
        self._save_survey_to_csv(responses, csv_path)
        saved_files['csv'] = str(csv_path)
        
        # 분석 요약 저장
        summary_path = self.output_dir / f"{filename}_summary.txt"
        self._save_survey_summary(responses, summary_path)
        saved_files['summary'] = str(summary_path)
        
        self.console.print(f"\n[bold green]✓ 설문조사 결과 저장 완료[/bold green]")
        for format_name, path in saved_files.items():
            self.console.print(f"  [{format_name.upper()}] {path}")
        self.console.print()
        
        return saved_files
    
    def save_interview_results(
        self,
        interviews: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> Dict[str, str]:
        """
        인터뷰 결과를 여러 형식으로 저장합니다.
        
        Args:
            interviews: 인터뷰 리스트
            filename: 파일명 (없으면 자동 생성)
        
        Returns:
            저장된 파일 경로들
        """
        if not interviews:
            self.console.print("[yellow]⚠ 저장할 결과가 없습니다.[/yellow]")
            return {}
        
        # 파일명 생성
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            interview_title = interviews[0].get('interview_title', 'interview')
            safe_title = "".join(c for c in interview_title if c.isalnum() or c in (' ', '_')).strip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}_{timestamp}"
        
        saved_files = {}
        
        # JSON 형식 저장
        json_path = self.output_dir / f"{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(interviews, f, ensure_ascii=False, indent=2)
        saved_files['json'] = str(json_path)
        
        # 인터뷰록 형식 저장
        transcript_path = self.output_dir / f"{filename}_transcript.txt"
        self._save_interview_transcript(interviews, transcript_path)
        saved_files['transcript'] = str(transcript_path)
        
        # CSV 형식 저장
        csv_path = self.output_dir / f"{filename}.csv"
        self._save_interview_to_csv(interviews, csv_path)
        saved_files['csv'] = str(csv_path)
        
        self.console.print(f"\n[bold green]✓ 인터뷰 결과 저장 완료[/bold green]")
        for format_name, path in saved_files.items():
            self.console.print(f"  [{format_name.upper()}] {path}")
        self.console.print()
        
        return saved_files
    
    def _save_survey_to_csv(self, responses: List[Dict[str, Any]], filepath: Path) -> None:
        """설문조사 결과를 CSV로 저장합니다."""
        # DataFrame 생성
        rows = []
        for resp in responses:
            row = {
                'persona_id': resp.get('persona_id'),
                'question_id': resp.get('question_id'),
                'question': resp.get('question'),
                'score': resp.get('score'),
                'reasoning': resp.get('reasoning'),
                'category': resp.get('category'),
                'timestamp': resp.get('timestamp')
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    def _save_survey_summary(self, responses: List[Dict[str, Any]], filepath: Path) -> None:
        """설문조사 결과 요약을 텍스트로 저장합니다."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("설문조사 결과 요약\n")
            f.write("="*80 + "\n\n")
            
            # 기본 정보
            survey_title = responses[0].get('survey_title', 'Unknown')
            total_responses = len(responses)
            unique_personas = len(set(r.get('persona_id') for r in responses))
            unique_questions = len(set(r.get('question_id') for r in responses))
            
            f.write(f"설문조사: {survey_title}\n")
            f.write(f"총 응답: {total_responses}개\n")
            f.write(f"응답자: {unique_personas}명\n")
            f.write(f"질문: {unique_questions}개\n\n")
            
            # 질문별 통계
            f.write("-"*80 + "\n")
            f.write("질문별 통계\n")
            f.write("-"*80 + "\n\n")
            
            question_stats = {}
            for resp in responses:
                qid = resp.get('question_id', 'Unknown')
                question = resp.get('question', '')
                score = resp.get('score')
                
                if qid not in question_stats:
                    question_stats[qid] = {
                        'question': question,
                        'scores': [],
                        'errors': 0
                    }
                
                if score is not None:
                    question_stats[qid]['scores'].append(score)
                else:
                    question_stats[qid]['errors'] += 1
            
            for qid, stats in question_stats.items():
                f.write(f"[{qid}] {stats['question']}\n")
                
                if stats['scores']:
                    mean = sum(stats['scores']) / len(stats['scores'])
                    min_score = min(stats['scores'])
                    max_score = max(stats['scores'])
                    
                    # 분포 계산
                    distribution = {i: stats['scores'].count(i) for i in range(1, 8)}
                    
                    f.write(f"  평균: {mean:.2f}\n")
                    f.write(f"  범위: {min_score} ~ {max_score}\n")
                    f.write(f"  응답 수: {len(stats['scores'])}\n")
                    f.write(f"  분포: {distribution}\n")
                
                if stats['errors'] > 0:
                    f.write(f"  오류: {stats['errors']}개\n")
                
                f.write("\n")
    
    def _save_interview_transcript(self, interviews: List[Dict[str, Any]], filepath: Path) -> None:
        """인터뷰를 인터뷰록 형식으로 저장합니다."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("인터뷰 인터뷰록\n")
            f.write("="*80 + "\n\n")
            
            for idx, interview in enumerate(interviews, 1):
                f.write(f"인터뷰 #{idx}\n")
                f.write("-"*80 + "\n")
                f.write(f"응답자 ID: {interview['persona_id']}\n")
                f.write(f"인터뷰 제목: {interview['interview_title']}\n")
                f.write(f"일시: {interview['timestamp']}\n")
                f.write("-"*80 + "\n\n")
                
                for resp in interview.get('responses', []):
                    f.write(f"Q: {resp['question']}\n\n")
                    
                    if resp.get('response'):
                        f.write(f"A: {resp['response']}\n\n")
                    else:
                        f.write("A: [응답 없음]\n\n")
                    
                    if resp.get('category'):
                        f.write(f"   (카테고리: {resp['category']})\n\n")
                    
                    f.write("-"*40 + "\n\n")
                
                f.write("\n" + "="*80 + "\n\n")
    
    def _save_interview_to_csv(self, interviews: List[Dict[str, Any]], filepath: Path) -> None:
        """인터뷰 결과를 CSV로 저장합니다."""
        rows = []
        for interview in interviews:
            persona_id = interview['persona_id']
            interview_title = interview['interview_title']
            
            for resp in interview.get('responses', []):
                row = {
                    'persona_id': persona_id,
                    'interview_title': interview_title,
                    'question_id': resp.get('question_id'),
                    'question': resp.get('question'),
                    'response': resp.get('response'),
                    'category': resp.get('category'),
                    'timestamp': resp.get('timestamp')
                }
                rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    def analyze_survey_results(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        설문조사 결과를 분석합니다.
        
        Args:
            responses: 설문조사 응답 리스트
        
        Returns:
            분석 결과 딕셔너리
        """
        if not responses:
            return {}
        
        analysis = {
            'total_responses': len(responses),
            'unique_personas': len(set(r.get('persona_id') for r in responses)),
            'unique_questions': len(set(r.get('question_id') for r in responses)),
            'questions': {}
        }
        
        # 질문별 분석
        for resp in responses:
            qid = resp.get('question_id', 'Unknown')
            
            if qid not in analysis['questions']:
                analysis['questions'][qid] = {
                    'question': resp.get('question', ''),
                    'scores': [],
                    'errors': 0
                }
            
            score = resp.get('score')
            if score is not None:
                analysis['questions'][qid]['scores'].append(score)
            else:
                analysis['questions'][qid]['errors'] += 1
        
        # 통계 계산
        for qid, data in analysis['questions'].items():
            if data['scores']:
                scores = data['scores']
                data['mean'] = sum(scores) / len(scores)
                data['min'] = min(scores)
                data['max'] = max(scores)
                data['count'] = len(scores)
                data['distribution'] = {i: scores.count(i) for i in range(1, 8)}
        
        return analysis
    
    def show_survey_analysis(self, responses: List[Dict[str, Any]]) -> None:
        """설문조사 분석 결과를 콘솔에 표시합니다."""
        analysis = self.analyze_survey_results(responses)
        
        if not analysis:
            self.console.print("[yellow]⚠ 분석할 결과가 없습니다.[/yellow]")
            return
        
        self.console.print("\n[bold cyan]═══ 설문조사 결과 분석 ═══[/bold cyan]\n")
        
        # 기본 정보
        info_table = Table(box=box.ROUNDED)
        info_table.add_column("항목", style="cyan")
        info_table.add_column("값", style="green")
        
        info_table.add_row("총 응답 수", str(analysis['total_responses']))
        info_table.add_row("응답자 수", str(analysis['unique_personas']))
        info_table.add_row("질문 수", str(analysis['unique_questions']))
        
        self.console.print(info_table)
        self.console.print()
        
        # 질문별 통계
        stats_table = Table(title="질문별 통계", box=box.ROUNDED)
        stats_table.add_column("질문 ID", style="cyan")
        stats_table.add_column("평균", style="green", justify="right")
        stats_table.add_column("범위", style="yellow", justify="center")
        stats_table.add_column("응답 수", style="blue", justify="right")
        
        for qid, data in analysis['questions'].items():
            if 'mean' in data:
                stats_table.add_row(
                    qid,
                    f"{data['mean']:.2f}",
                    f"{data['min']} ~ {data['max']}",
                    str(data['count'])
                )
        
        self.console.print(stats_table)
        self.console.print()
    
    def export_to_excel(
        self,
        survey_responses: Optional[List[Dict[str, Any]]] = None,
        interviews: Optional[List[Dict[str, Any]]] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        결과를 Excel 파일로 내보냅니다.
        
        Args:
            survey_responses: 설문조사 응답
            interviews: 인터뷰 결과
            filename: 파일명
        
        Returns:
            저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results_{timestamp}.xlsx"
        
        filepath = self.output_dir / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # 설문조사 결과
            if survey_responses:
                rows = []
                for resp in survey_responses:
                    row = {
                        'persona_id': resp.get('persona_id'),
                        'question_id': resp.get('question_id'),
                        'question': resp.get('question'),
                        'score': resp.get('score'),
                        'reasoning': resp.get('reasoning'),
                        'category': resp.get('category')
                    }
                    rows.append(row)
                
                df = pd.DataFrame(rows)
                df.to_excel(writer, sheet_name='Survey', index=False)
            
            # 인터뷰 결과
            if interviews:
                rows = []
                for interview in interviews:
                    persona_id = interview['persona_id']
                    
                    for resp in interview.get('responses', []):
                        row = {
                            'persona_id': persona_id,
                            'question_id': resp.get('question_id'),
                            'question': resp.get('question'),
                            'response': resp.get('response'),
                            'category': resp.get('category')
                        }
                        rows.append(row)
                
                df = pd.DataFrame(rows)
                df.to_excel(writer, sheet_name='Interview', index=False)
        
        self.console.print(f"[green]✓ Excel 파일 저장됨: {filepath}[/green]")
        return str(filepath)


if __name__ == "__main__":
    # 테스트 코드
    manager = ResultsManager()
    
    # 테스트 데이터
    test_survey = [
        {
            'persona_id': '1',
            'survey_title': 'Test Survey',
            'question_id': 'Q1',
            'question': 'Test question?',
            'score': 5,
            'reasoning': 'Test reasoning',
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    manager.show_survey_analysis(test_survey)


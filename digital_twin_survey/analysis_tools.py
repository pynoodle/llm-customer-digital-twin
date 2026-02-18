"""
결과 분석 및 시각화 유틸리티
설문/인터뷰 결과를 분석하고 시각화하는 도구
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict
import json


class SurveyAnalyzer:
    """설문 결과 분석 클래스"""
    
    def __init__(self, csv_file: str):
        """
        Args:
            csv_file: 설문 결과 CSV 파일 경로
        """
        self.df = pd.read_csv(csv_file)
        self.response_cols = [col for col in self.df.columns 
                             if col.startswith('Q') and not col.endswith('_reasoning')]
        
        # 한글 폰트 설정 (시각화용)
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
    
    def basic_statistics(self) -> pd.DataFrame:
        """기본 통계량 계산"""
        stats = self.df[self.response_cols].describe()
        return stats
    
    def distribution_plot(self, save_path: str = None):
        """응답 분포 시각화"""
        n_questions = len(self.response_cols)
        fig, axes = plt.subplots(1, n_questions, figsize=(5*n_questions, 4))
        
        if n_questions == 1:
            axes = [axes]
        
        for idx, col in enumerate(self.response_cols):
            # 히스토그램
            axes[idx].hist(self.df[col].dropna(), bins=7, range=(0.5, 7.5), 
                          edgecolor='black', alpha=0.7)
            axes[idx].set_xlabel('Response Score')
            axes[idx].set_ylabel('Frequency')
            axes[idx].set_title(f'{col} Distribution')
            axes[idx].set_xticks(range(1, 8))
            axes[idx].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 분포 차트 저장: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def correlation_heatmap(self, save_path: str = None):
        """질문 간 상관관계 히트맵"""
        if len(self.response_cols) < 2:
            print("⚠️ 상관관계 분석을 위해서는 최소 2개 이상의 질문이 필요합니다.")
            return
        
        corr_matrix = self.df[self.response_cols].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        plt.title('Question Correlation Matrix', fontsize=14, pad=20)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 상관관계 차트 저장: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def response_patterns(self) -> Dict:
        """응답 패턴 분석"""
        patterns = {
            'high_scorers': [],  # 평균 6 이상
            'low_scorers': [],   # 평균 3 이하
            'neutral': [],       # 평균 3-6
            'consistent': [],    # 표준편차 < 1
            'variable': []       # 표준편차 >= 2
        }
        
        for idx, row in self.df.iterrows():
            scores = row[self.response_cols].dropna()
            mean_score = scores.mean()
            std_score = scores.std()
            
            pid = row.get('participant_id', f'P{idx}')
            
            if mean_score >= 6:
                patterns['high_scorers'].append(pid)
            elif mean_score <= 3:
                patterns['low_scorers'].append(pid)
            else:
                patterns['neutral'].append(pid)
            
            if std_score < 1:
                patterns['consistent'].append(pid)
            elif std_score >= 2:
                patterns['variable'].append(pid)
        
        return patterns
    
    def summary_report(self) -> str:
        """종합 리포트 생성"""
        report = []
        report.append("="*80)
        report.append("📊 설문 분석 리포트")
        report.append("="*80)
        report.append("")
        
        # 기본 정보
        report.append(f"응답자 수: {len(self.df)}명")
        report.append(f"질문 수: {len(self.response_cols)}개")
        report.append("")
        
        # 질문별 통계
        report.append("질문별 통계:")
        report.append("-"*80)
        for col in self.response_cols:
            data = self.df[col].dropna()
            report.append(f"\n{col}:")
            report.append(f"  평균: {data.mean():.2f}")
            report.append(f"  중앙값: {data.median():.1f}")
            report.append(f"  표준편차: {data.std():.2f}")
            report.append(f"  최빈값: {data.mode()[0] if len(data.mode()) > 0 else 'N/A'}")
            
            # 분포
            value_counts = data.value_counts().sort_index()
            report.append(f"  분포: {dict(value_counts)}")
        
        report.append("")
        
        # 응답 패턴
        patterns = self.response_patterns()
        report.append("응답 패턴:")
        report.append("-"*80)
        report.append(f"긍정적 응답자 (평균 ≥6): {len(patterns['high_scorers'])}명")
        report.append(f"부정적 응답자 (평균 ≤3): {len(patterns['low_scorers'])}명")
        report.append(f"일관적 응답자 (표준편차 <1): {len(patterns['consistent'])}명")
        report.append(f"변동적 응답자 (표준편차 ≥2): {len(patterns['variable'])}명")
        
        report.append("")
        report.append("="*80)
        
        return "\n".join(report)


class InterviewAnalyzer:
    """인터뷰 결과 분석 클래스"""
    
    def __init__(self, csv_file: str):
        """
        Args:
            csv_file: 인터뷰 결과 CSV 파일 경로
        """
        self.df = pd.read_csv(csv_file)
        self.response_cols = [col for col in self.df.columns 
                             if col.startswith('Q')]
    
    def word_frequency(self, question_col: str, top_n: int = 20) -> pd.DataFrame:
        """특정 질문의 단어 빈도 분석"""
        from collections import Counter
        import re
        
        # 모든 응답 합치기
        all_text = ' '.join(self.df[question_col].dropna().astype(str))
        
        # 단어 추출 (알파벳만)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        
        # 불용어 제거
        stop_words = set(['the', 'and', 'that', 'this', 'with', 'for', 'are', 'was', 
                         'but', 'not', 'you', 'all', 'can', 'her', 'has', 'had', 
                         'have', 'what', 'when', 'where', 'who', 'will', 'would'])
        
        words = [w for w in words if w not in stop_words]
        
        # 빈도 계산
        word_freq = Counter(words)
        
        # 데이터프레임으로 변환
        freq_df = pd.DataFrame(word_freq.most_common(top_n), 
                              columns=['Word', 'Frequency'])
        
        return freq_df
    
    def response_length_analysis(self) -> pd.DataFrame:
        """응답 길이 분석"""
        length_data = []
        
        for col in self.response_cols:
            lengths = self.df[col].dropna().apply(lambda x: len(str(x).split()))
            length_data.append({
                'Question': col,
                'Avg_Words': lengths.mean(),
                'Min_Words': lengths.min(),
                'Max_Words': lengths.max(),
                'Std_Words': lengths.std()
            })
        
        return pd.DataFrame(length_data)
    
    def sentiment_indicators(self) -> pd.DataFrame:
        """간단한 감성 지표 (긍정/부정 단어 빈도)"""
        positive_words = set(['good', 'great', 'excellent', 'love', 'enjoy', 'happy', 
                             'satisfied', 'amazing', 'wonderful', 'fantastic', 'positive'])
        negative_words = set(['bad', 'poor', 'terrible', 'hate', 'dislike', 'unhappy', 
                             'dissatisfied', 'awful', 'horrible', 'negative'])
        
        sentiment_data = []
        
        for col in self.response_cols:
            pos_count = 0
            neg_count = 0
            
            for response in self.df[col].dropna():
                words = response.lower().split()
                pos_count += sum(1 for w in words if w in positive_words)
                neg_count += sum(1 for w in words if w in negative_words)
            
            sentiment_data.append({
                'Question': col,
                'Positive_Words': pos_count,
                'Negative_Words': neg_count,
                'Sentiment_Ratio': pos_count / (neg_count + 1)  # 0으로 나누기 방지
            })
        
        return pd.DataFrame(sentiment_data)
    
    def summary_report(self) -> str:
        """종합 리포트 생성"""
        report = []
        report.append("="*80)
        report.append("🎤 인터뷰 분석 리포트")
        report.append("="*80)
        report.append("")
        
        # 기본 정보
        report.append(f"응답자 수: {len(self.df)}명")
        report.append(f"질문 수: {len(self.response_cols)}개")
        report.append("")
        
        # 응답 길이 분석
        length_df = self.response_length_analysis()
        report.append("응답 길이 분석:")
        report.append("-"*80)
        report.append(length_df.to_string(index=False))
        report.append("")
        
        # 감성 분석
        sentiment_df = self.sentiment_indicators()
        report.append("감성 지표:")
        report.append("-"*80)
        report.append(sentiment_df.to_string(index=False))
        report.append("")
        
        # 각 질문별 주요 단어
        report.append("질문별 주요 키워드 (Top 10):")
        report.append("-"*80)
        for col in self.response_cols:
            report.append(f"\n{col}:")
            freq_df = self.word_frequency(col, top_n=10)
            for _, row in freq_df.iterrows():
                report.append(f"  {row['Word']}: {row['Frequency']}회")
        
        report.append("")
        report.append("="*80)
        
        return "\n".join(report)


def analyze_survey_file(csv_file: str, output_prefix: str):
    """설문 결과 파일 분석 실행"""
    print(f"\n📊 설문 결과 분석: {csv_file}")
    print("="*80)
    
    analyzer = SurveyAnalyzer(csv_file)
    
    # 기본 통계
    print("\n기본 통계:")
    print(analyzer.basic_statistics())
    
    # 분포 차트
    analyzer.distribution_plot(f"{output_prefix}_distribution.png")
    
    # 상관관계 (질문이 2개 이상일 때)
    if len(analyzer.response_cols) >= 2:
        analyzer.correlation_heatmap(f"{output_prefix}_correlation.png")
    
    # 종합 리포트
    report = analyzer.summary_report()
    print("\n" + report)
    
    # 리포트 저장
    with open(f"{output_prefix}_report.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✅ 리포트 저장: {output_prefix}_report.txt")


def analyze_interview_file(csv_file: str, output_prefix: str):
    """인터뷰 결과 파일 분석 실행"""
    print(f"\n🎤 인터뷰 결과 분석: {csv_file}")
    print("="*80)
    
    analyzer = InterviewAnalyzer(csv_file)
    
    # 종합 리포트
    report = analyzer.summary_report()
    print("\n" + report)
    
    # 리포트 저장
    with open(f"{output_prefix}_report.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✅ 리포트 저장: {output_prefix}_report.txt")


def main():
    """메인 분석 함수"""
    print("="*80)
    print("📈 설문/인터뷰 결과 분석 도구")
    print("="*80)
    
    # 파일 선택
    print("\n분석할 파일 유형을 선택하세요:")
    print("1. 설문조사 결과 (Survey)")
    print("2. 인터뷰 결과 (Interview)")
    
    choice = input("\n선택 (1-2): ").strip()
    
    csv_file = input("CSV 파일 경로를 입력하세요: ").strip()
    output_prefix = input("출력 파일명 접두사 (기본값: analysis): ").strip() or "analysis"
    
    try:
        if choice == "1":
            analyze_survey_file(csv_file, output_prefix)
        elif choice == "2":
            analyze_interview_file(csv_file, output_prefix)
        else:
            print("❌ 잘못된 선택입니다.")
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {csv_file}")
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")


if __name__ == "__main__":
    main()

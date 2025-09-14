# KoACD: Korean Adolescent Cognitive Distortion Dataset

한국 청소년 인지왜곡 분석을 위한 최초의 대규모 데이터셋

[![Paper](https://img.shields.io/badge/Paper-arXiv-red.svg)](#)
[![Dataset](https://img.shields.io/badge/Dataset-108K-blue.svg)](#)
[![License](https://img.shields.io/badge/License-CC_BY_4.0-green.svg)](#)

## 개요

KoACD는 한국 청소년의 인지왜곡을 분석하기 위한 최초의 대규모 데이터셋입니다. 

- **108,717개** 인스턴스 포함
- **10가지** 인지왜곡 유형 균형 분포
- **Multi-LLM 협상** 프레임워크 활용
- **전문가 검증** 완료

## 데이터셋 구성

| 인지왜곡 유형 | 인지명료화 (%) | 인지균형화 | 총합 |
|-------------|---------------|----------|-----|
| 흑백사고 (All-or-Nothing Thinking) | 5,949 (10.50%) | 4,920 (9.46%) | 10,869 (10.00%) |
| 과잉일반화 (Overgeneralization) | 11,418 (20.14%) | 0 (0.00%) | 11,418 (10.50%) |
| 부정적 편향 (Mental Filtering) | 2,763 (4.88%) | 8,139 (15.64%) | 10,902 (10.03%) |
| 긍정 축소화 (Discounting the Positive) | 822 (1.45%) | 9,873 (18.98%) | 10,695 (9.84%) |
| 성급한 판단 (Jumping to Conclusions) | 10,479 (18.48%) | 183 (0.35%) | 10,662 (9.81%) |
| 확대와 축소 (Magnification and Minimization) | 6,078 (10.72%) | 4,836 (9.30%) | 10,914 (10.04%) |
| 감정적 추론 (Emotional Reasoning) | 10,842 (19.12%) | 0 (0.00%) | 10,842 (9.98%) |
| "해야한다" 진술 ("Should" Statements) | 2,697 (4.76%) | 7,998 (15.37%) | 10,695 (9.84%) |
| 낙인찍기 (Labeling) | 2,373 (4.19%) | 8,463 (16.27%) | 10,836 (9.97%) |
| 개인화 (Personalization) | 3,270 (5.77%) | 7,614 (14.63%) | 10,884 (10.01%) |
| **총합** | **56,691 (100.00%)** | **52,026 (100.00%)** | **108,717 (100.00%)** |

## 파일 구조

```
KoACD/
├── Cognitive_Balancing_Claude.xlsx    # Claude 3 Haiku 인지균형화 데이터
├── Cognitive_Balancing_Gemini.xlsx    # Gemini 1.5 Flash 인지균형화 데이터
├── Cognitive_Balancing_Gpt.xlsx       # GPT-4o mini 인지균형화 데이터
├── Cognitive_Clarification_Claude.xlsx # Claude 3 Haiku 인지명료화 데이터
├── Cognitive_Clarification_Gemini.xlsx # Gemini 1.5 Flash 인지명료화 데이터
├── Cognitive_Clarification_Gpt.xlsx   # GPT-4o mini 인지명료화 데이터
└── README.md
```

## 방법론

### Multi-LLM 협상 프레임워크

- **사용 모델**: Gemini 1.5 Flash, GPT-4o mini, Claude 3 Haiku
- **역할 교체**: Analyzer ↔ Evaluator 역할 번갈아 수행
- **협상 라운드**: 최대 5라운드까지 진행
- **편향 감소**: 다중 모델 관점으로 정확도 향상

### 합성 데이터 생성

1. **인지명료화 (Cognitive Clarification)**
   - 원본 텍스트의 의미 보존하며 명확하게 재작성
   - 56,691개 인스턴스 생성

2. **인지균형화 (Cognitive Balancing)**
   - 불균형한 인지왜곡 분포 해결
   - 52,026개 인스턴스 생성

## 평가 결과

### LLM vs 인간 평가 비교

| 평가 기준 | LLM 평가 | 인간 평가 |
|----------|----------|----------|
| 일관성 (Consistency) | 2.287 | 2.278 |
| 정확성 (Accuracy) | 2.582 | 2.558 |
| 유창성 (Fluency) | 2.598 | 2.815 |

### 검증 점수 분포

| 점수 | 개수 | 비율 |
|-----|-----|-----|
| 1점 | 11 | 0.06% |
| 2점 | 874 | 4.41% |
| 3점 | 18,897 | 95.53% |

## 인용

본 데이터셋을 사용하실 경우 다음과 같이 인용해 주세요:

```bibtex
@inproceedings{kim2025koacd,
  title={KoACD: The First Korean Adolescent Dataset for Cognitive Distortion Analysis},
  author={Kim, JunSeo and Kim, HyeHyeon},
  booktitle={Findings of the Association for Computational Linguistics: EMNLP 2025},
  year={2025},
  url={https://arxiv.org/abs/2505.00367}
}
```

## 연락처

- **김준서** (Junseo Kim) - kma80kjs@gachon.ac.kr
- **김혜현** (Hye Hyeon Kim) - hye_hyeon@yonsei.ac.kr

## 라이선스

이 데이터셋은 연구 목적으로만 사용 가능합니다. 상세한 라이선스 조건은 [LICENSE](LICENSE) 파일을 참조하세요.

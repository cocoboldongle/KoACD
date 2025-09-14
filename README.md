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

| 인지왜곡 유형 | 개수 | 비율 |
|-------------|-----|-----|
| 흑백사고 (All-or-Nothing Thinking) | 10,869 | 10.00% |
| 과잉일반화 (Overgeneralization) | 11,418 | 10.50% |
| 부정적 편향 (Mental Filtering) | 10,902 | 10.03% |
| 긍정 축소화 (Discounting the Positive) | 10,695 | 9.84% |
| 성급한 판단 (Jumping to Conclusions) | 10,662 | 9.81% |
| 확대와 축소 (Magnification and Minimization) | 10,914 | 10.04% |
| 감정적 추론 (Emotional Reasoning) | 10,842 | 9.98% |
| "해야한다" 진술 ("Should" Statements) | 10,695 | 9.84% |
| 낙인찍기 (Labeling) | 10,836 | 9.97% |
| 개인화 (Personalization) | 10,884 | 10.01% |
| **총합** | **108,717** | **100.00%** |

## 데이터 예시

```json
{
  "text": "시험 성적이 좋지 않은 내가 찐따일 거야.",
  "cognitive_distortion": "Labeling",
  "confidence_score": 3,
  "generation_method": "cognitive_clarification",
  "metadata": {
    "age_group": "16-17",
    "gender": "male",
    "validation_score": 3
  }
}
```

## 파일 구조

```
KoACD/
├── data/
│   ├── koacd_full_dataset.json      # 전체 데이터셋 (108,717개)
│   ├── koacd_train.json             # 훈련용 데이터
│   ├── koacd_valid.json             # 검증용 데이터
│   └── koacd_test.json              # 테스트용 데이터
├── evaluation/
│   ├── expert_evaluation.json      # 전문가 평가 결과
│   └── llm_evaluation.json         # LLM 평가 결과
└── README.md
```

## 데이터 사용법

### Python으로 데이터 로드

```python
import json
import pandas as pd

# 데이터 로드
with open('data/koacd_full_dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# DataFrame으로 변환
df = pd.DataFrame(data)

# 기본 통계
print(f"총 데이터 수: {len(df)}")
print(f"인지왜곡 유형 분포:\n{df['cognitive_distortion'].value_counts()}")
```

### 데이터 필터링

```python
# 특정 인지왜곡 유형만 추출
labeling_data = df[df['cognitive_distortion'] == 'Labeling']

# 높은 신뢰도 데이터만 추출
high_confidence_data = df[df['confidence_score'] == 3]

# 특정 생성 방법 데이터만 추출
clarification_data = df[df['generation_method'] == 'cognitive_clarification']
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

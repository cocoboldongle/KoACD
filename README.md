# KoACD: Korean Adolescent Cognitive Distortion Dataset

The first large-scale dataset for cognitive distortion analysis in Korean adolescents

[![Paper](https://img.shields.io/badge/Paper-EMNLP%202025-red.svg)](https://arxiv.org/abs/2505.00367)
[![Dataset](https://img.shields.io/badge/Dataset-108K-blue.svg)](#)
[![License](https://img.shields.io/badge/License-CC_BY_4.0-green.svg)](#)

## Overview

KoACD is the first large-scale dataset for cognitive distortion analysis in Korean adolescents.

- **108,717** instances included
- **10 types** of cognitive distortions with balanced distribution
- **Multi-LLM negotiation** framework utilized
- **Expert validation** completed

## Dataset Composition

| Cognitive Distortion Type | Cognitive Clarification (%) | Cognitive Balancing | Total |
|---------------------------|------------------------------|-------------------|-------|
| All-or-Nothing Thinking | 5,949 (10.50%) | 4,920 (9.46%) | 10,869 (10.00%) |
| Overgeneralization | 11,418 (20.14%) | 0 (0.00%) | 11,418 (10.50%) |
| Mental Filtering | 2,763 (4.88%) | 8,139 (15.64%) | 10,902 (10.03%) |
| Discounting the Positive | 822 (1.45%) | 9,873 (18.98%) | 10,695 (9.84%) |
| Jumping to Conclusions | 10,479 (18.48%) | 183 (0.35%) | 10,662 (9.81%) |
| Magnification and Minimization | 6,078 (10.72%) | 4,836 (9.30%) | 10,914 (10.04%) |
| Emotional Reasoning | 10,842 (19.12%) | 0 (0.00%) | 10,842 (9.98%) |
| "Should" Statements | 2,697 (4.76%) | 7,998 (15.37%) | 10,695 (9.84%) |
| Labeling | 2,373 (4.19%) | 8,463 (16.27%) | 10,836 (9.97%) |
| Personalization | 3,270 (5.77%) | 7,614 (14.63%) | 10,884 (10.01%) |
| **Total** | **56,691 (100.00%)** | **52,026 (100.00%)** | **108,717 (100.00%)** |

## File Structure

```
KoACD/
├── Cognitive_Balancing_Claude.xlsx    # Claude 3 Haiku cognitive balancing data
├── Cognitive_Balancing_Gemini.xlsx    # Gemini 1.5 Flash cognitive balancing data
├── Cognitive_Balancing_Gpt.xlsx       # GPT-4o mini cognitive balancing data
├── Cognitive_Clarification_Claude.xlsx # Claude 3 Haiku cognitive clarification data
├── Cognitive_Clarification_Gemini.xlsx # Gemini 1.5 Flash cognitive clarification data
├── Cognitive_Clarification_Gpt.xlsx   # GPT-4o mini cognitive clarification data
└── README.md
```

## Methodology

### Multi-LLM Negotiation Framework

- **Models Used**: Gemini 1.5 Flash, GPT-4o mini, Claude 3 Haiku
- **Role Switching**: Alternating between Analyzer ↔ Evaluator roles
- **Negotiation Rounds**: Up to 5 rounds conducted
- **Bias Reduction**: Improved accuracy through multi-model perspectives

### Synthetic Data Generation

1. **Cognitive Clarification**
   - Rephrasing original text clearly while preserving meaning
   - 56,691 instances generated

2. **Cognitive Balancing**
   - Addressing imbalanced cognitive distortion distribution
   - 52,026 instances generated

## Evaluation Results

### LLM vs Human Evaluation Comparison

| Evaluation Criteria | LLM Evaluation | Human Evaluation |
|-------------------|----------------|------------------|
| Consistency | 2.287 | 2.278 |
| Accuracy | 2.582 | 2.558 |
| Fluency | 2.598 | 2.815 |

### Validation Score Distribution

| Score | Count | Percentage |
|-------|-------|------------|
| 1 | 11 | 0.06% |
| 2 | 874 | 4.41% |
| 3 | 18,897 | 95.53% |

## Citation

If you use this dataset, please cite:

```bibtex
@inproceedings{kim2025koacd,
  title={KoACD: The First Korean Adolescent Dataset for Cognitive Distortion Analysis},
  author={Kim, JunSeo and Kim, HyeHyeon},
  booktitle={Findings of the Association for Computational Linguistics: EMNLP 2025},
  year={2025},
  url={https://arxiv.org/abs/2505.00367}
}
```

## Contact

- **JunSeo Kim** - kma80kjs@gachon.ac.kr
- **HyeHyeon Kim** - hye_hyeon@yonsei.ac.kr

## License

This dataset is available for research purposes only. Please refer to the [LICENSE](LICENSE) file for detailed license terms.

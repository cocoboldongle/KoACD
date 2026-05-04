"""
KoACD: Multi-LLM Negotiation for Cognitive Distortion Analysis
EMNLP Findings 2025

This script implements the role-switching multi-LLM negotiation framework
described in the paper. Gemini 1.5 Flash and GPT-4o mini alternate between
Analyzer and Evaluator roles across negotiation rounds to identify the most
appropriate cognitive distortion label for each adolescent utterance.

Usage:
    python negotiation.py --input data.xlsx --output_dir ./results

Requirements:
    pip install openai google-generativeai pandas openpyxl python-dotenv
"""

import os
import re
import argparse
import pandas as pd
import openai
import google.generativeai as genai
from dotenv import load_dotenv

# ── Load API keys from environment variables
load_dotenv()
client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# ── Cognitive distortion labels (Beck, 1979)
PATTERN_KEYWORDS = [
    "All-or-Nothing Thinking",
    "Overgeneralization",
    "Mental Filtering",
    "Discounting the Positive",
    "Jumping to Conclusions",
    "Magnification and Minimization",
    "Emotional Reasoning",
    "Should Statements",
    "Labeling",
    "Personalization",
    "Unknown",
]

# ── LLM hyperparameters
LLM_TEMPERATURE = 0.5
LLM_MAX_TOKENS  = 1024
LLM_TOP_P       = 0.9


# ─────────────────────────────────────────────────────────────────────────────
# Utility functions
# ─────────────────────────────────────────────────────────────────────────────

def normalize_pattern(pattern_text: str) -> str:
    """Strip markdown artifacts and map text to a canonical distortion label."""
    if not pattern_text:
        return "Unknown"

    # Remove markdown symbols (keep hyphens to preserve distortion names like "All-or-Nothing")
    pattern_text = re.sub(r"\*\*", "", pattern_text)
    pattern_text = re.sub(r"[\*\(\)_:]+", "", pattern_text)
    pattern_text = re.sub(r"\s+", " ", pattern_text).strip()

    for keyword in PATTERN_KEYWORDS:
        if keyword.lower() in pattern_text.lower():
            return keyword

    return "Unknown"


def load_prompt(file_path: str) -> str | None:
    """Load a prompt template from a text file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"[Prompt loaded] {file_path} ({len(content)} chars)")
        return content
    except Exception as e:
        print(f"[Error] Failed to load prompt: {e}")
        return None


def parse_model_response(content: str, previous_patterns: list[str] | None = None):
    """
    Parse a model response into (pattern, related_text, reason).
    Returns ("Unknown", "", reason) if the response indicates no distortion
    or if the pattern was already rejected in a previous round.
    """
    if previous_patterns is None:
        previous_patterns = []

    pattern      = "Unknown"
    related_text = ""
    reason       = ""

    if "Unknown" in content:
        return "Unknown", "", "No identifiable cognitive distortion"

    if "Cognitive Distortion:" in content:
        start = content.index("Cognitive Distortion:") + len("Cognitive Distortion:")
        end   = content.find("\n", start)
        if end == -1:
            end = content.find("Relevant Sentences", start)
        if end != -1:
            raw = content[start:end].strip()
            if any(prev in raw for prev in previous_patterns):
                print(f"[Duplicate pattern detected] '{raw}' was already rejected.")
                return "Unknown", "", "Rejected pattern reused"
            pattern = normalize_pattern(raw)

    if "Relevant Sentences/Paragraphs:" in content:
        start = content.index("Relevant Sentences/Paragraphs:") + len("Relevant Sentences/Paragraphs:")
        end   = content.find("Reason for Selection:", start)
        related_text = content[start: end if end != -1 else len(content)].strip()

    if "Reason for Selection:" in content:
        start  = content.index("Reason for Selection:") + len("Reason for Selection:")
        reason = content[start:].strip()

    return pattern, related_text, reason


def extract_analysis_parts(analysis: str):
    """Extract (pattern, related_text, reason) from a formatted analysis string."""
    pattern      = ""
    related_text = ""
    reason       = ""

    if "Cognitive Distortion:" in analysis:
        pattern = analysis.split("\n")[0].replace("Cognitive Distortion:", "").strip()

    if "Relevant Sentences/Paragraphs:" in analysis:
        related_text = (
            analysis.split("Relevant Sentences/Paragraphs:")[1]
                    .split("Reason for Selection:")[0]
                    .strip()
        )

    if "Reason for Selection:" in analysis:
        reason = analysis.split("Reason for Selection:")[1].strip()

    return pattern, related_text, reason


def is_new_pattern(pattern: str, previous_patterns: list[str]) -> bool:
    """Return True if pattern has not been rejected before."""
    return normalize_pattern(pattern) not in [normalize_pattern(p) for p in previous_patterns]


def _unknown_response(reason: str) -> str:
    return (
        f"Cognitive Distortion: Unknown\n"
        f"Relevant Sentences/Paragraphs: N/A\n"
        f"Reason for Selection: {reason}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Analyzer functions
# ─────────────────────────────────────────────────────────────────────────────

def _build_analyzer_prompt(
    input_text: str,
    previous_patterns: list[str],
    previous_reasons: list[str],
    template: str,
) -> str:
    patterns_fmt = "\n".join(f"- {p}" for p in previous_patterns) if previous_patterns else "None"
    reasons_fmt  = "\n".join(f"- {r}" for r in previous_reasons)  if previous_reasons  else "None"
    return template.format(
        input_text=input_text,
        previous_patterns=patterns_fmt,
        previous_reasons=reasons_fmt,
    )


def analyze_with_gemini(
    input_text: str,
    previous_patterns: list[str],
    previous_reasons: list[str],
    analyzer_template: str,
) -> str:
    """Gemini 1.5 Flash acts as the Analyzer."""
    print("\n[Analyzer] Gemini 1.5 Flash")
    try:
        prompt = _build_analyzer_prompt(input_text, previous_patterns, previous_reasons, analyzer_template)
        model  = genai.GenerativeModel("gemini-1.5-flash")
        resp   = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=LLM_TEMPERATURE,
                max_output_tokens=LLM_MAX_TOKENS,
                top_p=LLM_TOP_P,
            ),
        )
        result = resp.text.strip()
        print(f"  → {result[:120]}...")

        pattern, _, _ = parse_model_response(result, previous_patterns)
        if pattern in [normalize_pattern(p) for p in previous_patterns]:
            return _unknown_response("Rejected pattern reused by Gemini Analyzer")
        return result

    except Exception as e:
        print(f"[Error] Gemini Analyzer: {e}")
        return _unknown_response(f"Gemini Analyzer error: {e}")


def analyze_with_gpt(
    input_text: str,
    previous_patterns: list[str],
    previous_reasons: list[str],
    analyzer_template: str,
) -> str:
    """GPT-4o mini acts as the Analyzer."""
    print("\n[Analyzer] GPT-4o mini")
    try:
        prompt = _build_analyzer_prompt(input_text, previous_patterns, previous_reasons, analyzer_template)
        resp   = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            top_p=LLM_TOP_P,
        )
        result = resp.choices[0].message.content.strip()
        print(f"  → {result[:120]}...")

        pattern, _, _ = parse_model_response(result, previous_patterns)
        if pattern in [normalize_pattern(p) for p in previous_patterns]:
            return _unknown_response("Rejected pattern reused by GPT Analyzer")
        return result

    except Exception as e:
        print(f"[Error] GPT Analyzer: {e}")
        return _unknown_response(f"GPT Analyzer error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Evaluator functions
# ─────────────────────────────────────────────────────────────────────────────

def _build_evaluator_prompt(input_text: str, current_analysis: str, template: str) -> str:
    pattern, related_text, reason_text = extract_analysis_parts(current_analysis)
    return template.format(
        input_text=input_text,
        generated_pattern=pattern,
        related_text=related_text,
        reason_text=reason_text,
    )


def _parse_eval_response(response_text: str) -> dict:
    is_appropriate = (
        "The current analysis is valid" in response_text
        and "Inappropriate" not in response_text
    )
    reason = (
        response_text.split("Evaluation Reason:")[1].strip()
        if "Evaluation Reason:" in response_text
        else "No reason provided"
    )
    return {"is_appropriate": is_appropriate, "reason": reason, "full_response": response_text}


def evaluate_with_gemini(input_text: str, current_analysis: str, evaluator_template: str) -> dict:
    """Gemini 1.5 Flash acts as the Evaluator."""
    print("\n[Evaluator] Gemini 1.5 Flash")
    try:
        prompt = _build_evaluator_prompt(input_text, current_analysis, evaluator_template)
        model  = genai.GenerativeModel("gemini-1.5-flash")
        resp   = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=LLM_TEMPERATURE,
                max_output_tokens=LLM_MAX_TOKENS,
                top_p=LLM_TOP_P,
            ),
        )
        result = resp.text.strip()
        print(f"  → {result[:120]}...")
        return _parse_eval_response(result)

    except Exception as e:
        print(f"[Error] Gemini Evaluator: {e}")
        return {"is_appropriate": False, "reason": str(e), "full_response": ""}


def evaluate_with_gpt(input_text: str, current_analysis: str, evaluator_template: str) -> dict:
    """GPT-4o mini acts as the Evaluator."""
    print("\n[Evaluator] GPT-4o mini")
    try:
        prompt = _build_evaluator_prompt(input_text, current_analysis, evaluator_template)
        resp   = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            top_p=LLM_TOP_P,
        )
        result = resp.choices[0].message.content.strip()
        print(f"  → {result[:120]}...")
        return _parse_eval_response(result)

    except Exception as e:
        print(f"[Error] GPT Evaluator: {e}")
        return {"is_appropriate": False, "reason": str(e), "full_response": ""}


# ─────────────────────────────────────────────────────────────────────────────
# Role-switching helpers  (Figure 1 in the paper)
# ─────────────────────────────────────────────────────────────────────────────

def get_roles_for_round(round_num: int) -> dict:
    """
    Odd  rounds: Gemini = Analyzer, GPT    = Evaluator
    Even rounds: GPT    = Analyzer, Gemini = Evaluator
    """
    if round_num % 2 == 1:
        return {"analyzer": "gemini", "evaluator": "gpt"}
    return {"analyzer": "gpt", "evaluator": "gemini"}


def run_analyzer(role: str, input_text: str,
                 previous_patterns: list, previous_reasons: list,
                 analyzer_template: str) -> str:
    if role == "gemini":
        return analyze_with_gemini(input_text, previous_patterns, previous_reasons, analyzer_template)
    return analyze_with_gpt(input_text, previous_patterns, previous_reasons, analyzer_template)


def run_evaluator(role: str, input_text: str,
                  current_analysis: str, evaluator_template: str) -> dict:
    if role == "gemini":
        return evaluate_with_gemini(input_text, current_analysis, evaluator_template)
    return evaluate_with_gpt(input_text, current_analysis, evaluator_template)


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 – Initial analysis  (Round 1, T1: Gemini as Analyzer)
# ─────────────────────────────────────────────────────────────────────────────

def initial_analysis(df: pd.DataFrame, analyzer_prompt_path: str,
                     output_path: str) -> pd.DataFrame:
    """
    Gemini performs the first-pass analysis for every utterance.
    Results are saved to output_path and returned as a DataFrame.
    """
    print("\n" + "="*60)
    print("Stage 1: Initial Analysis  (Gemini Analyzer, Round 1 T1)")
    print("="*60)

    template = load_prompt(analyzer_prompt_path)
    if template is None:
        raise ValueError("Analyzer prompt could not be loaded.")

    # Remove placeholders used only in re-analysis rounds
    initial_template = (
        template
        .replace("{previous_patterns} were deemed inappropriate in the previous analysis."
                 " Do not select them again under any circumstances.\n\n", "")
        .replace("Previously rejected distortions: {previous_patterns}\n", "")
        .replace("Reason for rejection: {previous_reasons}\n\n", "")
        .replace(
            "[Important] Since {previous_patterns} were already deemed inappropriate:\n"
            "1. Do not select any of the above distortions again.\n"
            "2. Choose only from the remaining distortions.\n"
            "3. If none of the remaining distortions are appropriate, respond with \"Unknown\".\n\n",
            ""
        )
    )

    patterns, related_texts, reasons = [], [], []
    total = len(df)

    for idx, row in df.iterrows():
        sentence = row["utterance"]
        print(f"\n[{idx + 1}/{total}] Analyzing...")
        print(f"  Input: {str(sentence)[:100]}")

        if pd.isna(sentence):
            patterns.append("Unknown")
            related_texts.append("")
            reasons.append("Empty utterance")
            continue

        try:
            prompt = initial_template.replace("{input_text}", str(sentence))
            model  = genai.GenerativeModel("gemini-1.5-flash")
            resp   = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=LLM_TEMPERATURE,
                    max_output_tokens=LLM_MAX_TOKENS,
                    top_p=LLM_TOP_P,
                ),
            )
            content = resp.text.strip()
            pattern, related_text, reason = parse_model_response(content)

            patterns.append(pattern)
            related_texts.append(related_text)
            reasons.append(reason)
            print(f"  Pattern: {pattern}")

        except Exception as e:
            print(f"[Error] {e}")
            patterns.append("Error")
            related_texts.append("")
            reasons.append(str(e))

    df["initial_pattern"]      = patterns
    df["initial_related_text"] = related_texts
    df["initial_reason"]       = reasons

    df.to_excel(output_path, index=False)
    print(f"\n[Stage 1 complete] Saved to: {output_path}")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 – Negotiation  (Role-Switching, up to 5 rounds)
# ─────────────────────────────────────────────────────────────────────────────

def negotiation_analysis(df: pd.DataFrame, analyzer_prompt_path: str,
                         evaluator_prompt_path: str, output_path: str,
                         max_rounds: int = 5) -> pd.DataFrame:
    """
    Multi-round negotiation with role-switching between Gemini and GPT.

    Round structure (Figure 1 in the paper):
      T1 : Analyzer proposes a distortion  →  Evaluator judges
      T2 : Analyzer re-analyzes (if T1 rejected)  →  Evaluator re-judges
    Roles switch every round:
      Odd  rounds: Gemini = Analyzer, GPT    = Evaluator
      Even rounds: GPT    = Analyzer, Gemini = Evaluator
    """
    print("\n" + "="*60)
    print("Stage 2: Role-Switching Multi-LLM Negotiation")
    print("="*60)

    # load_prompt returns None when the file doesn't exist;
    # fall back to treating the path argument itself as the template string
    # so unit tests can inject a dummy string without needing real files.
    analyzer_template  = load_prompt(analyzer_prompt_path)  or analyzer_prompt_path  or ""
    evaluator_template = load_prompt(evaluator_prompt_path) or evaluator_prompt_path or ""

    final_patterns, final_texts, final_reasons = [], [], []
    history_all = []

    total = len(df)

    for idx, row in df.iterrows():
        sentence = row["utterance"]
        print(f"\n{'='*60}")
        print(f"[{idx + 1}/{total}] Negotiation start")
        print(f"  Input: {str(sentence)[:100]}")

        # ── Skip empty utterances
        if pd.isna(sentence):
            final_patterns.append("Unknown")
            final_texts.append("")
            final_reasons.append("Empty utterance")
            history_all.append([])
            continue

        # ── Initialise from Stage 1 result (Round 1 T1: Gemini Analyzer)
        current_analysis = (
            f"Cognitive Distortion: {row['initial_pattern']}\n"
            f"Relevant Sentences/Paragraphs: {row['initial_related_text']}\n"
            f"Reason for Selection: {row['initial_reason']}"
        )
        local_history = [f"Round1_T1 [Gemini Analyzer]: {current_analysis}"]

        previous_patterns: list[str] = []
        previous_reasons:  list[str] = []

        init_norm = normalize_pattern(row["initial_pattern"])
        if init_norm != "Unknown":
            previous_patterns.append(init_norm)

        final_analysis = current_analysis

        for round_num in range(1, max_rounds + 1):
            roles         = get_roles_for_round(round_num)
            analyzer_role = roles["analyzer"]
            evaluator_role= roles["evaluator"]

            print(f"\n--- Round {round_num} | "
                  f"Analyzer={analyzer_role.upper()} / Evaluator={evaluator_role.upper()} ---")

            # ── Round 2+: Analyzer re-analyzes at T1
            if round_num > 1:
                new_analysis = run_analyzer(
                    analyzer_role, str(sentence),
                    previous_patterns, previous_reasons,
                    analyzer_template,
                )
                local_history.append(
                    f"Round{round_num}_T1 [{analyzer_role.upper()} Analyzer]: {new_analysis}"
                )

                if "Unknown" in new_analysis:
                    final_analysis = new_analysis
                    break

                new_pattern = normalize_pattern(extract_analysis_parts(new_analysis)[0])
                if new_pattern in [normalize_pattern(p) for p in previous_patterns]:
                    print("  [Duplicate pattern] → Unknown")
                    final_analysis = _unknown_response("Duplicate pattern — no new distortion found")
                    local_history.append(f"Round{round_num}_T1 [Duplicate]: {final_analysis}")
                    break

                current_analysis = new_analysis

            # ── T1 Evaluation
            eval1 = run_evaluator(evaluator_role, str(sentence), current_analysis, evaluator_template)
            local_history.append(
                f"Round{round_num}_T1_Eval [{evaluator_role.upper()} Evaluator]: {eval1['full_response']}"
            )

            if eval1["is_appropriate"]:
                print(f"  [Appropriate at T1] → Accept and terminate")
                final_analysis = current_analysis
                break

            # Rejected: record pattern + reason
            cur_p = normalize_pattern(extract_analysis_parts(current_analysis)[0])
            if cur_p != "Unknown" and cur_p not in previous_patterns:
                previous_patterns.append(cur_p)
                previous_reasons.append(eval1["reason"])

            # ── T2 Re-analysis (same round, same roles)
            new_analysis2 = run_analyzer(
                analyzer_role, str(sentence),
                previous_patterns, previous_reasons,
                analyzer_template,
            )
            local_history.append(
                f"Round{round_num}_T2 [{analyzer_role.upper()} Analyzer]: {new_analysis2}"
            )

            if "Unknown" in new_analysis2:
                final_analysis = new_analysis2
                break

            new_pattern2 = normalize_pattern(extract_analysis_parts(new_analysis2)[0])
            if new_pattern2 in [normalize_pattern(p) for p in previous_patterns]:
                print("  [Duplicate pattern at T2] → Unknown")
                final_analysis = _unknown_response("Duplicate pattern at T2 — no new distortion found")
                local_history.append(f"Round{round_num}_T2 [Duplicate]: {final_analysis}")
                break

            current_analysis = new_analysis2

            # ── T2 Evaluation
            eval2 = run_evaluator(evaluator_role, str(sentence), current_analysis, evaluator_template)
            local_history.append(
                f"Round{round_num}_T2_Eval [{evaluator_role.upper()} Evaluator]: {eval2['full_response']}"
            )

            if eval2["is_appropriate"]:
                print(f"  [Appropriate at T2] → Accept and terminate")
                final_analysis = current_analysis
                break

            # Rejected at T2: record
            cur_p2 = normalize_pattern(extract_analysis_parts(current_analysis)[0])
            if cur_p2 != "Unknown" and cur_p2 not in previous_patterns:
                previous_patterns.append(cur_p2)
                previous_reasons.append(eval2["reason"])

            # Max rounds reached
            if round_num == max_rounds:
                print(f"  [Max rounds ({max_rounds}) reached] → Unknown")
                final_analysis = _unknown_response(
                    f"No consensus after {max_rounds} rounds"
                )
                local_history.append(f"Round{round_num} [Max rounds]: {final_analysis}")

        # ── Store final result
        fp, ft, fr = extract_analysis_parts(final_analysis)
        final_patterns.append(fp)
        final_texts.append(ft)
        final_reasons.append(fr)
        history_all.append(local_history)

    # ── Write results to DataFrame
    df["final_pattern"]      = final_patterns
    df["final_related_text"] = final_texts
    df["final_reason"]       = final_reasons

    # Initial analysis columns (from Stage 1, already in df)
    # Negotiation history columns (one column per step)
    max_steps = max_rounds * 4
    for step_idx in range(max_steps):
        col = f"negotiation_history_step{step_idx + 1}"
        df[col] = [
            (h[step_idx] if h and step_idx < len(h) else "")
            for h in history_all
        ]

    df.to_excel(output_path, index=False)
    print(f"\n[Stage 2 complete] Saved to: {output_path}")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="KoACD: Multi-LLM Negotiation for Cognitive Distortion Analysis"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to the input Excel file (.xlsx). "
             "Must contain a column named 'utterance'."
    )
    parser.add_argument(
        "--output_dir", default="./results",
        help="Directory where intermediate and final results are saved. "
             "(default: ./results)"
    )
    parser.add_argument(
        "--analyzer_prompt", default="./prompts/analyzer_prompt.txt",
        help="Path to the Analyzer prompt template. (default: ./prompts/analyzer_prompt.txt)"
    )
    parser.add_argument(
        "--evaluator_prompt", default="./prompts/evaluator_prompt.txt",
        help="Path to the Evaluator prompt template. (default: ./prompts/evaluator_prompt.txt)"
    )
    parser.add_argument(
        "--max_rounds", type=int, default=5,
        help="Maximum number of negotiation rounds. (default: 5)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    intermediate_path = os.path.join(args.output_dir, "stage1_initial_analysis.xlsx")
    final_path        = os.path.join(args.output_dir, "stage2_negotiation_result.xlsx")

    print("="*60)
    print("KoACD Multi-LLM Negotiation")
    print("="*60)
    print(f"  Input file     : {args.input}")
    print(f"  Output dir     : {args.output_dir}")
    print(f"  Analyzer prompt: {args.analyzer_prompt}")
    print(f"  Evaluator prompt: {args.evaluator_prompt}")
    print(f"  Max rounds     : {args.max_rounds}")

    # Load data
    df = pd.read_excel(args.input)
    if "utterance" not in df.columns:
        raise KeyError("Input file must contain a column named 'utterance'.")
    print(f"\n  Loaded {len(df)} utterances.")

    # Stage 1
    df = initial_analysis(df, args.analyzer_prompt, intermediate_path)

    # Stage 2
    df = negotiation_analysis(
        df,
        analyzer_prompt_path=args.analyzer_prompt,
        evaluator_prompt_path=args.evaluator_prompt,
        output_path=final_path,
        max_rounds=args.max_rounds,
    )

    # Summary statistics
    total         = len(df)
    unknown_count = (df["final_pattern"] == "Unknown").sum()
    error_count   = (df["final_pattern"] == "Error").sum()
    found_count   = total - unknown_count - error_count

    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"  Total utterances : {total}")
    print(f"  Pattern found    : {found_count} ({found_count/total*100:.1f}%)")
    print(f"  Unknown          : {unknown_count} ({unknown_count/total*100:.1f}%)")
    print(f"  Error            : {error_count} ({error_count/total*100:.1f}%)")
    print(f"\n  Intermediate result : {intermediate_path}")
    print(f"  Final result        : {final_path}")
    print("="*60)


if __name__ == "__main__":
    main()
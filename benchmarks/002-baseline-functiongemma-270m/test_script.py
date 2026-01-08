#!/usr/bin/env python3
"""
Test FunctionGemma-270M base model on notification classification.
Uses FunctionGemma's function calling format with control tokens.
"""

import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"

import json
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer

# Configuration
BASE_MODEL = str(Path(__file__).parent.parent / "models" / "functiongemma-270m")
DATASET_PATH = Path(__file__).parent.parent / "training_data.jsonl"
SAMPLE_SIZE = 100

def escape_str(s: str) -> str:
    """Wrap string in <escape> delimiters as required by FunctionGemma."""
    return f"<escape>{s}<escape>"

def build_function_declaration():
    """Build the classify_notification function declaration."""
    folders_desc = "Work: professional messages from Slack, Jira, Teams, email, Feishu, DingTalk. Personal: friends and family via WhatsApp, WeChat, Telegram, Douyin, RedNote. Promotions: marketing, deals, spam, shopping. Alerts: banking, security, system notifications, delivery updates"

    return (
        "declaration:classify_notification{"
        f"description:{escape_str('Classify notification into folder and priority. ' + folders_desc)},"
        "parameters:{"
        "properties:{"
        "folder:{"
        f"description:{escape_str('One of: Work, Personal, Promotions, Alerts')},"
        f"enum:[{escape_str('Work')},{escape_str('Personal')},{escape_str('Promotions')},{escape_str('Alerts')}],"
        f"type:{escape_str('STRING')}"
        "},"
        "priority:{"
        f"description:{escape_str('Priority 1-5. 1=ignore, 2=low, 3=normal, 4=important, 5=urgent')},"
        f"enum:[{escape_str('1')},{escape_str('2')},{escape_str('3')},{escape_str('4')},{escape_str('5')}],"
        f"type:{escape_str('STRING')}"
        "}"
        "},"
        f"required:[{escape_str('folder')},{escape_str('priority')}],"
        f"type:{escape_str('OBJECT')}"
        "}"
        "}"
    )

def build_prompt(app_name, title, body):
    """Build FunctionGemma prompt."""
    func_decl = build_function_declaration()

    return (
        "<start_of_turn>developer\n"
        "You are a model that can do function calling with the following functions"
        f"<start_function_declaration>{func_decl}<end_function_declaration>\n"
        "<end_of_turn>\n"
        "<start_of_turn>user\n"
        f"App: {app_name}\n"
        f"Title: {title}\n"
        f"Body: {body}\n"
        "<end_of_turn>\n"
        "<start_of_turn>model\n"
    )

def parse_response(text):
    """Extract folder and priority from FunctionGemma response."""
    # FunctionGemma outputs: <start_function_call>classify_notification{folder:<escape>...<escape>,priority:<escape>...<escape>}<end_function_call>
    try:
        # Find function call block
        if "<start_function_call>" not in text:
            return None, None

        start = text.find("<start_function_call>")
        end = text.find("<end_function_call>")
        if start < 0 or end < 0:
            return None, None

        call_text = text[start:end]

        # Extract folder
        folder = None
        if "folder:" in call_text:
            folder_start = call_text.find("folder:") + 7
            folder_end = call_text.find(",", folder_start)
            if folder_end < 0:
                folder_end = call_text.find("}", folder_start)
            folder_text = call_text[folder_start:folder_end]
            # Remove <escape> tags
            folder = folder_text.replace("<escape>", "").strip()

        # Extract priority
        priority = None
        if "priority:" in call_text:
            priority_start = call_text.find("priority:") + 9
            priority_end = call_text.find("}", priority_start)
            priority_text = call_text[priority_start:priority_end]
            # Remove <escape> tags
            priority_str = priority_text.replace("<escape>", "").strip()
            try:
                priority = int(priority_str)
            except:
                pass

        return folder, priority
    except:
        return None, None

def main():
    print("="*70)
    print("BASELINE TEST: FunctionGemma-270M Base Model (NO FINE-TUNING)")
    print("="*70)
    print()

    # Load model
    print(f"Loading model: {BASE_MODEL}")
    print("Loading...")
    print()

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )
    model.eval()

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    print(f"Model loaded on: {model.device}")
    print(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
    print()

    # Load dataset
    print(f"Loading {SAMPLE_SIZE} examples from {DATASET_PATH}...")
    examples = []
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= SAMPLE_SIZE:
                break
            examples.append(json.loads(line))

    print(f"Loaded {len(examples)} examples")
    print()
    print("="*70)
    print("RUNNING INFERENCE")
    print("="*70)
    print()

    # Test
    correct_folder = 0
    correct_priority = 0
    parse_failures = 0
    errors = []

    for i, example in enumerate(examples, 1):
        notif = example["notification"]
        expected = example["classification"]

        # Build prompt
        prompt = build_prompt(
            notif["app_display_name"],
            notif["title"],
            notif["body"]
        )

        # Generate
        inputs = tokenizer([prompt], return_tensors="pt", padding=True)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        response = tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=False  # Keep control tokens for parsing
        )

        # Parse
        predicted_folder, predicted_priority = parse_response(response)

        if not predicted_folder:
            parse_failures += 1
            errors.append({
                "example": i,
                "app": notif["app_display_name"],
                "title": notif["title"][:50],
                "expected": expected,
                "output": response[:100],
                "error": "Parse failure"
            })
        else:
            if predicted_folder == expected["folder"]:
                correct_folder += 1
            else:
                errors.append({
                    "example": i,
                    "app": notif["app_display_name"],
                    "title": notif["title"][:50],
                    "expected_folder": expected["folder"],
                    "predicted_folder": predicted_folder
                })

            if predicted_priority == expected["priority"]:
                correct_priority += 1

        # Progress
        if i % 10 == 0:
            print(f"Progress: {i}/{len(examples)} ({i/len(examples)*100:.0f}%)")

    # Results
    total = len(examples)
    print()
    print("="*70)
    print("RESULTS")
    print("="*70)
    print()
    print(f"Total examples:     {total}")
    print(f"Folder accuracy:    {correct_folder}/{total} ({correct_folder/total*100:.1f}%)")
    print(f"Priority accuracy:  {correct_priority}/{total} ({correct_priority/total*100:.1f}%)")
    print(f"Parse failures:     {parse_failures}/{total} ({parse_failures/total*100:.1f}%)")
    print()

    # Show sample errors
    if errors:
        print("Sample Errors (first 10):")
        print("-"*70)
        for err in errors[:10]:
            try:
                if "error" in err:
                    print(f"\n[{err['example']}] {err['app']} - {err['title']}")
                    print(f"  Error: {err['error']}")
                    print(f"  Output: {err['output']}")
                else:
                    print(f"\n[{err['example']}] {err['app']} - {err['title']}")
                    print(f"  Expected: {err['expected_folder']}")
                    print(f"  Predicted: {err['predicted_folder']}")
            except UnicodeEncodeError:
                print(f"\n[{err['example']}] (Unicode error in output)")
                continue

    print()
    print("="*70)
    print("CONCLUSION")
    print("="*70)
    print()

    if correct_folder / total >= 0.80:
        print("[OK] Base model achieves >80% folder accuracy!")
        print("     Phase 1 baseline is viable without fine-tuning.")
    else:
        print("[NEEDS WORK] Base model accuracy below 80%")
        print("             Consider fine-tuning or better prompting")

    if parse_failures / total > 0.10:
        print()
        print("[WARNING] High parse failure rate (>10%)")
        print("          FunctionGemma format may need adjustments")
    else:
        print()
        print("[OK] Low parse failure rate (<10%)")
        print("     Model generates valid function calls consistently")

    print()
    print("="*70)

    # Save results
    results = {
        "model": BASE_MODEL,
        "total": total,
        "folder_accuracy": correct_folder / total,
        "priority_accuracy": correct_priority / total,
        "parse_failure_rate": parse_failures / total,
        "errors": errors[:20]
    }

    output_path = Path(__file__).parent.parent / "functiongemma_baseline_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")

if __name__ == "__main__":
    main()

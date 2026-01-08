#!/usr/bin/env python3
"""
Fine-tune FunctionGemma-270M on notification classification.
Uses official format with apply_chat_template and tools parameter.
"""

import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"

import json
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForSeq2Seq
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import BitsAndBytesConfig

# Configuration
BASE_MODEL = str(Path(__file__).parent.parent / "models" / "functiongemma-270m")
TRAIN_FILE = Path(__file__).parent.parent / "functiongemma_train.jsonl"
OUTPUT_DIR = Path(__file__).parent.parent / "functiongemma-finetuned-notif"

# Tool definition
def classify_notification(app_name: str, title: str, body: str, folder: str = None, priority: int = None):
    """
    Classify a notification into a folder and priority level.

    Args:
        app_name: The name of the app that sent the notification
        title: The notification title
        body: The notification body/content
        folder: One of: Work, Personal, Promotions, Alerts
        priority: Priority level from 1 (ignore) to 5 (urgent)

    Returns:
        A dictionary with folder and priority
    """
    return {"folder": folder, "priority": priority}

TOOLS = [classify_notification]

def load_dataset_from_jsonl(file_path):
    """Load dataset from JSONL."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return Dataset.from_list(data)

def format_dataset(example, tokenizer):
    """Format example using apply_chat_template with tools."""
    messages = example["messages"]

    # Apply chat template with tools - get text first
    text = tokenizer.apply_chat_template(
        messages,
        tools=TOOLS,
        tokenize=False,
        add_generation_prompt=False  # False because we include model response in messages
    )

    # Now tokenize
    encoded = tokenizer(
        text,
        truncation=True,
        max_length=2048,
        padding=False,  # Will pad in data collator
        return_tensors=None
    )

    # Add labels (same as input_ids for causal LM)
    encoded["labels"] = encoded["input_ids"].copy()

    return encoded

def main():
    print("="*70)
    print("FUNCTIONGEMMA FINE-TUNING")
    print("="*70)
    print()

    # Load tokenizer and model
    print(f"Loading model from {BASE_MODEL}...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    # 4-bit quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )

    # Prepare for k-bit training
    model = prepare_model_for_kbit_training(model)

    # LoRA config
    lora_config = LoraConfig(
        r=16,
        lora_alpha=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Load and format dataset
    print(f"\nLoading dataset from {TRAIN_FILE}...")
    dataset = load_dataset_from_jsonl(TRAIN_FILE)
    print(f"Loaded {len(dataset)} examples")

    print("\nFormatting dataset with apply_chat_template...")
    dataset = dataset.map(
        lambda x: format_dataset(x, tokenizer),
        remove_columns=dataset.column_names
    )

    print(f"\nDataset formatted. Sample length: {len(dataset[0]['input_ids'])} tokens")
    print()

    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        logging_steps=50,
        save_strategy="epoch",
        bf16=True,
        optim="adamw_8bit",
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        report_to="none",
    )

    # Data collator for padding - handles labels properly
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
        pad_to_multiple_of=8,
        label_pad_token_id=-100  # Ignore padding tokens in loss
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    print("="*70)
    print("STARTING TRAINING")
    print("="*70)
    print()

    # Train
    trainer.train()

    # Save
    print("\nSaving model...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print()
    print("="*70)
    print("✓ TRAINING COMPLETE")
    print("="*70)
    print(f"Model saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

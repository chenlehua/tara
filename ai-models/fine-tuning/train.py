#!/usr/bin/env python3
"""Fine-tuning script for TARA models."""
import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq,
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, TaskType


def load_config(config_path: str) -> Dict[str, Any]:
    """Load training configuration."""
    with open(config_path) as f:
        return json.load(f)


def prepare_model_and_tokenizer(model_name: str, use_lora: bool = True):
    """Load and prepare model for fine-tuning."""
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
        padding_side="right",
    )
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    
    # Apply LoRA if specified
    if use_lora:
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=16,
            lora_alpha=32,
            lora_dropout=0.05,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        )
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
    
    return model, tokenizer


def format_messages(example: Dict, tokenizer) -> Dict:
    """Format messages for training."""
    messages = example.get("messages", [])
    
    # Convert to chat format
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )
    
    # Tokenize
    result = tokenizer(
        text,
        truncation=True,
        max_length=2048,
        padding=False,
    )
    
    result["labels"] = result["input_ids"].copy()
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Fine-tune TARA model")
    parser.add_argument(
        "--config",
        default="configs/finetune_config.json",
        help="Training configuration file",
    )
    parser.add_argument(
        "--model",
        default="Qwen/Qwen2.5-7B-Instruct",
        help="Base model name",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Training data directory",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for checkpoints",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Batch size per device",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=2e-5,
        help="Learning rate",
    )
    parser.add_argument(
        "--no-lora",
        action="store_true",
        help="Disable LoRA fine-tuning",
    )
    args = parser.parse_args()
    
    # Load model and tokenizer
    print(f"Loading model: {args.model}")
    model, tokenizer = prepare_model_and_tokenizer(
        args.model,
        use_lora=not args.no_lora,
    )
    
    # Load dataset
    print(f"Loading dataset from: {args.data_dir}")
    dataset = load_dataset(
        "json",
        data_files={
            "train": f"{args.data_dir}/train.jsonl",
            "validation": f"{args.data_dir}/val.jsonl",
        },
    )
    
    # Preprocess dataset
    def preprocess_function(examples):
        return format_messages(examples, tokenizer)
    
    tokenized_dataset = dataset.map(
        preprocess_function,
        remove_columns=dataset["train"].column_names,
    )
    
    # Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=4,
        learning_rate=args.learning_rate,
        weight_decay=0.01,
        warmup_ratio=0.1,
        logging_steps=10,
        save_steps=100,
        eval_steps=100,
        evaluation_strategy="steps",
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        bf16=True,
        report_to="tensorboard",
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["validation"],
        data_collator=data_collator,
    )
    
    # Train
    print("Starting training...")
    trainer.train()
    
    # Save final model
    print(f"Saving model to: {args.output_dir}/final")
    trainer.save_model(f"{args.output_dir}/final")
    tokenizer.save_pretrained(f"{args.output_dir}/final")
    
    print("Training complete!")


if __name__ == "__main__":
    main()

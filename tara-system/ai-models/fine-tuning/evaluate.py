#!/usr/bin/env python3
"""Evaluate fine-tuned TARA models."""
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm


def load_model(model_path: str):
    """Load fine-tuned model."""
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True,
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    
    return model, tokenizer


def load_test_data(path: str) -> List[Dict]:
    """Load test dataset."""
    examples = []
    with open(path) as f:
        for line in f:
            examples.append(json.loads(line))
    return examples


def generate_response(
    model,
    tokenizer,
    messages: List[Dict],
    max_new_tokens: int = 1024,
) -> str:
    """Generate model response."""
    # Remove assistant message for generation
    input_messages = [m for m in messages if m["role"] != "assistant"]
    
    text = tokenizer.apply_chat_template(
        input_messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
        )
    
    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )
    
    return response


def evaluate_json_accuracy(predicted: str, expected: str) -> Dict[str, float]:
    """Evaluate JSON output accuracy."""
    try:
        pred_json = json.loads(predicted)
        exp_json = json.loads(expected)
        
        # Check structure match
        def compare_structure(p, e):
            if type(p) != type(e):
                return 0.0
            if isinstance(p, dict):
                if not e:
                    return 1.0 if not p else 0.0
                common_keys = set(p.keys()) & set(e.keys())
                if not common_keys:
                    return 0.0
                return sum(compare_structure(p.get(k), e.get(k)) for k in common_keys) / len(e)
            elif isinstance(p, list):
                if not e:
                    return 1.0 if not p else 0.0
                return min(len(p), len(e)) / len(e)
            else:
                return 1.0 if p == e else 0.0
        
        structure_score = compare_structure(pred_json, exp_json)
        
        return {
            "valid_json": 1.0,
            "structure_score": structure_score,
        }
    except json.JSONDecodeError:
        return {
            "valid_json": 0.0,
            "structure_score": 0.0,
        }


def evaluate_threat_quality(predicted: str) -> Dict[str, float]:
    """Evaluate threat analysis quality."""
    try:
        pred = json.loads(predicted)
        threats = pred.get("threats", [])
        
        scores = {
            "has_threats": 1.0 if threats else 0.0,
            "avg_fields": 0.0,
        }
        
        required_fields = ["threat_name", "threat_type", "description"]
        
        if threats:
            field_counts = []
            for threat in threats:
                count = sum(1 for f in required_fields if f in threat)
                field_counts.append(count / len(required_fields))
            scores["avg_fields"] = sum(field_counts) / len(field_counts)
        
        return scores
    except:
        return {"has_threats": 0.0, "avg_fields": 0.0}


def main():
    parser = argparse.ArgumentParser(description="Evaluate fine-tuned model")
    parser.add_argument(
        "--model",
        required=True,
        help="Path to fine-tuned model",
    )
    parser.add_argument(
        "--test-data",
        default="data/test.jsonl",
        help="Test data path",
    )
    parser.add_argument(
        "--output",
        default="evaluation_results.json",
        help="Output file for results",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=100,
        help="Maximum samples to evaluate",
    )
    args = parser.parse_args()
    
    # Load model
    print(f"Loading model from: {args.model}")
    model, tokenizer = load_model(args.model)
    
    # Load test data
    print(f"Loading test data from: {args.test_data}")
    test_data = load_test_data(args.test_data)[:args.max_samples]
    
    # Evaluate
    results = []
    metrics = {
        "valid_json": [],
        "structure_score": [],
        "has_threats": [],
        "avg_fields": [],
    }
    
    print("Evaluating...")
    for example in tqdm(test_data):
        messages = example["messages"]
        expected = messages[-1]["content"]
        
        # Generate response
        predicted = generate_response(model, tokenizer, messages)
        
        # Evaluate
        json_scores = evaluate_json_accuracy(predicted, expected)
        threat_scores = evaluate_threat_quality(predicted)
        
        result = {
            "input": messages[:-1],
            "expected": expected,
            "predicted": predicted,
            "scores": {**json_scores, **threat_scores},
        }
        results.append(result)
        
        for key in metrics:
            if key in result["scores"]:
                metrics[key].append(result["scores"][key])
    
    # Calculate averages
    avg_metrics = {
        key: sum(values) / len(values) if values else 0.0
        for key, values in metrics.items()
    }
    
    # Print results
    print("\n=== Evaluation Results ===")
    print(f"Samples evaluated: {len(test_data)}")
    for key, value in avg_metrics.items():
        print(f"  {key}: {value:.4f}")
    
    # Save results
    output = {
        "metrics": avg_metrics,
        "samples": len(test_data),
        "results": results,
    }
    
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {args.output}")


if __name__ == "__main__":
    main()

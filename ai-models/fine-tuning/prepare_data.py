#!/usr/bin/env python3
"""Prepare training data for fine-tuning TARA models."""
import argparse
import json
import random
from pathlib import Path
from typing import List, Dict, Any


def load_threat_library(path: str) -> List[Dict]:
    """Load threat library data."""
    with open(path) as f:
        data = json.load(f)
    return data.get("threats", [])


def load_control_library(path: str) -> List[Dict]:
    """Load control library data."""
    with open(path) as f:
        data = json.load(f)
    return data.get("controls", [])


def generate_stride_training_examples(threats: List[Dict]) -> List[Dict]:
    """Generate training examples for STRIDE analysis."""
    examples = []
    
    for threat in threats:
        # Create asset context
        asset_context = {
            "name": random.choice(threat.get("target_assets", ["ECU"])),
            "type": "ecu",
            "interfaces": ["CAN"],
        }
        
        # Create training example
        example = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an automotive cybersecurity expert performing STRIDE analysis."
                },
                {
                    "role": "user",
                    "content": f"Identify {threat['stride_type']} threats for asset: {json.dumps(asset_context)}"
                },
                {
                    "role": "assistant",
                    "content": json.dumps({
                        "threats": [{
                            "threat_name": threat["name"],
                            "threat_type": threat["stride_type"],
                            "description": threat["description"],
                            "attack_vector": threat.get("attack_vector", "network"),
                            "impact": threat.get("impact", {}),
                        }]
                    })
                }
            ]
        }
        examples.append(example)
    
    return examples


def generate_control_training_examples(controls: List[Dict]) -> List[Dict]:
    """Generate training examples for control recommendations."""
    examples = []
    
    for control in controls:
        # Create threat context
        threat_context = {
            "threat_type": random.choice(control.get("applicable_threats", ["Tampering"])),
            "asset_type": random.choice(control.get("applicable_assets", ["ecu"])),
        }
        
        example = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an automotive cybersecurity expert recommending control measures."
                },
                {
                    "role": "user",
                    "content": f"Recommend controls for: {json.dumps(threat_context)}"
                },
                {
                    "role": "assistant",
                    "content": json.dumps({
                        "controls": [{
                            "name": control["name"],
                            "description": control["description"],
                            "type": control["control_type"],
                            "category": control["category"],
                            "effectiveness": control["effectiveness"],
                        }]
                    })
                }
            ]
        }
        examples.append(example)
    
    return examples


def split_dataset(
    examples: List[Dict],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
) -> tuple:
    """Split dataset into train/val/test."""
    random.shuffle(examples)
    
    n = len(examples)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    return (
        examples[:train_end],
        examples[train_end:val_end],
        examples[val_end:],
    )


def save_jsonl(examples: List[Dict], path: str):
    """Save examples to JSONL format."""
    with open(path, "w") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Prepare fine-tuning data")
    parser.add_argument(
        "--knowledge-base",
        default="../../backend/knowledge-service/data",
        help="Path to knowledge base directory",
    )
    parser.add_argument(
        "--output-dir",
        default="./data",
        help="Output directory for training data",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="Training set ratio",
    )
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load knowledge base
    kb_path = Path(args.knowledge_base)
    
    all_examples = []
    
    # Load and process threat library
    threat_path = kb_path / "threat_library" / "automotive_threats.json"
    if threat_path.exists():
        threats = load_threat_library(str(threat_path))
        examples = generate_stride_training_examples(threats)
        all_examples.extend(examples)
        print(f"Generated {len(examples)} STRIDE examples")
    
    # Load and process control library
    control_path = kb_path / "control_library" / "automotive_controls.json"
    if control_path.exists():
        controls = load_control_library(str(control_path))
        examples = generate_control_training_examples(controls)
        all_examples.extend(examples)
        print(f"Generated {len(examples)} control examples")
    
    # Split dataset
    train, val, test = split_dataset(all_examples, args.train_ratio)
    
    # Save datasets
    save_jsonl(train, str(output_dir / "train.jsonl"))
    save_jsonl(val, str(output_dir / "val.jsonl"))
    save_jsonl(test, str(output_dir / "test.jsonl"))
    
    print(f"\nDataset prepared:")
    print(f"  Training:   {len(train)} examples")
    print(f"  Validation: {len(val)} examples")
    print(f"  Test:       {len(test)} examples")
    print(f"\nSaved to: {output_dir}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate security keys and secrets for TARA System."""
import argparse
import secrets
import base64
import hashlib
from datetime import datetime, timedelta
from pathlib import Path


def generate_jwt_secret(length: int = 64) -> str:
    """Generate a secure JWT secret key."""
    return secrets.token_hex(length)


def generate_api_key(prefix: str = "tara") -> str:
    """Generate an API key with prefix."""
    key = secrets.token_urlsafe(32)
    return f"{prefix}_{key}"


def generate_password(length: int = 16) -> str:
    """Generate a secure random password."""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_encryption_key() -> str:
    """Generate a Fernet encryption key."""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()


def update_env_file(key_name: str, key_value: str, env_file: str = ".env"):
    """Update or add key to .env file."""
    env_path = Path(env_file)
    
    if not env_path.exists():
        print(f"Creating {env_file}")
        env_path.touch()
    
    lines = env_path.read_text().splitlines()
    found = False
    
    for i, line in enumerate(lines):
        if line.startswith(f"{key_name}="):
            lines[i] = f"{key_name}={key_value}"
            found = True
            break
    
    if not found:
        lines.append(f"{key_name}={key_value}")
    
    env_path.write_text("\n".join(lines) + "\n")
    print(f"✓ Updated {key_name} in {env_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate security keys for TARA System")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # JWT secret
    jwt_parser = subparsers.add_parser("jwt", help="Generate JWT secret")
    jwt_parser.add_argument("--length", type=int, default=64, help="Key length")
    jwt_parser.add_argument("--update-env", action="store_true", help="Update .env file")
    
    # API key
    api_parser = subparsers.add_parser("api-key", help="Generate API key")
    api_parser.add_argument("--prefix", default="tara", help="Key prefix")
    
    # Password
    pwd_parser = subparsers.add_parser("password", help="Generate password")
    pwd_parser.add_argument("--length", type=int, default=16, help="Password length")
    
    # Encryption key
    enc_parser = subparsers.add_parser("encryption", help="Generate encryption key")
    enc_parser.add_argument("--update-env", action="store_true", help="Update .env file")
    
    # Generate all
    all_parser = subparsers.add_parser("all", help="Generate all keys")
    all_parser.add_argument("--update-env", action="store_true", help="Update .env file")
    
    args = parser.parse_args()
    
    if args.command == "jwt":
        key = generate_jwt_secret(args.length)
        print(f"JWT Secret: {key}")
        if args.update_env:
            update_env_file("JWT_SECRET_KEY", key)
    
    elif args.command == "api-key":
        key = generate_api_key(args.prefix)
        print(f"API Key: {key}")
    
    elif args.command == "password":
        pwd = generate_password(args.length)
        print(f"Password: {pwd}")
    
    elif args.command == "encryption":
        key = generate_encryption_key()
        print(f"Encryption Key: {key}")
        if args.update_env:
            update_env_file("ENCRYPTION_KEY", key)
    
    elif args.command == "all":
        print("=== Generated Keys ===\n")
        
        jwt_key = generate_jwt_secret()
        print(f"JWT Secret: {jwt_key}")
        
        api_key = generate_api_key()
        print(f"API Key: {api_key}")
        
        mysql_pwd = generate_password()
        print(f"MySQL Password: {mysql_pwd}")
        
        redis_pwd = generate_password()
        print(f"Redis Password: {redis_pwd}")
        
        minio_key = generate_password()
        print(f"MinIO Secret Key: {minio_key}")
        
        enc_key = generate_encryption_key()
        print(f"Encryption Key: {enc_key}")
        
        if args.update_env:
            print("\nUpdating .env file...")
            update_env_file("JWT_SECRET_KEY", jwt_key)
            update_env_file("MYSQL_PASSWORD", mysql_pwd)
            update_env_file("REDIS_PASSWORD", redis_pwd)
            update_env_file("MINIO_SECRET_KEY", minio_key)
            update_env_file("ENCRYPTION_KEY", enc_key)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Database migration tool for TARA System."""
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend" / "shared"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class MigrationManager:
    """Manage database migrations."""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://tara:tara_password@localhost:3306/tara_db"
        )
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.migrations_dir = Path(__file__).parent / "versions"
        self.migrations_dir.mkdir(exist_ok=True)

    def init(self):
        """Initialize migrations table."""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    version VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        print("✓ Migrations table initialized")

    def get_applied_versions(self) -> list:
        """Get list of applied migration versions."""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT version FROM migrations ORDER BY id"))
            return [row[0] for row in result]

    def get_pending_migrations(self) -> list:
        """Get list of pending migrations."""
        applied = set(self.get_applied_versions())
        all_migrations = sorted(self.migrations_dir.glob("*.py"))
        pending = []
        
        for migration_file in all_migrations:
            version = migration_file.stem
            if version not in applied and not version.startswith("__"):
                pending.append(migration_file)
        
        return pending

    def upgrade(self, target: str = None):
        """Apply pending migrations."""
        self.init()
        pending = self.get_pending_migrations()
        
        if not pending:
            print("No pending migrations")
            return
        
        for migration_file in pending:
            version = migration_file.stem
            
            if target and version > target:
                break
            
            print(f"Applying migration: {version}")
            
            # Load and execute migration
            spec = __import__(f"versions.{version}", fromlist=["upgrade"])
            if hasattr(spec, "upgrade"):
                spec.upgrade(self.engine)
            
            # Record migration
            with self.engine.connect() as conn:
                conn.execute(
                    text("INSERT INTO migrations (version) VALUES (:version)"),
                    {"version": version}
                )
                conn.commit()
            
            print(f"✓ Applied: {version}")
        
        print("✓ All migrations applied")

    def downgrade(self, target: str = None):
        """Rollback migrations."""
        applied = self.get_applied_versions()
        
        if not applied:
            print("No migrations to rollback")
            return
        
        # Rollback in reverse order
        for version in reversed(applied):
            if target and version <= target:
                break
            
            print(f"Rolling back: {version}")
            
            migration_file = self.migrations_dir / f"{version}.py"
            if migration_file.exists():
                spec = __import__(f"versions.{version}", fromlist=["downgrade"])
                if hasattr(spec, "downgrade"):
                    spec.downgrade(self.engine)
            
            # Remove migration record
            with self.engine.connect() as conn:
                conn.execute(
                    text("DELETE FROM migrations WHERE version = :version"),
                    {"version": version}
                )
                conn.commit()
            
            print(f"✓ Rolled back: {version}")

    def status(self):
        """Show migration status."""
        self.init()
        applied = self.get_applied_versions()
        pending = self.get_pending_migrations()
        
        print("\n=== Migration Status ===\n")
        
        print("Applied migrations:")
        if applied:
            for version in applied:
                print(f"  ✓ {version}")
        else:
            print("  (none)")
        
        print("\nPending migrations:")
        if pending:
            for migration in pending:
                print(f"  ○ {migration.stem}")
        else:
            print("  (none)")
        
        print()

    def create(self, name: str):
        """Create a new migration file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.py"
        filepath = self.migrations_dir / filename
        
        template = '''"""
Migration: {name}
Created: {timestamp}
"""
from sqlalchemy import text


def upgrade(engine):
    """Apply migration."""
    with engine.connect() as conn:
        # Add your upgrade SQL here
        # conn.execute(text("ALTER TABLE ..."))
        conn.commit()


def downgrade(engine):
    """Rollback migration."""
    with engine.connect() as conn:
        # Add your downgrade SQL here
        # conn.execute(text("ALTER TABLE ..."))
        conn.commit()
'''
        
        filepath.write_text(template.format(
            name=name,
            timestamp=datetime.now().isoformat()
        ))
        
        print(f"✓ Created migration: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="TARA Database Migration Tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Apply migrations")
    upgrade_parser.add_argument("--target", help="Target version")
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Rollback migrations")
    downgrade_parser.add_argument("--target", help="Target version")
    
    # Status command
    subparsers.add_parser("status", help="Show migration status")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create new migration")
    create_parser.add_argument("name", help="Migration name")
    
    args = parser.parse_args()
    
    manager = MigrationManager()
    
    if args.command == "upgrade":
        manager.upgrade(args.target)
    elif args.command == "downgrade":
        manager.downgrade(args.target)
    elif args.command == "status":
        manager.status()
    elif args.command == "create":
        manager.create(args.name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

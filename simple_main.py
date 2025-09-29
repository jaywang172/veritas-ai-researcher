#!/usr/bin/env python3
"""
Veritas Simple Main - Actually works
Clean, linear execution. No bullshit.

Usage: python simple_main.py
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Import the simple workflow
from workflows.simple_workflow import WorkflowError, run_simple_research

load_dotenv()


def print_header():
    print("=" * 60)
    print("Veritas Simple - Research That Actually Works".center(60))
    print("Linear Pipeline. No Lies. No 70-Field Monsters.".center(60))
    print("=" * 60 + "\n")


def save_result(content: str, goal: str) -> str:
    """Save research result to results directory with clean naming."""
    # Create results directory
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    # Create session-specific subdirectory
    from datetime import datetime

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = results_dir / f"simple_research_{session_id}"
    session_dir.mkdir(exist_ok=True)

    # Create a safe filename
    safe_goal = "".join(c for c in goal if c.isalnum() or c in (" ", "-", "_")).strip()
    safe_goal = safe_goal.replace(" ", "_")[:30]  # Limit length

    filename = session_dir / f"research_{safe_goal}.txt"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Simple Research Report: {goal}\n")
            f.write(f"# Generated: {Path().absolute()}\n")
            f.write(f"# Session: {session_id}\n")
            f.write(f"# Results Directory: {session_dir}\n")
            f.write("=" * 60 + "\n\n")
            f.write(content)

        print(f"📁 Results directory: {session_dir}")
        return str(filename)
    except Exception as e:
        print(f"⚠️  Could not save to {filename}: {e}")
        return None


def main():
    """Main function - simple and direct."""
    print_header()

    print("Simple research pipeline:")
    print("  1. Literature research (always)")
    print("  2. Data analysis (if file provided)")
    print("  3. Synthesize findings")
    print("  4. Create outline")
    print("  5. Write content")
    print("  6. Edit and polish")
    print("  7. Format citations")
    print()

    # Get user input
    goal = input("Research goal: ").strip()
    if not goal:
        print("Error: Goal cannot be empty")
        return 1

    data_file = input("Data file (optional, press Enter to skip): ").strip()
    if data_file and not Path(data_file).exists():
        print(f"File '{data_file}' not found, proceeding without data analysis")
        data_file = None

    print("\nStarting research pipeline...")
    print(f"Goal: {goal}")
    if data_file:
        print(f"Data: {data_file}")
    print()

    try:
        # Run the simple workflow
        result = run_simple_research(goal, data_file)

        # Save result
        filename = save_result(result, goal)

        # Report success
        print("\n" + "=" * 60)
        print("Research Completed Successfully!")
        print("=" * 60)
        if filename:
            print(f"Saved to: {filename}")
        print(f"Content length: {len(result)} characters")
        print(f"Word count: ~{len(result.split())} words")

        return 0

    except WorkflowError as e:
        print(f"\nResearch failed: {e}")
        print("\nThis is a real failure, not a fake 'completion'.")
        return 1

    except KeyboardInterrupt:
        print("\n⏸Research interrupted by user")
        return 1

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

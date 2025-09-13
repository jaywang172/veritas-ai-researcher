#!/usr/bin/env python3
"""
Organize existing results into results directory.
Move generated charts and files to proper structure.
"""

import shutil
from pathlib import Path
from datetime import datetime


def organize_existing_files():
    """Move existing generated files to results directory."""
    
    # Create results directory structure
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Create a legacy directory for existing files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    legacy_dir = results_dir / f"legacy_results_{timestamp}"
    legacy_dir.mkdir(exist_ok=True)
    
    # Files to move
    files_to_move = [
        "nvidia_revenue_trend.png",
        "nvidia_revenue_stock_trend.png", 
        "research_基於sales_datacsv提供的五年期詳細財報深度剖析N.txt",
        "enhanced_research_基於sales_datacsv提供的五年期詳細財報深度剖析N.txt"
    ]
    
    moved_files = []
    
    print(f"📁 Creating legacy results directory: {legacy_dir}")
    
    for filename in files_to_move:
        source = Path(filename)
        if source.exists():
            destination = legacy_dir / filename
            try:
                shutil.move(str(source), str(destination))
                moved_files.append(filename)
                print(f"✅ Moved: {filename} -> {destination}")
            except Exception as e:
                print(f"❌ Failed to move {filename}: {e}")
    
    # Also check for any version files
    for version_file in Path(".").glob("version_*.txt"):
        try:
            destination = legacy_dir / version_file.name
            shutil.move(str(version_file), str(destination))
            moved_files.append(version_file.name)
            print(f"✅ Moved: {version_file.name} -> {destination}")
        except Exception as e:
            print(f"❌ Failed to move {version_file.name}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   • Files moved: {len(moved_files)}")
    print(f"   • Legacy directory: {legacy_dir}")
    
    if moved_files:
        print(f"\n📋 Moved files:")
        for file in moved_files:
            print(f"   • {file}")
    else:
        print(f"\n💡 No existing result files found to move.")
    
    print(f"\n🎯 Going forward, all results will be saved to:")
    print(f"   • Simple workflow: results/simple_research_YYYYMMDD_HHMMSS/")
    print(f"   • Enhanced workflow: results/research_YYYYMMDD_HHMMSS/")


if __name__ == "__main__":
    organize_existing_files()

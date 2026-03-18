#!/usr/bin/env python3
import sys
import re
import json
from pathlib import Path

def validate_solution(filepath):
    """Quick validator for testing"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract solution from frontmatter
        solution_match = re.search(r'solution:\s*["\'](.+?)["\']', content, re.DOTALL)
        if not solution_match:
            print("❌ NO SOLUTION FOUND")
            return False
        
        solution = solution_match.group(1).strip()
        
        # For Day 1: Check if it's the ROT13 answer
        correct_answer = "THE CRAZY KEY IS MY SECRET POST"
        
        # Normalize both
        sol_clean = re.sub(r'[^a-z0-9]', '', solution.lower())
        ans_clean = re.sub(r'[^a-z0-9]', '', correct_answer.lower())
        
        if sol_clean == ans_clean:
            print("🎯 SIGNAL ACQUIRED. The relay acknowledges your decryption.")
            return True
        else:
            print("❌ NO SIGNAL. Your decryption key is incompatible.")
            return False
    
    except Exception as e:
        print(f"🔥 ERROR: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validator.py <solution_file>")
        sys.exit(1)
    
    is_valid = validate_solution(sys.argv[1])
    sys.exit(0 if is_valid else 1)
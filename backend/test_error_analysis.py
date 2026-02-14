
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.upload import _analyze_error

def test_analysis():
    print("Testing Error Analysis Logic...")
    
    # Date Error
    err1 = "Line Error: Date: 12-2-2026 does not exist!"
    res1 = _analyze_error(err1)
    print(f"\nError: {err1}")
    print(f"Analysis: {res1}")
    if "financial period" not in res1["reason"]:
        print("FAILED: Reason mismatch")
        exit(1)

    # Ledger Error
    err2 = "Line Error: Ledger 'Unknown Party' does not exist!"
    res2 = _analyze_error(err2)
    print(f"\nError: {err2}")
    print(f"Analysis: {res2}")
    if "ledger name" not in res2["reason"]:
        print("FAILED: Reason mismatch")
        exit(1)
    
    # Amount Error
    err3 = "Amount '$500' is invalid"
    res3 = _analyze_error(err3)
    print(f"\nError: {err3}")
    print(f"Analysis: {res3}")
    if "amount" not in res3["reason"]:
        print("FAILED: Reason mismatch")
        exit(1)
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_analysis()

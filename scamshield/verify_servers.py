import urllib.request
import json
import time

def test_frontend():
    print("Testing Next.js frontend...")
    try:
        response = urllib.request.urlopen("http://localhost:3210/")
        html = response.read().decode("utf-8")
        if "VigilantAI" in html:
            print("[OK] Next.js home page loaded successfully (found 'VigilantAI')")
            return True
        else:
            print("[FAIL] Next.js page did not contain the text 'VigilantAI'")
            return False
    except Exception as e:
        print(f"[FAIL] Next.js request failed: {e}")
        return False

def test_backend():
    print("Testing FastAPI backend api...")
    data = json.dumps({
        "message": "Aapka SBI account block ho gaya hai. KYC update karein: http://bit.ly/sbi-kyc"
    }).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/analyze",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        response = urllib.request.urlopen(req)
        res_data = json.loads(response.read().decode("utf-8"))
        print("[OK] Backend response received:")
        print(json.dumps(res_data, indent=2))
        
        # Verify fields
        assert "category" in res_data
        assert "badge" in res_data
        assert "confidence" in res_data
        assert "advice" in res_data
        assert "red_flags" in res_data
        assert "route" in res_data
        assert "follow_up_questions" in res_data
        print("[OK] All response fields validated successfully!")
        return True
    except Exception as e:
        print(f"[FAIL] Backend API request failed: {e}")
        return False

if __name__ == "__main__":
    # Give the backend server a moment to startup
    time.sleep(2)
    frontend_ok = test_frontend()
    backend_ok = test_backend()
    if frontend_ok and backend_ok:
        print("\n*** ALL LOCAL SERVERS VERIFIED AND INTEGRATED SUCCESSFULLY! ***")
    else:
        print("\n*** VERIFICATION FAILED. CHECK LOGS ABOVE. ***")

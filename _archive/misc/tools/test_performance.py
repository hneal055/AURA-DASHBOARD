import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8083"

def test_health():
    """Test health endpoint"""
    print("🧪 Testing Health Endpoint...")
    start_time = time.time()
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data['status']}")
            print(f"   Response Time: {response_time:.2f}ms")
            print(f"   Requests Processed: {data['requests_processed']}")
            print(f"   Successful Parses: {data['successful_parses']}")
            return True, response_time
        else:
            print(f"❌ Health failed: {response.status_code}")
            return False, response_time
    except Exception as e:
        print(f"❌ Health error: {e}")
        return False, (time.time() - start_time) * 1000

def test_metrics():
    """Test metrics endpoint"""
    print("\n📊 Testing Metrics Endpoint...")
    start_time = time.time()
    
    try:
        response = requests.get(f"{BASE_URL}/api/metrics", timeout=5)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Metrics:")
            print(f"   Response Time: {response_time:.2f}ms")
            print(f"   Total Requests: {data['requests_total']}")
            print(f"   Success Rate: {data['success_rate']}%")
            print(f"   Uptime: {data['uptime_seconds']}s")
            return True, response_time
        else:
            print(f"❌ Metrics failed: {response.status_code}")
            return False, response_time
    except Exception as e:
        print(f"❌ Metrics error: {e}")
        return False, (time.time() - start_time) * 1000

def test_single_parse():
    """Test single screenplay parsing"""
    print("\n📝 Testing Single Parse...")
    start_time = time.time()
    
    screenplay_data = {
        "screenplay": """INT. WRITER'S ROOM - DAY

HARRY, late 30s, stares at his monitor. The room is littered with coffee cups.

HARRY
(muttering)
Why won't this dialogue work?

He types furiously, then deletes everything.

HARRY
(cont'd)
Come on, Harry. You're a professional.

The phone RINGS. He ignores it.

HARRY
(cont'd)
Just one more scene...

FADE TO BLACK.""",
        "format": "final_draft"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/parse",
            json=screenplay_data,
            timeout=10
        )
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Single Parse:")
            print(f"   Response Time: {response_time:.2f}ms")
            print(f"   Success: {data['success']}")
            print(f"   Word Count: {data['data']['word_count']}")
            print(f"   Line Count: {data['data']['line_count']}")
            print(f"   Pages: {data['data']['estimated_pages']}")
            return True, response_time
        else:
            print(f"❌ Single Parse failed: {response.status_code}")
            return False, response_time
    except Exception as e:
        print(f"❌ Single Parse error: {e}")
        return False, (time.time() - start_time) * 1000

def test_batch_parse():
    """Test batch screenplay parsing"""
    print("\n📦 Testing Batch Parse...")
    start_time = time.time()
    
    batch_data = {
        "screenplays": [
            "INT. OFFICE - DAY\nJohn works at his computer.\nJOHN\nThis is the first screenplay.",
            "EXT. PARK - DAY\nSarah walks through the park.\nSARAH\nWhat a beautiful day.",
            "INT. COFFEE SHOP - NIGHT\nMike sips his coffee.\nMIKE\nI need to finish this script.",
            "INT. STUDIO - DAY\nDirector shouts action.\nDIRECTOR\nAnd... scene!",
            "EXT. BEACH - SUNSET\nCouple walks hand in hand.\nANNA\nThis is perfect."
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/batch/parse",
            json=batch_data,
            timeout=15
        )
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batch Parse:")
            print(f"   Response Time: {response_time:.2f}ms")
            print(f"   Batch Size: {data['batch_size']}")
            print(f"   Processed: {data['processed']}")
            print(f"   Results: {len(data['results'])}")
            return True, response_time
        else:
            print(f"❌ Batch Parse failed: {response.status_code}")
            return False, response_time
    except Exception as e:
        print(f"❌ Batch Parse error: {e}")
        return False, (time.time() - start_time) * 1000

def test_concurrent_requests():
    """Test multiple concurrent requests"""
    print("\n⚡ Testing Concurrent Requests...")
    import threading
    
    results = []
    
    def make_request(request_id):
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            results.append((request_id, response_time, response.status_code == 200))
        except Exception as e:
            results.append((request_id, 0, False))
    
    # Create 5 concurrent requests
    threads = []
    for i in range(5):
        thread = threading.Thread(target=make_request, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Analyze results
    successful = sum(1 for r in results if r[2])
    response_times = [r[1] for r in results if r[1] > 0]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    print(f"✅ Concurrent Test:")
    print(f"   Successful: {successful}/5")
    print(f"   Avg Response Time: {avg_response_time:.2f}ms")
    print(f"   Min/Max: {min(response_times):.2f}ms / {max(response_times):.2f}ms")
    
    return successful == 5, avg_response_time

def test_dashboard():
    """Test dashboard loading"""
    print("\n🌐 Testing Dashboard...")
    start_time = time.time()
    
    try:
        response = requests.get(BASE_URL, timeout=5)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            print(f"✅ Dashboard:")
            print(f"   Response Time: {response_time:.2f}ms")
            print(f"   Content Length: {len(response.text)} bytes")
            return True, response_time
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            return False, response_time
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False, (time.time() - start_time) * 1000

def run_comprehensive_test():
    """Run all performance tests"""
    print("🚀 STARTING COMPREHENSIVE PERFORMANCE TEST")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Health Check", *test_health()))
    test_results.append(("Metrics", *test_metrics()))
    test_results.append(("Single Parse", *test_single_parse()))
    test_results.append(("Batch Parse", *test_batch_parse()))
    test_results.append(("Dashboard", *test_dashboard()))
    test_results.append(("Concurrent", *test_concurrent_requests()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 PERFORMANCE TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = sum(1 for result in test_results if result[1])
    total_tests = len(test_results)
    
    print(f"Tests Passed: {successful_tests}/{total_tests}")
    
    # Calculate average response time for successful tests
    successful_response_times = [result[2] for result in test_results if result[1]]
    if successful_response_times:
        avg_response_time = sum(successful_response_times) / len(successful_response_times)
        print(f"Average Response Time: {avg_response_time:.2f}ms")
    
    # Performance grading
    if successful_tests == total_tests:
        if avg_response_time < 100:
            grade = "A+ 🎉"
        elif avg_response_time < 200:
            grade = "A 👍"
        elif avg_response_time < 500:
            grade = "B ✅"
        else:
            grade = "C ⚠️"
        
        print(f"Performance Grade: {grade}")
        print("🎯 Enhanced AURA API is performing excellently!")
    else:
        print("❌ Some tests failed. Check the API server.")
    
    print("=" * 60)

if __name__ == "__main__":
    # Make sure your API server is running first!
    print("⚠️  Make sure your AURA API is running on http://localhost:8083")
    input("Press Enter to start performance tests...")
    run_comprehensive_test()
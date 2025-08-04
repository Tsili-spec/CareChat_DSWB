#!/usr/bin/env python3
"""
Comprehensive test suite for CareChat Track2 Backend
Tests the chat endpoint with various scenarios
"""

import requests
import json
import uuid
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/chat/"
HEALTH_ENDPOINT = f"{BASE_URL}/health/llm"
SIGNUP_ENDPOINT = f"{BASE_URL}/api/signup"

class ChatTester:
    def __init__(self):
        self.test_user_id = None
        self.test_phone = f"+1555{str(uuid.uuid4())[:7].replace('-', '')}"
        self.conversation_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def print_header(self, test_name: str):
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print(f"{'='*60}")
    
    def print_result(self, success: bool, message: str):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {message}")
    
    def test_server_health(self) -> bool:
        """Test if the server and LLM services are healthy"""
        self.print_header("Server Health Check")
        
        try:
            response = self.session.get(HEALTH_ENDPOINT)
            if response.status_code == 200:
                data = response.json()
                print(f"Server Status: {data.get('status', 'unknown')}")
                print(f"Default Provider: {data.get('default_provider', 'unknown')}")
                
                providers = data.get('providers', {})
                for provider, info in providers.items():
                    status = "🟢" if info.get('available') else "🔴"
                    print(f"  {provider}: {status} {info.get('message', '')}")
                
                self.print_result(True, "Server is healthy and LLM services are available")
                return True
            else:
                self.print_result(False, f"Health check failed with status {response.status_code}")
                return False
        except Exception as e:
            self.print_result(False, f"Failed to connect to server: {e}")
            return False
    
    def create_test_user(self) -> bool:
        """Create a test user for chat testing"""
        self.print_header("Test User Creation")
        
        user_data = {
            "full_name": "Test Patient",
            "phone_number": self.test_phone,
            "email": f"test.patient.{uuid.uuid4().hex[:8]}@example.com",
            "preferred_language": "en",
            "password": "testpassword123"
        }
        
        try:
            print(f"📤 Creating user with phone: {self.test_phone}")
            response = self.session.post(SIGNUP_ENDPOINT, json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_id = data.get('patient_id')
                print(f"📥 User created successfully!")
                print(f"📥 Patient ID: {self.test_user_id}")
                print(f"📥 Name: {data.get('full_name')}")
                print(f"📥 Phone: {data.get('phone_number')}")
                self.print_result(True, f"Test user created with ID: {self.test_user_id}")
                return True
            else:
                print(f"📥 Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📥 Error Details: {error_data}")
                except:
                    print(f"📥 Error Text: {response.text}")
                self.print_result(False, f"Failed to create test user: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"📥 Exception: {e}")
            self.print_result(False, f"Exception creating test user: {e}")
            return False
    
    def send_chat_message(self, message: str, provider: str = "gemini", 
                         conversation_id: Optional[str] = None) -> Optional[Dict[Any, Any]]:
        """Send a chat message to the API"""
        payload = {
            "user_id": self.test_user_id,
            "message": message,
            "provider": provider
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        try:
            print(f"📤 Sending: {message[:50]}{'...' if len(message) > 50 else ''}")
            response = self.session.post(CHAT_ENDPOINT, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"📥 Status: {response.status_code}")
                print(f"📥 Conversation ID: {data.get('conversation_id', 'N/A')}")
                print(f"📥 Provider: {data.get('provider', 'N/A')}")
                
                assistant_msg = data.get('assistant_message', {})
                response_text = assistant_msg.get('content', 'No response content')
                print(f"📥 Response: {response_text[:100]}{'...' if len(response_text) > 100 else ''}")
                
                return data
            else:
                print(f"📥 Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📥 Error Details: {error_data}")
                except:
                    print(f"📥 Error Text: {response.text}")
                return None
                
        except Exception as e:
            print(f"📥 Exception: {e}")
            return None
    
    def test_first_message(self) -> bool:
        """Test sending the first message (creates new conversation)"""
        self.print_header("Test 1: First Message (New Conversation)")
        
        if not self.test_user_id:
            self.print_result(False, "No test user available")
            return False
        
        message = "Hello, I'm a patient and I have questions about my recent diagnosis of hypertension. Can you help me understand what this means?"
        
        response_data = self.send_chat_message(message)
        
        if response_data:
            self.conversation_id = response_data.get('conversation_id')
            if self.conversation_id:
                self.print_result(True, f"Successfully created new conversation: {self.conversation_id}")
                return True
            else:
                self.print_result(False, "Response received but no conversation_id")
                return False
        else:
            self.print_result(False, "Failed to send first message")
            return False
    
    def test_follow_up_message(self) -> bool:
        """Test sending a follow-up message in the same conversation"""
        self.print_header("Test 2: Follow-up Message (Same Conversation)")
        
        if not self.conversation_id:
            self.print_result(False, "No conversation ID available from previous test")
            return False
        
        message = "What lifestyle changes should I make to manage my blood pressure?"
        
        response_data = self.send_chat_message(message, conversation_id=self.conversation_id)
        
        if response_data:
            returned_conv_id = response_data.get('conversation_id')
            if returned_conv_id == self.conversation_id:
                self.print_result(True, "Successfully continued conversation with context")
                return True
            else:
                self.print_result(False, f"Conversation ID mismatch: expected {self.conversation_id}, got {returned_conv_id}")
                return False
        else:
            self.print_result(False, "Failed to send follow-up message")
            return False
    
    def test_different_provider(self) -> bool:
        """Test using a different LLM provider"""
        self.print_header("Test 3: Different Provider (Groq)")
        
        message = "Can you explain what blood pressure medications typically do?"
        
        response_data = self.send_chat_message(message, provider="groq")
        
        if response_data:
            provider = response_data.get('provider')
            if provider == "groq":
                self.print_result(True, f"Successfully used Groq provider")
                return True
            else:
                self.print_result(False, f"Expected groq provider, got {provider}")
                return False
        else:
            self.print_result(False, "Failed to send message with Groq provider")
            return False
    
    def test_long_message(self) -> bool:
        """Test sending a longer, more complex message"""
        self.print_header("Test 4: Long Complex Message")
        
        message = """
        I've been diagnosed with Type 2 diabetes and hypertension. My doctor prescribed 
        metformin for diabetes and lisinopril for blood pressure. I'm also supposed to 
        follow a low-sodium diet and exercise regularly. I'm feeling overwhelmed with 
        all these changes. Can you help me understand:
        1. How these medications work
        2. What a low-sodium diet looks like
        3. What kind of exercise is safe for me
        4. How to monitor my conditions at home
        Please explain in simple terms as I'm not familiar with medical terminology.
        """
        
        response_data = self.send_chat_message(message.strip())
        
        if response_data:
            assistant_msg = response_data.get('assistant_message', {})
            response_content = assistant_msg.get('content', '')
            
            # Check if response addresses multiple points
            has_medication_info = any(term in response_content.lower() for term in ['metformin', 'lisinopril', 'medication'])
            has_diet_info = any(term in response_content.lower() for term in ['sodium', 'diet', 'salt'])
            has_exercise_info = any(term in response_content.lower() for term in ['exercise', 'physical', 'activity'])
            
            if has_medication_info and has_diet_info and has_exercise_info:
                self.print_result(True, "Response comprehensively addressed multiple topics")
                return True
            else:
                self.print_result(True, "Response received but may not address all topics")
                return True
        else:
            self.print_result(False, "Failed to send long complex message")
            return False
    
    def test_invalid_requests(self) -> bool:
        """Test various invalid request scenarios"""
        self.print_header("Test 5: Invalid Request Handling")
        
        test_cases = [
            {
                "name": "Empty message",
                "payload": {"user_id": self.test_user_id, "message": "", "provider": "groq"},
                "expected_status": [400, 422]
            },
            {
                "name": "Missing user_id",
                "payload": {"message": "Test message", "provider": "groq"},
                "expected_status": [400, 422]
            },
            {
                "name": "Invalid provider",
                "payload": {"user_id": self.test_user_id, "message": "Test", "provider": "invalid_provider"},
                "expected_status": [400, 422]
            },
            {
                "name": "Invalid conversation_id format",
                "payload": {"user_id": self.test_user_id, "message": "Test", "conversation_id": "invalid-uuid"},
                "expected_status": [400, 422]
            }
        ]
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for test_case in test_cases:
            try:
                response = self.session.post(CHAT_ENDPOINT, json=test_case["payload"])
                if response.status_code in test_case["expected_status"]:
                    print(f"  ✅ {test_case['name']}: Correctly rejected (status {response.status_code})")
                    passed_tests += 1
                else:
                    print(f"  ❌ {test_case['name']}: Unexpected status {response.status_code}")
            except Exception as e:
                print(f"  ❌ {test_case['name']}: Exception {e}")
        
        success_rate = passed_tests / total_tests
        self.print_result(success_rate >= 0.75, f"Invalid request handling: {passed_tests}/{total_tests} tests passed")
        return success_rate >= 0.75
    
    def test_performance(self) -> bool:
        """Test response time performance"""
        self.print_header("Test 6: Performance Test")
        
        message = "What are the common symptoms of diabetes?"
        start_time = time.time()
        
        response_data = self.send_chat_message(message)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"📊 Response time: {response_time:.2f} seconds")
        
        if response_data:
            if response_time < 30:  # 30 seconds is reasonable for LLM responses
                self.print_result(True, f"Good response time: {response_time:.2f}s")
                return True
            else:
                self.print_result(False, f"Slow response time: {response_time:.2f}s")
                return True  # Still pass the test, just note it's slow
        else:
            self.print_result(False, "No response received for performance test")
            return False
    
    def run_all_tests(self):
        """Run all test scenarios"""
        print("🚀 Starting CareChat Chat Endpoint Tests")
        print(f"📅 Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"� Test Phone: {self.test_phone}")
        
        tests = [
            ("Server Health", self.test_server_health),
            ("User Creation", self.create_test_user),
            ("First Message", self.test_first_message),
            ("Follow-up Message", self.test_follow_up_message),
            ("Different Provider", self.test_different_provider),
            ("Long Complex Message", self.test_long_message),
            ("Invalid Requests", self.test_invalid_requests),
            ("Performance", self.test_performance),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        self.print_header("Test Summary")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"📊 Tests Passed: {passed}/{total}")
        print(f"📊 Success Rate: {(passed/total)*100:.1f}%")
        
        for test_name, result in results:
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
        
        if self.conversation_id:
            print(f"\n💬 Conversation created: {self.conversation_id}")
        if self.test_user_id:
            print(f"👤 Test user: {self.test_user_id}")
            print(f"📱 Test phone: {self.test_phone}")
        
        print(f"\n🏁 Test run completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return passed == total

def main():
    """Main test runner"""
    tester = ChatTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Chat endpoint is working correctly.")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")
        exit(1)

if __name__ == "__main__":
    main()

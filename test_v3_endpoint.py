"""
Test script for v3.0 API endpoint

Tests the /api/message/v3 endpoint with various product types
to validate universal coverage and guardrail enforcement.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"
V3_ENDPOINT = f"{BASE_URL}/api/message/v3"


class TestSession:
    """Manages a test session with cookies"""

    def __init__(self):
        self.session = requests.Session()
        self.conversation = []

    def send_message(self, message):
        """Send a message to v3 endpoint"""
        response = self.session.post(
            V3_ENDPOINT,
            json={'message': message},
            headers={'Content-Type': 'application/json'}
        )
        return response.json()

    def run_conversation(self, product_name, answers):
        """Run a full conversation"""
        print(f"\n{'='*60}")
        print(f"Testing: {product_name}")
        print(f"{'='*60}")

        # First message: product identification
        print(f"\n👤 User: {product_name}")
        result = self.send_message(product_name)

        if not result.get('success'):
            print(f"❌ Error: {result.get('error')}")
            return False

        print(f"🤖 AI: {result.get('message', '')}")
        if result.get('question'):
            print(f"    {result.get('question')}")
            if result.get('quick_options'):
                print(f"    Options: {result.get('quick_options')[:3]}...")

        question_count = 0
        max_questions = 4

        # Answer questions
        for i, answer in enumerate(answers):
            if result.get('should_calculate'):
                print(f"\n✅ Offer calculation triggered after {question_count} questions")
                break

            if question_count >= max_questions:
                print(f"\n⚠️  Reached max questions ({max_questions})")
                break

            print(f"\n👤 User: {answer}")
            result = self.send_message(answer)

            if not result.get('success'):
                print(f"❌ Error: {result.get('error')}")
                return False

            question_count += 1

            if result.get('should_calculate'):
                print(f"✅ Offer calculation triggered after {question_count} questions")
                print(f"   Message: {result.get('message')}")
                break

            if result.get('question'):
                print(f"🤖 AI: {result.get('question')}")
                if result.get('quick_options'):
                    print(f"    Options: {result.get('quick_options')[:3]}...")
                if result.get('progress'):
                    prog = result['progress']
                    print(f"    Progress: {prog['current']}/{prog['total']}")

        # Validation
        print(f"\n📊 Test Results:")
        print(f"   Questions asked: {question_count}")
        print(f"   Within limit (≤4): {'✅' if question_count <= 4 else '❌'}")
        print(f"   Reached offer: {'✅' if result.get('should_calculate') else '❌'}")

        return question_count <= 4 and result.get('should_calculate')


def main():
    """Run all test scenarios"""

    print("\n" + "="*60)
    print("V3.0 API ENDPOINT TESTS")
    print("="*60)

    test_scenarios = [
        {
            'name': 'iPhone 14 128GB',
            'answers': ['Screen cracked', 'Yes, unlocked', 'Yes, free from contract']
        },
        {
            'name': '2019 VW Polo 1.0 TSI',
            'answers': ['About 85,000km', 'Few scratches on bumper', 'Full service history']
        },
        {
            'name': 'Nike Air Jordan 4 Retro size 10',
            'answers': ['Military Black', 'Light scuffs, have the box']
        },
        {
            'name': 'Dyson Airwrap',
            'answers': ['Complete Long', 'All attachments, like new']
        },
        {
            'name': 'MacBook Air M2',
            'answers': ['8GB/256GB', 'Minor scratches', 'Yes, signed out of Apple ID']
        }
    ]

    results = []

    for scenario in test_scenarios:
        session = TestSession()  # Fresh session for each test
        time.sleep(1)  # Be nice to the API

        try:
            success = session.run_conversation(
                scenario['name'],
                scenario['answers']
            )
            results.append({
                'product': scenario['name'],
                'success': success
            })
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            results.append({
                'product': scenario['name'],
                'success': False,
                'error': str(e)
            })

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for r in results if r['success'])
    total = len(results)

    for result in results:
        status = "✅" if result['success'] else "❌"
        error = f" ({result.get('error')})" if 'error' in result else ""
        print(f"{status} {result['product']}{error}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == '__main__':
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        print("✅ Server is running")
    except:
        print("❌ Server not running. Start with: python3 app.py")
        exit(1)

    main()

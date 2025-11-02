#!/usr/bin/env python3
"""
Demo script for Voice Shopping Assistant API

This script demonstrates how to use the API endpoints for voice shopping functionality.
"""

import sys
import time
import json
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class VoiceShoppingAPIDemo:
    """Demo client for Voice Shopping Assistant API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize demo client
        
        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
        self.session_id = f"demo-session-{int(time.time())}"
        
    def check_health(self):
        """Check API health"""
        print("🔍 Checking API health...")
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API is healthy: {data['status']}")
                print(f"   Components: {', '.join(data['components'].keys())}")
                return True
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to API: {e}")
            return False
    
    def process_text_command(self, text: str):
        """Process a text command
        
        Args:
            text: Text command to process
        """
        print(f"\n💬 Processing text: '{text}'")
        
        try:
            payload = {
                "session_id": self.session_id,
                "text": text
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/text/process",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response_text']}")
                print(f"   Intent: {data['intent']['type']} (confidence: {data['intent']['confidence']:.2f})")
                print(f"   Entities: {len(data['entities'])} found")
                print(f"   Processing time: {data['processing_time']:.3f}s")
                return data
            else:
                print(f"❌ Text processing failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_cart(self):
        """Get current cart contents"""
        print(f"\n🛒 Getting cart for session: {self.session_id}")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/cart/{self.session_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['cart_summary']:
                    cart = data['cart_summary']
                    print(f"✅ Cart has {cart['total_items']} items (₹{cart['total_price']:.2f})")
                    for item in cart['items']:
                        product = item['product']
                        print(f"   - {item['quantity']}x {product['name']} (₹{item['total_price']:.2f})")
                else:
                    print("✅ Cart is empty")
                return data
            else:
                print(f"❌ Get cart failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def search_products(self, query: str):
        """Search for products
        
        Args:
            query: Search query
        """
        print(f"\n🔍 Searching for products: '{query}'")
        
        try:
            payload = {
                "query": query,
                "limit": 5
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/products/search",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {data['total_found']} products")
                for product in data['products']:
                    print(f"   - {product['name']} (₹{product['price']:.2f}) - {product['category']}")
                return data
            else:
                print(f"❌ Product search failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_api_stats(self):
        """Get API statistics"""
        print(f"\n📊 Getting API statistics...")
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Statistics:")
                print(f"   Total requests: {data['total_requests']}")
                print(f"   Successful: {data['successful_requests']}")
                print(f"   Errors: {data['error_requests']}")
                print(f"   Avg processing time: {data['average_processing_time']:.3f}s")
                print(f"   Active sessions: {data['active_sessions']}")
                print(f"   Uptime: {data['uptime']:.1f}s")
                return data
            else:
                print(f"❌ Get stats failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_performance_metrics(self):
        """Get performance metrics"""
        print(f"\n⚡ Getting performance metrics...")
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/performance", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                overall = data['overall']
                print(f"✅ Performance Metrics:")
                print(f"   Total requests: {overall['total_requests']}")
                print(f"   Success rate: {overall['success_rate_percent']:.1f}%")
                print(f"   Avg processing time: {overall['average_processing_time']:.3f}s")
                print(f"   Endpoints monitored: {overall['endpoints_monitored']}")
                print(f"   Recent alerts: {overall['recent_alerts']}")
                
                if data['slow_requests']:
                    print(f"   Recent slow requests: {len(data['slow_requests'])}")
                
                return data
            else:
                print(f"❌ Get performance metrics failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def run_demo(self):
        """Run complete demo"""
        print("🎤 Voice Shopping Assistant API Demo")
        print("=" * 50)
        
        # Check health
        if not self.check_health():
            print("❌ API is not available. Please start the server first:")
            print("   python run_api.py")
            return False
        
        # Demo commands
        demo_commands = [
            "add two red shirts to my cart",
            "search for blue jeans",
            "show me my cart",
            "remove red shirts from cart",
            "help me with checkout"
        ]
        
        print(f"\n🎯 Demo Session ID: {self.session_id}")
        
        # Process demo commands
        for i, command in enumerate(demo_commands, 1):
            print(f"\n--- Demo Command {i}/{len(demo_commands)} ---")
            result = self.process_text_command(command)
            
            if result:
                # Show cart after add/remove commands
                if any(word in command.lower() for word in ['add', 'remove']):
                    self.get_cart()
            
            time.sleep(1)  # Brief pause between commands
        
        # Search for products
        self.search_products("shirt")
        
        # Show final statistics
        self.get_api_stats()
        self.get_performance_metrics()
        
        print("\n✅ Demo completed successfully!")
        return True


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice Shopping Assistant API Demo")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--command", help="Single command to test")
    
    args = parser.parse_args()
    
    # Create demo client
    demo = VoiceShoppingAPIDemo(args.url)
    
    if args.command:
        # Test single command
        print("🎤 Voice Shopping Assistant API - Single Command Test")
        print("=" * 60)
        
        if demo.check_health():
            demo.process_text_command(args.command)
            demo.get_cart()
        
    else:
        # Run full demo
        demo.run_demo()


if __name__ == "__main__":
    main()
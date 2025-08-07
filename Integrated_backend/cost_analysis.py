#!/usr/bin/env python3
"""
CareChat Project Cost Analysis Tool
Analyzes potential costs for running the CareChat backend system
"""

import os
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
import sys

class CostAnalyzer:
    def __init__(self):
        self.costs = {
            "llm_services": {},
            "sms_services": {},
            "database": {},
            "hosting": {},
            "storage": {},
            "total_monthly": 0.0,
            "total_yearly": 0.0
        }
        
        # Pricing data (USD as of August 2025 estimates)
        self.pricing = {
            "groq": {
                "llama3_70b": 0.59 / 1000000,  # per token
                "llama3_8b": 0.05 / 1000000,   # per token
                "mixtral": 0.27 / 1000000,     # per token
                "free_tier": 6000,             # requests per day
                "description": "Groq LLM API"
            },
            "gemini": {
                "pro": 0.50 / 1000000,         # per token (input)
                "pro_output": 1.50 / 1000000,  # per token (output)
                "free_tier": 15,               # requests per minute
                "description": "Google Gemini API"
            },
            "twilio": {
                "sms_us": 0.0075,              # per SMS in US
                "sms_international": 0.04,     # per SMS international
                "phone_number": 1.15,          # per month
                "description": "Twilio SMS Service"
            },
            "mongodb": {
                "atlas_m0": 0.0,              # Free tier (512MB)
                "atlas_m2": 9.0,              # per month (2GB)
                "atlas_m5": 25.0,             # per month (5GB)
                "atlas_m10": 57.0,            # per month (10GB)
                "description": "MongoDB Atlas"
            },
            "hosting": {
                "vps_basic": 5.0,             # per month (1GB RAM, 1 CPU)
                "vps_standard": 10.0,         # per month (2GB RAM, 1 CPU)
                "vps_premium": 20.0,          # per month (4GB RAM, 2 CPU)
                "aws_t3_micro": 8.5,          # per month
                "gcp_e2_micro": 6.11,         # per month
                "description": "Server Hosting"
            }
        }

    def analyze_llm_costs(self, requests_per_day: int = 100, avg_tokens_per_request: int = 500):
        """Analyze LLM API costs"""
        print("\n🤖 LLM Services Cost Analysis")
        print("=" * 50)
        
        monthly_requests = requests_per_day * 30
        monthly_tokens = monthly_requests * avg_tokens_per_request
        
        # Groq Analysis
        groq_monthly = (monthly_tokens * self.pricing["groq"]["llama3_8b"]) if monthly_requests > (self.pricing["groq"]["free_tier"] * 30) else 0
        self.costs["llm_services"]["groq"] = groq_monthly
        
        print(f"Groq (Llama3-8B):")
        print(f"  - Monthly requests: {monthly_requests:,}")
        print(f"  - Monthly tokens: {monthly_tokens:,}")
        print(f"  - Free tier: {self.pricing['groq']['free_tier']} requests/day")
        print(f"  - Monthly cost: ${groq_monthly:.2f}")
        
        # Gemini Analysis
        gemini_monthly = (monthly_tokens * self.pricing["gemini"]["pro"]) + (monthly_tokens * 0.3 * self.pricing["gemini"]["pro_output"])
        if monthly_requests <= (self.pricing["gemini"]["free_tier"] * 60 * 24 * 30):  # Free tier
            gemini_monthly = 0
        self.costs["llm_services"]["gemini"] = gemini_monthly
        
        print(f"\nGemini Pro:")
        print(f"  - Monthly requests: {monthly_requests:,}")
        print(f"  - Monthly tokens: {monthly_tokens:,}")
        print(f"  - Free tier: {self.pricing['gemini']['free_tier']} requests/minute")
        print(f"  - Monthly cost: ${gemini_monthly:.2f}")

    def analyze_sms_costs(self, sms_per_day: int = 20):
        """Analyze SMS service costs"""
        print("\n📱 SMS Services Cost Analysis")
        print("=" * 50)
        
        monthly_sms = sms_per_day * 30
        twilio_sms_cost = monthly_sms * self.pricing["twilio"]["sms_us"]
        twilio_phone_cost = self.pricing["twilio"]["phone_number"]
        twilio_total = twilio_sms_cost + twilio_phone_cost
        
        self.costs["sms_services"]["twilio"] = twilio_total
        
        print(f"Twilio SMS:")
        print(f"  - Monthly SMS: {monthly_sms:,}")
        print(f"  - SMS cost: ${twilio_sms_cost:.2f}")
        print(f"  - Phone number: ${twilio_phone_cost:.2f}")
        print(f"  - Total monthly: ${twilio_total:.2f}")

    def analyze_database_costs(self, storage_gb: float = 1.0):
        """Analyze database costs"""
        print("\n🗄️ Database Cost Analysis")
        print("=" * 50)
        
        if storage_gb <= 0.5:
            db_cost = self.pricing["mongodb"]["atlas_m0"]
            tier = "M0 (Free)"
        elif storage_gb <= 2:
            db_cost = self.pricing["mongodb"]["atlas_m2"]
            tier = "M2"
        elif storage_gb <= 5:
            db_cost = self.pricing["mongodb"]["atlas_m5"]
            tier = "M5"
        else:
            db_cost = self.pricing["mongodb"]["atlas_m10"]
            tier = "M10"
        
        self.costs["database"]["mongodb"] = db_cost
        
        print(f"MongoDB Atlas:")
        print(f"  - Storage needed: {storage_gb:.1f} GB")
        print(f"  - Recommended tier: {tier}")
        print(f"  - Monthly cost: ${db_cost:.2f}")

    def analyze_hosting_costs(self, hosting_type: str = "vps_standard"):
        """Analyze hosting costs"""
        print("\n🖥️ Hosting Cost Analysis")
        print("=" * 50)
        
        hosting_cost = self.pricing["hosting"].get(hosting_type, self.pricing["hosting"]["vps_standard"])
        self.costs["hosting"][hosting_type] = hosting_cost
        
        print(f"Hosting Options:")
        for option, cost in self.pricing["hosting"].items():
            if option != "description":
                marker = "✓" if option == hosting_type else " "
                print(f"  {marker} {option.replace('_', ' ').title()}: ${cost:.2f}/month")
        
        print(f"\nSelected: {hosting_type.replace('_', ' ').title()}")
        print(f"Monthly cost: ${hosting_cost:.2f}")

    def calculate_total_costs(self):
        """Calculate total costs"""
        print("\n💰 Total Cost Summary")
        print("=" * 50)
        
        total_monthly = 0
        
        for category, services in self.costs.items():
            if category not in ["total_monthly", "total_yearly"] and services:
                category_total = sum(services.values()) if isinstance(services, dict) else 0
                total_monthly += category_total
                print(f"{category.replace('_', ' ').title()}: ${category_total:.2f}/month")
        
        self.costs["total_monthly"] = total_monthly
        self.costs["total_yearly"] = total_monthly * 12
        
        print(f"\n{'='*30}")
        print(f"TOTAL MONTHLY: ${total_monthly:.2f}")
        print(f"TOTAL YEARLY: ${total_monthly * 12:.2f}")
        print(f"{'='*30}")

    def generate_scaling_analysis(self):
        """Generate scaling cost analysis"""
        print("\n📈 Scaling Cost Analysis")
        print("=" * 50)
        
        scenarios = [
            {"name": "Development", "requests": 50, "sms": 10, "storage": 0.5},
            {"name": "Small Production", "requests": 200, "sms": 50, "storage": 2.0},
            {"name": "Medium Production", "requests": 1000, "sms": 200, "storage": 10.0},
            {"name": "Large Production", "requests": 5000, "sms": 1000, "storage": 50.0}
        ]
        
        print(f"{'Scenario':<20} {'Requests/Day':<15} {'SMS/Day':<10} {'Storage(GB)':<12} {'Est. Monthly Cost':<15}")
        print("-" * 80)
        
        for scenario in scenarios:
            # Quick cost estimation
            requests = scenario["requests"]
            sms = scenario["sms"]
            storage = scenario["storage"]
            
            # LLM cost (using Groq)
            monthly_tokens = requests * 30 * 500
            llm_cost = (monthly_tokens * self.pricing["groq"]["llama3_8b"]) if requests > 200 else 0
            
            # SMS cost
            sms_cost = (sms * 30 * self.pricing["twilio"]["sms_us"]) + self.pricing["twilio"]["phone_number"]
            
            # Database cost
            if storage <= 0.5:
                db_cost = 0
            elif storage <= 2:
                db_cost = 9
            elif storage <= 5:
                db_cost = 25
            else:
                db_cost = 57 + ((storage - 10) * 5)  # Rough estimate for larger storage
            
            # Hosting cost (scales with usage)
            if requests <= 100:
                hosting_cost = 5
            elif requests <= 500:
                hosting_cost = 10
            elif requests <= 2000:
                hosting_cost = 20
            else:
                hosting_cost = 40
            
            total_cost = llm_cost + sms_cost + db_cost + hosting_cost
            
            print(f"{scenario['name']:<20} {requests:<15} {sms:<10} {storage:<12} ${total_cost:.2f}")

    def save_results(self, filename: str = "cost_analysis_results.json"):
        """Save analysis results to JSON file"""
        self.costs["analysis_date"] = datetime.now().isoformat()
        self.costs["assumptions"] = {
            "llm_requests_per_day": 100,
            "average_tokens_per_request": 500,
            "sms_per_day": 20,
            "storage_gb": 1.0,
            "hosting_type": "vps_standard"
        }
        
        with open(filename, 'w') as f:
            json.dump(self.costs, f, indent=2)
        
        print(f"\n📄 Results saved to: {filename}")

    def run_full_analysis(self, requests_per_day: int = 100, sms_per_day: int = 20, storage_gb: float = 1.0):
        """Run complete cost analysis"""
        print("🔍 CareChat Project Cost Analysis")
        print("=" * 60)
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Analysis Assumptions:")
        print(f"  - LLM requests per day: {requests_per_day}")
        print(f"  - SMS messages per day: {sms_per_day}")
        print(f"  - Storage requirements: {storage_gb} GB")
        
        self.analyze_llm_costs(requests_per_day)
        self.analyze_sms_costs(sms_per_day)
        self.analyze_database_costs(storage_gb)
        self.analyze_hosting_costs()
        self.calculate_total_costs()
        self.generate_scaling_analysis()
        
        # Cost optimization recommendations
        print("\n💡 Cost Optimization Recommendations")
        print("=" * 50)
        print("1. Start with free tiers (Groq free tier, MongoDB M0)")
        print("2. Use Groq over Gemini for cost-effective LLM processing")
        print("3. Monitor SMS usage - consider batching notifications")
        print("4. Implement caching to reduce LLM API calls")
        print("5. Use compression for database storage")
        print("6. Consider serverless hosting for variable workloads")
        
        self.save_results()

def main():
    """Main function with command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CareChat Cost Analysis Tool")
    parser.add_argument("--requests", type=int, default=100, help="LLM requests per day (default: 100)")
    parser.add_argument("--sms", type=int, default=20, help="SMS messages per day (default: 20)")
    parser.add_argument("--storage", type=float, default=1.0, help="Storage in GB (default: 1.0)")
    parser.add_argument("--output", type=str, default="cost_analysis_results.json", help="Output file name")
    
    args = parser.parse_args()
    
    analyzer = CostAnalyzer()
    analyzer.run_full_analysis(
        requests_per_day=args.requests,
        sms_per_day=args.sms,
        storage_gb=args.storage
    )

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

# Standard library imports
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, 'backend')

# Local application imports
from app.services.llm_analyzer import LLMAnalyzer

test_transcripts = [
    {
        "name": "Mary Smith Fall",
        "transcript": """
Support Worker: "Hello, Emma Care support line."
Mary Smith: "Hi, I'm Mary Smith. I've fallen in my bedroom and I can't get up. My hip hurts."
Support Worker: "I understand Mary. Are you injured?"
Mary Smith: "Yes, I think I hurt my hip. This is the second time this week."
"""
    },
    {
        "name": "John Doe Confusion",
        "transcript": """
Carer: "Good morning, how are you feeling?"
John Doe: "I'm John Doe... I think. I'm feeling very confused. I can't remember if I took my medication."
Carer: "It's okay John. Let me check your medication chart."
John Doe: "I'm in the kitchen but I don't know why I came here."
"""
    },
    {
        "name": "No Name Mentioned",
        "transcript": """
Support: "Emergency support line, how can I help?"
Caller: "Someone has fallen at the care home. Please come quickly!"
Support: "Can you tell me more details?"
Caller: "They're in the dining room, not responding well."
"""
    }
]

async def test_llm_extraction():
    print("Testing LLM Extraction")
    print("=" * 50)
    
    analyzer = LLMAnalyzer()
    
    if not analyzer.client:
        print(f"WARNING: No API key configured for {analyzer.provider}")
        print("The system will use rule-based fallback")
        print("To use LLM, set your API key in .env file")
        print()
    
    for test in test_transcripts:
        print(f"\nTest: {test['name']}")
        print("-" * 30)
        
        result = await analyzer.analyze(test['transcript'])
        
        print(f"Service User: {result.get('service_user_name', 'Not found')}")
        print(f"Location: {result.get('location', 'Not found')}")
        print(f"Incident Type: {result.get('incident_type', 'Not found')}")
        print(f"LLM Used: {result.get('extracted_facts', {}).get('llm_used', True)}")
        
        if result.get('violations'):
            print(f"Violations Found: {len(result['violations'])}")
            for v in result['violations']:
                print(f"  - {v.get('policy_section')}: {v.get('description')}")

if __name__ == "__main__":
    asyncio.run(test_llm_extraction())

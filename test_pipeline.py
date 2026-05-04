import asyncio
import json
from app.processing.analyzer import analyze_post

def test_groq_extraction():
    print("🧪 Testing Groq extraction...")
    
    sample_text = "يا جماعة انا لقيت محفظة فيها بطاقة باسم احمد محمد في شارع عباس العقاد في مدينة نصر امبارح بليل، اللي يعرفه يخليه يكلمني على 01012345678"
    
    print("\n📝 Input Text:")
    print(sample_text)
    
    result = analyze_post(sample_text)
    
    print("\n✅ Extracted JSON:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Assertions
    assert result["type"] == "found", f"Expected 'found', got {result.get('type')}"
    assert result["item"] is not None, "Item should not be null"
    assert result["location"] is not None, "Location should not be null"
    assert result["contact"] == "01012345678", "Contact should be 01012345678"
    
    print("\n✨ Test passed!")

if __name__ == "__main__":
    test_groq_extraction()

#!/usr/bin/env python3

import asyncio
import requests
from PIL import Image
import io
from pathlib import Path

async def example_api_usage():
    """
    Example of how to use the Site Survey AI API
    """
    api_base = "http://localhost:8000"
    
    # Check if the API is running
    try:
        response = requests.get(f"{api_base}/")
        print("✅ API is running:", response.json())
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Start it with: python main.py")
        return
    
    # Get database stats
    stats = requests.get(f"{api_base}/stats").json()
    print("📊 Database stats:", stats)
    
    # Example: Analyze a survey (you would need actual images)
    print("\n🔍 To analyze a survey, use:")
    print("curl -X POST 'http://localhost:8000/analyze-survey' \\")
    print("  -F 'images=@path/to/image1.jpg' \\")
    print("  -F 'images=@path/to/image2.jpg' \\")
    print("  -F 'notes=Equipment inspection - check bolts and connections'")

def create_test_image():
    """Create a simple test image for demonstration"""
    from PIL import Image, ImageDraw
    
    # Create a 512x512 test image
    img = Image.new('RGB', (512, 512), color='lightgray')
    draw = ImageDraw.Draw(img)
    
    # Draw some simple "equipment" shapes
    # Rectangle (equipment housing)
    draw.rectangle([100, 100, 400, 300], fill='darkgray', outline='black', width=3)
    
    # Circles (bolts)
    bolt_positions = [(130, 130), (370, 130), (130, 270), (370, 270)]
    for x, y in bolt_positions:
        draw.ellipse([x-15, y-15, x+15, y+15], fill='silver', outline='black', width=2)
    
    # Line (connection/wire)
    draw.line([(250, 300), (250, 400)], fill='red', width=5)
    
    # Save test image
    img.save("test_equipment.jpg", "JPEG")
    print("📸 Created test image: test_equipment.jpg")
    return "test_equipment.jpg"

async def example_direct_usage():
    """
    Example of using the Site Survey AI components directly
    """
    from src.site_survey_ai.agents.survey_workflow import SurveyAnalysisWorkflow
    from PIL import Image
    
    # Create a test image
    test_image_path = create_test_image()
    
    # Load the test image
    image = Image.open(test_image_path)
    
    # Initialize the workflow
    print("🔄 Initializing Survey Analysis Workflow...")
    workflow = SurveyAnalysisWorkflow()
    await workflow.initialize()
    
    print("🔍 Running analysis on test image...")
    
    # Run the analysis
    result = await workflow.run_survey_analysis(
        images=[image],
        text_notes="Test equipment inspection - automated example",
        survey_id="test-001"
    )
    
    print("\n📊 Analysis Results:")
    print(f"Status: {result['overall_status']}")
    print(f"Confidence: {result['confidence_score']:.2f}")
    print(f"Report: {result['final_report'][:200]}...")
    
    # Clean up
    Path(test_image_path).unlink()

if __name__ == "__main__":
    print("🎯 Site Survey AI - Example Usage")
    print("=" * 40)
    
    choice = input("Choose example:\n1. API usage (requires running server)\n2. Direct usage\n> ")
    
    if choice == "1":
        asyncio.run(example_api_usage())
    elif choice == "2":
        asyncio.run(example_direct_usage())
    else:
        print("Invalid choice")
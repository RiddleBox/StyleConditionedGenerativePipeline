"""
Usage Examples for StyleConditionedGenerativePipeline

This file demonstrates how to use the pipeline in different modes.
"""

# Example 1: Manual Mode - Generate prompt for manual use in ChatGPT
def example_manual_mode():
    """
    Manual Mode: Generate a prompt that you can copy-paste into ChatGPT
    """
    from src.pipeline.manual_mode import ManualModePipeline
    
    # Define your desired style
    style = {
        "palette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"],
        "color_temperature": "warm",
        "color_harmony": "analogous",
        "saturation_level": 0.75,
        "brightness_level": 0.65,
        "contrast_level": 0.55,
        "line_style": "smooth",
        "line_weight": 0.6,
        "line_density": 0.5,
        "lighting_direction": "side",
        "lighting_quality": "soft",
        "shadow_intensity": 0.4,
        "composition_rule": "rule_of_thirds",
        "focal_point": "center",
        "depth_of_field": 0.6,
        "material_finish": "matte",
        "texture_scale": 0.5,
        "detail_level": 0.7
    }
    
    # Create pipeline
    pipeline = ManualModePipeline()
    
    # Generate prompt
    result = pipeline.generate_prompt_for_manual_use(
        style=style,
        subject="a serene mountain landscape at sunset"
    )
    
    # Save to file
    pipeline.save_prompt_to_file(result, "my_prompt.txt")
    
    print("Prompt generated and saved to my_prompt.txt")
    print("\nPrompt preview:")
    print(result["prompt"][:200] + "...")
    print("\nNow copy this prompt and paste it into ChatGPT Image Generator!")


# Example 2: Learning Mode - Optimize style from reference image
def example_learning_mode():
    """
    Learning Mode: Learn style from a reference image and optimize
    
    Note: This requires manual image generation in each iteration
    """
    from src.pipeline.learning_mode import LearningModePipeline
    from PIL import Image
    
    # Load reference image
    reference_image = Image.open("reference.jpg")
    
    # Define initial style (can be rough estimate)
    initial_style = {
        "palette": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"],
        "color_temperature": "warm",
        "saturation_level": 0.7,
        # ... other parameters
    }
    
    # Create pipeline
    pipeline = LearningModePipeline()
    
    # Run optimization loop
    # Note: You'll need to manually generate images in each iteration
    result = pipeline.run_learning_loop(
        reference_image=reference_image,
        initial_style=initial_style,
        subject="abstract art",
        max_iterations=5,
        target_score=0.85
    )
    
    print(f"Optimization complete!")
    print(f"Final score: {result['final_score']:.3f}")
    print(f"Iterations: {result['iterations']}")
    
    # Save optimized style to library
    pipeline.library.save_style(
        name="my_optimized_style",
        style=result['final_style']
    )


# Example 3: Auto Mode - Fully automated with API
def example_auto_mode():
    """
    Auto Mode: Fully automated style extraction and generation
    
    Requires: OPENAI_API_KEY environment variable
    """
    import os
    from src.pipeline.auto_mode import AutoModePipeline
    from PIL import Image
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set")
        return
    
    # Load reference image
    reference_image = Image.open("reference.jpg")
    
    # Create pipeline
    pipeline = AutoModePipeline(
        llm_provider="openai",
        dalle_model="dall-e-3",
        dalle_quality="standard"
    )
    
    # Estimate cost
    cost = pipeline.estimate_cost(mode="learning", num_iterations=5)
    print(f"Estimated cost: ${cost:.2f}")
    
    # Run learning mode (fully automated)
    result = pipeline.learn_from_reference(
        reference_image=reference_image,
        style_name="my_auto_style",
        subject="abstract art",
        max_iterations=5,
        target_score=0.85,
        save_to_library=True
    )
    
    print(f"Learning complete!")
    print(f"Final score: {result['final_score']:.3f}")
    print(f"Style saved to library as 'my_auto_style'")
    
    # Generate new image with learned style
    new_image = pipeline.generate_from_library(
        style_name="my_auto_style",
        subject="a cat in a garden",
        save_path="output.png"
    )
    
    print("New image generated and saved to output.png")


# Example 4: Production Mode - Fast generation from library
def example_production_mode():
    """
    Production Mode: Generate images using pre-saved styles
    
    Requires: OPENAI_API_KEY environment variable
    """
    import os
    from src.pipeline.production_mode import ProductionMode
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set")
        return
    
    # Create pipeline
    pipeline = ProductionMode(
        dalle_model="dall-e-3",
        dalle_quality="standard"
    )
    
    # List available styles
    styles = pipeline.list_available_styles()
    print(f"Available styles: {styles}")
    
    # Generate image
    image = pipeline.generate(
        style_name="my_optimized_style",
        subject="a futuristic cityscape",
        save_path="cityscape.png"
    )
    
    print("Image generated and saved to cityscape.png")
    
    # Batch generation
    subjects = [
        "a cat",
        "a dog",
        "a bird"
    ]
    
    images = pipeline.generate_batch(
        style_name="my_optimized_style",
        subjects=subjects,
        save_dir="batch_output/"
    )
    
    print(f"Generated {len(images)} images in batch_output/")


if __name__ == "__main__":
    print("StyleConditionedGenerativePipeline - Usage Examples")
    print("=" * 60)
    print("\n1. Manual Mode (no API required)")
    print("2. Learning Mode (manual iteration)")
    print("3. Auto Mode (fully automated, requires API)")
    print("4. Production Mode (fast generation, requires API)")
    print("\nUncomment the example you want to run:")
    
    # Uncomment one of these:
    # example_manual_mode()
    # example_learning_mode()
    # example_auto_mode()
    # example_production_mode()

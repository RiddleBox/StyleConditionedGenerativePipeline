"""
Manual Mode Pipeline for StyleConditionedGenerativePipeline

This module implements the manual mode where:
1. User provides a Style JSON
2. System generates a prompt using Prompt Generator
3. System outputs the prompt and instructions
4. User manually generates image in ChatGPT
5. User provides feedback (optional)

This mode is used to validate Prompt Generator quality before implementing automation.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

from ..core.schema import validate_style_json
from ..core.engine import StyleEngine
from ..core.prompt_generator import PromptGenerator


class ManualModePipeline:
    """Pipeline for manual image generation workflow"""
    
    def __init__(self):
        self.engine = StyleEngine()
        self.prompt_generator = PromptGenerator()
    
    def generate_prompt_for_manual_use(
        self,
        style_json: Dict[str, Any],
        subject: str = "",
        validate: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Generate a prompt from Style JSON for manual use in ChatGPT.
        
        Args:
            style_json: The style parameters
            subject: The subject to generate (default: "")
            validate: Whether to validate the Style JSON (default: True)
        
        Returns:
            Tuple of (success, result)
            - If success: result contains 'prompt', 'negative_prompt', 'instructions', 'normalized_style'
            - If failure: result contains 'error' and 'details'
        """
        # Step 1: Validate Style JSON
        if validate:
            is_valid, errors = validate_style_json(style_json)
            if not is_valid:
                return False, {
                    'error': 'Invalid Style JSON',
                    'details': errors
                }
        
        # Step 2: Normalize Style JSON
        try:
            normalized_style = self.engine.normalize(style_json)
        except Exception as e:
            return False, {
                'error': 'Style normalization failed',
                'details': str(e)
            }
        
        # Step 3: Generate style prompt (without subject)
        try:
            style_prompt = self.prompt_generator.generate(normalized_style)
            negative_prompt = self.prompt_generator.get_negative_prompt(normalized_style)
        except Exception as e:
            return False, {
                'error': 'Prompt generation failed',
                'details': str(e)
            }
        
        # Step 4: Combine subject with style prompt
        if subject:
            full_prompt = f"{subject}, {style_prompt}"
        else:
            full_prompt = style_prompt
        
        # Step 5: Generate instructions for user
        instructions = self._generate_instructions(full_prompt, negative_prompt)
        
        return True, {
            'prompt': full_prompt,
            'negative_prompt': negative_prompt,
            'normalized_style': normalized_style,
            'instructions': instructions
        }
    
    def _generate_instructions(self, prompt: str, negative_prompt: str) -> str:
        """Generate usage instructions for the user"""
        return f"""
=== Manual Image Generation Instructions ===

1. Copy the following prompt to ChatGPT (DALL-E 3):

---PROMPT START---
{prompt}
---PROMPT END---

---NEGATIVE PROMPT START---
{negative_prompt}
---NEGATIVE PROMPT END---

2. Generate the image in ChatGPT

3. Review the result:
   - Does it match the intended style?
   - Are the style parameters correctly reflected?
   - Any unexpected elements?

4. (Optional) Provide feedback for improvement

=== Tips ===
- DALL-E 3 in ChatGPT doesn't support negative prompts directly
- You may need to add negative constraints to the main prompt
- Generate 2-3 variations to see consistency
- Save all generated images for comparison

=== Next Steps ===
After generating images:
1. Evaluate if the style matches your expectations
2. If not satisfied, provide feedback on what's wrong
3. We'll adjust the Style JSON and try again

=== End Instructions ===
"""
    
    def save_prompt_to_file(
        self,
        prompt: str,
        negative_prompt: str,
        filepath: str,
        style_json: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save the generated prompt to a file.
        
        Args:
            prompt: The main prompt text
            negative_prompt: The negative prompt text
            filepath: Path to save the prompt
            style_json: Optional normalized style JSON to include
        
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'prompt': prompt,
                'negative_prompt': negative_prompt
            }
            
            if style_json is not None:
                data['style_json'] = style_json
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving prompt to file: {e}")
            return False
    
    def load_prompt_from_file(
        self,
        filepath: str
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Load a previously saved prompt from file.
        
        Args:
            filepath: Path to the saved prompt file
        
        Returns:
            Tuple of (success, data)
            - If success: data contains the loaded prompt dict
            - If failure: data contains error dict
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return True, data
        except Exception as e:
            return False, {'error': 'Failed to load prompt', 'details': str(e)}

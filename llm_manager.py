# llm_manager.py
import requests
import json
from typing import Dict, Any

class LLMManager:
    def __init__(self, model_name: str = "", base_url: str = "http://10.0.0.162:11434"):
        self.base_url = base_url
        self.model_name = model_name
    
    def generate_documentation(self, code_context: Dict) -> str:
        """Generate documentation using local LLM"""

        edited_wiki_file = "prev_output.md"

        # Read the manually edited wiki
        try:
            with open(edited_wiki_file, 'r', encoding='utf-8') as f:
                existing_context = f.read()
                if not existing_context:
                    prompt = self._build_prompt(code_context)
                else:
                    prompt = self._build_refinement_prompt(code_context, existing_context)
        except (FileNotFoundError, OSError):
            # File doesn't exist or can't be read
            prompt = self._build_prompt(code_context)


        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": "qwen2.5-coder:7b",
                      "prompt": prompt,
                      "stream":False,
                      "max-tokens":1000,
                      "temperature":0.1
                }
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                raise Exception("Error generating documentation: {response.status_code}")
                
        except Exception as e:
            raise Exception("Error connecting to LLM")
    
    def _build_prompt(self, code_context: Dict) -> str:
        """Build prompt for documentation generation"""
        
        # Create a summary of the codebase for the prompt
        code_summary = self._create_code_summary(code_context)
        
        prompt = f"""You are a senior software engineer doing  codebase analysis, your task is to create comprehensive document:

1. Find every comment that starts with `// #LLM_ATTENTION` followed by a number (like `// #LLM_ATTENTION 1`).
2. For each such comment, record:
   a. The number after `#LLM_ATTENTION`, if there is no number, make assumption
   b. The name of the class and method (function) that contains this comment.
   c. Try to interpret what the code before or after // #LLM_ATTENTION to figure out what it does approximately

3. Sort the recorded items by the number (ascending).

4. Output in Markdown , with each item in the format: `#LLM_READ <number>: In class <ClassName>, method <MethodName>: and the three lines of code`.

Here is the codebase summary:
{code_summary}



"""
        
        return prompt

    def _build_refinement_prompt(self, code_context: Dict, existing_doc: str) -> str:
            """Build prompt for refining existing documentation"""

            code_summary = self._create_code_summary(code_context)

            prompt = f"""You are a senior software engineer tasked with improving existing documentation in point forms.
            use this sequence as a base

    You have been given:
    1. A codebase analysis {code_summary}
    2. try to generate run squence based off {existing_doc}

    Please:
    1. Explain what this code trace sequence
    2. Add missing technical details from the code analysis
    3. Improve organization and clarity
    
    

    Return the improved documentation in Markdown format.
    """

            return prompt

    def _create_code_summary(self, code_context: Dict) -> str:
        """Create a concise summary of the codebase for the prompt"""
        
        summary = f"""
Project: {code_context.get('project_name', 'Unknown')}
Total Files: {code_context.get('total_files', 0)}
Languages: {', '.join(code_context.get('languages_used', []))}
Total Functions: {code_context.get('total_functions', 0)}
Total Classes: {code_context.get('total_classes', 0)}

Main Files:
"""
        
        # Include first few files with their key functions
        for file_analysis in code_context['files'][:10]:  # Limit to first 10 files
            summary += f"\n- {file_analysis['path']}"
            if file_analysis['functions']:
                func_names = [f['name'] for f in file_analysis['functions'][:5]]
                summary += f" (Functions: {', '.join(func_names)})"
        
        if len(code_context['files']) > 10:
            summary += f"\n... and {len(code_context['files']) - 10} more files"
        
        return summary
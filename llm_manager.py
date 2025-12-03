# llm_manager.py
import requests
import json
from typing import Dict, Any

class LLMManager:
    def __init__(self, model_name: str = "", base_url: str = "http://localhost:11435"):
        self.base_url = base_url
        self.model_name = model_name
    
    def generate_documentation(self, code_context: Dict) -> str:
        """Generate documentation using local LLM"""
        
        prompt = self._build_prompt(code_context)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_predict": 4000
                    }
                },
                timeout=1
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
        
        prompt = f"""You are a senior software engineer creating comprehensive documentation for a codebase.

CODEBASE SUMMARY:
{code_summary}

Please generate detailed technical documentation in Markdown format that includes:

1. **Project Overview**: High-level description of what this codebase does
2. **Architecture**: Main components and how they interact
3. **Key Functions**: Important functions and their purposes
4. **Usage**: How to use the main components
5. **Dependencies**: Key libraries and frameworks used
6. **Setup**: Basic setup instructions if apparent from the code

Be technical and specific. Reference actual file names, function names, and classes from the codebase.

Format your response as clean Markdown with appropriate headers and code examples where relevant.
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
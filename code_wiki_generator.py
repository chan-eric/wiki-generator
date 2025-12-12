# code_wiki_generator.py
import os
import argparse
from pathlib import Path
import json
from datetime import datetime

from code_analyzer import CodeAnalyzer
from llm_manager import LLMManager

class SimpleCodeWikiGenerator:

    def __init__(self, model_name: str = ""):
        self.model_name = model_name
        self.analyzer = CodeAnalyzer()
        self.llm_manager = LLMManager(model_name)
    
    def generate_wiki(self, code_folder: str, output_file: str = "code_wiki.md"):
        """Main method to generate wiki from code folder"""
        
        print(f"📁 Analyzing code in: {code_folder}")
        
        # Analyze codebase
        analysis = self.analyzer.analyze_directory(code_folder)

        if not analysis['files']:
            print("❌ No code files found in the specified folder!")
            return None
        
        # Calculate total functions from all files
        total_functions = sum(len(file.get('functions', [])) for file in analysis['files'])
        total_classes = sum(len(file.get('classes', [])) for file in analysis['files'])
        
        print(f"📊 Found {len(analysis['files'])} files, {total_functions} functions, {total_classes} classes")
        print(f"🌐 Languages: {', '.join(analysis['languages_used'])}")
        
        # Generate documentation using LLM
        print("🤖 Generating documentation with LLM...")
        try:
            documentation = self.llm_manager.generate_documentation(analysis)
        
            # Save wiki
            self._save_wiki(documentation, analysis, output_file)
            
            print(f"✅ Wiki generated successfully: {output_file}")
        except Exception as e:
            # log it, return something safe, whatever you need
            print(f"❌ Failed to generate documentation: {e}")
            documentation = None  # or "" or some fallback
    
    def _save_wiki(self, documentation: str, analysis: dict, output_file: str):
        """Save the generated wiki to a markdown file"""
        
        # Calculate totals
        total_functions = sum(len(file.get('functions', [])) for file in analysis['files'])
        total_classes = sum(len(file.get('classes', [])) for file in analysis['files'])
        
        wiki_content = f"""# Codebase Documentation

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Total files: {len(analysis['files'])}*

{documentation}
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(wiki_content)
    
    def _generate_file_tree(self, analysis: dict) -> str:
        """Generate a file tree structure"""
        tree_lines = ["```"]
        for file_analysis in analysis['files']:
            tree_lines.append(f"📄 {file_analysis['path']}")
            for func in file_analysis['functions']:
                tree_lines.append(f"   └── 🎯 {func['name']}")
        tree_lines.append("```")
        return "\n".join(tree_lines)
    
    def _generate_detailed_analysis(self, analysis: dict) -> str:
        """Generate detailed analysis of each file"""
        detailed_content = []
        
        for file_analysis in analysis['files']:
            detailed_content.append(f"### 📁 {file_analysis['path']}")
            detailed_content.append(f"**Language:** {file_analysis['extension']}")
            
            if file_analysis['functions']:
                detailed_content.append("#### Functions:")
                for func in file_analysis['functions']:
                    detailed_content.append(f"- `{func['name']}` (Line {func['line']})")
                    if func.get('docstring'):
                        detailed_content.append(f"  - *{func['docstring']}*")
            
            if file_analysis['classes']:
                detailed_content.append("#### Classes:")
                for cls in file_analysis['classes']:
                    detailed_content.append(f"- `{cls['name']}`")
            
            detailed_content.append("")  # Empty line between files
        
        return "\n".join(detailed_content)


def main():

    llm_model = "NT-java:latest"
    
    parser = argparse.ArgumentParser(description='Generate wiki documentation from codebase')
    parser.add_argument('folder', help='Path to code folder')
    parser.add_argument('-o', '--output', default='code_wiki.md', help='Output file name')
    parser.add_argument('-m', '--model', default=llm_model, help='LLM model to use')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.folder):
        print(f"❌ Error: Folder '{args.folder}' does not exist")
        return
    
    generator = SimpleCodeWikiGenerator(model_name=args.model)
    generator.generate_wiki(args.folder, args.output)


if __name__ == "__main__":
    main()
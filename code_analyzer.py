# code_analyzer.py
import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Any

class CodeAnalyzer:
    def __init__(self):
        self.supported_extensions = {

            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rs': 'rust',
            '.go': 'go',
            '.php': 'php',
            '.rb': 'ruby'
        }
    
    def analyze_directory(self, root_path: str) -> Dict[str, Any]:
        """Analyze entire codebase structure"""
        analysis = {
            'project_name': Path(root_path).name,
            'files': [],
            'total_files': 0,
            'total_functions': 0,
            'total_classes': 0,
            'languages_used': set(),
            'structure': {}
        }
        
        for file_path in Path(root_path).rglob('*'):
            if file_path.is_file() and file_path.suffix in self.supported_extensions:
                file_analysis = self.analyze_file(file_path)
                if file_analysis:
                    analysis['files'].append(file_analysis)
                    analysis['total_files'] += 1
                    analysis['total_functions'] += len(file_analysis['functions'])
                    analysis['total_classes'] += len(file_analysis['classes'])
                    analysis['languages_used'].add(self.supported_extensions[file_path.suffix])
        
        analysis['languages_used'] = list(analysis['languages_used'])
        return analysis
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze individual file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
            return None
        
        file_analysis = {
            'path': str(file_path.relative_to(file_path.parent.parent)),
            'name': file_path.name,
            'extension': file_path.suffix,
            'language': self.supported_extensions.get(file_path.suffix, 'unknown'),
            'content': content,
            'functions': self.extract_functions(content, file_path.suffix),
            'classes': self.extract_classes(content, file_path.suffix),
            'imports': self.extract_imports(content, file_path.suffix),
            'line_count': len(content.splitlines())
        }
        
        return file_analysis
    
    def extract_functions(self, content: str, extension: str) -> List[Dict]:
        """Extract function definitions based on language"""
        if extension == '.py':
            return self._extract_python_functions(content)
        elif extension in ['.js', '.ts']:
            return self._extract_javascript_functions(content)
        elif extension == '.java':
            return self._extract_java_functions(content)
        elif extension in ['.cpp', '.c']:
            return self._extract_cpp_functions(content)
        else:
            return self._extract_generic_functions(content, extension)
    
    def _extract_python_functions(self, content: str) -> List[Dict]:
        """Extract Python functions using AST"""
        functions = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node) or '',
                        'type': 'function'
                    })
        except Exception as e:
            # Fallback to regex for problematic files
            functions = self._extract_python_functions_regex(content)
        
        return functions
    
    def _extract_python_functions_regex(self, content: str) -> List[Dict]:
        """Fallback Python function extraction using regex"""
        functions = []
        pattern = r'def\s+(\w+)\s*\(([^)]*)\)'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            functions.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1,
                'args': [arg.strip() for arg in match.group(2).split(',') if arg.strip()],
                'docstring': '',
                'type': 'function'
            })
        
        return functions
    
    def _extract_javascript_functions(self, content: str) -> List[Dict]:
        """Extract JavaScript/TypeScript functions"""
        functions = []
        patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)',
            r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>',
            r'let\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>',
            r'(\w+)\s*\(([^)]*)\)\s*\{'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                functions.append({
                    'name': match.group(1),
                    'line': content[:match.start()].count('\n') + 1,
                    'args': [arg.strip() for arg in match.group(2).split(',') if arg.strip()],
                    'docstring': '',
                    'type': 'function'
                })
        
        return functions
    
    def _extract_java_functions(self, content: str) -> List[Dict]:
        """Extract Java methods"""
        functions = []
        pattern = r'(public|private|protected)\s+\w+\s+(\w+)\s*\(([^)]*)\)'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            functions.append({
                'name': match.group(2),
                'line': content[:match.start()].count('\n') + 1,
                'args': [arg.strip() for arg in match.group(3).split(',') if arg.strip()],
                'docstring': '',
                'type': 'method'
            })
        
        return functions
    
    def _extract_cpp_functions(self, content: str) -> List[Dict]:
        """Extract C++ functions"""
        functions = []
        pattern = r'\w+\s+(\w+)\s*\(([^)]*)\)'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            functions.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1,
                'args': [arg.strip() for arg in match.group(2).split(',') if arg.strip()],
                'docstring': '',
                'type': 'function'
            })
        
        return functions
    
    def _extract_generic_functions(self, content: str, extension: str) -> List[Dict]:
        """Generic function extraction for other languages"""
        functions = []
        # Simple pattern that works for many languages
        pattern = r'def\s+(\w+)|function\s+(\w+)|fn\s+(\w+)|fun\s+(\w+)'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            name = next((group for group in match.groups() if group), 'unknown')
            functions.append({
                'name': name,
                'line': content[:match.start()].count('\n') + 1,
                'args': [],
                'docstring': '',
                'type': 'function'
            })
        
        return functions
    
    def extract_classes(self, content: str, extension: str) -> List[Dict]:
        """Extract class definitions"""
        classes = []
        
        if extension == '.py':
            pattern = r'class\s+(\w+)'
        elif extension in ['.js', '.ts']:
            pattern = r'class\s+(\w+)'
        elif extension == '.java':
            pattern = r'class\s+(\w+)'
        else:
            pattern = r'class\s+(\w+)'
        
        matches = re.finditer(pattern, content)
        for match in matches:
            classes.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return classes
    
    def extract_imports(self, content: str, extension: str) -> List[str]:
        """Extract import statements"""
        imports = []
        
        if extension == '.py':
            pattern = r'^(import|from)\s+(\w+)'
        elif extension in ['.js', '.ts']:
            pattern = r'^import\s+.*from\s+[\'"]([^\'"]+)[\'"]'
        elif extension == '.java':
            pattern = r'^import\s+([^;]+);'
        else:
            return imports
        
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            imports.append(match.group(0).strip())
        
        return imports
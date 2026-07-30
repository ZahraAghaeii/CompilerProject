import re
import os

class LanguageDetector:
    def __init__(self):
        # نگاشت الگوهای Shebang به زبان‌ها
        self.shebang_patterns = {
            'python': r'^#!\s*/usr/bin/(env\s+)?python',
            'javascript': r'^#!\s*/usr/bin/(env\s+)?node',
            'bash': r'^#!\s*/(bin|usr/bin)/(env\s+)?(bash|sh)',
            'c_cpp': r'^#!\s*/usr/bin/(env\s+)?tcc'
        }

        # کلمات کلیدی و الگوهای مشخصه هر زبان
        self.language_features = {
            'bash': {
                'keywords': [r'\becho\b', r'\bdone\b', r'\bfi\b', r'\bexit\b', r'\bsource\b', r'\bexport\b'],
                'delimiters': [r'\$', r'\[\[', r'\]\]'],
                'weight': 1.0
            },
            'c_cpp': {
                'keywords': [r'\binclude\b', r'\bmain\b', r'\bint\b', r'\bprintf\b', r'\bcout\b', r'\bvoid\b', r'\bstruct\b', r'#define'],
                'delimiters': [r'\{', r'\}', r';'],
                'weight': 1.0
            },
            'python': {
                'keywords': [r'\bdef\b', r'\bimport\b', r'\bfrom\b', r'\bclass\b', r'\belif\b', r'\bself\b', r'\bNone\b', r'\bTrue\b', r'\bFalse\b'],
                'delimiters': [r':$'],
                'weight': 1.0
            },
            'javascript': {
                'keywords': [r'\bconst\b', r'\blet\b', r'\bvar\b', r'\bfunction\b', r'\bconsole\.log\b', r'\basync\b', r'\bawait\b', r'=>'],
                'delimiters': [r'\{', r'\}', r';'],
                'weight': 1.0
            },
            'java': {
                'keywords': [r'\bpublic\b', r'\bclass\b', r'\bstatic\b', r'\bvoid\b', r'\bSystem\.out\.println\b', r'\bextends\b', r'\bimplements\b'],
                'delimiters': [r'\{', r'\}', r';'],
                'weight': 1.0
            }
        }

        # نگاشت پسوند فایل‌ها
        self.extension_map = {
            '.sh': 'bash',
            '.bash': 'bash',
            '.c': 'c_cpp',
            '.cpp': 'c_cpp',
            '.h': 'c_cpp',
            '.hpp': 'c_cpp',
            '.py': 'python',
            '.js': 'javascript',
            '.java': 'java'
        }

    def detect(self, code: str, filename: str = None) -> dict:
        lines = code.splitlines()
        scores = {lang: 0.0 for lang in self.language_features}

        if not code.strip():
            return {"language": "Unknown", "confidence": 0.0, "scores": scores}

        # ۱. بررسی Shebang (خط اول)
        if lines:
            first_line = lines[0].strip()
            for lang, pattern in self.shebang_patterns.items():
                if re.match(pattern, first_line):
                    if lang in scores:
                        scores[lang] += 10.0  # وزن بالای Shebang

        # ۲. بررسی پسوند فایل
        if filename:
            ext = os.path.splitext(filename)[1].lower()
            if ext in self.extension_map:
                scores[self.extension_map[ext]] += 5.0

        # ۳. بررسی Indentation Style (مخصوص پایتون)
        indented_lines = [line for line in lines if line.startswith('    ') or line.startswith('\t')]
        has_block_delimiters = any('{' in line or '}' in line for line in lines)
        
        if len(indented_lines) > 0 and not has_block_delimiters:
            scores['python'] += 1.5

        # ۴. بررسی کلمات کلیدی و Delimiter Patterns
        for lang, features in self.language_features.items():
            for kw in features['keywords']:
                matches = len(re.findall(kw, code))
                scores[lang] += matches * 1.0

            for delim in features['delimiters']:
                matches = len(re.findall(delim, code, re.MULTILINE))
                scores[lang] += matches * 0.3

        # ۵. محاسبه نهایی درصد اطمینان
        total_score = sum(scores.values())
        if total_score == 0:
            return {"language": "Unknown", "confidence": 0.0, "scores": {lang: 0.0 for lang in self.language_features}}

        best_lang = max(scores, key=scores.get)
        confidence = round((scores[best_lang] / total_score) * 100, 2)

        normalized_scores = {
            lang: round((score / total_score) * 100, 2)
            for lang, score in scores.items()
        }

        return {
            "language": best_lang,
            "confidence": confidence,
            "scores": normalized_scores
        }
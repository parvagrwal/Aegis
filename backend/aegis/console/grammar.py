import re

class CommandParser:
    def __init__(self):
        self.hex_map = {
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
            "alpha": "a", "a": "a", "bravo": "b", "b": "b",
            "charlie": "c", "c": "c", "delta": "d", "d": "d",
            "echo": "e", "e": "e", "foxtrot": "f", "f": "f"
        }
        
    def parse(self, text: str) -> dict:
        text = text.lower()
        
        # Check for confirm intent
        confirm_match = re.search(r"confirm\s+(.*)", text)
        if confirm_match:
            code = self._spoken_to_string(confirm_match.group(1))
            return {"intent": "CONFIRM", "code": code}
            
        # Check for investigate intent
        inv_match = re.search(r"investigate address ending in\s+(.*)", text)
        if inv_match:
            suffix = self._spoken_to_string(inv_match.group(1))
            return {"intent": "INVESTIGATE", "suffix": suffix}
            
        return {"intent": "UNKNOWN"}
        
    def _spoken_to_string(self, spoken: str) -> str:
        words = spoken.split()
        res = ""
        for w in words:
            if w in self.hex_map:
                res += self.hex_map[w]
            elif w.isdigit():
                res += w
        return res

from typing import List

def lengthOfLongestSubstring(s: str) -> int:
    max_length = 0
    for i in range(len(s)):
        letters = set()
        for j in range(i, len(s)):
            if s[j] in letters:
                break
            letters.add(s[j])
        max_length = max(max_length, len(letters))
    return max_length


s = "xbawtvebluuagttbeqbihnlucpmg"
print(lengthOfLongestSubstring(s))
from django import template

register = template.Library()

@register.filter
def country_flag(country_code):
    """Convert country code to flag emoji"""
    if not country_code or len(country_code) != 2:
        return ""
    
    # Convert country code to flag emoji
    # Each letter is converted to its regional indicator symbol
    flag = ""
    for char in country_code.upper():
        flag += chr(ord(char) - ord('A') + 0x1F1E6)
    
    return flag
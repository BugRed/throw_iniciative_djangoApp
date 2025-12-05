from django import template
    
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Acessa um item de dicionário usando uma chave variável no template."""
    return dictionary.get(key)

@register.filter
def add_sign(value):
    """Adiciona sinal de '+' a números positivos, ou retorna o valor se for negativo/zero."""
    try:
        val = int(value)
        # Retorna "+X" se positivo, ou o número (incluindo negativos e zero)
        return f"+{val}" if val > 0 else str(val)
    except (ValueError, TypeError):
        # Retorna o valor original se não for um número válido (ex: None, string)
        return value
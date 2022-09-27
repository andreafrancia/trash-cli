try:
    from urllib import quote as url_quote
except ImportError:
    from urllib.parse import quote as url_quote
url_quote = url_quote

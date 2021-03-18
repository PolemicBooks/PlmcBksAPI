BASE = """\
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:dc="http://purl.org/dc/terms/"
      xmlns:opds="http://opds-spec.org/2010/catalog">
  <title>{}</title>
  <updated>{}</updated>
  <link rel="http://opds-spec.org/image"
      href="{}"
      type="image/jpeg"/>
  <link type="application/atom+xml" title="Buscar no Polemic Books" href="/opds/search/books?query_name={{searchTerms}}" rel="search"/>
  <author>
    <name>Polemic Books</name>
    <uri>https://t.me/PolemicBooks</uri>
    <email>46784020+SnwMds@users.noreply.github.com</email>
  </author>
  <subtitle>{}</subtitle>
"""

ITEM_BASE = """\
  <entry>
    <title>{}</title>
    <id>{}</id>
    <link rel="http://opds-spec.org/image"
        href="{}"
        type="image/jpeg"/>
    <updated>{}</updated>
    <link type="application/atom+xml" href="/opds/{}"/>
    <content type="text">{}</content>
  </entry>
"""

NEXT_PAGE_BASE = """\
  <link type="application/atom+xml" title="Próxima" href="{}" rel="next"/>
"""

SELF_BASE = """\
  <link type="application/atom+xml" href="{}" rel="self"/>
"""

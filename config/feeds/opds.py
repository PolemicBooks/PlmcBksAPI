BASE = """\
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:dc="http://purl.org/dc/terms/"
      xmlns:opds="http://opds-spec.org/2010/catalog"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
  <title>{}</title>
  <updated>{}</updated>
  <link rel="http://opds-spec.org/image"
      href="{}"
      type="image/jpeg"/>
  <icon>https://polemicbooks.github.io/images/polemicbooks.jpg</icon>
  <link rel="search"
      href="/opds/search/books?query_name={{searchTerms}}"
      type="application/atom+xml"
      title="Buscar no Polemic Books"/>
  <author>
    <name>Polemic Books</name>
    <uri>https://t.me/PolemicBooks</uri>
    <email>plmcbks@pm.me</email>
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
    <link type="application/atom+xml"
        href="/opds/{}"/>
    <content type="text">{}</content>
  </entry>
"""

NEXT_PAGE_BASE = """\
  <link rel="next"
      href="{}"
      type="application/atom+xml"
      title="Próxima"/>
"""

SELF_BASE = """\
  <link rel="self"
      href="{}"
      type="application/atom+xml"/>
"""

RELATED_BASE = """\
  <link rel="related"
      href="{}"
      title="{}"/>
"""
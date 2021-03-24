from ..urls import urls

BASE = f"""\
<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Polemic Books</title>
    <link>https://t.me/PolemicBooks</link>
    <description>Últimos livros adicionados</description>
    <language>pt-BR</language>
    <category>Livros</category>
    <ttl>60</ttl>
    <atom:link href="{urls.API_URL + "/rss"}" rel="self" type="application/rss+xml" />
{{}}
  </channel>
</rss>
"""

ITEM_BASE = """\
    <item>
      <title>{}</title>
      <link>{}</link>
      <guid isPermaLink="true">{}</guid>
      <enclosure url="{}" length="{}" type="{}"/>
      <author>{}</author>
      <pubDate>{}</pubDate>
      <description>{}</description>
    </item>
"""
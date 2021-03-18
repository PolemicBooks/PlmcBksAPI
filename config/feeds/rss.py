from ..urls import urls

BASE = """\
<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0">
  <channel>
    <title>Polemic Books</title>
    <link>https://t.me/PolemicBooks</link>
    <description>Últimos livros adicionados</description>
    <language>pt-BR</language>
    <category>Livros</category>
    <ttl>60</ttl>
{}
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
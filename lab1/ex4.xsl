<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/1999/xhtml">
    <xsl:output
        method="xml"
        doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"
        doctype-public="-//W3C//DTD XHTML 1.1//EN"
        indent="yes"
    />

<xsl:template match="/">
  <html>
      <body>
          <h2 align="center">Smartphones</h2>
          <table border="1" align="center">
                <tr bgcolor="red">
                    <th>Description</th>
                    <th>Price</th>
                    <th>Image</th>
                </tr>
                <xsl:for-each select="data/article">
                    <tr>
                        <td align="center">
                            <p><xsl:value-of select="@description"/></p>
                        </td>
                        <td align="center">
                            <p><xsl:value-of select="price"/></p>
                        </td>
                        <td>
                            <xsl:apply-templates select="image"/>
                        </td>
                    </tr>
                </xsl:for-each>
          </table>
      </body>
  </html>
</xsl:template>

<xsl:template match="image">
<p> <img src="{.}"/> </p>
</xsl:template>

</xsl:stylesheet>
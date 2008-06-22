<xsl:stylesheet version = '1.0'
     xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>

<!-- ###################################################################### -->

<xsl:template match="/">
    <html>
        <head>
            <title>Airs Series Overview</title>
        </head>
        <body>
            <h1>Airs Series Overview</h1>
            <table>
                <tr>
                    <td><u><b>Series Name</b></u></td>
                    <td><u><b># Episodes  </b></u></td>
                </tr>
                <xsl:for-each select="airs/series/item">
                    <tr>
                        <td>
                          <a>
                              <xsl:attribute name="href">series?id=<xsl:value-of select="@id"/></xsl:attribute>
                              <xsl:value-of select="@name"/>
                          </a>
                        </td>
                        <td><xsl:value-of select="@count" /></td>
                    </tr>
                </xsl:for-each>
            </table>
        </body>
    </html>
</xsl:template>

</xsl:stylesheet>
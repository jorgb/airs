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
                <xsl:for-each select="airs/series/item">
                    <tr>
                        <td><a>
                                <xsl:attribute name="href">http://127.0.0.1/airs/series_select?id=<xsl:value-of select="@id"/></xsl:attribute>
                                <xsl:value-of select="@name"/>
                            </a>     
                        </td>
                    </tr>
                </xsl:for-each>
            </table>
        </body>
    </html>
</xsl:template>

</xsl:stylesheet>
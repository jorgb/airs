<xsl:stylesheet version = '1.0'
     xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>

<!-- ###################################################################### -->

<xsl:template match="/">
    <html>
        <head>
            <link rel="stylesheet" type="text/css" href="www/airs.css" />

            <title>Airs Series Overview</title>
        </head>
        <body>
            <div id="overall">
              <div id="title">Airs Series Overview</div>
              <div id="series_area">
                <table>
                    <tr>
                        <td><div id="sheader">Series Name</div></td>
                        <td><div id="eheader"># Episodes</div></td>
                    </tr>
                    <xsl:for-each select="airs/series/item">
                        <tr>
                            <td class="">
                              <div id="seriestitle">
                                <a>
                                    <xsl:attribute name="class">series_name</xsl:attribute>
                                    <xsl:attribute name="href">series?id=<xsl:value-of select="@id"/></xsl:attribute>
                                    <xsl:value-of select="@name"/>
                                </a>
                              </div>
                            </td>
                            <td><div id="seriescount"><xsl:value-of select="@count"/></div></td>
                        </tr>
                    </xsl:for-each>
                </table>
              </div>
            </div>
        </body>
    </html>
</xsl:template>

</xsl:stylesheet>
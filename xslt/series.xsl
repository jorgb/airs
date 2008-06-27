<xsl:stylesheet version = '1.0'
     xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>

<!-- ###################################################################### -->

<xsl:template match="/">
    <html>
        <head>
            <link rel="stylesheet" type="text/css" href="www/screen/airs.css" />

            <title>Airs Series Overview</title>
        </head>
        <body>
            <div id="overall">
              
              <div id="title">Airs Series Overview</div>

              <div id="series_area">

                <table>
                    <!-- Main Table Header -->
                    <tr class="captionrow">
                        <td class="header"><div id="headertext">Series Name</div></td>
                        <td class="header"><div id="headertext"># Episodes</div></td>
                    </tr>
                    
                    <!-- Repeating table rows per series item -->
                    <xsl:for-each select="airs/series/item">
                      <tr>
                        <!-- Alternating table color cosmetics -->
                        <xsl:if test="position() mod 2 =0 ">
                          <xsl:attribute name="class">evenrow</xsl:attribute>
                        </xsl:if>
                        <xsl:if test="position() mod 2 =1 ">
                          <xsl:attribute name="class">oddrow</xsl:attribute>
                        </xsl:if>
                          
                        <td class="seriestitle">
                          <a>
                            <xsl:attribute name="class">series_name</xsl:attribute>
                            <xsl:attribute name="href">series?cmd_get_series=<xsl:value-of select="@id"/></xsl:attribute>
                            <xsl:value-of select="@name"/>
                          </a>
                        </td>
                        
                        <td>
                          <div id="seriescount"><xsl:value-of select="@count"/></div>
                        </td>
                      </tr>
                    </xsl:for-each>
                </table>
              </div>
            </div>
        </body>
    </html>
</xsl:template>

</xsl:stylesheet>

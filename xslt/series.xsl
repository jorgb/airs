<xsl:stylesheet version = '1.0'
     xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>

<!-- ###################################################################### -->

<xsl:template match="/">    
    <xsl:variable name="layout">
      <xsl:value-of select="/airs/options/layout" />
    </xsl:variable>

    <html>
        <head>
            <link rel="stylesheet" type="text/css" href="www/{$layout}/airs.css" />
            <title>Airs Series Overview</title>
        </head>
        <body>
            <div id="overall">
              
              <div id="title">Airs Series Overview</div>

              <div id="series_area">
                <table>
                    <!-- Main Table Header -->
                    <xsl:if test="$layout != 'mobile'">
                      <tr class="captionrow">
                        <td class="header"><div id="headertext">Series Name</div></td>
                        <td class="header" colspan="2"><div id="headertext">Not Watched</div></td>
                        <td class="header"><div id="headertext">Files</div></td>
                      </tr>
                    </xsl:if>
                    
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
                            <xsl:choose>
                                <xsl:when test="number(@mediacount) > 0">
                                    <xsl:attribute name="class">withmedia</xsl:attribute>
                                </xsl:when>
                                <xsl:when test="number(@mediacount) = 0 and number(@seencount) &lt; number(@count)">
                                    <xsl:attribute name="class">nomedia</xsl:attribute>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:attribute name="class">series</xsl:attribute>
                                </xsl:otherwise>
                            </xsl:choose>
                                
                            <xsl:attribute name="href">series?cmd_get_series=<xsl:value-of select="@id"/></xsl:attribute>
                            <xsl:value-of select="@name"/>
                          </a>
                          <xsl:if test="$layout = 'mobile'">
                            <xsl:text>  [</xsl:text><xsl:value-of select="@seencount"/><xsl:text>]  </xsl:text>
                            <xsl:text>  [</xsl:text>
                            <xsl:choose> 
                              <xsl:when test="number(@seencount) > 0">
                                <xsl:number value=" (100*number(@seencount)) div number(@count)"/>
                              </xsl:when>
                              <xsl:otherwise>0</xsl:otherwise>
                            </xsl:choose>%<xsl:text>]  </xsl:text>
                            <xsl:text>  [</xsl:text><xsl:value-of select="@mediacount"/><xsl:text>]</xsl:text>
                          </xsl:if>
                        </td>
                        
                        <xsl:if test="$layout != 'mobile'">
                          <td class="number">
                            <div id="seriescount"><xsl:value-of select="@seencount"/></div>
                          </td>
                          <td class="number">
                            <div id="seriescount">
                               <xsl:choose> 
                                 <xsl:when test="number(@seencount) > 0">
                                   <xsl:number value=" (100*number(@seencount)) div number(@count)"/>
                                 </xsl:when>
                                 <xsl:otherwise>0</xsl:otherwise>
                               </xsl:choose>%
                             </div> 
                          </td>
                          <td class="number">
                            <div id="seriescount"><xsl:value-of select="@mediacount"/></div>
                          </td>
                        </xsl:if>
                      </tr>
                    </xsl:for-each>
                </table>
              </div>
            </div>
        </body>
    </html>
</xsl:template>


</xsl:stylesheet>

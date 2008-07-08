<xsl:stylesheet version = '1.0'
     xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>

<!-- ###################################################################### -->

    <xsl:variable name="layout">
        <xsl:value-of select="/airs/options/layout" />
    </xsl:variable>

    <xsl:template match="/">    
      <html>
        <xsl:apply-templates select="/" mode="header" />
        <xsl:apply-templates select="/" mode="overview" />
      </html>
    </xsl:template>

<!-- ####################################################################### --> 

    <xsl:template match="/" mode="header">
      <head>
        <link rel="stylesheet" type="text/css" href="www/{$layout}/airs.css" />
        <title>Airs Series Overview</title>
      </head>
    </xsl:template>

<!-- ####################################################################### --> 

    <xsl:template match="/" mode="overview">
      <body>        
        <div id="overall">
          
          <div id="title">Airs Series Overview</div>
          
          <div id="series_area">
            <table>

               <!-- Main Table Header -->
               <xsl:if test="$layout != 'mobile'">
                 <tr class="captionrow">
                   <td class="header"><div id="headertext">Series Name</div></td>
                   <td class="header" colspan="2"><div id="headertext">Seen</div></td>
                   <td class="header"><div id="headertext">Files</div></td>
                 </tr>
              </xsl:if>

              <xsl:apply-templates select="/" mode="serieslist">
                <xsl:with-param name="filter">show-busy</xsl:with-param>
              </xsl:apply-templates>

              <xsl:apply-templates select="/" mode="serieslist">
                <xsl:with-param name="filter">show-done</xsl:with-param>
              </xsl:apply-templates>
                             
            </table>
          </div>


        </div>
      </body>               
    </xsl:template>

<!-- ####################################################################### --> 

    <xsl:template match="/" mode="serieslist">
        <xsl:param name="filter" />
        
        <!-- Repeating table rows per series item -->
        <xsl:for-each select="airs/series/item">
          <xsl:if test="($filter = 'show-busy' and (number(@mediacount) &gt; 0 or number(@seencount) &lt; number(@count))) or ($filter = 'show-done' and number(@mediacount) = 0 and (number(@seencount) = number(@count)))">              
              <!-- hide all cancelled series, that have no media files and no unseen episodes ALWAYS -->
              <xsl:if test="(number(@mediacount) &gt; 0) or (number(@seencount) &lt; number(@count)) or (@cancelled = '0')">
                  <tr>
                    <!-- Alternating table color cosmetics -->
                    <!-- 
                      <xsl:if test="position() mod 2 =0 ">
                        <xsl:attribute name="class">evenrow</xsl:attribute>
                      </xsl:if>
                      <xsl:if test="position() mod 2 =1 ">
                        <xsl:attribute name="class">oddrow</xsl:attribute>
                      </xsl:if>
                    -->
                    <xsl:attribute name="class">singlerow</xsl:attribute>
                      
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
                      <td class="percentage" colspan="2">
                        <!-- <div id="seriescount">
                           <xsl:choose> 
                             <xsl:when test="number(@seencount) > 0">
                               <xsl:number value=" (100*number(@seencount)) div number(@count)"/>
                             </xsl:when>
                             <xsl:otherwise>0</xsl:otherwise>
                           </xsl:choose>%
                        </div>
                       -->
                        
                        <div id="percdiff">
                            <div id="percinner">
                                <xsl:attribute name="style">
                                    <xsl:choose>
                                        <xsl:when test="number(@count) = 0 or number(@seencount) = 0">
                                          width:0;
                                          border-width:0px;
                                          background-color: transparent;
                                        </xsl:when>
                                        <xsl:otherwise>
                                          width:<xsl:number value= "(100*number(@seencount)) div number(@count)" />%;                                      
                                       </xsl:otherwise>
                                   </xsl:choose>
                                </xsl:attribute>
                                <xsl:choose>
                                  <xsl:when test="number(@seencount) > 0">
                                    <xsl:number value="(100*number(@seencount)) div number(@count)"/>
                                  </xsl:when>
                                  <xsl:otherwise><xsl:text>  </xsl:text>0</xsl:otherwise>
                                </xsl:choose>%
                            </div>        
                        </div>
                      </td>
                      <td class="number">
                        <div id="seriescount"><xsl:value-of select="@mediacount"/></div>
                      </td>
                    </xsl:if>
                  </tr>
             </xsl:if>
          </xsl:if>
      </xsl:for-each>
  </xsl:template>


</xsl:stylesheet>

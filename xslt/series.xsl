<xsl:stylesheet version = '1.0'
     xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>

<!-- ###################################################################### -->

   <xsl:output method="html" />
   <xsl:output doctype-system="http://www.w3.org/TR/html4/strict.dtd" />
   <xsl:output doctype-public="-//W3C//DTD HTML 4.01//EN" />
   <xsl:output indent="yes" />
   
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
        <xsl:if test="$layout != 'mobile'">        
          <link rel="stylesheet" type="text/css" href="www/airs-global.css" />        
        </xsl:if>        
        <link rel="stylesheet" type="text/css" href="www/{$layout}/airs.css" />
        <title>Airs Series Overview</title>
        
        <script type="text/javascript">
           <![CDATA[
               function kleuren() {
                  var seriesTable     = document.getElementById("series_table");
                  var seriesTableRows = seriesTable.getElementsByTagName("tr");
                  var k=0;
                  for( var i=1; i < seriesTableRows.length; i++ ) {
                     if( k == 0 ) {
                        seriesTableRows[ i ].className = "oddrow";
                        k = 1;
                     }
                     else if( k == 1 ) {
                        seriesTableRows[ i ].className = "evenrow";
                        k = 0;
                     }
                  }
               }
         ]]>
      </script>
      </head>
    </xsl:template>

<!-- ####################################################################### --> 

    <xsl:template match="/" mode="overview">
      <body onload="kleuren()">        
        <div id="overall">
          
          <div id="title">Airs Series Overview</div>
          
          <xsl:if test="number(/airs/series/@airedcount) &gt; 0">
            <div id="subcaption">
                <a class="subcaption" href="series?cmd_open_airs=nowdarnit">There are <xsl:value-of select="/airs/series/@airedcount" /> new aired episodes.</a>
            </div>
          </xsl:if>
          
          <div id="series_area">
            <table id="series_table">

               <!-- Main Table Header -->
               <xsl:if test="$layout != 'mobile'">
                 <tr class="captionrow">
                   <td class="header"><div class="headertext">Series Name</div></td>
                   <td class="header" colspan="2"><div class="headertext">Seen</div></td>
                   <td class="header"><div class="headertext">Files</div></td>
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
        
        <div id="copyright">Airs (c) Jorgen Bodde, ImpossibleSoft</div>        
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
                        
                        <div class="percdiff">
                            <div class="percinner">
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
                        <div class="seriescount"><xsl:value-of select="@mediacount"/></div>
                      </td>
                    </xsl:if>
                  </tr>
             </xsl:if>
          </xsl:if>
      </xsl:for-each>
  </xsl:template>


</xsl:stylesheet>

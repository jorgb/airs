<xsl:stylesheet version = '1.0'
     xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>

<!-- ###################################################################### -->

<xsl:template match="/">
    <html>
        <head>
            <title><xsl:value-of select="airs/episodes/@name" /></title>
            <link rel="stylesheet" type="text/css" href="www/screen/airs.css" />
        </head>
        <body>
            <div id="overall">
              <div id="title"><xsl:value-of select="airs/episodes/@name" /></div>
              <a class="subcaption" href="series">Return to episode list</a>
              <div id="titlespacing" />
              <table>
                  <!-- <tr class="captionrow">
                      <td class="header"><div id="headertext">Number</div></td>
                      <td class="header"><div id="headertext">Season</div></td>
                      <td class="header"><div id="headertext">Title</div></td>
                      <td colspan="2" class="actionheader"><div id="headertext">Actions</div></td>
                  </tr> -->
                  
                  <tr>
                    <td colspan="5" class="header"><div id="orphaned">Episodes</div></td>
                  </tr>
                  
                  <xsl:for-each select="airs/episodes/item">
                    <xsl:if test="@status != 4">
                        <tr>
                          <!-- Alternating table color cosmetics -->
                          <!-- <xsl:if test="position() mod 2 =0 ">
                            <xsl:attribute name="class">evenrow</xsl:attribute>
                          </xsl:if>
                          <xsl:if test="position() mod 2 =1 ">
                            <xsl:attribute name="class">oddrow</xsl:attribute>
                          </xsl:if> -->
                          
                          <!-- Variable that determines if an episode is already aired
                               the var 'aired' will contain 'no' if it is not aired, and
                               'yes' if it's aired (or in doubt) -->
                          <xsl:variable name="aired">
                            <xsl:choose>
                              <xsl:when test="@aired = ''">no</xsl:when>
                              <xsl:when test="/airs/options/@today &lt; @aired">no</xsl:when>
                              <xsl:otherwise>yes</xsl:otherwise>
                            </xsl:choose>
                          </xsl:variable>
                                      
                          <!-- Change the style of unaired items -->      
                          <xsl:variable name="epstyle">
                            <xsl:choose>               
                              <xsl:when test="$aired = 'yes'">epaired</xsl:when>
                              <xsl:when test="$aired = 'no'">epunaired</xsl:when>
                            </xsl:choose>
                          </xsl:variable>
                                                    
                          <td class="eprow"><div id="{$epstyle}"><xsl:value-of select="@number"/>.</div></td>
                          <td class="eprow"><div id="{$epstyle}"><xsl:value-of select="@season"/></div></td>
                          <td class="eprow">
                            <div id="{$epstyle}"><xsl:value-of select="@title"/></div>
                          </td>
                          <td></td>
                          <td>
                            <!-- <xsl:if test="$aired = 'yes'"> -->
                              <a>
                                <xsl:attribute name="href">series?cmd_mark_seen=<xsl:value-of select="@id"/></xsl:attribute>
                                <img src="www/screen/icon_check.png" />
                              </a>
                            <!-- </xsl:if> -->     
                          </td>
                        </tr>
                        <!-- If we have files to display prepare a table and list them -->
                        <xsl:if test="count(files/file) &gt; 0">
                          <xsl:for-each select="files/file">
                            <tr>
                              <td></td>
                              <td colspan="2">
                                <a>
                                  <xsl:attribute name="href">series?cmd_play_file=<xsl:value-of select="@filepath"/></xsl:attribute>
                                  <xsl:attribute name="class">playfile</xsl:attribute>
                                  <xsl:value-of select="@filename"/>
                                </a>
                              </td>
                              <td>
                                <img src="www/screen/icon_delete.png" />
                              </td>
                              <td>
                              </td>                          
                            </tr>
                          </xsl:for-each>
                        </xsl:if>       <!-- <xsl:if test="count(files/file) &gt; 0"> -->
                      </xsl:if>           <!-- <xsl:if test="@status != 4"> -->
                  </xsl:for-each>
                  <tr>
                    <td><br/></td>
                  </tr>                  
                  <xsl:if test="count(airs/orphans/file) &gt; 0">
                    <tr>
                      <td colspan="5" class="header"><div id="orphaned">Orphaned Media Files</div></td>
                    </tr>
                    <xsl:for-each select="airs/orphans/file">
                      <tr>
                        <td></td>
                        <td colspan="2">
                          <a>
                            <xsl:attribute name="href">series?cmd_play_file=<xsl:value-of select="@filepath"/></xsl:attribute>
                            <xsl:attribute name="class">playfile</xsl:attribute>
                            <xsl:value-of select="@filename"/>
                          </a>
                        </td>
                        <td>
                          <img src="www/screen/icon_delete.png" />
                        </td>
                        <td>
                        </td>
                      </tr>
                    </xsl:for-each>      <!-- <xsl:for-each select="airs/orphans/file"> --> 
                  </xsl:if>                <!-- <xsl:if test="count(airs/orphans/file) &gt; 0"> --> 
              </table>
            </div>
            
            <table>
            </table>
        </body>
    </html>
</xsl:template>

</xsl:stylesheet>

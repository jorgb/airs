<xsl:stylesheet version = '1.0'
     xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>

<!-- ###################################################################### -->

<xsl:template match="/airs/episodes">
    <html>
        <head>
            <title><xsl:value-of select="@name" /></title>
            <link rel="stylesheet" type="text/css" href="www/airs.css" />
        </head>
        <body>
            <div id="overall">
              <div id="title"><xsl:value-of select="@name" /></div>
              <table>
                  <tr class="captionrow">
                      <td class="header"><div id="headertext">Number</div></td>
                      <td class="header"><div id="headertext">Season</div></td>
                      <td class="header"><div id="headertext">Title</div></td>
                      <td class="header"><div id="headertext">Actions</div></td>
                  </tr>
                  
                  <xsl:for-each select="item">
                    <tr>
                      <!-- Alternating table color cosmetics -->
                      <!-- <xsl:if test="position() mod 2 =0 ">
                        <xsl:attribute name="class">evenrow</xsl:attribute>
                      </xsl:if>
                      <xsl:if test="position() mod 2 =1 ">
                        <xsl:attribute name="class">oddrow</xsl:attribute>
                      </xsl:if> -->

                      <td class="eprow"><div id="eptext"><xsl:value-of select="@number"/></div></td>
                      <td class="eprow"><div id="eptext"><xsl:value-of select="@season"/></div></td>
                      <td class="eprow">
                        <div id="epcaption"><xsl:value-of select="@title"/></div>
                      </td>
                      <td>
                        <a>
                          <xsl:attribute name="href">series?seen=<xsl:value-of select="@id"/></xsl:attribute>
                          <img src="www/icon_delete_big.png" />
                        </a>     
                      </td>
                    </tr>
                    <!-- If we have files to display prepare a table and list them -->
                    <xsl:if test="count(files/file) &gt; 0">
                      <xsl:for-each select="files/file">
                        <tr valign="center">
                          <td colspan="3" >
                            <img src="www/icon_play_large.png" />
                            <img src="www/icon_delete_big.png" />
                            <img src="www/icon_archive_big.png" />
                            <a>
                              <xsl:attribute name="href">series?play=<xsl:value-of select="@filepath"/></xsl:attribute>
                              <xsl:value-of select="@filename"/>
                            </a>
                          </td>
                        </tr>
                      </xsl:for-each>
                    </xsl:if>
                  </xsl:for-each>
              </table>
            </div>
        </body>
    </html>
</xsl:template>

</xsl:stylesheet>
<xsl:stylesheet version = '1.0'
     xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>

<!-- ###################################################################### -->

<xsl:template match="/airs/episodes">
    <html>
        <head>
            <title><xsl:value-of select="@name" /></title>
        </head>
        <body>
            <img src="www/icon_about.png" /><br/>
            <h1><xsl:value-of select="@name" /></h1>
            <table>
                <tr>
                    <td><u><b>Number</b></u></td>
                    <td><u><b>Season</b></u></td>
                    <td><u><b>Title</b></u></td>
                    <td><u><b>Actions</b></u></td>
                </tr>
                <xsl:for-each select="item">
                    <tr>
                        <td><xsl:value-of select="@number"/></td>
                        <td><xsl:value-of select="@season"/></td>
                        <td>
                          <xsl:value-of select="@title"/>
                        
                          <!-- If we have files to display prepare a table and list them -->
                          <xsl:if test="count(files/file) &gt; 0">
                            <br/>
                            <table>
                              <xsl:for-each select="files/file">
                                <tr>
                                  <td>
                                  </td>
                                  <td>
                                    <a>
                                      <xsl:attribute name="href">series?play=<xsl:value-of select="@filepath"/></xsl:attribute>
                                      <xsl:value-of select="@filename"/>
                                    </a>
                                  </td>
                                  <td>
                                    <a>
                                      <xsl:attribute name="href">series?delete=<xsl:value-of select="@filepath"/></xsl:attribute>
                                      [DELETE]
                                    </a>
                                  </td>
                                  <td>
                                    <a>
                                      <xsl:attribute name="href">series?archive=<xsl:value-of select="@filepath"/></xsl:attribute>
                                      [ARCHIVE]
                                    </a>
                                  </td>
                                </tr>
                              </xsl:for-each>
                            </table>
                          </xsl:if>
                        </td>
                        <td>
                          <a>
                              <xsl:attribute name="href">series?seen=<xsl:value-of select="@id"/></xsl:attribute>
                              [MARK SEEN]
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
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" indent="no"/>
  <xsl:preserve-space elements="line"/>

  <xsl:template match="/">
      <div class="song">

        <xsl:apply-templates select="/song/title"/>
        
        <div class="songbody">
          <xsl:apply-templates/> <!-- if we don't want the title do this: select="/song/chunk"/>-->
        </div>

      </div>
  </xsl:template>

  <xsl:template match="title">
    <h2 class="songtitle">
      <xsl:value-of select="/song/title"/>
    </h2>
  </xsl:template>
  
  <xsl:template match="chunk[@type='verse']">
    <div class="verse">
      <span class="versenum"><xsl:number count="chunk[@type='verse']"/>)</span>
      <xsl:apply-templates/>
  </div>
  </xsl:template>
  <xsl:template match="chunk[@type='chorus']">
    <div class="chorus">
      <b>Chorus:</b>
      <xsl:apply-templates/>
    </div>
  </xsl:template>
                                                        
  <xsl:template match="line">
    <div class="line"><xsl:apply-templates/></div>
  </xsl:template>

  <xsl:template match="c"><span class="cordouter"><span class="cordinner"><xsl:value-of select="text()"/></span></span></xsl:template>

  <xsl:template match="text()"><pre class="text"><xsl:value-of select="."/></pre></xsl:template>

</xsl:stylesheet>

<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" indent="no"/>
  <xsl:preserve-space elements="line"/>

  <xsl:template match="/">
      <div class="song">

        <xsl:apply-templates/>

      </div>
  </xsl:template>

  <xsl:template match="title">
    <h2 class="songtitle">
      <xsl:value-of select="/song/title"/>
    </h2>
  </xsl:template>
  
  <xsl:template match="categories">
    <pre id="categories">
      <xsl:apply-templates/>
    </pre>
  </xsl:template>

  <xsl:template match="chunk[@type='verse']">
    <div class="verse">
      <span class="versenum"><xsl:number count="chunk[@type='verse']"/>)</span>
      <xsl:apply-templates/>
    </div>
  </xsl:template>
   
  <xsl:template match="chunk[@type='pre-chorus']">
    <div class="non_verse">
      <i>Pre-Chorus:</i>
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="chunk[@type='chorus']">
    <div class="non_verse">
      <i>Chorus:</i>
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="chunk[@type='final chorus']">
    <div class="non_verse">
      <i>Final Chorus:</i>
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="chunk[@type='bridge']">
    <div class="non_verse">
      <i>Bridge:</i>
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="chunk[@type='ending']">
    <div class="non_verse">
      <i>Ending:</i>
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="chunk[@type='no label']">
    <div class="non_verse">
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="author">
    <div class="author">
      <xsl:apply-templates/>
    </div>
  </xsl:template>
  
  <xsl:template match="cclis">
    <div class="cclis">
      <xsl:apply-templates/>
    </div>
  </xsl:template>
  
  <xsl:template match="introduction">
    <div class="introduction">
      <xsl:apply-templates/>
    </div>
  </xsl:template>
  
  <xsl:template match="copyright">
    <div class="copyright">
      <b>
        <xsl:apply-templates/>
      </b>
    </div>
  </xsl:template>

  <xsl:template match="line">
    <div class="line"><xsl:apply-templates/></div>
  </xsl:template>

  <xsl:template match="c"><span class="cordouter"><span class="cordinner"><xsl:value-of select="text()"/></span></span></xsl:template>

  <xsl:template match="text()"><pre class="text"><xsl:value-of select="."/></pre></xsl:template>

</xsl:stylesheet>

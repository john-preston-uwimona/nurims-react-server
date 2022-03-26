<?xml version='1.0'?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:d="http://docbook.org/ns/docbook"
  xmlns:fo="http://www.w3.org/1999/XSL/Format"
  version="1.0">

  <xsl:import href="./docbook.xsl"/>

  <xsl:param name="title.font.family">ITC-Officiana-San-Standard-Book</xsl:param>
  <xsl:param name="body.font.family">ITC-Officiana-San-Standard-Book</xsl:param>
  <xsl:param name="double.sided">1</xsl:param>
  <xsl:param name="force.blank.pages" select="0"></xsl:param>
  <xsl:param name="generate.toc" select="'article toc'"/>
  <xsl:param name="page.height.portrait">11in</xsl:param>
  <xsl:param name="page.width.portrait">8.5in</xsl:param>
  <xsl:param name="page.margin.inner">0.50in</xsl:param>
  <xsl:param name="page.margin.outer">0.50in</xsl:param>
  <xsl:param name="page.margin.top">0.2in</xsl:param>
  <xsl:param name="page.margin.bottom">0.2in</xsl:param>
  <xsl:param name="body.margin.top">0.6in</xsl:param>
  <xsl:param name="body.margin.bottom">0.25in</xsl:param>
  <xsl:param name="body.start.indent">0in</xsl:param>
  <xsl:param name="body.margin.inner">0in</xsl:param>
  <xsl:param name="body.margin.outer">0in</xsl:param>
  <xsl:param name="body.font.master">10</xsl:param>
  <xsl:param name="header.rule">0</xsl:param>
  <xsl:param name="header.column.widths">2 4 2</xsl:param>
  <xsl:param name="footer.column.widths">10 0 3</xsl:param>
  <xsl:param name="footer.rule">0</xsl:param>
  <xsl:param name="table.footnote.number.symbols">123456</xsl:param>
  <xsl:param name="table.layout">fixed</xsl:param>
  <xsl:param name="region.before.extent">0.15in</xsl:param>
  <xsl:param name="region.after.extent">0.3in</xsl:param>

  <xsl:attribute-set name="toc.margin.properties">
    <xsl:attribute name="start-indent">0in</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="toc.line.properties">
    <xsl:attribute name="font-size">12pt</xsl:attribute>
  </xsl:attribute-set>

  <xsl:template match="processing-instruction('hard-pagebreak')">
    <fo:block break-after='page'/>
  </xsl:template>

  <xsl:template name="head.sep.rule">
    <xsl:param name="pageclass"/>
    <xsl:param name="sequence"/>
    <xsl:param name="gentext-key"/>

    <xsl:attribute name="border-bottom-width">2.0pt</xsl:attribute>
    <xsl:attribute name="border-bottom-style">solid</xsl:attribute>
    <xsl:attribute name="border-bottom-color">black</xsl:attribute>
  </xsl:template>


  <xsl:attribute-set name="header.content.properties">
    <xsl:attribute name="font-style">normal</xsl:attribute>
    <xsl:attribute name="font-size">10pt</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="footer.content.properties">
    <xsl:attribute name="font-style">normal</xsl:attribute>
    <xsl:attribute name="font-size">10pt</xsl:attribute>
  </xsl:attribute-set>

  <xsl:template name="header.content">
    <xsl:param name="pageclass" select="''"/>
    <xsl:param name="sequence" select="''"/>
    <xsl:param name="position" select="''"/>
    <xsl:param name="gentext-key" select="''"/>

    <fo:block>
      <xsl:choose>
        <xsl:when test="$position = 'left'">
          <fo:block>
            Date: <xsl:value-of select="d:info/d:date"/>
          </fo:block>
          <fo:block>
            &#160;
          </fo:block>
          <fo:block>
            Page: <fo:page-number/>
          </fo:block>
        </xsl:when>

        <xsl:when test="$position = 'right'">
          <fo:block>
            <xsl:value-of select="d:info/d:publisher"/>
          </fo:block>
          <fo:block>
            <xsl:value-of select="d:info/d:address"/>
          </fo:block>
          <fo:block>
            <xsl:value-of select="d:info/d:address1"/>
          </fo:block>
        </xsl:when>

        <xsl:when test="$position = 'center'">
          <fo:block>
            <xsl:value-of select="d:info/d:title"/>
          </fo:block>
        </xsl:when>

      </xsl:choose>
    </fo:block>
  </xsl:template>

  <xsl:template name="footer.content">
    <xsl:param name="pageclass" select="''"/>
    <xsl:param name="sequence" select="''"/>
    <xsl:param name="position" select="''"/>
    <xsl:param name="gentext-key" select="''"/>

    <fo:block>
      <xsl:choose>
        <xsl:when test="$position = 'left'">
          <fo:block>
            <xsl:value-of select="d:info/d:productname"/>
          </fo:block>
        </xsl:when>

        <xsl:when test="$position = 'right'">
          <fo:block>
            NURAS Ltd.
            <fo:external-graphic content-height=".2in" src="./images/nuras-logo.png"/>
          </fo:block>
        </xsl:when>

        <xsl:when test="$position = 'center'">
        </xsl:when>

      </xsl:choose>
    </fo:block>
  </xsl:template>

  <xsl:template match="processing-instruction('hard-pagebreak')">
    <fo:block break-after='page'/>
  </xsl:template>

  <xsl:template match="processing-instruction('linebreak')">
    <fo:block/>
  </xsl:template>

  <xsl:param name="local.l10n.xml" select="document('')"/>
  <l:i18n xmlns:l="http://docbook.sourceforge.net/xmlns/l10n/1.0">
    <l:l10n language="en">
      <l:context name="title">
        <l:template name="table" text="%t"/>
      </l:context>
      <l:context name="xref-number-and-title">
        <l:template name="table" text="the table titled &#8220;%t&#8221;"/>
      </l:context>
    </l:l10n>
  </l:i18n>

  <xsl:template match="table" mode="label.markup"/>

  <xsl:attribute-set name="table.cell.padding">
    <xsl:attribute name="padding-left">2pt</xsl:attribute>
    <xsl:attribute name="padding-right">2pt</xsl:attribute>
    <xsl:attribute name="padding-top">4pt</xsl:attribute>
    <xsl:attribute name="padding-bottom">4pt</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="table.properties">
    <xsl:attribute name="start-indent">0pt</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="monospace.verbatim.properties">
    <xsl:attribute name="text-align">
      <xsl:choose>
        <xsl:when test="processing-instruction('db-align-right')">
          <xsl:value-of select="text()" />
        </xsl:when>
        <xsl:otherwise>inherit</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
    <xsl:attribute name="font-size">
      <xsl:choose>
        <xsl:when test="processing-instruction('db-font-size')">
          <xsl:value-of select="processing-instruction('db-font-size')"/>
        </xsl:when>
        <xsl:otherwise>inherit</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:attribute-set>

  <xsl:template match="para[@font-size]">
    <fo:block font-size="{@font-size}">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <xsl:attribute-set name="itemizedlist.properties" use-attribute-sets="list.block.properties">
    <xsl:attribute name="font-size">
      <xsl:choose>
        <xsl:when test="processing-instruction('db-font-size')">
          <xsl:value-of select="processing-instruction('db-font-size')"/>
        </xsl:when>
        <xsl:otherwise>inherit</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:attribute-set>

  <xsl:template match="d:phrase[@align]">
    <fo:block text-align="{@align}">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <xsl:template match="d:phrase[@role='large']">
    <fo:block font-size="18pt">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <xsl:template match="d:phrase[@role='normal']">
    <fo:block font-size="12pt">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <xsl:template match="d:phrase[@role='small']">
    <fo:block font-size="8pt">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <xsl:template match="d:phrase[@role='inverted'] | phrase[@role='inverted']">
    <fo:inline color="black" background-color="#ddeecc">
      <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

  <xsl:template name="footer.table">
    <xsl:param name="pageclass" select="''"/>
    <xsl:param name="sequence" select="''"/>
    <xsl:param name="gentext-key" select="''"/>

    <!-- default is a single table style for all footers -->
    <!-- Customize it for different page classes or sequence location -->

    <xsl:variable name="column1">
      <xsl:choose>
        <xsl:when test="$double.sided = 0">1</xsl:when>
        <xsl:when test="$sequence = 'first' or $sequence = 'odd'">1</xsl:when>
        <xsl:otherwise>3</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:variable name="column3">
      <xsl:choose>
        <xsl:when test="$double.sided = 0">3</xsl:when>
        <xsl:when test="$sequence = 'first' or $sequence = 'odd'">3</xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:variable name="candidate">
      <fo:table xsl:use-attribute-sets="footer.table.properties">
        <xsl:call-template name="foot.sep.rule">
          <xsl:with-param name="pageclass" select="$pageclass"/>
          <xsl:with-param name="sequence" select="$sequence"/>
          <xsl:with-param name="gentext-key" select="$gentext-key"/>
        </xsl:call-template>
        <fo:table-column column-number="1">
          <xsl:attribute name="column-width">
            <xsl:text>proportional-column-width(8)</xsl:text>
          </xsl:attribute>
        </fo:table-column>
        <fo:table-column column-number="2">
          <xsl:attribute name="column-width">
            <xsl:text>proportional-column-width(0)</xsl:text>
          </xsl:attribute>
        </fo:table-column>
        <fo:table-column column-number="3">
          <xsl:attribute name="column-width">
            <xsl:text>proportional-column-width(2)</xsl:text>
          </xsl:attribute>
        </fo:table-column>

        <fo:table-body>
          <fo:table-row>
            <xsl:attribute name="block-progression-dimension.minimum">
              <xsl:value-of select="$footer.table.height"/>
            </xsl:attribute>
            <fo:table-cell text-align="start"
                           display-align="after">
              <xsl:if test="$fop.extensions = 0">
                <xsl:attribute name="relative-align">baseline</xsl:attribute>
              </xsl:if>
              <fo:block>
                <xsl:call-template name="footer.content">
                  <xsl:with-param name="pageclass" select="$pageclass"/>
                  <xsl:with-param name="sequence" select="$sequence"/>
                  <xsl:with-param name="position" select="$direction.align.start"/>
                  <xsl:with-param name="gentext-key" select="$gentext-key"/>
                </xsl:call-template>
              </fo:block>
            </fo:table-cell>
            <fo:table-cell text-align="center"
                           display-align="after">
              <xsl:if test="$fop.extensions = 0">
                <xsl:attribute name="relative-align">baseline</xsl:attribute>
              </xsl:if>
              <fo:block>
                <xsl:call-template name="footer.content">
                  <xsl:with-param name="pageclass" select="$pageclass"/>
                  <xsl:with-param name="sequence" select="$sequence"/>
                  <xsl:with-param name="position" select="'center'"/>
                  <xsl:with-param name="gentext-key" select="$gentext-key"/>
                </xsl:call-template>
              </fo:block>
            </fo:table-cell>
            <fo:table-cell text-align="end"
                           display-align="after">
              <xsl:if test="$fop.extensions = 0">
                <xsl:attribute name="relative-align">baseline</xsl:attribute>
              </xsl:if>
              <fo:block>
                <xsl:call-template name="footer.content">
                  <xsl:with-param name="pageclass" select="$pageclass"/>
                  <xsl:with-param name="sequence" select="$sequence"/>
                  <xsl:with-param name="position" select="$direction.align.end"/>
                  <xsl:with-param name="gentext-key" select="$gentext-key"/>
                </xsl:call-template>
              </fo:block>
            </fo:table-cell>
          </fo:table-row>
        </fo:table-body>
      </fo:table>
    </xsl:variable>

    <!-- Really output a footer? -->
    <xsl:choose>
      <xsl:when test="$pageclass='titlepage' and $gentext-key='book'
                    and $sequence='first'">
        <!-- no, book titlepages have no footers at all -->
      </xsl:when>
      <xsl:when test="$sequence = 'blank' and $footers.on.blank.pages = 0">
        <!-- no output -->
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy-of select="$candidate"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


</xsl:stylesheet>
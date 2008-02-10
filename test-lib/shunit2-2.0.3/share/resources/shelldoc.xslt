<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: shelldoc.xslt 62 2007-04-19 17:19:14Z sfsetse $ -->
<!--
example ways to process this xslt:
$ java -cp xalan-2.6.0.jar \
  org.apache.xalan.xslt.Process -xml -in log4sh.xml -xsl shelldoc.xslt

$ xsltproc shelldoc.xslt log4sh.xml |xmllint -noblanks -
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:s="http://www.forestent.com/projects/shelldoc/xsl/2005.0">
  <xsl:output
      method="xml"
      version="1.0"
      encoding="UTF-8"
      indent="yes"/>
  <xsl:strip-space elements="*" />

  <xsl:variable name="newline">
<xsl:text>
</xsl:text>
  </xsl:variable>

  <xsl:key name="groups" match="s:function" use="@group" />

  <xsl:template match="/">
    <chapter id="shelldoc" lang="en-US"><title>Function Reference</title>
    <xsl:for-each select="//s:function[generate-id(.)=generate-id(key('groups', @group)[1])]">
      <xsl:sort select="@group" />

      <section>
        <xsl:attribute name="id">shelldoc-section-<xsl:value-of select="@group" /></xsl:attribute>
        <title><xsl:value-of select="@group"/></title>
        <table>
          <xsl:attribute name="id">shelldoc-function-<xsl:value-of select="@group" /></xsl:attribute>
          <title><xsl:value-of select="@group"/></title>
          <tgroup cols="2"><tbody>
          <xsl:for-each select="key('groups', @group)">
            <!--<xsl:sort select="entry/funcsynopsis/funcprototype/funcdef/function" />-->
            <xsl:choose>
              <xsl:when test="@modifier">
                <xsl:if test="@modifier != 'private'">
                  <row valign="top">
                    <xsl:copy-of select="entry" />
                    <!--<xsl:apply-templates select="entry" />-->
                  </row>
                </xsl:if>
              </xsl:when>
              <xsl:otherwise>
                <row valign="top">
                  <xsl:copy-of select="entry" />
                  <!--<xsl:apply-templates select="entry" />-->
                </row>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:for-each>
          </tbody></tgroup>
        </table>
      </section>
    </xsl:for-each>
    </chapter>
  </xsl:template>

  <xsl:template match="entry">
    <entry>
    <xsl:copy-of select="*" />
    </entry>
  </xsl:template>

</xsl:stylesheet>

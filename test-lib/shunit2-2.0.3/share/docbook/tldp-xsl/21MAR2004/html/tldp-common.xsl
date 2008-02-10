<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!-- This file contains parameters that are applicable to all of the
     tldp-*.xsl files in the html directory. -->

<!-- Create a link to a CSS stylesheet named 'style.css' in all html
     output so that pages can be beautified.  Browsers not supporting
     CSS should safely ignore the link. -->
<xsl:param name="html.stylesheet.type">text/css</xsl:param>
<xsl:param name="html.stylesheet" select="'style.css'"></xsl:param>

<!-- Number all sections in the style of 'CH.S1.S2 Section Title' where
     CH is the chapter number,  S1 is the section number and S2 is the
     sub-section number.  The lables are not limited to any particular
     depth and can go as far as there are sections. -->
<xsl:param name="section.autolabel" select="1"></xsl:param>
<xsl:param name="section.label.includes.component.label" select="0"></xsl:param>

</xsl:stylesheet>

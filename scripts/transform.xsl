<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0">
    <xsl:output method="html" indent="yes"/>
    <xsl:template match="/">
        <html>
            <head>
                <title>Wildest Dreams TEI</title>
                <style>
                    body { font-family: sans-serif; padding: 20px; }
                    .card { border: 1px solid #ccc; padding: 20px; border-radius: 8px; }
                    del { color: red; text-decoration: line-through; }
                    .add { color: green; vertical-align: super; font-size: small; }
                    .entity { border-bottom: 1px dotted blue; background: #eef; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1><xsl:value-of select="//tei:titleStmt/tei:title"/></h1>
                    <xsl:apply-templates select="//tei:body"/>
                </div>
            </body>
        </html>
    </xsl:template>
    
    <xsl:template match="tei:lg">
        <div style="margin-bottom: 20px;"><xsl:apply-templates/></div>
    </xsl:template>
    
    <xsl:template match="tei:l">
        <div style="line-height: 1.5;"><xsl:apply-templates/></div>
    </xsl:template>
    
    <xsl:template match="tei:del"><del><xsl:apply-templates/></del></xsl:template>
    <xsl:template match="tei:add"><span class="add"><xsl:apply-templates/></span></xsl:template>
    <xsl:template match="tei:placeName|tei:objectName"><span class="entity"><xsl:apply-templates/></span></xsl:template>
</xsl:stylesheet>
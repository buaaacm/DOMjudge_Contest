\documentclass [11pt, a4paper, oneside] {article}

\usepackage [T2A] {fontenc}
\usepackage [utf8] {inputenc}
\usepackage [english, russian] {babel}
\usepackage {amsmath}
\usepackage {amssymb}
\usepackage <#if contest.language?? && contest.language="chinese">[chinese]<#elseif contest.language?? && contest.language="russian">[russian]<#elseif contest.language?? && contest.language="ukrainian">[ukrainian]</#if>{olymp}
\usepackage {comment}
\usepackage {epigraph}
\usepackage {expdlist}
\usepackage {graphicx}
\usepackage {siunitx}
\usepackage {ulem}
\usepackage {import}
\usepackage {ifpdf}
\usepackage [figurename=图,tablename=表]{caption}
\usepackage {tkz-graph}
\usepackage {listings}
\usepackage {xcolor}
\ifpdf
  \DeclareGraphicsRule{*}{mps}{*}{}
\fi

\usepackage [colorlinks,linkcolor=blue]{hyperref}

\numberwithin{figure}{section}
\numberwithin{table}{section}

\begin {document}

\contest
{${contest.name!}}%
{${contest.location!}}%
{${contest.date!}}%

\binoppenalty=10000
\relpenalty=10000

\renewcommand{\t}{\texttt}

<#if shortProblemTitle?? && shortProblemTitle>
  \def\ShortProblemTitle{}
</#if>

<#list tutorials as tutorial>
<#if tutorial.path??>
<#if tutorial.index??>
    \def\ProblemIndex{${tutorial.index}}
</#if>
\graphicspath{{${tutorial.path}}}
\import{${tutorial.path}}{./${tutorial.file}}
<#else>
\input ${tutorial.file}
</#if>
</#list>

\end {document}


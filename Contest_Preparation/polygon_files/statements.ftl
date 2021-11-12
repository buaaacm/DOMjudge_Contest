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
\usepackage {multicol}
\usepackage {listings}
\usepackage {tkz-graph}
\usepackage {xcolor}
\ifpdf
  \DeclareGraphicsRule{*}{mps}{*}{}
\fi

\usepackage [colorlinks,linkcolor=blue]{hyperref}

\newfontfamily{\lstconsolas}{Consolas}
\lstset{
  frame=single,
  tabsize=4,
  keywordstyle=\color[rgb]{0,0,0.54}\bfseries,
  commentstyle=\color{gray},
  stringstyle=\color[rgb]{0,0.50,0},
  showstringspaces=false,
  basicstyle=\lstconsolas\small,
}
\lstset{literate=%
 *{0}{{{\color{blue}0}}}1
  {1}{{{\color{blue}1}}}1
  {2}{{{\color{blue}2}}}1
  {3}{{{\color{blue}3}}}1
  {4}{{{\color{blue}4}}}1
  {5}{{{\color{blue}5}}}1
  {6}{{{\color{blue}6}}}1
  {7}{{{\color{blue}7}}}1
  {8}{{{\color{blue}8}}}1
  {9}{{{\color{blue}9}}}1
}

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

<#list statements as statement>
<#if statement.path??>
\graphicspath{{${statement.path}}}
<#if statement.index??>
  \def\ProblemIndex{${statement.index}}
</#if>
\import{${statement.path}}{./${statement.file}}
<#else>
\input ${statement.file}
</#if>
</#list>

\end {document}


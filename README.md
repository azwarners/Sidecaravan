# Sidecaravan

> **Give agents more to work with—and less they have to figure out from scratch.**
>
> Remember useful experience. Find better evidence. Put conventional computation
> to work before spending more generative inference.

Sidecaravan is a project to give AI agents and ordinary applications a shared
collection of useful capabilities: memory, vision, document understanding,
knowledge retrieval, software-engineering tools, and evidence preparation.

The ambition is simple: help an agent **remember, find, inspect, connect, and
verify** more while spending less inference on work ordinary software can do.

Some people want an AI companion who remembers them. Others want an efficient
coding agent, a terminal assistant, or a tool that answers a question and gets
out of the way. They should all be able to use the capabilities that help them.
Nobody should have to adopt an entire ecosystem to benefit from one good tool.

**Status: planning and initial development.** This README describes the vision,
not a catalog of shipped features. The first implementation priority is durable
agent memory and a working Apmatia experience that uses it. There is no released
Sidecaravan CLI to install yet. The planned command name is `scv).

## Give the agent a better starting point

Modern AI workflows can spend enormous amounts of inference searching for a
fact, rereading a repository, reconstructing an earlier decision, or extracting
information that a parser could have returned directly.

What if we let fifty years of NLP, information retrieval, expert systems,
fuzzy logic, graph algorithms, knowledge representation, automated planning,
statistics, and text mining help with the work?

What if an agent could ask for the relevant evidence instead of reading
everything? What if a conversation could leave behind useful, correctable
memories? What if an engineering agent could invoke the operations an IDE has
provided for decades instead of repeatedly improvising them?

Sidecaravan is an invitation to find out.

The project inherits the curiosity of Cognitive Front End: an archaeological
dig through techniques developed when processors were slow, memory was scarce,
and a few hundred milliseconds could make an approach commercially impractical.
Some ideas failed. Some were useful but unfashionable. Some were held back by
the hardware available to their authors.

The hardware changed.

Let's find out which ideas deserve another run.

## Memory that makes returning worthwhile

An agent should not have to meet you for the first time every time you open a
new conversation.

We want useful continuity: preferences you chose to share, decisions you made
together, approaches that failed, unfinished work, and the context behind a
successful fix. You should be able to inspect those memories, correct them,
and ask for them to be forgotten.

Imagine telling Luna why an Ansible role needs a particular exception. Tomorrow,
you return in a new conversation. She recalls the decision, knows where it came
from, and helps you continue without making you explain the whole project again.

That is our first concrete goal: **Apmatia agents with working memory.**
Apmatia supplies the character and relationship; Sidecaravan supplies reusable
memory capabilities that other agents can use too.

Useful memory needs more than storage:

- retrieve what matters to the current conversation;
- distinguish private memories from deliberately shared project knowledge;
- preserve sources, dates, corrections, and unresolved disagreements;
- separate what the user said from what a model inferred;
- let a session recall memories without necessarily saving new ones;
- keep a temporary hypothesis from quietly becoming a permanent fact.

Conversation history, durable memories, and evidence for the current task have
different purposes. Keeping those distinctions clear should make memory more
trustworthy and more useful.

The first version can be small: save, retrieve, correct, forget, and retain
records across restarts. It should not require a GPU, another model, or the
completion of the whole Sidecaravan roadmap.

## A caravan of useful capabilities

### Vision

Give a text-oriented agent access to useful information in images: screenshot
text, image properties, visible interface details, and descriptions when a
suitable vision provider is available.

Use conventional image processing and OCR where they fit. Make model-backed
interpretation optional and explicit. A caption is an interpretation; extracted
text and measured image properties are different kinds of evidence.

### Documents

Make documents usable without asking every agent to become a file-format
expert. Extract text and structure from supported PDFs, office documents, and
other sources; retain page or section references; make limitations visible.

An agent should be able to find the paragraph supporting an answer and show
you where it came from.

### Knowledge and a wiki worth keeping

Valuable conversations should not disappear into an unmaintainable list of
chat titles.

We want to recover useful explanations, connect related decisions, build
searchable collections, and produce a source-linked wiki from material the
user chooses to retain. Knowledge should remain revisable as sources change.
A generated summary should never silently replace the evidence behind it.

### Software engineering

Expose the machinery software engineering already has: symbol indexes,
definitions and references, dependency analysis, Git operations, parsers,
refactoring tools, linters, formatters, tests, builds, and careful patch
operations.

Codebase Memory MCP is one planned starting point for repository understanding.
Its structural code index complements conversational memory; the two solve
different problems.

The ambition is **an API for software engineering itself**: useful operations
an engineer agent can discover and call. Sidecaravan provides capabilities;
the engineer decides how to use them.

### Evidence and context preparation

Find relevant passages, trace relationships, recover constraints, retrieve
similar past cases, remove redundancy, and assemble a useful selection within
the caller's context budget.

Preserve original source material and show what was selected, where it came
from, and what remains uncertain. Less context is valuable only when it still
contains the evidence needed for the task.

### Connections to other applications

Make useful operations available across agents without copying an application's
business logic into every assistant.

An agent might consult OpenIPE for unfinished habits, ask for a Ladcemas alarm,
or use a repository-analysis capability. Those applications remain useful
independently. Users choose which capabilities are available in each context.

These domains describe the intended reach of Sidecaravan. They do not require
one giant installation, one agent personality, or one mandatory workflow.

## Useful throughout the task

The user should be able to ask for ordinary work:

> Look through this Python project. Users occasionally receive duplicate
> notifications after reconnecting. Find the likely cause, fix it, and add tests.

Useful supporting questions include:

- Which files, symbols, tests, and earlier decisions are relevant?
- What requirements and prohibitions were explicitly stated?
- Which relationships can be traced mechanically?
- What is ambiguous or unsupported by the available evidence?
- What can be calculated or checked before asking a model?
- Which passages deserve space in the context window?
- Did the result satisfy its mechanically checkable requirements?

The value continues after the first prompt. An agent investigating duplicate
notifications might ask:

> Find the paths that register, restore, retry, or remove notification listeners.
> Return relevant source passages within a 5,000-token budget.

After considering that evidence, it might ask:

> Trace notification identifiers from creation through acknowledgement and retry.
> Focus on idempotency and reconnect behavior.

Those are examples of desired interactions, not commands implemented today.

Literal search, lexical expansion, symbol indexes, retrieval scoring, call
relationships, and extractive selection could help answer them. The result
should include source locations, relevant relationships, uncertainty, and
coverage limitations.

An agent should be able to ask for another focused investigation whenever its
question changes. We want conventional computation to remain useful beside
generative reasoning for the entire task.

## Why slow inference changes the economics

Consider a large model running on a CPU server at less than one token per
second. A confused answer or unnecessary exploratory turn can cost minutes.
That same machine may have dozens of cores and hundreds of gigabytes of RAM
available for conventional analysis.

Indexing, retrieval, graph traversal, parsing, and constraint checking can be
much cheaper than the generation they help avoid. That is a hypothesis to
measure on real workloads, not a promise that every preprocessing step pays off.

> **Minimize wasted generative computation by maximizing useful conventional
> computation around it.**

If ten seconds of analysis improves a generation that takes forty minutes,
spend the ten seconds. If a minute of retrieval prevents a large model from
pursuing the wrong task, that can be a good trade.

Interactive conversation has a different budget. Luna should not take a minute
to prepare a greeting. The useful amount of supporting computation depends on
the task, the available hardware, and the user's latency expectations.

The aim is better completed work for the time and resources spent.

## Energy efficiency is part of the goal

A model should not need billions of matrix operations to repeat work a text
index, parser, graph traversal, calculator, or ordinary search utility can
perform more cheaply and reliably.

Sidecaravan may reduce wasted inference through:

- fewer irrelevant source and document tokens;
- fewer redundant searches and exploratory generations;
- fewer corrective turns caused by missing evidence;
- smaller, more useful context selections;
- fewer unnecessary invocations of larger models.

The meaningful comparison is **energy consumed per successfully completed,
quality-validated task**. Fewer tokens alone do not establish a win.

Measure conventional CPU time and memory, prompt and generated tokens,
accelerator work, total elapsed time, model loads, and task quality. Measure
energy directly where telemetry permits, and distinguish measurements from
estimates. A costly analysis step that makes the final result worse does not
belong in the default path.

## The archaeological dig: cheap techniques worth investigating

This is the heart of the project. The list is intentionally broad. We are not
claiming that every technique will help. We intend to investigate them one at a time, measure their contribution, and
keep the winners. This is a research menu, not an implementation checklist or
a requirement for the first usable release.

### Lexical and linguistic structure

- tokenization and sentence segmentation
- stemming, lemmatization, and morphological analysis
- part-of-speech tagging
- noun-phrase chunking and shallow parsing
- constituency and dependency parsing
- finite-state grammars and transducers
- transformation rules and regex grammars
- named-entity recognition with rules, CRFs, and gazetteers
- discourse markers and rhetorical structure
- negation, modality, conditional, comparison, and superlative detection
- anaphora and coreference heuristics
- edit distance, phonetic matching, and spelling normalization
- Hearst patterns and other lexico-syntactic relation patterns
- frame semantics, semantic roles, slot filling, and unification

These techniques can contribute literal structure: what was said, which phrases
belong together, what is negated, what is conditional, and what relationships
are explicitly present.

### Keywords, terminology, and concept mining

- term frequency and TF-IDF
- BM25 term weighting
- Luhn significance
- RAKE and YAKE
- TextRank and graph-based keyword extraction
- C-value and NC-value terminology extraction
- n-grams and noun-phrase frequency
- collocation detection
- pointwise mutual information
- log-likelihood ratios
- chi-square term association
- domain dictionaries and gazetteers
- taxonomies, thesauri, and ontologies
- WordNet and semantic networks
- latent semantic analysis / latent semantic indexing
- vector-space models and cosine similarity

These do not need to understand the whole request. They can identify what is
salient, which technical concepts may be hiding in ordinary phrasing, and which
terms should drive retrieval or model capability estimates.

### Ambiguity and word-sense evidence

- Lesk and extended-Lesk word-sense disambiguation
- WordNet sense inventories
- lexical overlap and semantic relatedness
- competing parse trees
- syntactic ambiguity scores
- n-gram likelihood and entropy
- ontology and taxonomy lookup
- discourse coherence
- Bayesian confidence
- fuzzy membership
- Dempster-Shafer evidence

The goal is not to force certainty. A useful analysis tool can tell the target model
that one interpretation appears most likely while preserving plausible
alternatives.

### Information retrieval and knowledge activation

- Boolean retrieval
- TF-IDF and vector-space retrieval
- BM25
- proximity and phrase search
- Rocchio relevance feedback
- pseudo-relevance feedback
- query expansion
- thesaurus and taxonomy traversal
- LSA/LSI retrieval
- passage retrieval
- document clustering
- k-nearest-neighbor retrieval
- case-based reasoning
- association rules
- local and domain-specific indexes

Retrieval and generation remain separate. The retrieval system finds evidence;
it does not invent a summary of what it wishes the evidence had said.

### Extractive context distillation

- Luhn summarization
- TextRank and LexRank
- sentence centrality
- centroid-based summarization
- TF-IDF sentence scoring
- cue phrases and positional weighting
- graph centrality
- maximal marginal relevance
- redundancy suppression
- novelty scoring
- keyword and entity coverage
- TextTiling and topic segmentation
- discourse-aware extraction
- temporal and source-priority selection

The ambition is to turn a large collection of vaguely relevant history into
a smaller selection of useful original passages without requiring a generative
summary. Exact savings must be measured. Extracted passages can still mislead
if important context is omitted.

### Knowledge structures and graphs

- semantic networks
- frames and scripts
- subject-predicate-object triples
- ontologies and taxonomies
- co-occurrence graphs
- dependency-derived relations
- graph clustering and community detection
- timelines and event graphs
- truth-maintenance systems
- provenance and source graphs

An explicit graph can preserve relationships that are easy to lose in a pile of
text: who uses what, which model ran on which backend, which observation
superseded another, and which constraint applies to which candidate.

### Symbolic reasoning and constraint machinery

- production rules
- forward and backward chaining
- expert systems
- Prolog-style inference
- constraint satisfaction
- decision tables and decision trees
- rule engines
- truth-maintenance systems
- arithmetic and unit conversion
- temporal rules
- source precedence
- contradiction detection
- Bayesian inference
- fuzzy inference

Do not spend hundreds of billions of parameters rediscovering that a 135 GB
model cannot fit in 120 GB. Pre-solve the boring, deterministic parts and give
the LLM the derived facts.

### Evidence fusion and uncertainty

- weighted evidence
- voting and ensemble methods
- fuzzy sets and fuzzy controllers
- Bayesian classifiers and Bayesian networks
- maximum-entropy classifiers
- support-vector machines
- decision trees
- Dempster-Shafer theory
- confidence calibration
- entropy and uncertainty scoring
- abstention thresholds
- corroboration and conflict scoring

Twenty imperfect signals will disagree. Preserve the supporting evidence,
explain uncertainty, and distinguish a heuristic score from a calibrated
probability. A disagreement can be useful information.

### Classical classification and difficulty estimation

- Naive Bayes
- logistic and maximum-entropy classifiers
- support-vector machines
- k-nearest neighbors
- decision trees and random forests
- manually scored feature models
- fuzzy rule systems
- lexical entropy and rarity
- structural complexity measures
- historical failure statistics
- calibrated capability thresholds

Features may include the number of entities and constraints, nested
conditionals, mathematical or code content, domain rarity, context volume,
contradictions, required operations, and tool-use signals.

### Automated planning and workflow recognition

- STRIPS-style planning
- partial-order planning
- hierarchical task networks
- goal decomposition
- finite-state workflows
- Petri nets
- state machines
- dependency graphs
- critical-path methods
- means-ends analysis
- case-based plans
- plan validation and constraint checking

The system does not need to write the answer in advance. It may still be able
to derive a reliable checklist: inspect, trace, modify, test, and report.

### Context budgeting and compression

- relevance, recency, salience, and source-reliability scoring
- entity and topic overlap
- novelty and redundancy penalties
- submodular selection
- maximal marginal relevance
- knapsack-style budget allocation
- graph-based coverage
- passage granularity selection
- lossy versus lossless text normalization
- duplicate and near-duplicate detection

More context is not automatically better. Conventional IR may improve both
quality and prompt-evaluation time by supplying less.

### Deterministic post-generation quality control

- required-entity coverage
- requested-section and format checks
- constraint and forbidden-output checks
- numeric and unit consistency
- rule-derived fact verification
- contradiction detection
- source citation presence
- task-checklist coverage
- schema and grammar validation
- structured feedback for a caller's retry or correction decision

When a check detects a failure, it should provide specific evidence about what
was omitted or violated. The caller decides whether to spend another model
turn correcting it. These checks do not prove arbitrary answers are true.

### The especially interesting rejects

We want to search old papers and systems for phrases such as:

- *computationally expensive*
- *prohibitively expensive*
- *memory intensive*
- *impractical for large corpora*
- *too slow for interactive use*
- *quadratic complexity*
- *limited by available memory*

An algorithm rejected in 1994 because it needed 800 milliseconds or too much
of a 64 MB workstation may be trivial on a modern 56-thread server with 576 GB
of RAM. The unfashionable and formerly impractical ideas may be more interesting
than the famous survivors.

## Help the system choose appropriate resources

A user should not have to understand a shelf of model files to ask for useful
work. They should also remain free to choose a model explicitly.

One research direction is to estimate a task's needs—code, vision, context,
precision, or specialized knowledge—and compare those needs with measured
capabilities and resource costs. Such evidence could help a configured caller
choose an adequate model without always reaching for the largest one.

A birthday message might stay with the resident daily model. A difficult
concurrency problem might justify a stronger engineer. A major architecture
question might warrant more time and a larger context.

These are possibilities to evaluate. Sidecaravan's contribution is useful
evidence and capability information. Decisions about routing, loading models,
and running the task belong to the applications using it. Difficulty estimates
must remain estimates, with room to abstain.

## Scientific discipline, not a nostalgia museum

The old toolbox is inspiration, not a reason to collect algorithms indiscriminately.

For each technique:

1. State the useful evidence or operation it could provide.
2. Build fixtures that could prove the idea wrong.
3. Measure CPU time, memory, and operational cost.
4. Compare assisted and unassisted work under comparable conditions.
5. Judge quality blindly where practical.
6. Keep the technique only if its benefit justifies its cost and complexity.

For model comparisons, keep the target model and sampling settings consistent
where practical, repeat trials, and report uncertainty. A small apparent win
is a reason to investigate, not a universal claim.

We care about constraint retention, factual relevance, completeness, incorrect
claims, useful context, successful verification, and end-to-end time. We also
care whether a person finds the result helpful.

Start with straightforward baselines. More sophisticated machinery earns its
place by outperforming them on actual work.

## Principles worth carrying forward

- Preserve original requests and source material; make derived interpretations
  distinguishable.
- Return provenance and limitations with evidence. Abstain when the available
  information does not support a conclusion.
- Use conventional computation wherever it is a good fit. Do not require a
  hidden generative rewrite or summary before an agent can use basic tools.
- Label optional model-backed capabilities honestly. Vision or summarization
  may use inference; that does not make every other operation depend on it.
- Keep memories scoped, inspectable, correctable, and forgettable.
- Respect the user's choice of agent, client, provider, and applications.
- Make useful capabilities independently accessible. Using Sidecaravan should
  not require Apmatia or all of OpAIStackOS.
- Keep experimental techniques measurable and replaceable.
- Ship small, complete experiences before expanding the toolbox.

## Where we begin

The first experience we want to make real is personal and practical:

1. Create an Apmatia agent with a personality and a configured model.
2. Tell that agent something worth remembering.
3. Return in a new conversation.
4. Have it retrieve the relevant memory and continue with you.
5. Inspect, correct, or forget that memory when needed.

The same memory capability should work for an agent without an Apmatia
personality. Some people want a familiar companion; some want a dependable
utility. Both deserve useful continuity.

That first experience does not depend on completing the research catalog.
Vision, documents, knowledge, SWE, and richer evidence preparation can grow
through their own concrete, testable contributions.

Follow the [Sidecaravan roadmap](https://github.com/azwarners/Sidecaravan/issues/1),
starting with [durable memory](https://github.com/azwarners/Sidecaravan/issues/4)
and [cross-session recall](https://github.com/azwarners/Sidecaravan/issues/5).
The [Apmatia plan](https://github.com/azwarners/Apmatia/issues/1) tracks the
character experience alongside that work.

## From Cognitive Front End to Sidecaravan

Cognitive Front End was an early expression of this project's central idea:
give agents better evidence and useful conventional computation so they waste
less inference.

Sidecaravan carries that vision forward and broadens it to memory, vision,
documents, knowledge, engineering operations, and application capabilities.
This README preserves that ambition so the predecessor can remain historical.

Sidecaravan starts fresh. It does not depend on the CFE prototype or inherit
its architecture, milestones, or claims of implemented functionality.

## The bet

No single retrieval score, parser, rule engine, or graph algorithm needs to
understand the whole task to contribute something useful.

A collection of small, honest capabilities can help an agent remember an
important decision, find a crucial passage, check a calculation, understand a
repository, or avoid an unnecessary detour.

The model still has difficult work to do. Let's give it better materials and
better tools for doing it.

Modern AI can stand on decades of computational intelligence—and on the useful
experience you have already built together.

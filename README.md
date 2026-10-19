# Papers on LLM Agents and Agent Systems

A curated list of papers about LLM agents and the systems built around them: reasoning and
acting, tool use, memory, retrieval, multi-agent orchestration, coding and web agents, and the
evaluation and training work that decides whether any of it actually holds up.

Every entry's title, authors, year and link were taken from the arXiv API rather than typed by
hand, so a misremembered paper shows up as a mismatch instead of becoming a wrong citation.
See [sources](#sources) and [selection criteria](#selection-criteria) below.

<br/>

<details open>
<summary>List of papers by topic</summary>
<br/>

1. **Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. [Wei et al (2022)](https://arxiv.org/abs/2201.11903).**
    \
    <sub>Reasoning; Prompting</sub>
    * Self-Consistency Improves Chain of Thought Reasoning in Language Models. [Wang et al (2022)](https://arxiv.org/abs/2203.11171).
    * Least-to-Most Prompting Enables Complex Reasoning in Large Language Models. [Zhou et al (2022)](https://arxiv.org/abs/2205.10625).
    * Tree of Thoughts: Deliberate Problem Solving with Large Language Models. [Yao et al (2023)](https://arxiv.org/abs/2305.10601).

1. **ReAct: Synergizing Reasoning and Acting in Language Models. [Yao et al (2022)](https://arxiv.org/abs/2210.03629).**
    \
    <sub>Agents; Reasoning and Acting</sub>
    * Reflexion: Language Agents with Verbal Reinforcement Learning. [Shinn et al (2023)](https://arxiv.org/abs/2303.11366).
    * Self-Refine: Iterative Refinement with Self-Feedback. [Madaan et al (2023)](https://arxiv.org/abs/2303.17651).
    * Let's Verify Step by Step. [Lightman et al (2023)](https://arxiv.org/abs/2305.20050).
    * Chain of Agents: Large Language Models Collaborating on Long-Context Tasks. [Zhang et al (2024)](https://arxiv.org/abs/2406.02818).

1. **Toolformer: Language Models Can Teach Themselves to Use Tools. [Schick et al (2023)](https://arxiv.org/abs/2302.04761).**
    \
    <sub>Tool Use; Function Calling</sub>
    * ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs. [Qin et al (2023)](https://arxiv.org/abs/2307.16789).
    * Gorilla: Large Language Model Connected with Massive APIs. [Patil et al (2023)](https://arxiv.org/abs/2305.15334).
    * Executable Code Actions Elicit Better LLM Agents. [Wang et al (2024)](https://arxiv.org/abs/2402.01030).

1. **MemGPT: Towards LLMs as Operating Systems. [Packer et al (2023)](https://arxiv.org/abs/2310.08560).**
    \
    <sub>Agent Memory; Long-Term Memory</sub>
    * Generative Agents: Interactive Simulacra of Human Behavior. [Park et al (2023)](https://arxiv.org/abs/2304.03442).
    * LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory. [Wu et al (2024)](https://arxiv.org/abs/2410.10813).
    * A-MEM: Agentic Memory for LLM Agents. [Xu et al (2025)](https://arxiv.org/abs/2502.12110).
    * Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory. [Chhikara et al (2025)](https://arxiv.org/abs/2504.19413).

1. **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. [Lewis et al (2020)](https://arxiv.org/abs/2005.11401).**
    \
    <sub>Retrieval; Knowledge Grounding</sub>
    * Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection. [Asai et al (2023)](https://arxiv.org/abs/2310.11511).
    * Lost in the Middle: How Language Models Use Long Contexts. [Liu et al (2023)](https://arxiv.org/abs/2307.03172).

1. **Cognitive Architectures for Language Agents. [Sumers et al (2023)](https://arxiv.org/abs/2309.02427).**
    \
    <sub>Agent Architecture; Survey</sub>
    * The Rise and Potential of Large Language Model Based Agents: A Survey. [Xi et al (2023)](https://arxiv.org/abs/2309.07864).
    * A Survey on Large Language Model based Autonomous Agents. [Wang et al (2023)](https://arxiv.org/abs/2308.11432).
    * A Survey of AI Agent Protocols. [Yang et al (2025)](https://arxiv.org/abs/2504.16736).

1. **SWE-bench: Can Language Models Resolve Real-World GitHub Issues? [Jimenez et al (2023)](https://arxiv.org/abs/2310.06770).**
    \
    <sub>Coding Agents; Benchmarks</sub>
    * SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering. [Yang et al (2024)](https://arxiv.org/abs/2405.15793).
    * OpenHands: An Open Platform for AI Software Developers as Generalist Agents. [Wang et al (2024)](https://arxiv.org/abs/2407.16741).

1. **WebArena: A Realistic Web Environment for Building Autonomous Agents. [Zhou et al (2023)](https://arxiv.org/abs/2307.13854).**
    \
    <sub>Web Agents; Environments</sub>
    * OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments. [Xie et al (2024)](https://arxiv.org/abs/2404.07972).

1. **AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation. [Wu et al (2023)](https://arxiv.org/abs/2308.08155).**
    \
    <sub>Multi-Agent; Orchestration</sub>
    * MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework. [Hong et al (2023)](https://arxiv.org/abs/2308.00352).
    * CAMEL: Communicative Agents for "Mind" Exploration of Large Language Model Society. [Li et al (2023)](https://arxiv.org/abs/2303.17760).
    * ChatDev: Communicative Agents for Software Development. [Qian et al (2023)](https://arxiv.org/abs/2307.07924).
    * Why Do Multi-Agent LLM Systems Fail? [Cemri et al (2025)](https://arxiv.org/abs/2503.13657).

1. **AI Agents That Matter. [Kapoor et al (2024)](https://arxiv.org/abs/2407.01502).**
    \
    <sub>Evaluation; Rigor</sub>
    * AgentBench: Evaluating LLMs as Agents. [Liu et al (2023)](https://arxiv.org/abs/2308.03688).
    * $τ$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains. [Yao et al (2024)](https://arxiv.org/abs/2406.12045).
    * Agent-as-a-Judge: Evaluate Agents with Agents. [Zhuge et al (2024)](https://arxiv.org/abs/2410.10934).
    * The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity. [Shojaee et al (2025)](https://arxiv.org/abs/2506.06941).

1. **Training language models to follow instructions with human feedback. [Ouyang et al (2022)](https://arxiv.org/abs/2203.02155).**
    \
    <sub>Alignment; Training</sub>
    * Constitutional AI: Harmlessness from AI Feedback. [Bai et al (2022)](https://arxiv.org/abs/2212.08073).
    * Direct Preference Optimization: Your Language Model is Secretly a Reward Model. [Rafailov et al (2023)](https://arxiv.org/abs/2305.18290).
    * DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning. [DeepSeek-AI et al (2025)](https://arxiv.org/abs/2501.12948).

1. **Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters. [Snell et al (2024)](https://arxiv.org/abs/2408.03314).**
    \
    <sub>Test-Time Compute; Scaling</sub>
    * Measuring AI Ability to Complete Long Software Tasks. [Kwa et al (2025)](https://arxiv.org/abs/2503.14499).
    * Towards a Science of Scaling Agent Systems. [Kim et al (2025)](https://arxiv.org/abs/2512.08296).

1. **Voyager: An Open-Ended Embodied Agent with Large Language Models. [Wang et al (2023)](https://arxiv.org/abs/2305.16291).**
    \
    <sub>Open-Ended Agents; Lifelong Learning</sub>



</details>

<br/>

<details>
<summary>Top-level papers only</summary>
<br/>

1. **Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. [Wei et al (2022)](https://arxiv.org/abs/2201.11903).**
1. **ReAct: Synergizing Reasoning and Acting in Language Models. [Yao et al (2022)](https://arxiv.org/abs/2210.03629).**
1. **Toolformer: Language Models Can Teach Themselves to Use Tools. [Schick et al (2023)](https://arxiv.org/abs/2302.04761).**
1. **MemGPT: Towards LLMs as Operating Systems. [Packer et al (2023)](https://arxiv.org/abs/2310.08560).**
1. **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. [Lewis et al (2020)](https://arxiv.org/abs/2005.11401).**
1. **Cognitive Architectures for Language Agents. [Sumers et al (2023)](https://arxiv.org/abs/2309.02427).**
1. **SWE-bench: Can Language Models Resolve Real-World GitHub Issues? [Jimenez et al (2023)](https://arxiv.org/abs/2310.06770).**
1. **WebArena: A Realistic Web Environment for Building Autonomous Agents. [Zhou et al (2023)](https://arxiv.org/abs/2307.13854).**
1. **AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation. [Wu et al (2023)](https://arxiv.org/abs/2308.08155).**
1. **AI Agents That Matter. [Kapoor et al (2024)](https://arxiv.org/abs/2407.01502).**
1. **Training language models to follow instructions with human feedback. [Ouyang et al (2022)](https://arxiv.org/abs/2203.02155).**
1. **Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters. [Snell et al (2024)](https://arxiv.org/abs/2408.03314).**
1. **Voyager: An Open-Ended Embodied Agent with Large Language Models. [Wang et al (2023)](https://arxiv.org/abs/2305.16291).**


</details>

<br/>

<details>
<summary>All papers in chronological order </summary>
<br/>

1. **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. [Lewis et al (2020)](https://arxiv.org/abs/2005.11401).**
1. **Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. [Wei et al (2022)](https://arxiv.org/abs/2201.11903).**
1. Self-Consistency Improves Chain of Thought Reasoning in Language Models. [Wang et al (2022)](https://arxiv.org/abs/2203.11171).
1. Least-to-Most Prompting Enables Complex Reasoning in Large Language Models. [Zhou et al (2022)](https://arxiv.org/abs/2205.10625).
1. **ReAct: Synergizing Reasoning and Acting in Language Models. [Yao et al (2022)](https://arxiv.org/abs/2210.03629).**
1. **Training language models to follow instructions with human feedback. [Ouyang et al (2022)](https://arxiv.org/abs/2203.02155).**
1. Constitutional AI: Harmlessness from AI Feedback. [Bai et al (2022)](https://arxiv.org/abs/2212.08073).
1. Tree of Thoughts: Deliberate Problem Solving with Large Language Models. [Yao et al (2023)](https://arxiv.org/abs/2305.10601).
1. Reflexion: Language Agents with Verbal Reinforcement Learning. [Shinn et al (2023)](https://arxiv.org/abs/2303.11366).
1. Self-Refine: Iterative Refinement with Self-Feedback. [Madaan et al (2023)](https://arxiv.org/abs/2303.17651).
1. Let's Verify Step by Step. [Lightman et al (2023)](https://arxiv.org/abs/2305.20050).
1. **Toolformer: Language Models Can Teach Themselves to Use Tools. [Schick et al (2023)](https://arxiv.org/abs/2302.04761).**
1. ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs. [Qin et al (2023)](https://arxiv.org/abs/2307.16789).
1. Gorilla: Large Language Model Connected with Massive APIs. [Patil et al (2023)](https://arxiv.org/abs/2305.15334).
1. **MemGPT: Towards LLMs as Operating Systems. [Packer et al (2023)](https://arxiv.org/abs/2310.08560).**
1. Generative Agents: Interactive Simulacra of Human Behavior. [Park et al (2023)](https://arxiv.org/abs/2304.03442).
1. Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection. [Asai et al (2023)](https://arxiv.org/abs/2310.11511).
1. Lost in the Middle: How Language Models Use Long Contexts. [Liu et al (2023)](https://arxiv.org/abs/2307.03172).
1. **Cognitive Architectures for Language Agents. [Sumers et al (2023)](https://arxiv.org/abs/2309.02427).**
1. The Rise and Potential of Large Language Model Based Agents: A Survey. [Xi et al (2023)](https://arxiv.org/abs/2309.07864).
1. A Survey on Large Language Model based Autonomous Agents. [Wang et al (2023)](https://arxiv.org/abs/2308.11432).
1. **SWE-bench: Can Language Models Resolve Real-World GitHub Issues? [Jimenez et al (2023)](https://arxiv.org/abs/2310.06770).**
1. **WebArena: A Realistic Web Environment for Building Autonomous Agents. [Zhou et al (2023)](https://arxiv.org/abs/2307.13854).**
1. **AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation. [Wu et al (2023)](https://arxiv.org/abs/2308.08155).**
1. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework. [Hong et al (2023)](https://arxiv.org/abs/2308.00352).
1. CAMEL: Communicative Agents for "Mind" Exploration of Large Language Model Society. [Li et al (2023)](https://arxiv.org/abs/2303.17760).
1. ChatDev: Communicative Agents for Software Development. [Qian et al (2023)](https://arxiv.org/abs/2307.07924).
1. AgentBench: Evaluating LLMs as Agents. [Liu et al (2023)](https://arxiv.org/abs/2308.03688).
1. Direct Preference Optimization: Your Language Model is Secretly a Reward Model. [Rafailov et al (2023)](https://arxiv.org/abs/2305.18290).
1. **Voyager: An Open-Ended Embodied Agent with Large Language Models. [Wang et al (2023)](https://arxiv.org/abs/2305.16291).**
1. Chain of Agents: Large Language Models Collaborating on Long-Context Tasks. [Zhang et al (2024)](https://arxiv.org/abs/2406.02818).
1. Executable Code Actions Elicit Better LLM Agents. [Wang et al (2024)](https://arxiv.org/abs/2402.01030).
1. LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory. [Wu et al (2024)](https://arxiv.org/abs/2410.10813).
1. SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering. [Yang et al (2024)](https://arxiv.org/abs/2405.15793).
1. OpenHands: An Open Platform for AI Software Developers as Generalist Agents. [Wang et al (2024)](https://arxiv.org/abs/2407.16741).
1. OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments. [Xie et al (2024)](https://arxiv.org/abs/2404.07972).
1. **AI Agents That Matter. [Kapoor et al (2024)](https://arxiv.org/abs/2407.01502).**
1. $τ$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains. [Yao et al (2024)](https://arxiv.org/abs/2406.12045).
1. Agent-as-a-Judge: Evaluate Agents with Agents. [Zhuge et al (2024)](https://arxiv.org/abs/2410.10934).
1. **Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters. [Snell et al (2024)](https://arxiv.org/abs/2408.03314).**
1. A-MEM: Agentic Memory for LLM Agents. [Xu et al (2025)](https://arxiv.org/abs/2502.12110).
1. Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory. [Chhikara et al (2025)](https://arxiv.org/abs/2504.19413).
1. A Survey of AI Agent Protocols. [Yang et al (2025)](https://arxiv.org/abs/2504.16736).
1. Why Do Multi-Agent LLM Systems Fail? [Cemri et al (2025)](https://arxiv.org/abs/2503.13657).
1. The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity. [Shojaee et al (2025)](https://arxiv.org/abs/2506.06941).
1. DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning. [DeepSeek-AI et al (2025)](https://arxiv.org/abs/2501.12948).
1. Measuring AI Ability to Complete Long Software Tasks. [Kwa et al (2025)](https://arxiv.org/abs/2503.14499).
1. Towards a Science of Scaling Agent Systems. [Kim et al (2025)](https://arxiv.org/abs/2512.08296).


</details>

## How to read this

The top-level papers are the entry points; the nested items are follow-ups, alternatives, or
papers that disagree. Suggested reading order:

1. **Reasoning first** — Chain-of-Thought, then its refinements. Everything about agents assumes
   the model can reason in steps; know what that actually claims before building on it.
2. **Then the acting loop** — ReAct is the hinge of the whole field: reasoning interleaved with
   tool calls. Reflexion and Self-Refine add self-correction; Let's Verify Step by Step asks
   whether the model can tell good reasoning from bad.
3. **Then tools and memory** — Toolformer and friends cover calling APIs; MemGPT and Generative
   Agents cover keeping state across turns. These two are what separate a chatbot from an agent.
4. **Then architecture and surveys** — CoALA is the cleanest attempt to say what an agent *is*.
   Read it after the concrete papers, not before.
5. **Then the evaluation papers** — SWE-bench, WebArena, AgentBench, and above all *AI Agents
   That Matter*, which argues most agent benchmarks measure the wrong thing. Read this before
   believing any capability claim, including the ones earlier in the list.
6. **Multi-agent last** — AutoGen, MetaGPT, CAMEL, ChatDev. Then read *Why Do Multi-Agent LLM
   Systems Fail?*, which catalogues how these systems break in practice.

## Sources

This list was assembled from:

* [Papers We Love](https://paperswelove.org/)
* [Agent_Memory_Techniques](https://github.com/NirDiamant/Agent_Memory_Techniques) — 30 runnable
  notebooks and a memory-paper map
* [Agent-Memory-Paper-List](https://github.com/Shichun-Liu/Agent-Memory-Paper-List) — companion
  list to *Memory in the Age of AI Agents: A Survey*
* [kyegomez/ai-reading-list](https://github.com/kyegomez/ai-reading-list) — Transformer-era
  through 2025 frontier work
* [software-papers](https://github.com/facundoolano/software-papers) — the format this list
  reuses, and the reason the layering below is deliberate

## Selection criteria

Adapted from software-papers, with two changes for the agent field.

1. **The list should stay short.** No more than 30 top-level papers, each with a few related
   items. The goal is a list you can read start to finish, not a complete bibliography.
2. **One top-level paper per major topic.** Follow-ups, alternatives and rebuttals go in the
   nested list beneath it. Where two papers make the same point, the older or more precise one
   wins.
3. **Prefer papers that changed practice.** Agent research has a high ratio of surveys to
   results; a paper that introduced a mechanism people now build on beats a paper that
   taxonomises mechanisms.
4. **Freely available only.** Every link here resolves without a subscription. This is why the
   list is arXiv-heavy; notable exceptions are living benchmarks whose canonical home is a
   project site rather than a PDF.
5. **Include the negative results.** Benchmarks that show agents failing, and papers arguing the
   evaluation is broken, are load-bearing. A list of only capability papers is a marketing
   document.
6. **Skip the surveys you will not finish.** Long taxonomies of "LLM agent architectures" add
   vocabulary without adding capability. The two included here earn their place.
7. **Metadata is fetched, never typed.** Titles, author lists, years and links come from the
   arXiv API. This is the discipline that keeps a curated list from silently accumulating
   misattributions.


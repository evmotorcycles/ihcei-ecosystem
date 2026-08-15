# The layers — what has a GUI, and what deliberately does not

Two names in this project are **infrastructure**. They are not products, they have
no interface, and an ordinary person should never encounter them.

| | Expansion | What it is | GUI? |
|---|---|---|---|
| **IHCEI** | **Integrated Human Epistemological Interface** | The infrastructure layer the tools sit on. It carries the evidence model, the abstention contract, the receipt chain and the permission semantics. | **No — by design** |
| **NERE** | **Neural Epistemological Reasoning Engine** | The reasoning engine inside that layer. Scores evidence, detects ambiguity, routes claim types, decides when to decline. | **No — by design** |

## Why they have no interface

Because a person does not use them. A person uses **Cairn**, **Page Code**,
**HELM**, **Trig** or one of the nine **Novora** tools — and those sit on top.

The comparison is exact: nobody opens the TCP/IP stack. They open a browser. A
filesystem has no icon; a folder does. **Infrastructure that grows a user
interface has usually stopped being infrastructure and started being a product
competing with the things built on it.**

Two consequences that are enforced rather than intended:

1. **No page in this repository may be an IHCEI or NERE "console".** The
   browser-facing surfaces are the Governance Console, the Novora suite and the
   website. `test_layers.py` fails if a new HTML page appears that presents either
   name as a tool a person operates.
2. **The names stay out of the user-facing copy.** An ordinary person reading a
   result should never see the words "epistemological", "IHCEI" or "NERE". If they
   do, the interface has leaked its plumbing. The GUI tests check for this.

## The product layer, in the words a person would use

| Product | What a person calls it | What it does |
|---|---|---|
| **Cairn** | the label on the back of the packet | Shows what a claim is made of, and what is missing |
| **Page Code** | the valet key | Says what an app may touch; everything else is refused |
| **HELM** | the dashcam | A record where changing an old line visibly breaks the seal |
| **Trig** | the confidence meter | Checks whether stated confidence matches an independent measure |
| **Novora suite** | nine everyday checks | Contracts, decisions, messages, institutions, AI answers |

## What this rename does not change

Renaming a layer changes documentation, not behaviour. Every measured result in
this repository was produced by the same code before and after, and none of the
numbers move because a word did. This file exists so the distinction is written
down and testable — not to suggest anything was improved by writing it.

# Screening Task

First of all, if you are reading this then congrats! The Arva team thinks you have potential to be a great fit for the role.

The purpose of this task is to assess your ability to apply your full stack engineering and AI knowledge to a real world task and deliver value quickly. You have one week to complete this task. We expect you to spend a few hours (but not days) on it.

Please read this document carefully in full before starting your solution!

## Background

When an individual signs up for a regulated financial service e.g. a bank account, one of the checks that an analyst will typically have to perform is adverse media screening. This means performing a search for news articles that portray the entity in a negative light, e.g. lawsuits, scandals, bankruptcies. They will often use a data provider to surface these results, but those tools have very fuzzy matching leading to the analyst having to manually review a large number of false positives. They must justify why the article is or is not about their applicant by checking whether details such as name, date of birth or occupation are a likely match.

## Part 1

You have been tasked with building an MVP tool where an analyst can provide the name and optionally date of birth of an individual and the URL of a news article and the tool should determine:

- Whether or this person is a match to the individual described in the article, and
- If so, whether the article describes the person in a positive or negative light

You have been given a template as a starting point which performs a very simple web scrape and string comparison. You must flesh out this implementation to build a more effective tool.

You should approach this task carefully as you want to maximise the number of articles that can be discarded before they reach the analyst but cannot allow false negatives.

Since this is in a regulated context, you should also ensure that your output is explainable and auditable.

### Evaluation Criteria

We'll assess your solution based on:

- **Effectiveness**: Is what you have built an effective classifier?
- **Code quality**: Have you written clean, maintainable, and well-documented code?
- **User experience**: Is what you have built intuitive for a compliance analyst to use?
- **Explainability**: Is the result of your tool auditable and explainable?

You may receive additional credit for exploring a little further than what is explicitly stated above in whichever direction you find interesting.

## Part 2

Sometimes key details required to discount an article (such as middle names or dates of birth) are missing from the article itself but may be found by performing additional web research. Please include in your submission a detailed plan for how you might implement the automation of this additional enrichment. You are not required to actually implement this.

## Tools

It is up to you what tools you use to complete your solution. You may choose to use any of the current frontier or open source LLM providers such as OpenAI, Anthropic, Google or Huggingface. NB: DO NOT send us any API keys, assume that we have our own that we can use to test your tool.

You are welcome to use AI tools to help build your solution (Cursor, Copilot etc.) but please ensure that you understand the code you have written and are able to justify the decisions that you made. If your solution is identical to what Claude Code produces when given this task you probably have not put enough thought into it.

Have fun!

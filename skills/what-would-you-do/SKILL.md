---
name: what-would-you-do
description: "Explain a pending question or decision and recommend an answer, with the case for and against each option. Use when the user asks what you would do, or when you are about to ask the user a non-gate question: answer it yourself this way and act on the recommendation."
argument-hint: "[which question, or the part I do not follow]"
license: MIT
---

"What would you do?" The user answers a question you asked with this one, most often because they do not yet understand the problem well enough to choose. Take the most recent question or decision you put to them in this session; the arguments, if any, name another one, or the part they do not follow.

1. The question is the one you were about to ask, or the most recent one in this session. Neither exists: say so and stop.
2. Do the legwork the answer needs: read the code, config, docs, or output the question touches. Done when every claim you make about an option rests on something you read or ran in this session.
3. Explain the problem in plain words: what is being decided, why it came up, and what changes in the project with each answer. Define every term from the question the user may not know.
4. List the options as O1, O2, and so on: the ones you offered, plus any better one the legwork turned up. For each: what it does, why pick it, and why not (cost, risk, what it rules out later, how hard it is to reverse).
5. Recommend one in so many words ("I recommend O2") and give the deciding reason. When the answer hinges on something only the user knows (a preference, a deadline, a plan), name it and say which option each answer leads to. Not knowing the method is not one of those. Look up what people doing that job already do, with `research-with-sources`, and do that.
6. Hard question: the options stay close after the legwork and a wrong pick is costly to reverse. Give your lean anyway. Offer a jury line (`/jury` in Claude linked installs or Cursor, `/supermatt:jury` from the Claude plugin, `$jury` in Codex, `/skill:jury` in OMP, with the question, options, and constraints in full) only when the user asked for a jury, or the decision is a gate: a charge over $10, or a message a customer would receive. Otherwise the lean is the decision. Do not wait for them to run the jury.
7. A question that is not a gate: act on the recommendation in this turn. Do the work, commit and push under the repo's git rule, and tell the user one line what you chose and why. A charge of $10 or less is not a gate: do it and tell them the amount. Once $10 of those charges has been used, the next charge waits. If the best option depends on a fact only the user knows, name the assumption and still act, unless that fact is itself a gate. A gate: stop after the recommendation. They decide. A missing API key is not a gate: drive computer use, or the browser on a web page, to the copy control, then save it when they say "copied".

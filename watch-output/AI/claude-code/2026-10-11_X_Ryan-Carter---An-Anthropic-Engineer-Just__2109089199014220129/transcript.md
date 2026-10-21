# Ryan Carter - An Anthropic Engineer Just Revealed How Advanced Users Are Unlocking ...

_Source: captions (en, manual, unknown)._

```
[00:00] Hi, everyone
[00:02] I hope that you can hear me
[00:03] I'm not sure
[00:04] team here in Anthropic
[00:05] and
[00:06] today I want to talk about how you
[00:07] can get the most value out of your
[00:09] Claude Code sessions
[00:10] And just a quick bit of housekeeping first
[00:12] because I know there are so many of you here today
[00:14] which is great
[00:15] but it also means we won't be able
[00:17] to get to every question live
[00:19] So drop your questions in the Q&A as we'll go
[00:22] and we'll, you know
[00:23] answer as many as we can at the
[00:24] end
[00:25] And the ones we don't get to
[00:26] we'll follow up on afterwards together with the
[00:28] recording and the links
[00:30] But just so you know what this is about
[00:31] this session is about how Claude Code actually
[00:34] spends tokens when you work with it
[00:36] what you control about that
[00:37] so your own habits and set settings in a session
[00:40] and at the end also just the levers
[00:42] that you have if you set it up
[00:43] for a team
[00:44] I want you to walk out of this
[00:46] session here feeling in control of how efficiently
[00:48] you work in Claude Code
[00:50] and also with a good mental model
[00:52] of what a task ends up costing and
[00:54] and why
[00:56] And again
[00:56] if you're the person who sets up Claude
[00:57] Code for your whole team
[00:59] I hope you stay till the end
[01:00] because I'll also go through some of the
[01:01] levers that you have in our dashboard
[01:03] And
[01:04] I kind of want to show the mental model on purpose
[01:06] because I feel like we often just give you a checklist
[01:09] like, hey, do, do these things
[01:10] but that tends to go stale the moment
[01:12] we ship something new
[01:13] and personally, I think if you understand the mechanism behind something
[01:17] you can just work out the right move
[01:19] yourself for your environment
[01:21] in your context, all that kind of stuff
[01:23] And honestly
[01:23] I think this is a new skill for engineers
[01:25] You know
[01:26] software used to be a flat fee
[01:27] We used to pay for the tool or for the seats
[01:30] but in the era of agentic coding
[01:31] we're paying for the work itself
[01:34] right, task by task, you're paying per prompt
[01:36] So
[01:36] understanding how to be efficient with that is
[01:38] just part of the job now
[01:41] And the unit we're going to talk about most
[01:44] pretty much the whole time
[01:45] is tokens
[01:46] If your company runs Claude Code on API
[01:49] billing or through a cloud provider
[01:50] you're paying per token. So this table
[01:52] I'm sure you're familiar with this table
[01:54] you know tokens already
[01:56] But if you are on Pro or Max
[01:57] or Team or Enterprise
[01:58] you have these five-hour windows or a weekly window instead
[02:01] but also those windows are measured in tokens
[02:04] So whichever way you're set up
[02:06] tokens are the unit
[02:08] and how many
[02:09] tokens go into a task
[02:11] is what we're going to get better at
[02:12] today
[02:13] And this isn't about sending fewer of them
[02:14] or using Claude less
[02:16] we just want to make sure that the
[02:17] tokens that do go
[02:18] into a session actually go toward a thing you
[02:21] you know, ask Claude to do
[02:23] So let's take a step back real quick
[02:25] and look at what actually happens behind the
[02:27] scenes when we send a prompt to Claude
[02:29] So say that I have a failing test
[02:31] and I type fix the failing test in utils.test
[02:34] Yes, I press enter
[02:35] Now
[02:36] Claude Code doesn't just send that one prompt
[02:38] to the model
[02:39] When I started this session
[02:41] it already loaded a bunch of things for
[02:43] me
[02:43] Claude's own instructions, the system prompts
[02:46] the definitions of the built-in tools
[02:47] so read, edit, batch, and so on
[02:49] my environment, current working directory, git, everything
[02:53] We also have my CLAUDE.md file
[02:55] and I have some skills in here
[02:56] an MCP server set up
[02:58] and it will also include a short
[03:00] like
[03:00] name and description for all these things as
[03:02] well
[03:03] So
[03:04] all the way at the end is our
[03:05] message
[03:06] So all of this
[03:07] this entire bundle goes to the model as
[03:09] one request
[03:10] So that's already the first thing to understand
[03:12] It's never just the prompt
[03:13] And this bar down here
[03:14] as we're walking through this
[03:16] this is the context window
[03:17] So everything the model gets to see in this request
[03:20] and I'll keep this on the screen here
[03:21] because honestly this bar is what this talk
[03:23] is about. So our request arrives at the model
[03:26] but the model doesn't just read this as text
[03:28] it first goes through a tokenizer
[03:30] So this splits everything we send
[03:32] including the system prompts
[03:33] dot md, everything, into tokens, which are just small chunks
[03:37] roughly word sized, and the model processes those
[03:40] I won't go too deep into that today
[03:42] but it's important to understand that the input
[03:44] into the model is tokens
[03:45] and also whatever the model generates afterwards is
[03:48] also tokens. So from here on
[03:50] everything in this bar
[03:51] everything that comes back is token
[03:53] So the request arrives at the model
[03:55] the model reads all of it
[03:56] gets to my message
[03:57] and goes, okay, you want me to fix something
[03:59] but I only have a file name
[04:00] you didn't send the actual file
[04:02] So while it comes Back is not a fix
[04:04] it's just a tool call
[04:06] like hey, read utils.test.ts
[04:08] Claude Code or the harness then performs that
[04:10] it reads the file and sends this result
[04:12] back to the model
[04:13] and so on. Now
[04:13] I'm not going to walk through every step here
[04:15] that's not the point
[04:16] The point is the loop here
[04:18] The model decides that it needs to do something
[04:20] it sends a tool call back
[04:22] Claude Code performs it
[04:23] and then sends this result back to the
[04:24] model
[04:25] But notice that I didn't do anything here in the CLI
[04:28] it's the model choosing these tool calls
[04:30] and on every one of those round trip
[04:32] the bar grows
[04:33] So as we keep watching this
[04:35] you'll see a few things in the bar
[04:36] So there's a couple colors
[04:38] but two of these
[04:39] Whenever we send to the model
[04:40] I've marked blue, and whenever
[04:42] or whatever the model sends back is orange
[04:46] There's also this container around the beginning of
[04:48] the request that just keeps getting longer
[04:50] I'll get to that in a second
[04:52] But
[04:52] the most important thing here is what we're
[04:54] looking at is three kinds of tokens
[04:58] So first we have the input tokens
[04:59] which is everything we send to the model
[05:02] so everything in the bar
[05:03] We have output tokens
[05:05] which is everything the model sends back
[05:07] And that's not just the summary at the
[05:09] end. It's also the tool calls
[05:11] the edit, the thinking, everything the model did
[05:14] And everything inside this container
[05:16] these are cached tokens
[05:18] So we have three types
[05:19] We have input, output, and cached
[05:21] And you might recognize this from the pricing page
[05:24] because that's exactly how it's laid out
[05:26] right? Like we have a price per token
[05:27] per model, and then separate columns for the input
[05:30] cached input, and output
[05:32] Now I just want to quick
[05:32] take a quick look at why these are
[05:34] priced so differently
[05:36] First input. So whenever we send something to the model
[05:39] the model still has to process every input
[05:41] token
[05:42] But it can do all of them together
[05:43] like in one pass
[05:45] So GPUs are extremely good at that
[05:47] So per token, the input is pretty cheap
[05:49] but output is different. So the model writes
[05:52] one token at a time
[05:53] So to write something seemingly simple
[05:55] like const x equals one
[05:57] it does a full pass over everything in the context
[06:00] just to produce const
[06:01] appends it, does another full pass just to produce x
[06:04] and another one for equals
[06:05] and everything else
[06:07] So, so there's a lot more compute behind every output token
[06:11] and that's also why
[06:12] output is priced the highest
[06:14] of the token types
[06:16] And then there's cache tokens
[06:17] which is the cheapest one
[06:18] So
[06:19] a big part of the request is the same every time
[06:22] right? Like on every round trip
[06:23] we're only appending to the end
[06:25] But everything before that
[06:26] the model has already processed on the previous
[06:28] request. So the server doesn't treat that part as
[06:31] as brand new. It just
[06:33] keeps the internal state that it built up last time
[06:35] and only does all the recomputation
[06:38] or the computation on the point
[06:40] where this request starts to differ from The
[06:41] previous one. And that's the prompt cache
[06:44] So the identical part at the front is called the prefix
[06:48] and that's the container that you saw growing
[06:50] And this is read back for just a
[06:51] small fraction of the normal input price
[06:54] So the new part pays your full price once
[06:56] and then from the next request on
[06:58] it's inside the container
[07:00] Now, Claude Code sets this all up for you automatically
[07:03] but cache here, honestly, I think is your biggest lever
[07:05] because look at the bar again
[07:07] like a lot goes in
[07:09] and a very little comes out
[07:10] and nearly everything that goes in is inside
[07:13] that container. So in a healthy session
[07:16] most of your input
[07:17] is the cheap cached kind
[07:20] And you can check for that on your
[07:21] own session with usage
[07:24] So there's a line here for the prompt cache
[07:26] and that shows you exactly how much of
[07:28] your input came from cache
[07:29] In a healthy session
[07:30] that number should be high
[07:32] But there are a few things to keep in mind here
[07:34] because what we just saw is
[07:36] you know
[07:36] a list of things that we get to
[07:37] optimize. So how many tokens go in
[07:39] how many come out
[07:41] and how many of those are cached
[07:43] There's also one more thing is
[07:45] whether the model that's running all of this
[07:47] is actually the right model for the task
[07:49] Because we saw that the model has to
[07:51] process every single one of these tokens
[07:53] and a larger model
[07:54] like Opus or Fable
[07:56] is more expensive simply because per token
[07:59] it does a lot more computation
[08:01] And that's great for a lot of tasks
[08:03] but you might not need it for yours
[08:05] And because it applies to every token
[08:07] both in and out
[08:09] it directly multiplies everything else we're about to
[08:11] look at. So
[08:12] that's the first thing to get right
[08:14] Don't run the biggest model on a task that
[08:17] that just doesn't need it
[08:19] And also to be clear
[08:20] a smaller model is not a worse model
[08:22] The way I like to think about it
[08:23] is Sonnet is a really good generalist
[08:26] Opus is the expert
[08:27] and Fable is the specialist who's
[08:29] seen the problems no one else has
[08:31] And Haiku is just like a quick assistant
[08:32] Like an edit that you can describe precisely
[08:35] or a mechanical change or a question about
[08:37] the code that's already in the context
[08:39] that's great for generalist work and Sonnet gets you there perfectly
[08:42] paying way less per token
[08:45] But if there's like a subtle bug or just unfamiliar territory
[08:48] something you don't really know what's going on
[08:50] then Opus
[08:51] is a great expert and
[08:53] it's worth paying a bit more for that
[08:54] But that's not for every task
[08:55] right?
[08:56] The next thing is to give Claude the
[08:58] right context. So it needs fewer tool calls
[09:00] and fewer of these round trips to figure
[09:02] out what you're actually trying to do
[09:04] And some of that is in your prompt
[09:06] and some of this is having the right environment
[09:08] the right ClaudeMD skills set up
[09:10] And a really small one
[09:11] is
[09:12] you can actually add the file to the
[09:13] prompt. So in this case
[09:15] we could have said fix the failing test
[09:17] in at utils.test.ts
[09:19] So then before the request even goes to the model
[09:22] Claude Code already puts the contents of that
[09:25] file in
[09:26] So that first tool call
[09:27] just never happens because the model already has
[09:30] all the context
[09:31] Small one, of course, over a large session
[09:33] but I still like it
[09:35] Then it's also
[09:36] it's also important to make sure that
[09:39] there's not a bunch of stuff in your
[09:40] context that you don't need for this specific
[09:42] task
[09:43] And you can see what's in your context
[09:45] by typing context in a fresh session
[09:48] and you see exactly that
[09:49] So you see the system prompt
[09:50] you see the tools that are loaded
[09:52] your CLAUDE.md, how many tokens everything is using as well
[09:55] your skills, your MCPs
[09:57] So this is
[09:58] always worth doing before you start a new session
[10:01] just to make sure like
[10:02] okay, am I adding stuff that is unnecessary?
[10:06] Can I make my prompt more
[10:07] more lean?
[10:09] Now after seeing those insights
[10:10] there's a couple of things you can do
[10:11] The first one is CLAUDE.md
[10:13] Generally
[10:14] just
[10:14] don't keep anything in here that doesn't serve
[10:17] every task
[10:18] You might look at yours and find something like
[10:20] for database migrations, do this, do this, and do that
[10:23] but that doesn't apply to every task
[10:25] but we are still sending it on every prompt
[10:28] Those things
[10:29] usually you want to move to skills
[10:31] The nice thing about a skill is that
[10:33] they only load
[10:35] whenever the model decides that it actually needs
[10:37] them for this task
[10:39] it only sends by default the name and the description
[10:41] and based on the description
[10:42] the model can pick like
[10:43] okay
[10:44] this skill makes sense to load now because
[10:46] we are asking for a database migration
[10:48] But by default
[10:49] you don't want to add this to every
[10:50] single task if you're just asking for
[10:52] I don't know, a, a file rewrite or something
[10:55] something that has nothing to do with the
[10:56] database migration
[10:58] So
[10:58] a CLAUDE.md generally is just what applies for
[11:00] every task. And then second
[11:02] still in your CLAUDE.md
[11:03] is
[11:04] check if you still need all of this
[11:06] information
[11:07] Models have gotten really
[11:08] really good
[11:09] and
[11:09] instructions that you had to give the model
[11:11] maybe three months ago
[11:12] just might not apply anymore
[11:14] We have a skill for this now called
[11:16] /claude-api prompt-audit
[11:18] and this goes through all your instructions or your CLAUDE.md
[11:21] your skills
[11:21] and checks whether this is still relevant also
[11:24] for newer models
[11:25] And if not
[11:26] it proposes a diff with what you can
[11:28] Remove or refine for this model
[11:30] So that
[11:31] alone already takes a good chunk out of your input tokens
[11:35] and the same idea here for MCP server
[11:37] So
[11:38] you might have a lot of MCPs connected to your session
[11:41] and their full tool definitions load on demand
[11:43] these days
[11:44] So an idle server is pretty cheap
[11:46] but it's still not nothing
[11:47] So run MCP
[11:49] switch off whatever you're not using in that session
[11:52] or maybe use a CLI instead
[11:53] like the GitHub CLI
[11:54] AWS CLI, all of that stuff
[11:56] Claude can just run it and nothing
[11:57] you know, loads up front at all
[11:59] And then one other thing that also fills
[12:01] this bar is command output
[12:02] So
[12:03] whenever
[12:04] a command prints goes into this conversation exactly like a normal
[12:08] you know, file that Claude read
[12:10] and it stays there for the rest of
[12:12] the session
[12:13] Now a really big output is already handled
[12:15] by Claude Code. With past a certain size
[12:17] Claude Code writes it to a file and
[12:19] then only puts a short preview of the
[12:21] path in the conversation
[12:23] But a thing for
[12:23] to watch for is everything under that
[12:27] So a test runner that prints
[12:28] like one line for each of your
[12:30] 400 passing tests can come under that limit
[12:34] So
[12:34] all 400 lines are now part of every
[12:36] request after it
[12:38] So a quiet reporter that only prints the
[12:40] failures is also a tiny fraction of that
[12:42] And Claude will often add the quiet flag itself
[12:45] but the reliable way is to put the
[12:47] like two or three commands that you run
[12:49] all day in your CLAUDE.md
[12:50] also written exactly how you would run them
[12:53] So like
[12:53] run a single test with npx
[12:55] retest run filename and then reporter dot
[12:58] That's just once it's committed
[12:59] it's a team-wide setting
[13:00] or for something super noisy
[13:02] just have it run in a sub-agent
[13:04] which we'll get to in a moment
[13:06] Then in some cases
[13:07] you'll also notice the model reaches a lot
[13:08] further than you expected. It does a lot more
[13:11] more thinking, more tool calls, more file edits
[13:13] all that stuff
[13:15] In some session, you'll You, you, you can say, you know, make the button green
[13:20] and one time it just changes the color
[13:22] and another time it'll try to understand your
[13:24] whole code base and your design system
[13:26] everything
[13:27] And most of that is related to effort
[13:29] So effort goes along with your request
[13:31] and it just tells the model how thorough
[13:33] it should be
[13:34] before it calls the job done
[13:36] And the default that we set is usually fine
[13:39] but I also get that it's tempting to
[13:41] run on extra high or max because you
[13:43] you care about the task
[13:44] but that's really not always necessary
[13:47] And higher effort means more output tokens
[13:50] which then also means more input tokens
[13:52] everything else
[13:53] We see that with large
[13:54] larger models like Fable 5.1
[13:56] medium effort is excellent
[13:59] and even though the name medium might not sound like that
[14:02] that'll give you enough effort for the task you're doing
[14:06] lower effort levels are sometimes just as good
[14:09] as previous models on higher effort levels
[14:12] And this also gives you kind of a
[14:13] a nice rule of thumb when a result
[14:15] misses is Did it not know enough
[14:18] or did it not try hard enough?
[14:20] If it didn't know enough
[14:21] that's a model question. You might want to
[14:23] up the model
[14:24] If it skipped a file or it was lazy
[14:26] it didn't run the test or stopped halfway
[14:29] that's effort. And that also goes the other way
[14:31] right? Like if you notice that it's doing too much
[14:32] dial down the effort
[14:34] Now, now before we get to the cache
[14:36] one more thing about the amount of tokens
[14:39] the model only ever adds to your context
[14:41] It never removes anything. So in a long session
[14:44] everything we've talked about so far is still
[14:46] there on every request
[14:48] And even though most of it is cached
[14:50] cached is not zero
[14:52] So the model is still processing it
[14:54] and for most of the time
[14:55] you don't need it anymore
[14:57] So here, like in the top row
[14:58] I ran clear between the tasks
[15:00] so every task starts small again
[15:03] and the bottom row is a long
[15:04] session where every column still carries the task before it
[15:08] and then it just keeps getting taller
[15:10] Now the bottom session uses twice the amount
[15:12] of tokens as the top session
[15:13] just because
[15:14] task two and three were still carrying
[15:16] task one around the whole time
[15:19] So there's a couple things you can do
[15:20] here. The first is compaction
[15:22] So you can run compact
[15:23] while it replaces the
[15:24] whole conversation with a summary
[15:27] by the way
[15:27] you can also give it hints about what
[15:28] to remember and what to prioritize
[15:31] you can run rewind to drop the last
[15:33] few turns
[15:34] and run clear when you're starting something new
[15:38] And that's a top road that I kept
[15:39] doing there. So
[15:40] if you think you'll want the old conversation back later
[15:43] you can actually rename it first
[15:45] so rename the session
[15:46] then clear, and then resume still
[15:49] resume that old session if you want
[15:51] Now getting back to that cached prefix that
[15:53] we talked about earlier
[15:54] it's important to remember that the server can
[15:56] only
[15:56] reuse the part of the request that's identical
[15:59] to the previous request
[16:00] starting from the very first token
[16:03] And again
[16:03] that identical front part is called a prefix
[16:05] But the moment that one token is different
[16:08] everything after that point is new to the
[16:11] server and gets processed at full price
[16:14] So that's important to remember here with compact and clear
[16:16] we changed the prefix
[16:18] There's no way around that because we just
[16:20] changed everything that leads up to this point
[16:22] so it breaks the cache
[16:24] And then on the next request
[16:25] you pay the full price for whatever's in
[16:26] there now
[16:27] And after a compact
[16:28] that's just a small summary
[16:30] so that's usually pretty fine
[16:32] but everything else that's in this prefix is
[16:34] also good to know
[16:35] So
[16:35] this also includes the tool definitions and your
[16:37] system prompts
[16:39] the system prompt includes things like your working
[16:41] directory and the snapshot of your Git state
[16:43] when the session started
[16:44] then your CLAUDE.md
[16:45] and then the conversation so far
[16:47] And this is also why the same thing
[16:49] happens when you change models mid-session
[16:51] because the cache is that model's own internal
[16:53] state. So a different model has nothing to reuse
[16:56] and it just reads your
[16:57] whole conversation fresh once
[17:00] When you change the effort level on most models
[17:03] because that also sits in front of your request
[17:05] with fable five one being the exception
[17:07] you'll also break prompt cache when you change effort level
[17:11] We
[17:11] we do warn you
[17:12] a lot of the time before this happens
[17:14] so if you run model or effort while
[17:15] the cache is still warm
[17:17] Claude Code will ask you to confirm first
[17:19] And there's also plenty of things that are
[17:20] totally fine to change mid-session
[17:22] by the way, like editing files, changing permission mode
[17:25] that's all on the Claude Code side
[17:27] this never touches your request
[17:29] And your CLAUDE.md is only read once at session start
[17:31] so even if you edit this mid-session
[17:34] nothing changes
[17:35] it just
[17:35] shows up in your next session or after you clear
[17:38] Now, time is the next thing
[17:39] because we don't cache forever
[17:41] The server just keeps this prefix around for
[17:44] a limited amount of time
[17:45] and then every request you send resets this
[17:47] timer
[17:48] So while you're working
[17:49] the cache is still warm
[17:51] Today, that window is about an hour on the plan
[17:54] within your plan's usage
[17:55] and about five minutes on API billing or
[17:57] a cloud provider
[17:58] Sub-agents also get five minutes every on any plan or API
[18:01] but, but you can change that
[18:03] So there's a prompt cache TTL setting
[18:05] for the main conversation and also a matching
[18:07] one for a sub-agent
[18:09] But you don't always want to do this
[18:10] because the long window also isn't free
[18:13] Writing tokens into a one-hour cache is built
[18:15] at a higher rate
[18:16] than writing them into a five-minute one
[18:19] So if you work in like steady bursts
[18:21] and rarely pause for more than a few minutes
[18:24] the short window is usually cheaper
[18:27] because you'd be paying extra for the time
[18:28] that you never use
[18:30] So the long window pays off if you do step away
[18:32] maybe a meeting or a lunch or a long build
[18:34] and, you know, come back to the same session
[18:36] Okay, so practically, TLDR
[18:38] what does this mean and what can you do?
[18:40] Well, first
[18:40] don't break the cache yourself or try to
[18:42] avoid it
[18:43] Make the model an effort choice at the
[18:44] start of a session or right after you clear
[18:46] so there's nothing cached to lose
[18:48] Now
[18:48] if you do want to switch model in
[18:49] the middle of a task
[18:50] maybe compact first and then switch so that
[18:52] the new model
[18:53] only has to read a short summary
[18:55] instead of your entire conversation
[18:57] And also make sure that you compact while
[18:58] the cache is still warm
[18:59] because compacting means that the model will read
[19:01] your entire conversation one more time
[19:03] to write that summary
[19:05] So if the cache is still warm
[19:06] that read is pretty cheap
[19:07] But if you wait until after the window
[19:10] Say you come back after an hour and then compact
[19:13] that same read is now full price
[19:15] full input price
[19:16] So try to compact your change before you step away
[19:19] not when you come back
[19:20] And it's the same story when you resume
[19:22] an old session
[19:23] So by then, in most cases, the cache has already expired
[19:27] or at least mine has
[19:27] My sessions are long and I
[19:29] I take breaks
[19:30] So
[19:30] that first session or that first message back
[19:33] sends the whole conversation to the model again
[19:35] and none of it is cached
[19:37] So it's all just plain input
[19:39] And if you need that full context
[19:41] that's fine. It's only once
[19:42] but if you know that you'll come back tomorrow
[19:45] maybe it's better to run like compact first
[19:47] before you leave
[19:49] so that
[19:49] what you
[19:50] resume the next day is just a shorter
[19:52] summary
[19:53] And
[19:54] one more tool for keeping what's in your
[19:56] session useful is subagent
[19:58] So sometimes Claude needs to kind of research
[20:00] something bigger to answer your question
[20:02] maybe a long log
[20:03] a whole repo, a full test run
[20:05] something. And you really only want the conclusion
[20:08] but not all these thirty files that it
[20:10] read to get there
[20:11] And that's what a subagent is for
[20:13] So this runs in its own context
[20:15] which is own small system prompt
[20:17] your CLAUDE.md file
[20:18] and just a task
[20:20] And it does all the reading and all
[20:21] the tool calls over there
[20:23] and it only sends you the final conclusion
[20:25] back into the main conversation
[20:26] but everything else that it read dropped
[20:28] Now, token-wise, to be clear
[20:30] a sub-agent isn't free. It
[20:32] still has its own input and output tokens
[20:34] its own cache, and again
[20:35] that cache is that five-minute window
[20:38] so the total for that one job can
[20:40] even be a bit higher at some points
[20:42] but what you win is that your main
[20:44] conversation stays small and
[20:46] optimized for the task that you actually want Claude to do
[20:48] so every turn after that is cheaper
[20:51] And your context window
[20:52] is also not full of all these
[20:54] log files
[20:56] and you actually have a lot of control on sub-agents
[20:59] so you can run a different model than your session
[21:01] so a haiku or sonnet sub-agent for digging
[21:04] you can set the effort level
[21:06] and if you have any custom sub-agents
[21:08] just know that you can also set the
[21:09] model and effort level for that sub-agent
[21:12] So far, everything here was about your own sessions
[21:15] but if you're the person who sets Claude
[21:17] Code up for a whole team
[21:18] there's also an admin side to all of
[21:20] this. And it's really the same levers
[21:22] set once just for everyone
[21:24] And most of this lives in one place
[21:26] managed settings
[21:28] And this is a
[21:28] settings file that you define in the admin console
[21:31] so every install on your team picks it up at startup
[21:34] and users cannot override it
[21:36] There's a couple things that you can configure
[21:37] here. So first is the starting model
[21:39] and also which models people can pick at
[21:41] all
[21:42] So when a team spend is unexpectedly high
[21:45] this
[21:45] usually traces back to just the biggest model
[21:48] just being left on as a default
[21:50] You may not need that
[21:51] so you may just pick a smaller model
[21:53] That's just one line
[21:54] and it's the highest leverage thing here
[21:56] Second is the starting effort level
[21:58] and it's the same story as earlier
[22:00] People tend to leave it on highest because they care
[22:02] but you definitely don't always need the highest
[22:04] effort level
[22:05] So you can set the default once and
[22:07] still raise it for a task if you
[22:09] want to
[22:10] And on enterprise
[22:10] you can also cap the max
[22:12] Maximum per model. And third is the cache window
[22:15] if your team is on API or cloud
[22:17] So that's the prompt cache TTL from earlier
[22:19] You can just set it once for your
[22:20] whole team
[22:21] So if your developers tend to work in like steady bursts
[22:23] you can leave the short window
[22:25] but if they
[22:25] tend to disappear into meetings and come back
[22:28] to the same session
[22:29] you can
[22:29] set this to like an hour and just
[22:31] accept the higher write price
[22:33] You can also set which MCP servers are allowed
[22:35] so there isn't just a pile of idle
[22:37] ones sitting around
[22:38] And there's an organization-wide CLAUDE.md
[22:41] that you can ship to every machine
[22:42] So every session
[22:43] on the team starts with them
[22:45] Then you can also see what's happening
[22:47] So the console has this analytics view for
[22:49] adoption
[22:50] and a spend report per user and per
[22:52] model when you've turned on usage credits
[22:55] Another useful one is OpenTelemetry
[22:57] You just set it with two environment variables
[22:59] in that same manage settings file
[23:01] and then every install reports input
[23:03] output, cache reads, and cache writes per person
[23:06] And you can see the cache reads here
[23:08] as a share of all the input per user
[23:10] and that should be by far the biggest chunk
[23:12] because that means that their sessions are staying
[23:14] warm
[23:15] If someone's share for these cache tokens is low
[23:18] that means they're breaking the cache somewhere
[23:19] And, you know, as we talked about before
[23:22] maybe it's a model switch
[23:23] an effort switch
[23:24] And you can also see the input tokens
[23:26] per session over time. And what you want
[23:28] to see here is a line that climbs during a task
[23:31] but then drops back every time
[23:33] Clear or start a new session
[23:35] If it only ever climbs
[23:36] then someone, you know, is just living in one endless session
[23:40] and maybe resuming an older session when
[23:42] cache had already expired
[23:44] You can also see the cost by model
[23:46] per user. So this tells you
[23:48] which people have a bigger model for everything
[23:50] So those are
[23:51] kind of exactly the habits from this talk per person
[23:55] and each one is just
[23:56] you know, a one message fix
[23:57] Like, hey, I notice you've been doing that
[23:58] And last is limit. So on team and enterprise
[24:02] the seed's five hour and weekly window is
[24:04] the ceiling. So
[24:05] no one gets past that by accident
[24:07] But if you do want your people to keep working
[24:09] you can turn on usage credits and put
[24:11] a spend limit on it
[24:12] either per organization, per group, or per person
[24:14] And one related setting here is auto continue
[24:16] at usage limit
[24:18] And this defines whether a session that hit
[24:19] that window just waits
[24:21] but then automatically picks the task back up
[24:23] when the window resets
[24:25] So this matters for these long unattended runs
[24:27] So one prompt is many requests
[24:30] and every request carries the entire conversation
[24:33] And the cache
[24:34] makes that history cheap as long as the
[24:36] front or the prefix of the cache stays the same
[24:39] and you keep moving
[24:42] So ultimately
[24:42] what you should remember is three things
[24:45] One is to pick your model
[24:46] your effort level
[24:47] and your MCP servers at the start of
[24:49] a session and leave them alone
[24:51] You can change your effort level if you're using Fable 5.1
[24:54] but that's the only model that doesn't break
[24:56] prompt cache
[24:57] But by not changing any of these settings
[24:59] the front of every request keeps matching the one before it
[25:03] so it doesn't break prompt cache
[25:05] So Claude can keep reading from the cache
[25:07] instead of having to reprocess the whole conversation
[25:10] And two is to be deliberate about what
[25:12] you put into the conversation
[25:13] right? So point Claude at the files you already know about
[25:16] keep your command output quiet
[25:18] and send the really noisy digging into a subagent
[25:23] and so
[25:23] that way only the summary comes back into
[25:25] your main conversation
[25:27] And the third one is to make sure
[25:28] your session stays focused
[25:29] so clear whenever you start a new task
[25:32] So you're not, you know
[25:33] paying for task one during task three
[25:35] all that
[25:36] And try to compact if you're doing that
[25:37] before you step away while the cache is
[25:39] still warm. And
[25:41] remember that Resuming an old session
[25:43] or coming back after a long break
[25:45] after the cache expired means
[25:47] means one full read of everything
[25:49] And the model is a multiplier of all
[25:51] of this. So
[25:52] pick the model that's right for your task
[25:54] And for a team
[25:55] you can make those same choices in managed
[25:57] settings. So using Claude Code efficiently doesn't mean
[26:00] using fewer tokens
[26:02] You just want the ones that you do
[26:04] use
[26:04] going towards the thing you actually asked it
[26:06] Prices and features will keep changing
[26:08] but hopefully that part won't
[26:11] I hope this helped kind of demystify where tokens go
[26:14] at least a little bit
[26:15] appreciate you coming to this webinar
[26:17] Let me know if you have any questions
```

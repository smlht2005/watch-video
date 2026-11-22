# Hux - 今晚別刷Netflix了。  去看這個SpaceX AI工程師1小時的課程。  這是我見過最清晰、端到端講透GrokBot到底該怎麼真正用...

_Source: captions (en, manual, original)._

```
[00:01] personally, I think that, the best use of you
[00:06] of AI is really is like a
[00:08] like a pair, like someone you're pair programming with
[00:11] and not someone as
[00:12] not, not a
[00:13] not a tool to just replace the act of writing code
[00:16] or worse, outsourcing your thinking
[00:19] And I think there's a tendency
[00:20] like, you know, because AI is so exciting
[00:22] you wanna put
[00:23] AI everywhere and be seen as someone who's very
[00:26] you know, what do you call it
[00:29] like, on the ball, I guess, with, with AI, that you feel this pressure of
[00:35] like, you know, I'm just gonna, I gotta increase my productivity
[00:38] I gotta ship, like, a hundred PRs this week
[00:40] and barely understand what I'm doing
[00:42] and, you know, vibe code my way to a
[00:44] a million ARR or whatever
[00:49] but I think You know
[00:52] one of the things that I've personally seen
[00:53] is that although when I use AI
[00:56] I save some time
[00:57] you know, writing the code
[00:59] I actually find myself spending
[01:00] more time reviewing what the AI did and
[01:03] like, correcting it
[01:04] So, you know, like, I've, I've tried the
[01:06] the thing that a lot of people say
[01:07] like, you know, you
[01:09] instead of prompting an AI to just build the feature outright
[01:13] you sort of get it to
[01:15] build a spec for you first
[01:16] then you review that spec
[01:18] and then you do that whole thing
[01:19] Then it's like, okay
[01:21] so I assume you can see my screen?
[01:23] Yes, yeah, we're good
[01:25] So, yeah, today, yeah, I think
[01:27] I think the big theme for me
[01:28] as I've been using agents to write code
[01:31] and I'm sure a lot of you have
[01:32] had the same experience as well
[01:34] is how do you trust it?
[01:36] You know
[01:36] especially if you are an engineer that's been
[01:39] writing code for a very long time
[01:41] you have
[01:42] a lot of
[01:43] opinions and lessons that you've learned
[01:45] about doing good engineering
[01:47] And when you see agents just
[01:49] you know, winging it and, you know, guessing, hallucinating, you know
[01:54] confidently stating that they found the smoking gun
[01:57] for the hundredth time
[01:59] but it's actually not the real problem
[02:01] you lose a lot of trust
[02:03] And when you lose
[02:04] when you don't Much trust in your agents
[02:07] I feel like you
[02:08] you really can't get the most out of
[02:09] them
[02:10] And for me
[02:11] the parallel is like with management
[02:14] so if I'm an
[02:15] a manager, an engineering manager of a team
[02:17] and I have a bunch of
[02:19] you know, I have a team of engineers
[02:21] on my team, and I don't trust them
[02:24] then
[02:24] the mode of operation I'm going to be
[02:26] in is going to be like micromanagement
[02:28] right? I'll have to
[02:29] spend a lot of time
[02:31] looking over my reports' shoulders and
[02:34] checking that they're doing their work well
[02:36] you know
[02:36] that they're not shipping bugs to production
[02:40] And so I drew this chart because
[02:43] it's not, it's not a very scientific chart
[02:45] but like this is how I imagine
[02:48] myself and my journey through using agents
[02:52] So, you know, like fast forward or back forward
[02:56] or fast back, fast backwards, like a year or so when
[03:01] you know, nobody was
[03:02] or not many people were using agents to
[03:04] code
[03:06] I think you
[03:08] you get into this mode where you are
[03:12] In very heavily in the loop with one or several
[03:15] like a handful of agents
[03:17] and you find yourself just constantly fig
[03:20] you know, trying to understand what your agents are doing
[03:23] and you're very, very in the loop
[03:24] You're watching every single output
[03:26] You are sitting there prompting
[03:29] and you really can't parallelize beyond that because you don't
[03:34] again, you don't have that trust
[03:35] right? You can't go to a hundred agents
[03:38] like spawn a hundred agents when you don't
[03:39] even trust the output of one agent
[03:43] So, over the past five months
[03:45] I feel like I've really been able to
[03:48] like, ascend this trust curve
[03:51] and now I'm at the point where
[03:54] I actually have, this sounds kind of scary to say this
[03:57] and it makes me sound like a slop artist
[03:59] but I, I promise I'm not
[04:01] But I actually have my agents now
[04:03] auto-merging PRs for me
[04:05] which is like a wild thing to say
[04:07] but
[04:08] like I woke up today
[04:10] and there were like 20 PRs landed and
[04:12] I just reviewed them on main
[04:14] like they were already landed
[04:16] and they were good
[04:18] so how did I get to that point?
[04:19] It's basically what I wanted to talk about today
[04:24] and again, like, yeah
[04:25] feel free to jump in if you have questions
[04:27] Colin
[04:29] but, oh yeah, of course I gotta show this
[04:32] this chart, where
[04:38] oh, do, do not trust, someone requested to control my computer
[04:43] probably won't do that
[04:44] but Yeah, so this chart, I think, I, I
[04:48] I'm trying this chart not to kind of like flex
[04:50] but to kind of show like the journey
[04:53] Like, so you can see like the curve
[04:54] like it
[04:55] it sort of like inversely matches the
[04:57] contributions I've been able to land at cursor
[05:01] So I joined five months ago
[05:02] and five months ago
[05:03] like I, you know, my first month
[05:05] I was like not very productive because I was
[05:07] you know, I was learning the code base
[05:09] didn't know what the heck was going on
[05:12] And as I got more confident in
[05:14] in my agents
[05:15] I've really been able to kind of ramp
[05:17] up my productivity
[05:19] and again, like, yeah
[05:21] like last month I shipped a thousand PRs
[05:24] which is ridiculous
[05:26] and then this month
[05:27] we're only on the 12th
[05:28] I'm already at, like, almost 800 PRs landed
[05:33] so the velocity is definitely high
[05:36] and you, you, I
[05:37] I'm sure a lot of you will definitely be questioning
[05:39] like, how
[05:40] how much of this code is actually good
[05:42] and I think, yeah, like, that's definitely fair to question
[05:47] but, yeah, I think
[05:50] I think if you set up your agents well
[05:54] you can definitely get to
[05:55] a very similar level
[05:58] and so I'm going to talk about how
[05:59] we do that
[06:03] so for me, I think, I'm curious, like, I guess, Colin, your experience as well
[06:07] but, for me
[06:09] I think the most important skill
[06:12] that you should have in your toolbox
[06:15] when you work with agents is verification
[06:18] and by verification
[06:19] I mean
[06:20] the ability for an agent to actually run the code
[06:25] or take CPU traces or heap snapshots or
[06:30] you know, open an iOS simulator
[06:33] whatever, you know, however your application is exposed to your users
[06:37] it can do the same thing and
[06:41] run it for real
[06:42] and actually test and verify its own work
[06:45] Because that's the thing that really
[06:46] closes the loop
[06:48] it doesn't guarantee your agent writes good code
[06:51] but it allows them to at least write correct code
[06:56] which is a big
[06:56] a really big step forward for
[06:58] being able to trust your agents
[07:02] I will, I can share one example that we have
[07:06] within cursor
[07:10] oops, where, let me open this
[07:21] Let me, let me, make my full screen
[07:25] Here you go
[07:27] so for the, for Cursor's agent window
[07:31] so this is actually an interesting story
[07:33] but, when I joined Cursor five months ago
[07:37] they're actually, well
[07:40] I was supposed to join a different team
[07:41] I was supposed to join
[07:42] like, the cloud agents team
[07:44] but then since I have a lot of
[07:45] experience working on React
[07:47] and agents window is a React application
[07:51] I was
[07:53] I was asked to basically help out with
[07:56] the agent window work
[07:59] but
[08:02] There wasn't really a lot of
[08:03] like, skills to help me
[08:05] So I just found myself like
[08:06] okay, Agent's Windows is going to launch in like a week
[08:09] right? We have a really tight deadline
[08:11] and, there was, you know, I was just sitting there like
[08:15] okay, I'm going to open up the performant
[08:17] the, the Chrome DevTools and just like take a trace
[08:20] look at it myself
[08:21] and try to make sense of this flame
[08:22] graph
[08:23] And keep in mind
[08:24] I was just like in my first week
[08:26] so I had no idea what I was looking at
[08:28] no idea what, you know, I mean I had some idea
[08:30] but, you know, the
[08:31] the code base was completely fresh to me
[08:34] and I realized like my agent had no idea either
[08:37] you know, like I would take a screenshot of the trail
[08:39] download trace, or send it to it
[08:40] and it'd be like
[08:41] yeah, it kind of looks like this
[08:43] you know
[08:44] and it would like confidently state like it's this thing
[08:47] and then I'd try to fix that
[08:48] and turns out that's not the actual thing
[08:51] So this was a very
[08:53] very slow process
[08:54] And if you've ever done any like performance work yourself
[08:56] or, you know
[08:57] just even
[08:58] development with an agent where you don't have a verification skill
[09:02] you are the verifier
[09:03] right? You, you're the bottleneck
[09:05] You, you, you tell your agent to do something
[09:07] and then it goes off and writes some
[09:09] code
[09:09] Then you open up your
[09:10] you know, local dev build, and then you start to say
[09:13] oh, you know, it doesn't work
[09:14] Then you got to copy paste screen
[09:15] you know, screenshots or console errors or whatever
[09:19] and then your agent like slowly kind of like
[09:22] you know
[09:23] works with that and then tries to understand it and
[09:27] That fix the thing
[09:29] But then you're constantly just in the loop and
[09:31] and being a bottleneck. So there's really no
[09:32] way to parallelize
[09:34] So the control glass skills are like one
[09:36] of the first skills I built
[09:38] for cursor
[09:40] and glass, by the way
[09:40] is the code name for agent's window that we use internally
[09:44] but it's just cursor
[09:46] I guess
[09:48] and so this skill
[09:50] is, I guess the, the
[09:51] the code itself is not super interesting
[09:53] Your agent can very easily make one for you
[09:56] where if
[09:57] if you're building an electron app or a web app
[10:00] or even iOS, applications
[10:03] you can teach your agent how to use
[10:05] like, the Chrome DevTools protocol
[10:07] or through
[10:09] Apple has some
[10:11] utilities as well for running the simulator and
[10:13] taking traces and controlling programmatic control as well
[10:18] so that's really useful
[10:21] but one thing I actually want to talk about is
[10:24] the
[10:26] This thing
[10:29] ready to read me
[10:31] so this skill comes with this very unique feature called
[10:35] or not feature
[10:36] unique file called a feature map
[10:39] And so the story then is like
[10:41] I built this skill
[10:42] and so now the agent was able to
[10:45] actually run
[10:46] the agent window and take traces and whatnot
[10:50] but it had no idea what
[10:52] what the agent's window was
[10:54] So, you know, like someone would say like
[10:57] oh, the
[10:58] the left sidebar is like laggy or something like that
[11:02] Or, you know, the right side, the
[11:04] the PR tab is not working
[11:06] And the agent would just be like kind
[11:07] of flailing around. It would spend a lot
[11:08] of time trying to like look up the code and
[11:10] you know, where is this feature?
[11:11] How do I actually get to it
[11:13] on the UI?
[11:14] Which made it basically completely useless
[11:17] you know, like we would
[11:18] I would run this skill locally and
[11:22] you know, it would spawn a dev build
[11:24] but then it just be Churning
[11:26] like I just try to click here
[11:28] it wouldn't know how to get to things
[11:31] and it was just an awful experience
[11:33] so, who is putting arrows on my screen?
[11:38] so, yeah, this, this feature map has been really useful
[11:43] because it teaches the agent how to get
[11:45] to all of the features that you have
[11:48] and in PStack, the plugin that I
[11:50] I've made, if you search for PStack cursor on Google
[11:55] you'll, you'll find it
[11:57] but there is a create verification skill in that plugin
[12:01] where it actually helps you
[12:02] set up something like this for yourself
[12:04] including the feature map
[12:06] so it will actually explore the code
[12:08] and build up this initial feature map
[12:10] that tells your agent
[12:11] how to get to
[12:12] all of the different features that you have
[12:14] and this is extremely powerful because
[12:17] now that you have these user reports that come in
[12:20] you can actually map
[12:22] even like a vague report
[12:23] or even a screenshot
[12:25] So we have this
[12:27] internally at Cursor, where, we have a Slack channel with
[12:31] you know
[12:31] lots of
[12:32] people giving us feedback on the agents window
[12:35] and Grokbot and whatnot
[12:37] and oftentimes the report is very bad
[12:41] like very low quality. Like someone will just put
[12:43] very often we get like a screenshot
[12:45] like, and then someone just says question mark
[12:46] question mark, question mark, like, what is this?
[12:49] And, you know, like, without this, your agents
[12:51] I have no clue
[12:53] right? But with a feature map like this
[12:55] it has a lot more
[12:57] context and understanding of how to actually navigate
[13:01] how to get to all of the different features
[13:03] so like, you know, example, like, I guess, like the sidebar, like
[13:06] what is the sidebar?
[13:08] you know
[13:08] like all the different sub features
[13:10] that are present in it
[13:13] like from the user point of view
[13:14] which is where to
[13:15] how to get to it
[13:16] all the different keyboard shortcuts
[13:19] even like the, the, what do you call it
[13:22] the DOM elements or
[13:24] yeah
[13:24] like the attributes that you use for selecting
[13:26] things through the CDP
[13:29] are all there
[13:31] So, again, yeah, this is like really
[13:33] really powerful, for, for agents
[13:37] and a PStack ships
[13:39] that create verification skill
[13:40] but also a maintain verification skill
[13:44] so you can keep this up to date
[13:46] Cool, yeah
[13:47] I was just gonna ask how you created
[13:48] that. So do you mind sharing a little bit more about
[13:51] that, that process in the context of PStack
[13:52] and maybe just what PStack is for
[13:54] the folks who aren't familiar?
[13:56] Yeah, so PStack is pretty interesting because
[14:00] well, first of all
[14:00] the name is kind of goofy
[14:02] Like the P, the P in PStack is like potato
[14:05] potato stack
[14:07] Because I, so, there is a pretty
[14:13] famous person, Garry Tan, who is the CEO of Y Combinator
[14:17] and he's come up with this plugin called GStack
[14:21] GarryStack, and, funnily enough, we share the last name
[14:25] we have no relation
[14:27] but I thought it would be funny to kind of
[14:29] you know
[14:29] poke fun at Garry and make PStack my version of
[14:33] of, of, of his plugin
[14:36] but kind of just tailor it to
[14:37] my own set of engineering practices
[14:42] but I honestly actually never set out to
[14:43] build PStack
[14:45] it just started with a bunch of skills
[14:47] right? Like, I started with that control glass skill
[14:49] and then I started with another skill
[14:51] like, called HAL, which I also noticed through
[14:54] like, observing agents
[14:58] so, like, you know, in the early days of me
[15:00] you know, trying to climb this ladder
[15:01] I was, like, super in the loop
[15:02] and I was
[15:03] basically nitpicking my agents to an extreme degree
[15:06] I was like, I would tell it
[15:10] you know, this feature has stopped working
[15:12] Here's a bug report
[15:13] Like, why isn't it working?
[15:16] And very often, the agent would just
[15:18] like, confidently state, like, oh, it has to be this
[15:21] right? It has to be this thing
[15:23] And I noticed, like
[15:24] when I looked at the actual tool calls
[15:26] I noticed it wasn't actually reading the code
[15:29] that I thought should be affected
[15:31] and that made me just extremely suspicious
[15:33] And at that point
[15:34] I was just like
[15:34] I'm not gonna, I can't trust any
[15:36] this agent anymore, because it's just
[15:38] it's just completely hallucinating
[15:40] And I think I think it's very easy to just
[15:44] you know, like build up that distrust and not
[15:47] and kind of feel helpless
[15:49] like, you know
[15:50] you don't know how to help your agents succeed
[15:53] But like, again, I think the, the
[15:54] the management analogy is super helpful because like
[15:57] imagine if you were a manager of an
[15:58] engineering team
[16:00] and you had
[16:01] an engineer on your team who was a really good coder
[16:04] no business contacts whatsoever
[16:05] you know, they, they just, you just hired them and they
[16:08] they onboarded, you know, like five seconds ago
[16:12] and so how do you actually teach that
[16:14] person to be effective?
[16:16] So how you do that is through a
[16:17] skill
[16:18] a skill being just
[16:19] you know, it's just marked down
[16:21] right? But, you know, it encodes a lot of information
[16:24] instructions, a lot of
[16:27] you can really draw out
[16:28] a lot of Intelligence from an agent by
[16:32] well, some people on Twitter call it like
[16:34] you know, pull the agent to a different latent space
[16:37] which is kind of like a fancy way of just saying
[16:39] like since, you know, LLMs are sort of like
[16:41] they predict the next token
[16:44] when you give it some high quality tokens
[16:47] to begin with, then, you know, it
[16:48] it can kind of pattern match on
[16:51] like a higher space that's
[16:52] you know, smarter
[16:55] so that's like a very interesting model there
[16:59] But yeah, I built PStack very
[17:00] very incrementally
[17:02] so, started with just really observing how agents
[17:06] you know, all the fail, different failure modes of
[17:08] of that agents were having
[17:10] And every time I saw that
[17:11] I just, okay
[17:12] I'm just going to make that a skill
[17:13] Right, like stop hallucinating, actually go and search up
[17:17] look up the code
[17:18] use a lot of sub-agents
[17:20] and yeah, stop guessing
[17:26] Yeah, that makes sense. One
[17:27] one kind of follow-up question here
[17:28] both from myself and from a bunch of
[17:29] people in the chat. So
[17:31] I guess it's two
[17:32] two parts. So one is like
[17:33] how do you maintain these skills?
[17:34] So like the product changes over time
[17:36] Obviously
[17:36] there's a lot of people that should be
[17:37] against the code base
[17:38] So how do these skills get maintained?
[17:41] and then second to that is like
[17:42] how do you know when your verification is
[17:44] is good enough?
[17:46] like in, you know
[17:47] you can trust that the
[17:48] verification loops that you've built are gonna
[17:51] I guess you trust that the outputs
[17:52] when, when they're done
[17:56] yeah, maybe I'll talk about
[17:59] I think I have somewhat really
[18:00] maybe I'll start with this one first
[18:02] So like, how do I maintain these skills?
[18:07] So, if you're not familiar with this concept
[18:10] an eval is essentially like a way to
[18:14] well, I think the mental model I have is like
[18:16] it's like a unit test for an agent
[18:19] and, you can actually make your own evals
[18:22] You don't need like a special framework for
[18:24] them
[18:24] You can build, you can
[18:25] you can build one depending on like
[18:28] you know
[18:28] how
[18:29] scientific and how rigorous you want to be
[18:32] my screen is red
[18:34] Yeah, there's a little button
[18:37] sorry. Oh, is mine like disabling the drawing or something?
[18:39] I, I can't see my screen
[18:41] Yeah, sorry. If you guys could not draw on the screen
[18:43] that'd be great, but, there's a little button in the
[18:47] yeah, the, the little drop down
[18:50] Yeah
[18:53] Okay, yeah
[18:53] You got it, perfect
[18:55] Continue
[18:57] Yeah, so evals are a way to unit test your skills
[19:01] basically
[19:02] And actually, in PStack, we ship
[19:05] under Potato Mode, there's a playbook, if you search for it
[19:07] called eval playbook
[19:10] and it's
[19:12] it's like not, it's actually pretty
[19:14] pretty rigorous the way it's done
[19:17] but
[19:18] essentially what I do is
[19:19] I spawn a lot of different sub-agents
[19:22] I have, like, my main coordinator agent
[19:25] come up with a rubric for
[19:28] what I want the skill to do
[19:32] and then it spawns all these sub-agents
[19:33] and it, it creates individual directories for them
[19:37] which are cleverly named to not
[19:40] let the sub-agent know that it's being evaluated
[19:43] because, agents can actually tell
[19:46] and when they do
[19:47] they change their behavior
[19:49] but it does a bunch of stuff like that to
[19:53] essentially, yeah
[19:54] like test whether or not the skill
[19:56] I'm making or changing is actually doing
[19:59] what I think it does
[20:01] and one of the really nice things about
[20:02] Cursor is that we are
[20:04] we, we support so many different models
[20:06] so
[20:07] you can actually eval your skill across all
[20:09] sorts of different models
[20:12] And, you know
[20:12] get a sense of how well it performs
[20:14] across that different matrix
[20:18] especially for the models that you use
[20:21] so I do this a lot
[20:22] Every time I, I modify a skill
[20:24] I will run one of these
[20:26] like the eval playbook
[20:28] and make sure that
[20:29] you know
[20:29] it's actually leading to a result I want
[20:33] but I will say like
[20:35] Maintaining skills is actually pretty hard
[20:38] it requires, I think, a lot of taste and observation
[20:42] So
[20:42] you kind of need to
[20:44] be very good at being a backseat driver
[20:47] You know what I mean?
[20:47] Like, if you do pair
[20:48] if you've ever done pair programming
[20:50] for example, and you watch a coworker code
[20:53] and you just like
[20:54] you, you could probably do this better
[20:55] You know, you could do, you know
[20:56] like, why did you not do this
[20:57] right? You've, you've asked a lot of questions to your coworker
[21:00] and it's kind of a similar thing here
[21:01] You like
[21:02] you don't want to just be a passive
[21:04] observer of the agent
[21:05] you want to be very in the driver's seat
[21:07] in the initial stages when you're building up
[21:09] your own set of skills
[21:11] you know, obviously you can use something like DSAC
[21:13] but if you're building your own set of skills
[21:15] it's very, I think, you know, opening up the
[21:18] all the tool calls and like reading the
[21:20] code and reading all the
[21:23] the agent behavior and their thinking blocks
[21:26] is a really great way to see where they
[21:29] they fail, right? Like what, what
[21:32] You know, where are they being done?
[21:33] And then you can go and build a
[21:34] skill for that
[21:36] And then with verification
[21:37] how you trust it is
[21:39] it's, I think it's also a very similar iteration loop
[21:42] where, you know
[21:43] like I actually did the same process for
[21:45] verifying the verification skill
[21:48] where I actually get
[21:51] So one thing that's interesting about evals is
[21:53] that you can sort of hill climb them
[21:55] meaning that, your eval can produce a score
[21:59] right?
[21:59] a score that you can get your coordinator to produce
[22:03] but also
[22:04] you can have a judge agent of a different model to
[22:08] kind of
[22:09] cross-reference and make sure that the
[22:11] first model is not being biased
[22:13] right? The model that's judging all of the
[22:15] sub-agents that are running the thing
[22:17] but you can also like hill climb
[22:19] so meaning that you can
[22:20] you can use like slash loop in cursor
[22:23] and you can say
[22:24] okay, keep looping on this eval
[22:27] right, until everything is 10 out of 10
[22:29] as an example
[22:31] and I did the same
[22:32] the basically the same approach with the control skill
[22:34] and so I kind of
[22:35] it was very, it was very hands-off
[22:36] actually
[22:38] so, you know, I, I kind of built
[22:40] I built that skill that way
[22:42] like the CLI in that skill
[22:44] and over time, it's gotten really good
[22:48] but yeah, it was definitely not super smooth
[22:51] Beginning and required a lot of iteration
[22:54] And I think there's an analogy here for me
[22:57] which is, well
[22:59] I make this analogy later in a different
[23:01] slide on my drawing here
[23:03] but I think of it like
[23:06] you know, as a, as a engineer now
[23:09] you're sort of more like
[23:11] like maybe a manager
[23:13] or the analogy I like is like you're like a
[23:15] a chef in a restaurant
[23:18] you know, you're the head chef
[23:19] you're not cooking all the food yourself anymore
[23:22] You have a team of cooks
[23:23] right? You have line cooks
[23:24] you have a sous chef
[23:25] you have, you know, all these different stations
[23:29] and it's your job to really design the environment
[23:31] You know, you, you
[23:32] you're in charge of setting up the kitchen
[23:34] You're in charge of
[23:35] you know, like giving tasks to different people
[23:39] So
[23:41] yeah, it's a very interesting way of working
[23:46] but yeah, that's, that's how I basically built
[23:48] these verification skills
[23:50] Yeah, just, just one follow up there on like
[23:52] try to go one layer deeper
[23:54] So are you, let's say we wanted to build
[23:58] an eval or a skill for
[24:00] for something
[24:01] and we wanted to kind of get better on its own
[24:03] which is, is what I think you're suggesting
[24:05] are you doing that in like a work tree
[24:08] kind of isolated with like the sub-agents and
[24:10] and then the reviewer agents and
[24:12] and all that? Is it happening like in
[24:13] some type of cloud-hosted environment?
[24:15] Like what's the, the more, the practical steps?
[24:17] If I wanted to go do this
[24:19] and like set up a verification system for something
[24:21] what would I do or where would I
[24:22] start?
[24:26] I think that, the best place to start is local
[24:29] because you can observe
[24:31] You can definitely observe what your agents are doing
[24:33] So, if you're building a verification skill for yourself
[24:37] I would definitely start local and
[24:39] just have your agent bring up the application
[24:42] whether it's like a CLI or
[24:44] a desktop app or whatever
[24:46] And so you can actually observe
[24:47] right? You can see how the agent is interacting with the
[24:51] the application
[24:53] You can see it
[24:53] you know, how it calls like the different APIs that
[24:57] that allow it to interact with the
[25:00] the application
[25:03] but, for me personally
[25:05] I have basically been kind of all in
[25:08] mostly all in on cloud agents because they're
[25:10] extremely powerful
[25:12] and the really powerful thing about Cursor is the
[25:15] the cloud agents actually
[25:17] where if you spend a little bit of
[25:18] time setting up your environment
[25:21] These control skills
[25:22] these verification skills pay a
[25:24] huge amount of dividends
[25:25] because it's not just something that
[25:27] makes you as a single engineer better
[25:31] it actually levels up your whole team
[25:33] and even your whole company because
[25:35] you can actually start thinking about cloud agents
[25:38] you can start thinking about automations that automatically do things like
[25:44] I'll, I get, I
[25:44] I kind of talk about this a bit later
[25:46] but I'll just kind of Get into it
[25:49] where, where, you know, for example, like
[25:51] I talk a lot about this agent we have called Benny
[25:54] right, who, who, you know
[25:56] takes all of the bug reports that we get
[26:00] and it automatically goes off in the cloud
[26:02] opens up a cloud
[26:03] its, you know, its desktop
[26:05] It runs Cursor in its own computer
[26:08] and it uses the same control skills
[26:11] to interact with the application and try to reproduce the bug
[26:14] or the user report
[26:16] right? And this is so
[26:17] so powerful because at once I can immediately
[26:19] I get so much information from this automatically
[26:23] Like here in this example
[26:24] you can see that
[26:25] the Benny actually reproduced the bug
[26:28] but it's already fixed on me
[26:31] So it actually confirms that we fixed this problem already
[26:34] and all I need to do is just
[26:35] release another build of
[26:37] of Cursor
[26:39] so that's like huge information
[26:40] there that I didn't have to go off
[26:42] and sit with an agent
[26:43] you know, and spend an hour trying to figure
[26:45] like, is this fixed? Is this not fixed?
[26:47] So you You gain back so much time
[26:50] but, you know
[26:50] everybody on my team benefits from this
[26:52] Everybody in the company benefits from this
[26:56] So definitely think that
[26:58] you know, keeping these
[27:00] using cloud agents is super powerful
[27:03] But yeah, it's like a journey
[27:04] You have to trust it first
[27:06] right, before you get to this point
[27:09] And that's, it goes back to what I was saying here
[27:11] where, you know, it's very hard, it's almost impossible
[27:14] and I would
[27:15] definitely encourage you not to try to jump from
[27:18] you know, like, if you're still in this zone
[27:21] you don't want to jump to
[27:22] like
[27:22] I'm going to spawn a hundred
[27:24] or thousands of cloud agents right now
[27:26] because you're just going to waste a lot of tokens
[27:29] and it's going to be extremely expensive
[27:32] Yeah, so just to kind of recap so far
[27:34] basically the
[27:35] if we wanted to go on the journey
[27:36] that you've kind of gone on
[27:37] it would be just start with verification
[27:40] building
[27:41] some skills and
[27:42] some ways of determining that the agents are producing at least
[27:45] like, correct code, whether, like you said
[27:47] whether it's good code or Not as serious of a question
[27:49] but like it's, it's technically solving the problem by looking at
[27:52] you know, stack traces, looking at, you know
[27:54] the actual behavior in the app and so
[27:56] on
[27:57] and then once we trust it locally
[27:58] then we can start to think about scaling
[28:00] into the cloud and running more
[28:02] agents that are picking up signals
[28:04] I guess, on their own, right?
[28:05] So
[28:05] whether that's like a bug report that comes in or something
[28:07] they can go and pick it up and
[28:08] solve the problem and
[28:09] and give us backup PR
[28:11] And then maybe the last step is like
[28:13] auto merging the PRs
[28:14] which
[28:15] is where you're at and
[28:16] maybe not where I want to go
[28:18] and then interviewing them on main
[28:19] but, is that, is that about right?
[28:22] Yeah, exactly. I think, yeah, that's why I do this
[28:24] this, this, this curve, right?
[28:25] Because that, this, this basically describes my journey of
[28:29] you know, when I started, barely could use a couple agents
[28:32] and I was just observing every single thing
[28:35] I think there's really no shortcut for going
[28:37] from here to there
[28:38] because this is really about your personal level
[28:40] of trust in agents
[28:42] right?
[28:43] obviously, you know, as a, as an engineer
[28:45] you don't want to just slot code into
[28:46] production
[28:47] So how do you actually build up that trust takes
[28:51] a lot of, I guess, taste and judgment
[28:55] but, you know, like
[28:56] I think plugins like PStack definitely can help you
[29:01] get up to speed much quicker
[29:03] and so, I guess it's like
[29:05] if you trust me and you trust PStack
[29:07] then in, by extension
[29:09] you can maybe trust your agents
[29:11] But if you don't trust me
[29:12] and I
[29:12] I definitely would not encourage people to blindly trust me
[29:18] you know
[29:18] if you build up your own set of
[29:20] skills that you can obviously
[29:21] you know
[29:21] take a look at PStack and kind of fork it
[29:24] make it your own
[29:25] improve the skills, definitely encourage that
[29:28] but for me, it's really all about
[29:30] it, it, it just keeps coming back to trust
[29:32] You know
[29:32] every one of us
[29:33] here in this chat have a different standard for engineering
[29:37] and there are different things that
[29:39] are important for us in our code base
[29:41] And
[29:42] when you
[29:43] are able to encode all of that into
[29:45] skills and you can verify that your agent
[29:47] is actually doing them
[29:49] that allows you to really kind of ascend this curve
[29:51] And
[29:54] you know, start automating things
[29:56] there's another piece I wanted to talk about
[29:59] if there's... Yeah, go for it
[30:01] I'll think of more questions as I go
[30:02] but yeah. I think there's a third part to this
[30:05] which I haven't talked about yet
[30:06] which is kind of an interesting one
[30:08] which is like refactoring and rewriting
[30:11] Like one of the
[30:12] I guess most controversial
[30:14] one of the most controversial topics in the industry
[30:17] I think, is like
[30:18] should you rewrite your app or not?
[30:21] because I think engineers are very prone to this
[30:24] where especially when you join a company
[30:26] you come in and you see like the
[30:28] code base and you're like
[30:29] oh man, this is shit
[30:30] Like who wrote this code?
[30:32] You know
[30:32] it's terrible. I want to rewrite the whole
[30:34] thing
[30:34] There is a very common inclination and
[30:37] I think a lot of
[30:39] you know, before agents, and I guess arguably even now
[30:42] people will definitely discourage you from rewriting stuff
[30:46] But I'm actually here to make a case
[30:47] for why you might want to consider it
[30:51] because
[30:54] I think it really depends
[30:55] you know, Brownfield applications, I think
[30:58] are actually in a pretty good spot
[31:00] especially if they're set up well already
[31:03] and like recently I've been talking to some people
[31:05] but, you know, I was just observing
[31:08] I just noticed this parallel
[31:12] which is that
[31:13] a lot of big tech company problems are
[31:15] now everybody's problems
[31:18] and the big tech company problem
[31:19] you know, like when I was working at Meta
[31:21] like we had this giant monorepo
[31:23] we had like, I don't know
[31:24] tens of thousands of engineers just
[31:26] you know, like banging on their keyboards and
[31:28] and shipping code
[31:30] And a lot of really great engineers at Meta
[31:35] but, I'll say like, you know
[31:37] you'll be surprised that the code quality is
[31:39] actually not that good
[31:41] and so I often joke that like
[31:43] you know, before AI slop, we had human slop
[31:47] and so, you know
[31:47] I think a lot of big tech infra
[31:50] like, like what Meta has or Google
[31:53] you know, you know
[31:53] really big tech companies are actually designed for that
[31:56] where you're, you're sort of like
[31:58] you're catering to the
[31:59] the, you know, like, that sounds so bad to say
[32:02] but like the, the least capable engineer on your team
[32:05] right? You build, you build frameworks, you build conventions, you build guardrails
[32:10] you know, you restrict credentials so that
[32:12] you know, your intern doesn't wipe your production database
[32:17] There's, you know, if you have that level of infra already
[32:22] I think your agents can actually already do
[32:23] a very solid job
[32:25] right? Because they have
[32:26] the guardrails are already in place for
[32:29] agents to not cause havoc or not cause too much havoc
[32:33] in your codebase
[32:35] and you can always add more
[32:37] you know, guardrails
[32:39] but I think like Greenfield applications
[32:40] especially are, you know
[32:41] like the brand new applications are like the biggest risk
[32:45] in my opinion, and also the greatest opportunity
[32:49] Because, you know, if you vibe code a project
[32:52] a prototype, like we did for Grokbot
[32:55] you know, Grokbot was spun up very
[32:56] very, very quickly
[32:58] and if you, if you haven't heard of
[33:00] of Grokbot, it's like a
[33:01] a new application we just launched yesterday
[33:04] it's, it's really cool
[33:06] lets you orchestrate your
[33:08] create like individual agents that have their own identity
[33:11] and you can kind of orchestrate them
[33:12] It's super cool, definitely check it out
[33:15] but yeah, that was, it's like a very
[33:16] it was a very
[33:17] Field application like most prototypes are
[33:20] So it was like vibe coded very quickly
[33:22] Humans were not reading the code at all
[33:25] And, I had this tweet recently
[33:29] where I said something about organic architecture
[33:35] maybe I'll find it
[33:36] but the idea is that
[33:40] when you have a completely vibe coded application
[33:43] you essentially have no guardrails whatsoever
[33:45] So, your agents When you give them a task
[33:50] they will just solve it in whatever
[33:52] method is the most convenient
[33:54] And over time, you get into this
[33:57] situation where you have a code base that
[33:59] is spiraling out of control because you don't understand it
[34:03] your agents understand it
[34:05] I guess, in a way, but, like
[34:07] they've built something that is
[34:08] you know, optimized for short, for shortcuts
[34:12] and, you know, it will, you will suffer, you have a lot of
[34:15] of issues with that application
[34:19] so I think starting your code base with
[34:22] like, very strong constraints is very much needed
[34:28] because, like
[34:29] when you have a code base that you can trust
[34:31] right, when you have guardrails that actually help you
[34:35] help your agents, right? Good code
[34:38] You can get into the
[34:39] you know, like into this part of the curve where I
[34:41] I, where I, like I, I said, you know
[34:43] I woke up today and I had like 20 PRs merged
[34:47] by my agents
[34:48] And that's because I invested a lot
[34:50] a lot, a lot of time
[34:52] over 600 PRs. I
[34:54] I, I calculated yesterday
[34:57] when I refactored all of Grokbot to this
[34:59] new architecture that I've been building
[35:03] and yeah, I've, I've gotten to a point where I
[35:07] I don't really look
[35:07] I really don't look at the code anymore
[35:09] And, I say that not just
[35:12] you know, to sell you tokens
[35:13] but
[35:14] because it, I, you know, it, it
[35:16] it took a lot of work to get
[35:17] to that point. I spent a lot of
[35:18] tokens to get
[35:20] the code base to this point where I
[35:21] no longer have to look at it
[35:24] but I'm very excited because You know
[35:26] the potential where
[35:27] you know, it's not just
[35:28] it just doesn't just benefit me
[35:30] It benefits everyone contributing to Grokbot
[35:33] and it also empowers
[35:35] you know, designers and product managers and
[35:38] you know, people
[35:39] even GTM people to add features to Grokbot
[35:42] And I don't have to worry
[35:43] you know, I don't have to
[35:44] to wake up at night in
[35:45] in the middle of the night and worry like
[35:47] oh shit, someone's just merged a perf regression
[35:49] right? I have a ton of constraints and CI
[35:53] It's like, it's actually very annoying to write code in
[35:56] in Grokbot
[35:56] but like agents absorb all of that annoyance
[36:00] but yeah
[36:01] I'm happy to talk about what exactly that is
[36:05] Yeah, I think one question
[36:08] Before we get into the
[36:09] this part here is
[36:10] just around that element of like what your
[36:13] your, your CI looks like
[36:14] or maybe some of the constraints
[36:15] and then also like the average PR size
[36:17] I saw a question about that earlier
[36:18] Just to give people a
[36:19] you know, kind of a glance
[36:21] It doesn't have to be like mathematically average
[36:22] but just, you know, like what generally the size of the
[36:25] of PR is
[36:27] if it's only a couple lines of code or
[36:29] you know, yeah
[36:33] I think it depends
[36:35] Maybe
[36:37] I'm trying to do this in a way
[36:38] where I'm not gonna like
[36:39] Yeah, you don't have to share the actual number
[36:42] like the actual average
[36:43] I think this is fine
[36:45] But like we have
[36:46] so okay, this is not that interesting
[36:49] but well
[36:50] fun fact
[36:51] is that virtualization in Grokbot and in
[36:55] Cursor is actually powered by pretext
[36:59] which is a
[37:00] sort of new library that someone's built
[37:04] That's really interesting
[37:05] You should check it out
[37:07] But that's not really that important
[37:08] I think the average PR size
[37:10] I actually don't know
[37:12] I don't know if I want to click
[37:13] on these
[37:14] I probably can
[37:16] but I would say like
[37:17] they can range anywhere from
[37:19] a few hundred lines or 50 lines to like a thousand
[37:22] depending on what the thing is doing
[37:25] So like here, I'm actually like deleting a bunch of files
[37:28] so I expect that it's just like mostly deletion
[37:32] But yeah, it kind of varies
[37:34] There's no like, yeah
[37:36] There are like 50 line PRs
[37:38] There's no hard cap
[37:39] definitely no hard cap
[37:40] but
[37:40] I do encourage my agents to split up
[37:42] their work into multiple PRs
[37:45] I do that mostly because I like
[37:49] I like the idea of the
[37:51] I guess maybe this is much harder to
[37:52] do now as
[37:53] in the world of agents and you have
[37:54] like so many commits
[37:56] But I like the idea that
[37:57] you know
[37:57] the Git history is a very rich source
[37:59] of context
[38:01] And I like the
[38:02] I like each PR to sort of
[38:04] atomically describe what that small piece of thing is doing
[38:09] which also makes it easier for me to
[38:10] revert changes and like figure out
[38:12] you know, oh, I shipped a bug and it's this
[38:14] it's here. It's not in this
[38:16] 40,000 line PR where who knows what
[38:19] landed in there
[38:22] But I don't have a hard cap
[38:24] on PR size
[38:26] Cool. And then, yeah
[38:28] also quick question on like CI
[38:30] So again, you don't have to go into like
[38:31] the screen share like your
[38:32] your CI does, but just generally
[38:34] would you describe what the CI kind of looks like
[38:37] or how strict it is?
[38:40] yeah. So, well, specifically for Grokbot, so Dune is the
[38:45] is the sort of cheeky code
[38:47] code name for the architecture that we've built
[38:49] for Grokbot
[38:52] the CI looks pretty annoying because there's checks for everything
[38:57] So, like literally I have
[39:01] well, if you've written any React
[39:02] for example, you know
[39:03] you know that one of the biggest foot
[39:04] guns in React is useEffect
[39:07] so in Dune, and in Grokbot
[39:11] we've banned useEffect
[39:13] So Dune is just an
[39:14] you can, the, the mental model of what Dune is
[39:17] you can kind of think of it as like Next.js for
[39:20] Electron apps, and it's designed for agents to write
[39:24] and it's like custom for
[39:25] you know, our agent powered applications
[39:30] so the CI checks are very like specific to that
[39:31] like, you know, don't use useEffect
[39:33] It's, it's, it's banned, like CI will fail
[39:37] and yell at you
[39:38] We have, like
[39:39] some of the more interesting ones that people
[39:41] might raise eyebrows is like
[39:42] I actually ban code comments as well
[39:45] which is very interesting
[39:47] but I've noticed that 99% of the time
[39:51] agents just write code comments that
[39:54] kind of describe some historical thing that is
[39:56] actually totally irrelevant to the code
[40:00] like it will often say like
[40:01] you know, oh, Lauren said you should never do this
[40:03] and it's now in
[40:04] in a code comment. I'm like
[40:04] what?
[40:05] Like, why? That, that was
[40:07] I didn't say that as like a durable You know
[40:09] global rule. I just met like your
[40:11] this PR sucks and you should
[40:13] change that part
[40:15] Agents don't really understand this that well
[40:18] surprisingly
[40:20] and or they kind of assume too much
[40:22] and they kind of do things in like
[40:23] very stupid ways
[40:25] So like, yeah, we just ban everything
[40:27] Everything you can imagine like the agents are bad at
[40:30] we ban
[40:32] so
[40:33] one example that we actually suffer a lot
[40:35] in the agents window is we have
[40:39] you know, if you've used agents window
[40:40] you've definitely seen performance issues and
[40:42] you know, we're constantly trying to fix them
[40:44] but it's like a
[40:46] It's a never-ending struggle
[40:48] because there's so many pull requests that get
[40:50] merged
[40:51] Any one of them could just regress
[40:53] performance or stability or reliability
[40:56] you know
[40:56] the agents window doesn't have this architecture yet
[40:58] I plan to do
[40:59] bring this learning back there
[41:01] and kind of refactor everything there
[41:04] but, it just regresses super often
[41:08] because, there's, just one example is like
[41:11] we have very poor
[41:13] isolation between processes
[41:15] So like on, you know, on, on Electron
[41:17] you have a renderer thread that renders your UI
[41:20] but you also have like a main thread
[41:21] that you can run other code that
[41:23] you know, doesn't need to block the renderer
[41:27] but we do a poor job of separating those things
[41:29] and so oftentimes you just accidentally
[41:32] have code that gets pulled into running on the renderer thread
[41:35] and then all of a sudden you're competing with the
[41:38] the renderer that, you know, that has a very
[41:40] if you want like 60 FPS
[41:42] you have to every frame that gets drawn
[41:45] has to be done in 16 milliseconds
[41:47] So very, very small, you know, deadline per frame
[41:50] if you want, you know
[41:52] a very smooth product
[41:53] and when you start building
[41:54] bringing in, accidentally bringing in, you know
[41:57] things that are
[41:58] like very computationally heavy or they have a lot of IO
[42:02] then you just get into like a lot
[42:04] of jank
[42:04] And your, your FPS really drops
[42:06] you start, you know, losing frames
[42:09] you get long tasks that take more than 16 milliseconds
[42:12] and then you just get this really choppy
[42:14] experience
[42:16] So all of those patterns that we've learned
[42:18] basically building electron apps
[42:19] we've encoded into this framework
[42:21] and it becomes like a hard failure
[42:23] So I literally, in, in Grokbot
[42:25] we literally have a directory called electron main
[42:28] electron renderer, and we have, import CI, I guess
[42:34] where we actually
[42:36] check the dependency graph to make sure they're
[42:38] not accidentally importing
[42:40] code from one directory to another
[42:42] so that's enforced by CI
[42:45] as well as BugBot
[42:47] which is our, which cursors
[42:50] like code review tool that runs on CI
[42:53] you know, in our agents MD
[42:55] it's everywhere. Like, so I, I, I
[42:57] I, I have this thing here where I
[43:00] I talk about like
[43:02] you know, like there are multiple layers
[43:04] I think, for building a good code base
[43:07] obviously the code base is one where
[43:10] if you have an architecture like this
[43:12] where it's extremely strict
[43:14] you know, the, the
[43:15] the way to build features is very conventional
[43:18] That's like the strongest
[43:19] strongest level of enforcement
[43:21] because agents just love to copy existing patterns
[43:25] So
[43:26] one example of this in Grokbot is like we have this
[43:28] these concepts called like a feature
[43:31] and we have entry points and trans
[43:33] Cards, like all, you know
[43:34] the cards that you see in the chat
[43:36] these are all like
[43:37] like nouns, I guess, in, in the framework
[43:40] And so there's a very conventional way of
[43:42] creating them
[43:43] And so like a feature is all in
[43:46] in a single directory
[43:47] as an example
[43:48] And so all of the code that contributes
[43:50] to that feature lives in one directory
[43:53] So it's all co-located in one place
[43:55] Makes it super easy
[43:56] you know, agents don't have to like
[43:57] wrap around and try to figure out like
[43:59] where all the things are
[44:01] It just looks at the feature and like
[44:02] oh, okay
[44:03] I'm working on the onboarding feature in Grokbot
[44:07] I'm just going to work in this directory
[44:09] And for 80% of the work
[44:11] it's mostly just very encapsulated there
[44:14] But, like, it's like very, it's like design again for
[44:18] you know, like the dumbest agent
[44:20] like you don't have to think
[44:21] right? The, the, the
[44:23] one of the key principles I have for
[44:25] this framework is like the shortest
[44:28] the shortest path is the best path
[44:31] So
[44:32] because that plays exactly to how agents love to write code
[44:35] that they like to take shortcuts
[44:37] really
[44:37] You know, they'll find the quickest way to solve the problem
[44:41] so
[44:41] why not make that the best
[44:43] way to solve the problem?
[44:45] so, I, I
[44:46] I probably won't get into all the specific details
[44:48] and, the
[44:51] this framework's really more of a collection of
[44:53] ideas and principles rather than something that will
[44:56] open source
[44:57] you can, you can, you know, screenshot this, I guess, if you want, and
[45:01] tell your agent to
[45:03] do some, build, build something like this for you too
[45:08] yeah, but it's really all about the layers
[45:10] you know, like, the
[45:11] the code base is one part with features
[45:14] and directories and, you know, import, blocking import dependencies, that shouldn't be imported
[45:21] but, and, and it all enforces that and static analysis
[45:24] So, like, there's CI checks
[45:27] we have a lot of lint
[45:28] for bad patterns that we Serve
[45:31] compiler diagnostics
[45:34] there's also rules in BugBot
[45:35] which are, I think like three
[45:38] four, five are more soft
[45:40] right? These two actually make
[45:43] make CI red, right?
[45:45] So that, you know
[45:46] there's a hard constraint where the agent can't
[45:48] just write crappy code
[45:51] For rules and skills in BugBot
[45:54] Your agents can still forget
[45:56] right? You can still
[45:58] or it may not always consistently apply them
[46:01] So I like to layer them
[46:04] but I don't
[46:04] I don't like to
[46:06] rely on them as the only source
[46:08] of enforcement because it's very
[46:10] very soft, right? And if you
[46:11] if you only have rules and BugBot and
[46:13] skills and a style guide for your code
[46:15] you will
[46:16] it's only a matter of time before your
[46:18] code base looks like complete trash
[46:21] sorry to say that
[46:22] but, I definitely recommend, yeah, like, you know, investing
[46:25] in, you know, things that can be hard enforced
[46:29] right? And this is why
[46:30] you know, maybe
[46:31] the choice of tech stack that you use
[46:33] is also very important
[46:36] Like, I think, for example, Rust is sort of making
[46:38] you know, it's like getting super popular again
[46:42] because the compiler is so strict
[46:44] right? The compiler enforces so many different things
[46:47] you know, there's a borrow checker that you have to appease
[46:50] and
[46:50] as long as you make sure your agents
[46:51] don't write unsafe code blocks
[46:54] you can more or less feel
[46:56] somewhat confident that if the code compiles
[46:58] it probably works and it's good
[47:01] but you'll see it gives you that level
[47:02] of trust and confidence
[47:04] that
[47:05] you
[47:06] as a human engineer no longer
[47:08] need to go and check it yourself
[47:10] You, you know
[47:10] you rely on code and static analysis to actually make that
[47:17] a lot smoother
[47:20] and I, I guess the worst part
[47:21] the worst
[47:22] place to be in is if
[47:24] you are stuck in code review land
[47:26] where you actually enforce all of the constraints
[47:29] the invariants in your code base
[47:31] by literally the human person saying
[47:34] you know, reading the code and like
[47:35] okay, you should Do this
[47:37] right?
[47:38] Every time you have to do that
[47:39] you should consider that as a code smell
[47:41] like a, a, a anti-pattern, and you should say
[47:44] okay, instead of me commenting on the PR
[47:46] how do I turn this into a hard rule
[47:49] right? How do I turn this into a
[47:50] lint rule?
[47:51] How do I turn this into a CI
[47:53] failure?
[47:54] Or how do I even categorically eliminate this problem
[47:58] entirely?
[48:00] I, I can talk about another migration I've done
[48:02] but I'll probably pause here
[48:04] Sure
[48:05] Yeah, I feel like that's
[48:06] that's where I am
[48:07] to be honest, is, is what you're describing right now
[48:09] which is that, like, I don't have all of these rules
[48:11] so I have some things to go do after this session
[48:14] in terms of being able to scale my agents
[48:16] I'm, I'm definitely on, like, the
[48:18] you know, maybe a couple of parallel ones locally
[48:20] stage, like two to three locally
[48:22] and I'm sure most people here are on the same
[48:24] So, yeah
[48:25] I know we only have a couple minutes left
[48:27] Lauren, was there anything else that you wanted to
[48:29] to highlight? I, obviously, there's lots of questions
[48:31] so I can grab more
[48:32] but I want to give you a few minutes
[48:34] if there's anything else you want to talk about
[48:35] Well, I think I've been yapping
[48:36] Work on a lot
[48:36] so maybe let's just do questions
[48:39] Okay, cool
[48:40] One question that had a couple of
[48:42] came up a couple of times was just
[48:43] around like token usage
[48:46] So the question is like
[48:48] is what you're describing a realistic thing for
[48:50] people who are on
[48:51] you know, a normal set of token usage
[48:54] they don't have, you know
[48:56] basically unlimited tokens to work with?
[49:00] I think that's a really good point
[49:01] I mean, like obviously, you know
[49:02] I work at a AI lab where we have unlimited tokens
[49:06] so I definitely cannot say that
[49:10] you know
[49:10] this is something everyone
[49:12] should do in the exact same way that
[49:14] I did it
[49:15] I think it's possible to get to this point without
[49:17] you know, breaking the bank
[49:19] But, you know, if you're like an engineering leader or
[49:22] you know, you're, you, you have a startup that you lead
[49:25] I think to me it's a question of
[49:27] ROI
[49:28] and it's like, yes
[49:31] you spend
[49:32] a lot of money
[49:33] on tokens in the upfront stage
[49:36] You know
[49:36] like refactoring your code base is going to
[49:37] take a lot of tokens
[49:39] adding all these things
[49:41] is going to take a bunch of tokens
[49:43] But
[49:43] if we're heading to a world
[49:44] where agents are writing all the code and
[49:48] you know, you want to be very lean
[49:50] right? You don't want to have to hire
[49:52] you don't want to be
[49:52] you don't want to become like meta
[49:54] right? Like, I mean, like in terms of
[49:56] you don't want to become
[49:57] a 10,000 person engineering org because I mean
[50:00] that's a cool problem to have
[50:02] but also, you know
[50:03] you have so much overhead
[50:04] There's like planning, you know, like
[50:07] it's, it's, personally, I, I wouldn't, it's not super fun
[50:12] But, I think you want to stay very nimble
[50:15] right? And you want to
[50:16] you want to be
[50:16] like agents are all about
[50:18] allowing you to do
[50:19] things that you couldn't do before
[50:21] That's really, to me, like the value of agents
[50:24] You know
[50:24] it's not just throwing tokens on every single little thing
[50:28] But, to me
[50:29] like the thing I couldn't do before is
[50:30] like
[50:31] enforce this level of constraints in a code base by myself
[50:36] right? Like I'm just a single person
[50:38] you know
[50:39] it would have taken me years to build this framework
[50:43] and do all the refactoring and Test everything myself and verify
[50:49] you know, like run, imagine if there, it was just me
[50:51] right? You know, in, in pre-agent era
[50:53] just like running, you know, by my
[50:55] it would take me so long
[50:57] right? And my salary is pretty high
[50:59] right? Like, so, you know, the
[51:01] the question I think an engineering leader might
[51:03] have is just then
[51:05] you know, like, what is, there's a trade-off of
[51:07] do you hire someone to do this
[51:10] or do you spend the tokens to set
[51:12] up a code base so that even the
[51:14] the most naive, right
[51:16] the dumbest agents can do a good job?
[51:19] And when you actually get to this point
[51:21] like even agents that are not
[51:23] you know, fable size do an excellent job of writing code
[51:27] and this pays a lot of dividends as
[51:29] well for me personally
[51:30] where I've empowered not just myself
[51:33] but again, like PMs, designers
[51:37] engineers who are not familiar with Grokbot to
[51:39] just contribute in a way that is sustainable
[51:44] So I think, yeah
[51:44] it's definitely like a trade-off for sure
[51:47] You know, like nothing's like free for sure
[51:49] and tokens are pretty expensive
[51:51] but oh, actually, I, I
[51:54] I don't know how many of you have seen this
[51:56] but we actually announced Grok 4.6 today
[51:59] So very exciting, finally out
[52:01] so yeah, Grok 4.6 would be like a great
[52:03] it's very, very smart
[52:05] it's really good on the
[52:07] on the benchmarks
[52:09] and it's the same
[52:09] the tokens, well, I hopefully I'm not saying this incorrectly
[52:13] but
[52:14] I believe the
[52:15] cost per token is the same as 4.5
[52:18] So you're actually getting
[52:19] more intelligence for the same cost
[52:23] I think this is an area that Cursor tries to
[52:26] Cursor and SpaceX AI try to really optimize for
[52:30] like that Pareto frontier of
[52:32] you know, cost versus intelligence
[52:35] you know
[52:35] we don't necessarily want to build the biggest
[52:37] model
[52:37] ever because that is extremely expensive to run
[52:40] It's really about like
[52:42] how do you find that sweet spot
[52:43] right? You don't You don't need a giant model
[52:45] but it's just super smart
[52:46] right? And it's not very expensive for inference
[52:50] but, yeah, I think to kind of round it up
[52:55] I think it's like a
[52:55] it's, it's, there's a, if you do your own analysis
[52:59] I feel like it's pretty positive
[53:01] It'll
[53:01] it'll be pretty positive that
[53:03] the ROI you get from investing in stuff like this
[53:07] just empowers not just yourself
[53:09] but your whole team to be so much more productive
[53:12] right? Like
[53:12] imagine if you have an army of
[53:14] engineers like me who are shipping so much improvements and
[53:18] and bug fixes, you know, every day, right?
[53:21] Like, that is pretty exciting
[53:25] Cool
[53:26] one last question before we wrap up
[53:27] Now, this one is for the people in product on the
[53:29] on the call
[53:30] So
[53:31] let's say we do have a number of
[53:32] engineers who are shipping like Lauren
[53:34] I'm just curious
[53:35] like
[53:36] how is the product team or other functions
[53:37] of your company keeping up given that
[53:40] like if you're shipping so quickly
[53:42] have, have
[53:42] are they using AI more to do their
[53:44] jobs? Like as much as you can speak to that
[53:46] I obviously you don't have
[53:47] like you're not in that role
[53:48] but just curious about how that works
[53:51] I think this is where Grokbot has been actually exceedingly powerful
[53:55] where, so before Grokbot, like, you know
[53:58] obviously cursor only had cursor
[54:01] like we only had agents window
[54:02] we had a CLI
[54:03] we had an IDE
[54:05] and these are really like power user tools
[54:08] right? Like they're designed for developers
[54:10] so it's very, very developer centric
[54:12] You can do knowledge work in them
[54:14] but it like the UI is not really
[54:16] optimized for that
[54:18] So we actually didn't really have
[54:21] well, I think like a lot of people in like
[54:22] you know, GTM product, like they might have used cursor
[54:27] to do their work
[54:27] but it definitely wasn't like a delightful experience
[54:30] for them
[54:31] I think now with Grokbot
[54:34] it's become
[54:36] Grokbot is basically like their cursor moment for
[54:39] people who are not in tech
[54:41] in my opinion. Like
[54:41] it's like, it's like a very
[54:43] very accessible way to use agents in a very comfortable
[54:47] very familiar interface. It looks like iMessage
[54:51] and it's very fun to
[54:52] you know
[54:52] you can give your agent a fun name
[54:55] you can have
[54:55] you can kind of do orchestration within a very
[54:58] like, natural way where you can sort of
[55:01] you know, each agent's like a person
[55:02] and now you got a team of agents
[55:03] like working on, you have one
[55:05] one agent per account that you manage
[55:06] as an example
[55:07] Or if you're a PM
[55:08] you have, you know
[55:09] you can have an agent that summarizes all
[55:11] the work that Lauren did last night
[55:13] and then now you know what I did
[55:14] right?
[55:15] So I think our PMs are leveraging that a lot
[55:18] and their shipping code too
[55:20] so, you know, like oftentimes they will just say
[55:22] "Oh, here's a bug, I fixed it
[55:24] Can you look at it?" And then I'll go review it
[55:25] and actually, it's just perfect on my okay stamp
[55:29] so, that, I think that shows that
[55:31] you know, the, the dune architecture is holding up
[55:33] right?
[55:34] The, all the
[55:35] the really strict constraints allow
[55:38] people who are not experts in engineering to
[55:40] contribute at a high level
[55:43] so I'm
[55:43] I feel like I'm already seeing
[55:44] that pay off a lot where
[55:46] you know, designers and PMs are just able to
[55:49] to, to ship features directly
[55:53] and that just makes the Grokbot team super fast
[55:57] right? Where we can ship so quickly
[56:01] and we have a lot planned
[56:02] so I'm very excited
[56:04] to, you know, to, to ship more
[56:08] ship more stuff
```

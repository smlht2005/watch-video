# Anthropic Prompting 101：用車禍報告範例逐步打造提示詞

_Source: captions (en, manual, original)._

```
[00:00] Hey
[00:00] everyone. Thank you for joining us today for
[00:02] Prompting 101. My name's Hannah
[00:05] I'm part of the Applied AI team
[00:06] here at Anthropic
[00:08] And with me is Christian
[00:09] also part of the Applied AI team
[00:11] And what we're going to do today is
[00:12] take you through a little bit of prompting best practices
[00:15] and we're going to use a real-world scenario
[00:17] and build up a prompt together
[00:20] So a little bit about what prompt engineering is
[00:23] prompt engineering
[00:24] you're all probably a little bit familiar with
[00:26] this
[00:26] This is the way that we communicate with
[00:28] a language model
[00:29] and try to get it to do what
[00:30] we want. So this is the practice of
[00:32] writing clear instructions for the model
[00:34] giving the model the context that it needs
[00:36] to complete the task
[00:37] and thinking through how we want to arrange
[00:39] that information
[00:40] in order to get the best result
[00:42] so there's a lot of detail here
[00:44] a lot of different ways you might want
[00:45] to think about building out a prompt
[00:47] and as always
[00:48] the best way to learn this is just
[00:50] to practice doing it
[00:52] so today we're going to go through a
[00:53] hands-on scenario
[00:54] we're going to use an example inspired by
[00:57] a real customer that we worked with
[00:59] So we've modified what the actual customer asked us to do
[01:02] but this is a really interesting case of
[01:03] trying to analyze some images and get
[01:06] factual information out of the images and have
[01:09] Claude make a judgment
[01:10] about what content it finds there
[01:12] And
[01:13] I actually do not speak the language that
[01:15] this content is in
[01:16] but luckily Christian and Claude both do
[01:19] so I'm going to pass it over to
[01:20] Christian to talk about the scenario and the
[01:21] content. So For this example that we have here
[01:25] it's, intended, so, so to set the stage
[01:28] imagine you're working for a Swedish insurance company
[01:30] and you deal with
[01:32] car insurance claims on a daily manner
[01:35] and the purpose of this is that you
[01:36] have two pieces of information
[01:38] we're going to these in detail as well
[01:40] but visually you can see on the left-hand
[01:41] side we have a car accident report form
[01:45] just detailing out what transpired before the action
[01:48] accident actually took place
[01:49] And then finally we have a sort of human-drawn
[01:53] sketch of
[01:54] how the accident took place as well
[01:56] So these two pieces of information
[01:57] is what we're gonna try to pass on to Claude
[02:00] and to begin with
[02:01] we could just take these two and throw them into
[02:03] the console and just see what
[02:05] what happens
[02:05] So if we transition over to a console as well
[02:08] we can actually do this
[02:09] in a real manner. And in this case here
[02:11] you can see we have our shiny
[02:13] beautiful Anthropic console. We're using the new
[02:16] Claude 4 Sonnet model as well
[02:18] In this case, Setting temperature to zero
[02:20] and having a, a, a huge max thinking budget as well
[02:23] just helping us make sure that there's no
[02:25] limitations to what Claude can do
[02:27] In this case
[02:28] you can see you have a very simple
[02:29] prompt just setting the stage of what Claude's supposed to do
[02:31] in this case, mentioning that this is
[02:34] intended to review a
[02:35] an accident report form
[02:37] and eventually also determine
[02:40] what happened in the accident and who's at
[02:41] fault
[02:42] So you can see here with this very simple prompt
[02:44] if I just run this
[02:45] let me go to preview
[02:48] We can see here that Claude
[02:51] thinks that this is in relation to
[02:53] skiing accidents that happened on a street called Schaffangatan
[02:58] it's a very common street in Sweden
[03:00] and in many ways
[03:01] you can sort of understand this innocent mistake
[03:03] in the sense that in our prompt
[03:05] we actually haven't done anything to
[03:07] set the stage on what
[03:08] is actually taking place here
[03:10] So this sort of first guess is not too bad
[03:12] but we still know there's a lot of
[03:14] intuition that we can bake into Claude
[03:17] So we switch back to slides
[03:19] You can see here that
[03:21] in many ways, prompt engineering is a very iterative
[03:24] empirical science
[03:25] in this case here
[03:26] we could almost have a test case
[03:28] where
[03:29] Claude is supposed to make sure it understands
[03:31] it's in a car or a vehicular environment
[03:33] nothing to do with skiing
[03:35] and in that way
[03:35] you iteratively
[03:37] build upon
[03:38] your prompt to make sure it's actually tackling
[03:40] the problem you're intending to solve
[03:42] and to do so
[03:43] we go through some best practices of how we
[03:45] we at Anthropic break this down
[03:48] internally
[03:48] and how we recommend others do so as
[03:50] well
[03:51] So we're going to talk about some best
[03:52] practices for developing a great prompt
[03:55] first we want to talk a little bit
[03:57] about what a great prompt structure looks like
[03:59] So
[03:59] you might be familiar with kind of interacting with a chatbot
[04:02] with Claude, going back and forth
[04:04] having a more kind of conversational style interaction
[04:07] When we're working with a task like this
[04:09] we're probably using the API
[04:11] and we kind of want to
[04:11] send
[04:12] one single message to Claude and have it
[04:14] nail the task the first time around
[04:16] without needing to
[04:18] kind of move back and forth
[04:20] so the kind of structure that we recommend
[04:22] is setting the task description up front
[04:24] so telling Claude
[04:25] what are you here to do?
[04:26] What's your role?
[04:27] What task are you trying to accomplish today?
[04:29] Then we provide content
[04:30] so in this case it's the images that Christian was showing
[04:33] the form
[04:34] and the drawing of the accident and how
[04:36] they occurred
[04:37] That's our dynamic content. This might also be
[04:39] something you're retrieving from another system
[04:41] depending on what your use case is
[04:42] We're going to give some detailed instructions to Claude
[04:45] so almost like a step-by-step list
[04:47] of how we want Claude to go through
[04:49] the task and how we want it to
[04:51] tackle the reasoning
[04:52] We may give some examples to Claude
[04:54] Here's an example of some piece of content
[04:56] you might receive. Here's how you should respond
[04:58] when given that content
[05:00] And at the end
[05:01] we usually recommend repeating anything that's really important
[05:03] for Claude to understand about this task
[05:06] Kind of, reviewing the information with Claude
[05:08] emphasizing things that are extra critical
[05:11] and then telling Claude
[05:12] okay, go ahead and do your work
[05:15] So here's another view. This has a little bit more detail
[05:17] a little bit more of a breakdown
[05:19] and we're going to walk through each of
[05:20] these ten points individually
[05:22] and show you how we build this up
[05:24] in the console
[05:25] So the first couple things
[05:27] Christian's going to talk about the task context
[05:29] and the tone context
[05:31] Perfect
[05:32] So yeah, if we begin with the task context
[05:34] as you realized when I went through a little demo there
[05:37] we didn't have much elaborating what
[05:39] what
[05:39] what's the
[05:40] scenario of Claude is actually working within
[05:42] And because of that
[05:43] you can also tell that Claude doesn't necessarily
[05:45] need to guess a lot more on what
[05:46] you actually want from it
[05:47] So in our case
[05:48] we really want to break that down
[05:49] make sure we can give more clear-cut instructions
[05:52] and also make sure we understand
[05:54] what's the task that we're asking Claude to
[05:55] to do
[05:57] secondly as well
[05:58] we also make sure we add a little
[05:59] bit of tone into it all
[06:02] key thing here is we want
[06:03] Claude to stay factual and to stay confident
[06:06] So if, Claude can't understand what it's looking at
[06:09] we don't want it to guess and just
[06:10] sort of mislead us. We want to make
[06:12] sure that any assessment
[06:14] and in our case
[06:14] we want to make sure that
[06:15] we can understand who's at fault here
[06:17] We want to make sure that assessment is
[06:19] as clear and as confident as possible
[06:21] If not
[06:21] we're sort of losing track of what we're
[06:23] doing
[06:23] So if we transition back to the
[06:25] to the console
[06:27] we can jump to a V2 that we
[06:29] have here
[06:30] So I'll just navigate to V2
[06:33] And you can see here
[06:35] I'll also just illustrate the data
[06:36] because we didn't really do that last time around
[06:38] just to really highlight what we're looking at
[06:39] So what we're seeing here
[06:40] this is the Car accident report form
[06:44] and it's just
[06:44] seventeen different check boxes going through
[06:47] what actually happened. You can see there's a
[06:48] vehicle A and vehicle B
[06:50] both on the left and right hand side
[06:51] and the main purpose of this is that
[06:52] we want to make sure that Claude can
[06:54] understand this
[06:55] manually generated data
[06:57] to assess what's actually going on
[06:59] And that is, corroborated by, if I navigate back here
[07:03] to this sketch that we can highlight here
[07:05] as well
[07:06] In this case, the form is just a different
[07:09] data point for the same scenario
[07:12] and in this case here
[07:12] I want to bake in more of that
[07:14] information into our version two
[07:16] and by doing so
[07:17] I'm actually
[07:18] elaborating a lot more on what's going on
[07:20] So you can see here I'm specifying that
[07:23] this AI system is supposed to help a human's claim
[07:25] claims adjuster
[07:26] that's reviewing car accident report forms in
[07:29] Swedish as well
[07:31] you can see here we're also elaborating that
[07:32] it's a human-drawn sketch of the incident
[07:35] and that it should not
[07:37] make an assessment if it's not actually fully
[07:39] confident
[07:40] And that's really key
[07:40] because if we run This
[07:42] you'll see that
[07:43] and you can see it's the same settings as well
[07:44] Claude four, a new shiny model
[07:46] zero temperature as well. If we run this
[07:49] we can see here what actually happens
[07:52] In this case, Claude's able to pick up that
[07:55] now it's relating to car accidents
[07:57] not skiing accidents, which is great
[07:59] We can see it's able to
[08:00] pick up that vehicle A was marked on
[08:03] on checkbox one
[08:04] and then vehicle B was on twelve
[08:07] and if we scroll down
[08:08] though
[08:08] we can still tell that there's some information
[08:10] missing for Claude to make
[08:11] a fully confident
[08:13] determination of who's at fault here
[08:15] And this is great. This is pertaining to
[08:17] the task we have set
[08:18] Make sure you don't make anything
[08:19] any claims that aren't
[08:22] factual and make sure you
[08:23] you only sort of assess things when you're
[08:25] when you're confident
[08:26] But there's a lot of information we're still missing here
[08:29] regarding the form, what the form actually entails
[08:33] and a lot of that information is what we want to
[08:34] want to bake into
[08:36] this LLM application as well
[08:38] And the best way of doing so is
[08:39] actually adding it to the system prompt
[08:40] which Hannah will elaborate on
[08:43] so back in the slides
[08:45] we have the next item we're going to
[08:46] add to the prompt
[08:47] and this is, background detail, data, documents, and images
[08:52] And here, as Christian was saying
[08:54] we actually know a lot about this form
[08:55] The form is going to be the same
[08:57] every single time. The form will never change
[08:59] And so this is a really great type
[09:01] of information to provide to Claude
[09:02] to tell Claude
[09:03] here's the structure of the form you'll be
[09:05] looking at. We know that will not
[09:07] ever alter between different queries
[09:09] The way the form is filled out will change
[09:11] but the form itself is not going to
[09:13] change. And so this is a great type of
[09:15] information to put into the system prompt
[09:18] Also a great thing to use prompt caching
[09:19] for. If you're considering using prompt caching
[09:21] this will always be the same
[09:22] And what this will help Claude do is
[09:24] spend less time trying to figure out what
[09:26] the form is
[09:27] the first time it sees the form each
[09:29] time
[09:30] And it's going to do a better job
[09:31] of reading the form because it already knows
[09:34] what to expect there
[09:36] So
[09:37] another thing I want to touch on here
[09:38] is how
[09:39] we like to organize information in prompts
[09:41] So Claude really loves structure
[09:43] loves organization. That's why we recommend following kind
[09:46] of a standard structure in your prompts
[09:48] And there's a couple other tools you can
[09:49] use to help Claude understand the information better
[09:53] I also just want to mention all of
[09:54] this is in our docs with a lot
[09:56] of really great examples. So definitely take pictures
[09:58] but if you forget to take a picture
[10:00] don't worry
[10:01] All of this content is online with
[10:03] lots of examples and definitely encourage you guys
[10:05] to check it out there too
[10:08] Anyway, the, so some things you can use
[10:11] delimiters, like XML tags, also markdown is pretty useful to Claude
[10:15] but
[10:15] XML tags are nice because you can actually
[10:17] specify what's inside those tags
[10:20] So we can tell Claude
[10:21] here's, here's user preferences
[10:23] Now you're going to read some content
[10:25] and these XML tags are letting you know
[10:26] that everything wrapped in those tags
[10:28] is related to the user's preferences
[10:30] and it helps Claude refer back to that information
[10:33] maybe at later points in the prompt
[10:35] so I want to show in the
[10:37] back in the console
[10:38] how we actually do this in this case
[10:41] And Christian's going to pull up our version
[10:43] three
[10:44] So we're keeping everything about the other part
[10:46] of the user prompt the same
[10:48] And we've decided in this case to put
[10:50] this information in the system prompt
[10:52] You can try this different ways
[10:53] We're doing it in the system prompt here
[10:55] And we're going to tell Claude everything it
[10:57] needs to know about this form
[10:58] So this is a Swedish car accident form
[11:00] The form will be in Swedish
[11:02] It'll have this title
[11:03] It'll have two columns. The columns represent different
[11:06] vehicles
[11:07] We'll tell Claude about each of the 17
[11:09] rows and what they mean
[11:11] You might have noticed when we ran it before
[11:13] Claude was
[11:14] reading
[11:14] individually
[11:15] each of the lines to understand what they
[11:17] are
[11:17] We can provide all of that information up
[11:19] front
[11:20] And we're also going to give Claude a
[11:21] little bit of information about how this form
[11:23] should be filled out
[11:24] This is also really useful for Claude
[11:26] We can tell it things like You know
[11:29] humans are filling this format
[11:30] basically. So it's not going to be perfect
[11:32] People might put a circle
[11:33] they might scribble
[11:34] they might not put an
[11:35] X in the box
[11:36] There could be many types of markings that
[11:38] you need to look for
[11:40] when you're reading this form
[11:42] we can also give Claude a little bit
[11:43] of information about how to interpret this or
[11:45] what the purpose or meaning of this form
[11:47] is
[11:47] And all of this is context that is
[11:49] hopefully really going to help Claude
[11:51] do a better job analyzing the form
[11:54] So if we run it
[11:56] everything else is still the same
[11:57] So we've kept the same user prompt down here
[12:00] Oh, your scroll is backwards from mine
[12:04] the, we have the same user prompt here
[12:05] still asking Claude to do the same task
[12:08] same context
[12:09] And we'll see here that it's spending less time
[12:12] it's kind of narrating to us a little
[12:13] bit less about what the form is
[12:15] because it already knows what that is
[12:17] and it's not concerned with kind of
[12:18] bringing us that information back
[12:21] It's going to give us a whole list
[12:22] of what it found to be checked
[12:24] what the sketch shows
[12:25] and here Claude is now becoming much more
[12:27] confident. With this additional context that we gave to Claude
[12:30] Claude now feels it's appropriate to say
[12:33] vehicle B was at fault in this case
[12:35] based on this drawing and based on this
[12:37] sketch
[12:37] So already we're seeing some improvement in the
[12:40] way Claude is analyzing these
[12:42] I think
[12:42] we could probably all agree if we looked
[12:44] at
[12:44] the drawing and at the list that vehicle
[12:46] B is at fault
[12:47] so we'd like to see that
[12:50] so we're gonna go back to the slides
[12:51] and talk about
[12:52] a couple of other items that we're not
[12:54] really using in this prompt
[12:56] but can be really helpful to building up
[13:00] building up your prompt and making it work
[13:01] better
[13:02] Exactly. I think
[13:03] one thing that we really highlight is examples
[13:06] I think examples or
[13:07] few shot is a mechanism that really
[13:10] is powerful in steering Claude
[13:13] So you can imagine this
[13:15] in, in quite a non-trivial way as well
[13:16] So imagine you have scenarios
[13:19] situations, even in this case
[13:20] concrete Accidents have happened that are
[13:24] tricky for Claude to get right
[13:25] but you, with your human intuition and your human label data
[13:30] is able to
[13:30] actually get to the right conclusion
[13:33] But you can bake that information into the
[13:34] system prompt itself by having clear-cut examples of
[13:38] A, the data that it's supposed to look at
[13:40] so you can have visual examples
[13:42] you can use Base64 encode
[13:45] an image
[13:46] and have that as part of
[13:47] the data that you're passing along into the
[13:48] examples
[13:49] And then on top of that
[13:50] you can have the sort of depiction or description
[13:52] rather
[13:52] of
[13:53] how to break that down and understand it
[13:55] This is something we really highlight and
[13:56] and emphasize in
[13:58] how you can sort of push the limits
[13:59] of your LLM application
[14:01] is by baking in these examples into system prompt
[14:04] And this, again
[14:05] is sort of the empirical science of prompt engineering
[14:07] so that you
[14:07] sort of always want to push the limits
[14:09] of your application
[14:10] and get that feedback loop in where it's going wrong
[14:12] and try to add that into system prompt
[14:14] so that next time
[14:15] one example that sort of mimics that
[14:18] takes place
[14:18] it's able to actually
[14:19] reference it in its example set
[14:22] You can see here as well
[14:23] this is just a little example of how
[14:24] we do this. Again
[14:26] really emphasizing the sort of XML structure that we
[14:29] we, we enjoy. It
[14:31] it gives a lot of structure to Claude
[14:33] It's what it's been fine-tuned on as well
[14:35] and it works perfectly well for this example
[14:37] In, in our case
[14:37] we're not doing this just because it's a simple demo
[14:39] but you can
[14:40] realistically imagine if you were building this for an insurance company
[14:44] you'd have tens
[14:45] maybe even hundreds of examples that are quite difficult
[14:47] maybe in the gray
[14:48] that you'd like to make sure that Claude
[14:50] actually has
[14:51] some basis in to make the
[14:53] verdict next time
[14:55] another topic we really want to highlight
[14:56] which we're not doing in this demo
[14:58] is conversation history
[14:59] It's in the same vein as examples
[15:02] we use this to make sure that there
[15:03] are enough context-rich information is at close disposal when
[15:08] when, when close working on
[15:10] on, on your behalf
[15:11] in our case now
[15:12] this isn't really a user-facing Edelman application
[15:15] It's more something happening in the background
[15:17] You can imagine for this insurance company
[15:19] they have this automated system
[15:20] some data is generated out of this
[15:22] and then you might have a human in
[15:23] the loop at towards the end
[15:25] If you were had to build something much more user-facing
[15:27] where you'd have a long conversation history that would be
[15:31] relevant to bring in
[15:32] this is a perfect place in the system prompt to include
[15:35] because it enriches the context that Claude
[15:38] Claude works within
[15:40] in our case, we haven't done so
[15:42] but what we do is
[15:43] and the next step is try to
[15:45] make sure we give
[15:46] a concrete reminder of the task at hand
[15:50] So now we're going to build out the
[15:51] final part of this prompt for Claude
[15:54] and that's coming back to the reminder of
[15:55] what the immediate task is and giving Claude
[15:58] a reminder about any important guidelines that we
[16:00] want it to follow
[16:01] Some reasons that we may do this are
[16:04] A, preventing hallucinations
[16:06] So we want Claude to
[16:08] not invent details that it's not finding in this prompt
[16:12] right, or not finding in the data
[16:13] If Claude can't tell which form is checked
[16:15] we don't want Claude to
[16:17] take its best guess or
[16:19] invent the idea that a box might be
[16:20] checked when it's not
[16:22] If the sketch is unintelligible
[16:24] the person did a really bad job drawing this drawing
[16:27] and even a human would not be able
[16:28] to figure it out
[16:29] we want Claude to be able to say
[16:30] that
[16:31] And so these are some of the things
[16:32] we'll include
[16:33] in this final
[16:34] reminder and kind of wrap-up step for Claude
[16:37] Remind it to do things like answer only
[16:39] if it's very confident. We could even ask
[16:40] it to refer back to what it has
[16:42] seen in the form
[16:43] anytime it's making a factual claim
[16:45] So if it wants to say
[16:46] vehicle B turned right
[16:48] it should say, I know this
[16:49] Based on the fact that box two is clearly checked
[16:52] or whatever it might be
[16:53] we can kind of give plots and guidelines
[16:55] about that
[16:56] So if we go back to the console
[16:58] we can see The next version of the prompt
[17:03] and we're going to keep
[17:04] we're going to keep everything the same here
[17:06] in the system prompt
[17:06] so we're not changing any of that background
[17:08] context that we gave to Claude about the form
[17:10] about how it's going to fill everything out
[17:12] We're not changing anything else about the context
[17:14] and the role. We're just adding this detailed list of tasks
[17:18] and this is how we want Claude to
[17:19] go about analyzing this
[17:21] And a really key thing that we found here
[17:23] as we were building this demo and when
[17:25] we were working on the customer example
[17:26] is that the order
[17:27] in which Claude analyzes this information is very
[17:30] important
[17:30] And this is
[17:31] analogous to the way
[17:32] you might think about doing this if you
[17:34] were a human
[17:35] You would probably not look at the drawing
[17:36] first and try to understand what was going on
[17:39] right? It's
[17:39] pretty unclear. It's a bunch of boxes and
[17:41] lines
[17:42] We don't really know what that drawing is
[17:43] supposed to mean without any additional context
[17:46] But if we have the form
[17:47] and we can read the form first and
[17:49] understand that we're talking about a car accident
[17:51] and that we're seeing some checkboxes that indicate
[17:53] what vehicles we're doing at certain times
[17:56] then we know a little bit more about
[17:57] how to understand what might be in the
[17:59] drawing
[18:00] And so that's the kind of detail that
[18:01] we're going to give Claude here
[18:02] is to say, hey, first
[18:04] go look at the form
[18:04] Look at it very carefully
[18:06] Make sure you can tell what boxes are
[18:07] checked. Make sure you're not missing anything here
[18:11] Make a list for yourself of what you see in that
[18:14] and then move on to the sketch
[18:16] So after you've kind of confidently
[18:18] gotten information out of the form
[18:19] and you can say what's factually true
[18:21] then you can go on
[18:23] and think about what you can gain from that sketch
[18:27] keeping in mind
[18:28] your understanding of the accident so far
[18:30] So whatever you've learned from the form
[18:32] you're trying to match that up with the
[18:33] sketch
[18:34] And that's how you're going to arrive
[18:36] at your final assessment of the form
[18:41] And we'll run it
[18:47] And here you can see
[18:48] one behavior that this produced for Claude
[18:50] Because I told it to very carefully examine the form
[18:54] it's showing me its work
[18:55] as it does that. So it's telling me each individual box
[18:59] is the box checked? Is it not checked?
[19:01] And so this is one thing you'll notice
[19:02] as you do prompt engineering
[19:04] In our previous prompts
[19:05] we were kind of letting Claude decide
[19:07] how much it wanted to tell us about
[19:08] what it saw in the form
[19:10] Here, because I've told it
[19:11] carefully examine each and every box
[19:14] it's very carefully examining each and every box
[19:16] And that might not be what we want in the end
[19:18] so that's something we might change
[19:20] But it's also going to give me these
[19:22] other things that I asked for
[19:23] in XML tags
[19:24] So a nice analysis of the form
[19:27] the accident summary so far
[19:28] it's going to give me a sketch analysis
[19:30] and it's going to continue to say that
[19:32] vehicle B appears to be clearly at fault
[19:35] In this, in this example, this pretty simple example
[19:37] with more complicated drawings
[19:39] more, less clarity in the forms
[19:42] this kind of step-by-step thinking for Claude is
[19:44] really Impactful in its ability to make
[19:47] a correct assessment here
[19:49] so I think we'll go back to the slides
[19:51] and
[19:52] Christian's gonna talk about a last kind of
[19:54] piece that we might add to this
[19:56] to really make it useful for a real world task
[19:59] Indeed, thank you so much
[20:01] So as Hannah mentioned
[20:03] we sort of set the stage in this
[20:04] prompt to make sure that
[20:06] Claude's really acting on our behalf in the right
[20:08] right manner
[20:09] and a key step
[20:10] that we also add towards the end of this prompt
[20:12] that I'm going to show you in a second
[20:13] is a
[20:14] simple sort of guidelines or reminder part as
[20:16] well. So just strengthening and
[20:18] reinforcing exactly what we want to get out
[20:19] of it
[20:20] And one important piece is actually output formatting
[20:23] You can imagine if you're a data engineer
[20:24] working on this LLM application
[20:27] all this sort of fancy preamble is great
[20:29] but at the end of the day
[20:30] you want your piece of information to
[20:32] to be stored in
[20:33] let's say, your SQL database
[20:34] wherever you want to store that data
[20:36] and the rest of it
[20:37] that is necessary for Claude to sort of
[20:39] give its verdict
[20:40] isn't really that necessary for your application
[20:42] You want the nitty gritty
[20:43] information for your
[20:45] application. So if we transition back to the console
[20:48] you'll see here that we just added a
[20:49] simple importance guidelines part
[20:52] And again
[20:53] this is just reinforcing
[20:55] the sort of mechanical behavior that we want
[20:57] out of Claude here
[20:58] We want to make sure that The summary is clear
[21:00] concise
[21:00] and accurate
[21:01] I want to make sure that
[21:02] nothing is sort of impeding in
[21:04] in, in Claude's assessment, apart from the
[21:07] the AS analyzing. And then finally
[21:09] when it comes to output formatting
[21:10] in my case here
[21:11] I'm just going to ask Claude to wrap its final verdict
[21:14] all other stuff I'm actually going to ignore from my application
[21:16] and just look at what it's actually assessing
[21:18] And that is, I can, I can use this
[21:20] if I want to build some sort of
[21:22] analytics tool afterwards as well
[21:24] or if I just want a clear cut
[21:26] determination
[21:27] this is the way I can do so
[21:29] So if I just run this here
[21:30] you'll see
[21:31] it's going through the same sort of process
[21:32] that we've seen before. In this case
[21:34] it's much more succinct because we've asked it to be
[21:36] to summarize its findings in a
[21:38] in a much more straightforward manner
[21:39] And then finally, towards the end
[21:41] you'll see that it'll
[21:42] wrap my output in these final verdict XML
[21:45] tags
[21:46] So you can see that during this demo
[21:48] we've gone from a skiing accident to sort of unconfident
[21:52] insecure outputs from
[21:54] perhaps a
[21:55] car accident in the second version
[21:57] to now a much more strictly formatted
[22:00] confident output that we can actually build
[22:02] and then let an application around and actually help
[22:05] you know, a real world, Car insurance company, for example
[22:10] finally, if we transition back to the
[22:13] slides
[22:14] another
[22:15] key way of shaping
[22:17] Claude's output is actually putting words in Claude's mouth
[22:21] or as we call it
[22:22] pre-filled responses
[22:24] You could imagine that parsing XML tags is nice and all
[22:27] but maybe you want a structured JSON
[22:29] output to make sure that
[22:31] its JSON is serializable
[22:32] and you can use this in a subsequent
[22:34] subsequent call, for example
[22:36] this is quite simple to do
[22:37] You could just add that
[22:40] Claude needs to begin its output with a
[22:42] certain format. This could be
[22:44] for example, a, open square bracket, square bracket, for example
[22:48] or even in this case that we see
[22:49] in front of us
[22:50] this would be an XML tag for itinerary
[22:52] In our case
[22:53] it could also be that final verdict XML
[22:54] tag
[22:56] and this is just a great way of
[22:57] again, shaping how Claude is supposed to respond
[23:02] without all the preamble if you don't want that
[23:04] even though that is also key in shaping
[23:06] its outputs to make sure that Claude is
[23:07] reasoning through the steps that we wanted
[23:09] So in our case here
[23:11] we would just wrap it in the final
[23:12] verdict and parse it afterwards
[23:14] but you can use prefill as well
[23:16] Now, finally
[23:18] one
[23:18] step that we'd like to highlight here as
[23:20] well is that both Claude 3.7 and especially Claude 4
[23:23] of course, is a, a sort of hybrid reasoning model
[23:26] meaning that there's extended thinking at your disposal
[23:30] and this is something we want to highlight
[23:31] because
[23:32] you can use extended thinking as a crutch
[23:34] for your prompt engineering
[23:36] Basically
[23:36] you can enable this to make sure that
[23:38] Claude actually has time to think
[23:39] It has its thinking tags and the scratchpad
[23:42] and the beauty of that is that you
[23:43] can actually analyze that transcript to understand how
[23:45] Claude is going about that data
[23:47] So as we mentioned
[23:48] we have these checkboxes where it goes through
[23:50] step by step of the
[23:52] scenario that transpired for the accident
[23:54] And in many ways there
[23:55] you can actually try to help Claude in
[23:57] building this into the system prompt itself
[23:59] It's not only more token efficient
[24:00] but it's a good way of understanding how
[24:02] these intelligent models
[24:04] that don't have our intuition actually go
[24:06] about the data that we provide them
[24:08] And because of that
[24:09] it's quite key in actually trying to
[24:10] break down how your system prompt can get
[24:12] a lot better
[24:14] and with that said
[24:15] I think
[24:16] I'd like to thank all of you for
[24:17] coming today
[24:18] We'll be around as well
[24:19] so if you have any questions around prompting
[24:20] please, please go ahead
[24:22] I know there's a prompting
[24:23] You want to learn more about prompting?
[24:25] In an hour, we have prompting for agents
[24:27] and right now, we have an amazing demo of ClaudePlays Pokémon
[24:31] so don't go anywhere for that
[24:33] And as Christian said
[24:34] we'll be around all day
[24:34] so
[24:35] I know we don't have time for Q&A in this session
[24:37] but
[24:37] please come find us if you want to
[24:38] chat. Thank you guys for coming
[24:40] Thank you so much
```

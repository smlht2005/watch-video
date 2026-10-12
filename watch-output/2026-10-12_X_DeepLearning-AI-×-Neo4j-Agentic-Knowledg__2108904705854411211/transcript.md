# DeepLearning.AI × Neo4j：Agentic Knowledge Graph Construction（知識圖譜與 Google ADK 多代理）

_Source: captions (en, manual, unknown)._

```
[00:00] As a partnership with Neo4j
[00:02] In this course
[00:02] you design a multi-agent system that transforms your
[00:05] structured and unstructured data into a knowledge graph
[00:09] I found knowledge graphs really useful for high-stakes
[00:11] applications
[00:12] where accuracy of the information we store and
[00:15] retrieve is important
[00:17] This course will teach you why
[00:18] and also give you a great set of
[00:19] tools for building these knowledge graphs
[00:22] I'm delighted the instructor for this course is Andreas Kollegger
[00:26] who is a developer evangelist for generative AI at Neo4j
[00:30] Thanks, Andrew
[00:32] I'm excited to be back here to work
[00:33] with you on this course
[00:35] Similar to RAG
[00:36] a knowledge graph system
[00:38] splits your text documents into chunks
[00:40] and stores them in a vector database
[00:43] But in addition to that
[00:44] it places the chunks into a graph structure
[00:47] which is chunk
[00:48] is linked to entities extracted from the chunks
[00:51] For example
[00:52] a text chunk from a product review
[00:54] can contain entities such as
[00:55] product orders or delivery issues or product defects
[00:59] To build a knowledge graph
[01:00] you extract the relevant entities from the chunks
[01:02] then connect the chunks
[01:03] and the entities in the graph through edges
[01:06] Here, each edge represents a relationship
[01:09] For example
[01:10] maybe it represents that this chunk mentioned a
[01:12] certain product or that that product
[01:14] has an issue
[01:15] The
[01:15] entities are retrieved alongside the relevant chunks
[01:19] to provide more relevant context to
[01:21] the LLM to
[01:23] generate more precise and accurate answers
[01:26] You can also connect this type of graph
[01:28] to another graph containing additional information extracted from
[01:32] structured data such as CSV files
[01:35] In this course
[01:36] engineers will walk you through how to build
[01:38] a multi-agent system that helps you do all
[01:40] this work of constructing this type of knowledge
[01:42] graph
[01:43] To transform your structured and unstructured data into a knowledge graph
[01:47] you first need to decide on the graph schema
[01:50] meaning what types of entities or nodes you
[01:52] can extract from the data
[01:54] and what relationships exist between them
[01:57] Once you have the schema defined
[01:58] you can construct the actual graph and store
[02:00] it in a graph database
[02:02] Instead of mainly looking at your data to
[02:04] find the graph schema
[02:05] you'll design a multi-agent system for doing that
[02:08] using Google's ADK or Agent Development Kit
[02:11] After you learn the basic syntax with ADK
[02:14] you'll design your system
[02:15] one agent at a time
[02:16] The first agent will converse with you to
[02:18] extract the goal and type of graph you
[02:20] want to build
[02:21] Then given that goal
[02:23] a group of agents will specialize in extracting
[02:25] the entities and relationships from your structured data
[02:29] and another group of agents will handle your unstructured data
[02:32] Finally
[02:33] a final set of agents will connect the
[02:34] two models and construct the graph accordingly
[02:38] Many people have worked to create this course
[02:40] I'd like to thank from Neo4j
[02:42] Martin O'Hanlon, and Adam Cowley
[02:45] From deeplearning.ai
[02:46] Christopher Polycastro and Hara Salami also contributed to
[02:49] this course. In the first lesson
[02:51] you'll learn more about the underlying structure of
[02:54] knowledge graphs and how you can build one
[02:56] and use it
[02:56] to identify root causes of product issues
[03:00] Sounds great
[03:01] Let's get started
[03:02] Go through what a knowledge graph means and
[03:04] how they help represent and retrieve relationships from
[03:07] your data
[03:08] You'll then explore the data set you'll work
[03:10] on to build a knowledge graph
[03:12] Let's dive in
[03:13] So, what is a knowledge graph?
[03:15] We're going to take a step back for
[03:16] a moment
[03:17] And
[03:18] reflect on relational databases and what a relational
[03:21] schema looks like
[03:22] We all probably are familiar with some scenario like this
[03:25] where there'll be
[03:26] some table on the left and some table on the right
[03:28] and this table in the middle that is
[03:30] the join table
[03:31] that allows for multiple connections between the persons
[03:34] and the products in this particular example
[03:36] So let's think about these two tables with
[03:38] the join table
[03:39] If you ask a question like
[03:41] what products has this person purchased?
[03:43] You'd first start with the person table
[03:45] and select this person here
[03:46] it's identified by ABK
[03:49] And of course
[03:49] you do a join over to the person product table
[03:52] and you'd see that
[03:53] the person product table
[03:54] has a join between the ABK and some chair
[03:57] ABK and a lamp
[03:57] ABK and a desk
[03:59] Fantastic
[04:01] One more join across from the person to
[04:03] the person product to the product table
[04:05] Now you've got a complete answer where from ABK
[04:08] you can see that here's the products that ABK has purchased
[04:11] this chair, lamp, and a desk
[04:12] and you can get the details about those
[04:14] purchases
[04:15] What if you extended that question
[04:17] and you asked, who else bought products that ABK bought?
[04:21] Well, you start with the same joins
[04:22] going from ABK to the products
[04:24] and then you would join back to the person product table
[04:27] and from there, back to the person table
[04:30] and now you would get
[04:31] this person EE
[04:32] who has bought some products that ABK
[04:34] also bought
[04:35] But notice that EE has also bought
[04:38] one extra product
[04:39] that's interesting
[04:41] So we could probably extend this one more step and ask
[04:45] well, what product should we recommend that ABK buy next?
[04:49] Now
[04:49] this is kind of the basics of doing
[04:50] a recommendation query
[04:52] If you've got some
[04:53] purchase pattern from ABK
[04:55] that matches a purchase pattern from
[04:57] some other person or other group of people
[05:00] the thing you want to recommend to ABK
[05:01] is what that other group of people bought
[05:03] that ABK has not
[05:05] So the same joins apply from ABK through to the products
[05:09] back to the other people that have bought
[05:10] those products
[05:11] There's too many joins. It's getting a little
[05:13] confusing
[05:15] There's actually a nicer way to actually think
[05:16] about this and to query this
[05:18] Let's turn this into a graph
[05:20] The first step
[05:22] is to just drop all the records that don't matter
[05:24] all those gray records that weren't part of
[05:25] the original query
[05:26] Let's put those aside for the moment and
[05:28] focus on the records that we know about
[05:30] that are part of the data set so
[05:31] far that matters for this query about
[05:33] recommending something to ABK
[05:35] Get rid of all the join table records in the middle
[05:37] turn those into arrows connecting ABK
[05:40] directly over to the products that he's purchased
[05:42] and the same thing for EE
[05:43] over to the products that they have purchased
[05:46] And now just rearrange the records a little
[05:47] bit. So you've got ABK on one side
[05:50] EE on the other side
[05:52] and now it looks much nicer
[05:53] It's much easier to understand what's going on
[05:55] Both ABK and EE are connected to these
[05:57] products in the middle
[05:58] but then also
[05:59] this person EE
[06:00] is connected to another product
[06:02] that has no connection to ABK
[06:04] You can start to turn this into a
[06:06] query by rephrasing it as a pattern match
[06:09] Starting with A B K on the left side
[06:11] you can describe a query in a query language called Cypher
[06:15] where
[06:15] it looks a little bit like SQL if
[06:17] SQL had pattern matching abilities
[06:20] So here we're going to describe a pattern
[06:21] that describes the data records that you want
[06:24] to find
[06:24] We're going to match from the data record
[06:26] that we're going to call A B K
[06:28] that has a label of person
[06:30] and that has a property
[06:31] with the name key
[06:32] where the value of it is A B
[06:33] K
[06:34] So that's in round parentheses
[06:35] we know that that's a node in graph
[06:37] terms
[06:38] And then we kind of have this
[06:40] right facing arrow with colon purchased in there
[06:43] That's a relationship type that is the purchased
[06:46] So
[06:46] match a pattern where A B K
[06:47] purchased
[06:48] over to some other parentheses
[06:50] that we're going to call A B K
[06:51] products
[06:52] That's going to be a pattern match from
[06:54] A B K
[06:54] to the products that A B K matched
[06:56] We can return those
[06:58] directly and that's going to be the products
[06:59] in the middle there
[07:01] We can extend that pattern
[07:03] to include the other people who bought those
[07:05] products
[07:06] Since we went from ABK to the products that ABK purchased
[07:09] we can also have relationships going in
[07:11] to those products and say
[07:12] okay
[07:13] there's some other people who bought those products
[07:15] This pattern will find
[07:17] all of the products that people have in
[07:18] common with ABK
[07:20] We can extend it a little bit more
[07:21] to ask that recommendation question problem
[07:24] where instead of
[07:24] saying that we just want to find these other products
[07:27] The other products have a unique property where
[07:29] they're actually something that ABK does not have
[07:33] So we have the same pattern match from
[07:34] ABK to some products
[07:35] to some other people
[07:37] and then extend that to other products
[07:40] and now we include a predicate
[07:41] saying we actually want a negative pattern to
[07:43] be true
[07:44] that ABK has not purchased those other products
[07:47] So we're not ABK purchased those other products
[07:50] So down there on the bottom
[07:51] that dotted line from ABK to the couch
[07:54] we want that to not exist
[07:56] Now we're describing a pattern that both has
[07:58] records that should exist
[07:59] something that should not exist
[08:01] The other products now
[08:03] will be reduced to only products that ABK
[08:05] has not purchased
[08:06] That's what we're going to use as a
[08:07] recommendation that he buy
[08:09] So what really is a knowledge graph?
[08:12] It's a kind of database that represents information as nodes
[08:14] representing things like people
[08:16] products, blogs
[08:17] whatever you might want to have as records
[08:19] in a database
[08:20] But then also relationships
[08:22] that aren't simply a convention of using a join table
[08:25] but that are first-class citizen
[08:26] They're actually data records inside of the database
[08:28] that have a semantic meaning
[08:30] They actually represent how two nodes are connected
[08:32] and they add information about those two nodes
[08:35] So both the nodes and relationships have key value properties
[08:38] they have multiple labels on nodes
[08:40] relationships always have a direction
[08:41] and they have a single type
[08:43] And the query language that you use for
[08:45] doing pattern matching is called Cypher
[08:47] And it turns out that this is super
[08:48] nice for mapping to natural language
[08:50] and really convenient for working with Gen AI and LLMs
[08:53] because LLMs are really good at natural language
[08:56] If we go back for a moment here
[08:58] And just look at that query at the
[08:59] top
[09:00] You can read that out loud and make
[09:01] sense of it
[09:02] Match ABK
[09:03] who's a person whose name is ABK
[09:06] that bought some products that some other people
[09:08] have bought
[09:09] They bought some other products
[09:10] where ABK has not purchased those other products
[09:13] The other thing that's interesting about knowledge graphs
[09:16] is that they're really convenient for combining unstructured
[09:18] data along with that structured data
[09:20] whether that was some products that we have or people
[09:23] whatever it might be in structured data
[09:25] you can then add any kind of chunked text
[09:27] do a vector representation of that
[09:29] store that in the database as well
[09:30] and combine both vector similarity search
[09:33] and pattern matching together for all kinds of
[09:35] powerful access patterns
[09:37] So for example, if you want to do root cause analysis
[09:40] and you imagine that you're a furniture manufacturer
[09:43] looking to understand customer complaints about your products
[09:46] so you turn to your team of experts
[09:47] you know, data engineering, data analysis team, and say, hey
[09:50] could you do some root cause analysis?
[09:52] I've heard a lot of complaints out on
[09:53] the internet about our products
[09:55] Let's try to figure out what's going on
[09:57] So the root cause analysis would include questions like
[10:00] which products have the most issues?
[10:02] And then based on those products
[10:03] well
[10:03] what part of the product is the actual
[10:05] problem?
[10:06] And then you might want to ask a question like
[10:07] is there a problem with the part itself?
[10:09] Perhaps there are other things that are going on
[10:10] people just don't like the product
[10:12] But if you can take corrective measures
[10:14] it would be because there's something either in
[10:15] the manufacturing process
[10:17] What you're looking for here is for corrective
[10:19] measures that you can take
[10:20] Do
[10:20] root cause analysis for something you can improve
[10:23] So if it's a design problem
[10:24] you could turn that over to the design
[10:25] team
[10:26] They could take a look at what people's
[10:27] complaints are about
[10:28] But
[10:29] if it's a manufacturing problem or a problem
[10:31] with a part somewhere
[10:32] you can do some analysis on that
[10:33] find the part problem
[10:35] and either swap out the part for a
[10:36] new one
[10:37] or figure out how to improve the process
[10:38] itself
[10:40] So as a data engineer
[10:41] if you were handed this task
[10:42] you would start with the usual thing
[10:44] ask some clarifying questions
[10:46] Why are we really doing this?
[10:48] You want to be able to understand that
[10:49] there's possible manufacturing problems in the supply chain
[10:52] Cool. Okay
[10:53] Second question is
[10:54] or if that's what we want to find out
[10:56] what data is available that we can do
[10:57] this analysis with?
[10:59] So it turns out in this scenario
[11:00] we've got a bill of materials
[11:02] some CSV files that connect
[11:04] the product all the way to the suppliers
[11:05] from those products
[11:06] Maybe it came from some spreadsheets
[11:08] maybe it came from some
[11:09] relational database that isn't really suited for doing
[11:11] analysis
[11:12] That's okay too
[11:13] And you also have some data from user
[11:15] reviews that you script from some websites on
[11:17] the internet
[11:18] You want to be able to combine those
[11:19] into one data set that you can then
[11:21] do some analysis on
[11:23] So to do that analysis
[11:24] you're going to build a knowledge graph that
[11:25] connects all the data
[11:27] So here's what the target data model is
[11:28] going to look like
[11:29] On the left, in the sort of beige boxes over there
[11:32] you see the CSV files that are available
[11:34] Each one of those is going to turn
[11:35] into nodes in the graph
[11:37] or relationships in the graph
[11:39] That's going to be the kind of what
[11:41] we're going to call the domain graph
[11:42] On the right-hand side
[11:44] on the bottom there
[11:44] you'll also see some beige boxes
[11:46] that represent Markdown files
[11:48] Those Markdown files are going to be chunked up
[11:50] they're going to create some documents inside of
[11:51] the graph as well
[11:53] and then all of this is going to
[11:54] get connected
[11:55] We'll look at some of the details as
[11:56] we actually go through doing the agent descriptions
[11:58] themselves
[11:59] But what I
[12:00] want to call out here for you right
[12:01] now is that these are really very connected
[12:04] but also very distinct parts of the graph
[12:06] We've got the data sources
[12:08] the structured data on the one side there
[12:10] that's going to turn into what we call
[12:11] the domain graph
[12:13] So that's the structured data that we know
[12:14] that we can query with pattern matching
[12:17] On the other side
[12:18] the unstructured data sources
[12:19] are not going to be queried in the same way
[12:21] and they're not going to be imported in
[12:22] the same way either
[12:24] So
[12:24] they're going to turn into what we call the lexical graph
[12:26] which represents the original textual data
[12:28] plus also the structure around that textual data
[12:31] To connect those two pieces
[12:33] the unstructured data and the structured data
[12:35] we've got this part in the middle that
[12:37] we're going to call the subject graph
[12:39] The subject graph is going to be
[12:40] subjects or entities that we pull out of the chunks
[12:43] so the chunks will have some text
[12:44] they'll be talking about products
[12:46] maybe they'll be usernames and things
[12:48] all of those things might be entities
[12:50] We're going to find those
[12:51] call those things subjects
[12:52] and those subjects are going to be connected to objects
[12:54] so the subjects talk about something
[12:56] So some user, let's say that it's me
[12:58] user ABK, loves this table
[13:02] And so there'll be a
[13:03] subject predicate object
[13:04] in the subject graph
[13:06] that talks about ABK loving some table
[13:08] That also, because ABK loves a table
[13:11] the table can correspond with the product that
[13:13] we have in the structured data
[13:15] If ABK mentions a table
[13:17] and the table is a product that exists
[13:18] in the structured data
[13:20] we can then connect
[13:21] the entities that we've extracted from the text
[13:24] all the way over to the structured data
[13:25] that we've got in from the CSV files
[13:28] Don't worry
[13:29] we're going to do this step by step
[13:31] On a high level
[13:32] this is what you're going to end up with
[13:33] a graph with subgraphs within it
[13:35] a domain graph, a subject graph
[13:37] and a lexical graph. All of the knowledge graph you'll build
[13:41] let's go through the details of the multi-agent
[13:44] system you'll design
[13:45] to first find the graph model and then
[13:47] construct the graph. There are lots of definitions
[13:49] for an agent
[13:50] Here's my definition
[13:52] I like to think about agents from an engineering perspective
[13:54] and for me
[13:55] it's a fancy new kind of control flow operator
[13:57] Basically, you have a loop
[13:59] and inside of the loop
[14:00] there's a call to an LLM
[14:01] that then figures out what it wants to do
[14:04] and then based on what it wants to do
[14:06] passes that back over to the computer side
[14:09] to the client side
[14:10] and really runs into a switch statement
[14:12] that performs potential actions
[14:14] So in this loop
[14:15] this is really just
[14:17] intelligent behavior that's happening because of the LLM call
[14:20] but the execution of that intelligent behavior is
[14:21] still happening through code
[14:24] What's great about this architecture
[14:25] of course
[14:25] is that agents are really powerful because you've
[14:27] got an LLM there to do some reasoning
[14:29] and
[14:29] call out to tools that can do anything
[14:31] you can do with code
[14:32] And it's adaptive because the LLM is given memory
[14:35] so it can learn what's happened
[14:36] either through the conversation or through things that
[14:38] you've saved into memory
[14:40] that are important for it to decide
[14:41] future outcomes
[14:43] And it's pretty easy to get started because
[14:45] you're really just doing natural language descriptions through
[14:47] the prompts about what the agent should do
[14:49] But
[14:50] all this power and ease comes with some
[14:51] downsides
[14:53] It can be slow working with an agent
[14:55] because the calls out to a remote LLM
[14:56] is a bit expensive and slow
[14:58] It's also non-deterministic, well, because LLMs are non-deterministic
[15:02] And, you know
[15:03] token cost over time can really add up
[15:05] quite a lot
[15:06] So if you're running an agent over time
[15:08] in production for thousands and thousands of calls
[15:11] the token cost gets really expensive really quickly
[15:14] That's one of the advantages of moving to
[15:16] a multi-agent system
[15:17] is that you can actually improve some of
[15:18] the downsides here
[15:20] So what is exactly a multi-agent system?
[15:23] It is, of course
[15:23] just a system where you have multiple agents
[15:25] working collaboratively on a single goal
[15:29] The agents interact in a couple different ways
[15:43] There's a main conversational thread that's basically happening with the user
[15:47] where the user might have some
[15:48] message that they kick off to work with
[15:50] and then each of the agents can decide
[15:52] is this work that I can do
[15:53] or something that somebody else should do?
[15:55] So
[15:56] can I delegate this to a different agent?
[15:58] So you can see in this illustration here
[15:59] that the root agent is able to delegate
[16:01] to either agent A or agent B
[16:03] Internally
[16:04] agent A and agent B
[16:05] can do some work using the tools that
[16:07] they've been given
[16:08] One of the tools in Agent B is
[16:09] unique
[16:10] This P agent here
[16:11] this P function, is actually going to be an agent itself
[16:15] but being called as if it were a
[16:16] tool
[16:17] So there's two ways for tools to interact
[16:19] either agents delegating to each other
[16:21] or an agent that's behaving as a tool
[16:23] being called by another agent
[16:25] And along the way
[16:26] you've got specific checkpoints with the user that
[16:28] are possible
[16:29] whenever you have any of these transitions
[16:31] So what is the multi-agent system that you'll
[16:33] build?
[16:34] You'll build parts of a knowledge graph agent
[16:36] focusing on the sub-agents that perform knowledge graph
[16:39] construction
[16:40] You'll learn the basics of building an agent
[16:42] using Google's ADK
[16:44] You'll learn what memory is and how to
[16:45] use it for recording critical information
[16:47] You'll define some tools. And of course
[16:49] all of this will converge from open-ended conversation
[16:52] to executable code
[16:54] This beautiful diagram
[16:56] are all the agents
[16:57] and the flow of agents and their interactions
[16:59] Let's walk through this a little bit at
[17:01] a time
[17:02] At the top level
[17:03] this is the agent that manages the overall
[17:06] introduction of the user to what's possible
[17:08] what the agent's responsibility is
[17:10] and helping the user understand what's the workflow that's possible here
[17:14] from knowledge graph construction all the way to
[17:16] doing graph retrieval
[17:18] So this is really a conversational agent that
[17:20] itself is not going to do any work
[17:21] but it's going to guide the user through
[17:23] the different phases of work that are going
[17:24] to occur
[17:26] It's this next level of agents down
[17:28] that are really going to manage the individual
[17:29] workflows
[17:30] And there are three major workflows
[17:32] If really on the left
[17:33] we've got two workflows
[17:35] the structured data agent and the unstructured data
[17:37] agent
[17:38] These are responsible for taking
[17:40] the user through the idea of like what
[17:41] they might want to do
[17:42] all the way to constructing a graph
[17:44] And then if those have done their job
[17:46] this third agent, the graph rag agent on the right side
[17:49] is responsible for helping the user actually
[17:51] answer questions using that graph
[17:53] Both the structured data agent and the unstructured
[17:55] data agent are workflow agents
[17:58] They perform their work by interacting with the
[18:00] user
[18:00] and helping them go through the steps of
[18:02] what needs to happen from
[18:03] the idea of what they want to do
[18:05] all the way to describing the graph
[18:07] And they do that by delegating to sub-agents
[18:08] that specialize in each phase of the workflow
[18:11] You'll see some replication here that both the
[18:13] structured and unstructured data have some agents that are in common
[18:17] and I'll touch on those as we get
[18:18] into the one level down
[18:20] Okay
[18:20] so here's the sub-agents that are actually doing
[18:22] the workflow for structured data
[18:24] Let's walk through these one at a time
[18:26] and also what's important to note here
[18:28] is the output of actually these agents doing
[18:30] their work
[18:31] If you think about yourself as being a
[18:33] data engineer
[18:34] that's been given the task of actually performing this work
[18:37] each of these agents are kind of what
[18:38] you would do yourself
[18:39] you're engaging in the work
[18:41] This first one, the user intent agent
[18:43] is what you would do when you've been
[18:45] asked to do some task for data analysis
[18:47] and whoever asked that
[18:49] you respond to with some questions
[18:51] Hey
[18:51] could you clarify what you want me to do?
[18:53] Give me, you know
[18:54] what are the goals you're after?
[18:55] What kind of analysis do you want me
[18:56] to perform?
[18:58] And it's really important to nail that down
[18:59] up front. This is the kind of the
[19:00] requirements or the direction overall
[19:03] of what the job is
[19:04] So this user intent agent
[19:06] even though it's collaborative and kind of conversational
[19:09] the output of this is really important
[19:10] We're capturing what is the user goal
[19:12] and what are they trying to get out
[19:13] of this work
[19:14] Based on that user goal then
[19:16] this next agent down
[19:17] the file suggestion agent
[19:19] is going to take into account
[19:21] what has been established through the user intent
[19:22] agent
[19:23] as the direction and the goal of what the work is
[19:26] and then it's going to look at the
[19:27] data files that are available and try to
[19:28] find from those data files
[19:30] which ones are useful for actually achieving that
[19:32] goal
[19:33] There might be more files that are available
[19:34] there might be even
[19:35] multiple data sources that are available
[19:37] Here we're simplifying it down to just making
[19:39] suggestions for files that are available on disk
[19:42] The output of that ends up being a
[19:43] list of suggested files that have been approved by the user
[19:47] and then that gets input into the next agent
[19:49] which is the schema proposal agent
[19:52] The schema proposal agent is actually a pair
[19:53] of agents formed in a critic pattern
[19:56] where one of the agents is responsible for
[19:58] making a proposal about what the schema could look like
[20:00] and the next one is going to be a critic saying
[20:02] well, maybe that's not quite so right
[20:04] Think about changing it in this way or
[20:05] that way
[20:06] We'll look at the details in a later
[20:08] lesson
[20:09] But the idea here is that this
[20:10] pairing of agents internally will loop through what's possible
[20:14] self-criticize itself
[20:16] and the outcome of that should be a
[20:17] good graph schema
[20:18] that uses the files that were approved from
[20:20] the previous agent and also in compliance with
[20:22] user goals that were set by the first agent
[20:24] producing a graph schema
[20:26] that can answer questions that are useful for
[20:28] the user
[20:29] So the output of all of that
[20:30] we're calling a graph construction plan
[20:32] It's not a graph itself
[20:34] but it's a description about how to construct
[20:36] that graph
[20:37] The second workflow in the middle
[20:38] the first two parts of that workflow
[20:40] are the exact same as the structured data
[20:42] workflow
[20:43] Here in the middle
[20:44] we're dealing with unstructured data
[20:46] but it still begins with understanding what is
[20:47] the user intent for bringing in the unstructured data
[20:50] and here that's Markdown files
[20:52] And then, okay
[20:53] if
[20:53] you understand why the user wants to bring
[20:55] in some Markdown files
[20:56] you can identify which files are relevant
[20:59] Again, a file suggestion agent would do that
[21:01] Similar behavior to the structured data
[21:03] but this third step is different
[21:06] In the third step
[21:07] rather than designing a schema based on some CSV files
[21:10] all you have is text
[21:12] And from that text
[21:13] how do you create a graph?
[21:14] Well
[21:15] the approach here is that we're going to
[21:16] have two specialized agents
[21:18] that look through the text and identify what are called entities
[21:21] so people, places, and things that occur within the text
[21:24] and also for those entities that identifies
[21:27] what facts are describing those entities within the
[21:30] text
[21:31] So let's say that it was
[21:32] you know
[21:33] I was in the text and I had
[21:34] some reviews of local coffee shops
[21:36] it might reveal that
[21:38] you know, ABK really loves to store coffee from Phil's
[21:41] because who doesn't?
[21:43] So those are facts that could be extracted
[21:44] from the text
[21:45] The goal of this agent is actually to
[21:47] find out what kinds of facts can be
[21:48] extracted and not do the extraction
[21:51] but simply describe what's possible
[21:53] And so that we're going to be calling
[21:54] a knowledge extraction plan
[21:57] The knowledge extraction plan paired with the graph
[21:59] construction plan from the structured data
[22:01] together give all the rules that we need
[22:03] using the graph construction plan and the graph
[22:05] extraction plan
[22:06] This red box down in the corner then
[22:08] is just a single tool that has multiple
[22:09] tools internally
[22:11] that actually can take those plans
[22:13] and do the extraction itself and do the
[22:14] construction itself
[22:16] It'll loop
[22:16] over all the construction rules to create a domain graph
[22:19] loop over all the markdown files
[22:21] chunk them up, do the vector embedding of those
[22:24] and then also extract entities and the facts
[22:27] and then connect those to the structured data
[22:30] In lessons four through eight
[22:31] you'll go through the entire workflow for structured data
[22:34] from user intent, file suggestions
[22:36] to the schema proposal
[22:38] Then we'll skip over to the unstructured data
[22:41] just the entity and fact type proposal
[22:43] and then finally we'll look at the particular
[22:45] tool in lesson eight
[22:46] that does the graph construction itself
[22:48] It does all the hard work that
[22:50] the previous agents really
[22:51] did the reasoning about what the work should
[22:53] be
[22:53] In the next lesson
[22:55] we'll actually get into doing some coding
[22:56] building your first agent. We're going to be
[22:58] using Google's ADK
[23:00] If you're already familiar with Google ADK
[23:01] you could skip over that lesson and move
[23:03] on to actually building the multi-agent system
[23:05] but I think it's a really good
[23:07] overview and also it helps you understand how
[23:09] I think about it
[23:10] and how I've implemented it in this particular multi-agent system
[23:13] so it's nice to walk through
[23:15] I'll see you there
[23:17] To build the multi-agent system
[23:19] you'll use Google's ADK or Agent Development Kit
[23:22] which is a framework for developing agents
[23:24] In this lesson
[23:25] you'll learn how to create and run
[23:27] one agent as well as a team of agents
[23:30] All right, let's go
[23:32] In this lesson, you'll familiarize yourself with Google's Agent Development Kit
[23:36] and you'll use that for building agents throughout
[23:38] this multi-agent system
[23:40] In this lesson
[23:40] you'll learn how to create and run an agent using ADK
[23:44] and the imports that we're doing here
[23:45] of course, the standard OS
[23:47] and then a bunch of stuff from Google
[23:48] ADK itself
[23:49] We're going to import this agent
[23:51] which is going to be the key thing
[23:52] for actually describing what an agent is
[23:54] For interacting with an LLM
[23:56] we're going to be using the LiteLLM library
[23:57] so we're going to import that here
[23:58] and this is a
[23:59] little wrapper for letting Google ADK
[24:01] talk to OpenAI
[24:03] And then we're also going to need some
[24:04] memory for the agent
[24:06] For the memory, we're going to use the memory session service
[24:08] and then finally, the agent also needs a way to run
[24:10] so we're going to import a runner
[24:12] We also have some typing stuff here that's
[24:14] not really so important for how all this
[24:15] works
[24:16] Let's go ahead and make sure that all that imports
[24:18] Great, all the libraries are imported
[24:21] So the next part then
[24:22] let's just start defining the
[24:23] models that we're going to use
[24:25] We're going to be using OpenAI for this course
[24:27] so let's go ahead and import
[24:29] we'll define what the model is going to be itself
[24:31] is OpenAI's GPT-4o. Again
[24:33] we're going to be using LiteLLM for actually
[24:36] reaching out to the OpenAI API
[24:38] and we're just going to go ahead and
[24:39] try
[24:40] a sample
[24:41] execution of completing a chat with that
[24:43] So if you look at the chat here
[24:45] you'll notice that we're just setting up a
[24:47] message that we're going to send to OpenAI
[24:49] and we're going to ask it the question
[24:51] are you ready?
[24:53] So if that all works successfully
[24:54] we'll get a good message from OpenAI
[24:56] letting us know that this works
[24:59] Looking at the model of response
[25:00] there's a lot of information here
[25:02] but the key part is that the response
[25:04] includes a message from OpenAI saying
[25:06] yes, I'm ready
[25:07] how can I assist you today?
[25:08] OpenAI is all set to go
[25:10] We're also using Neo4j today
[25:11] so we're going to import a helper library
[25:13] that combines Neo4j
[25:15] with Google ADK in a nice way
[25:17] And
[25:18] that library is something we can take a
[25:19] look at
[25:20] to see the details of what's going on
[25:22] The import that we're going to use
[25:23] is just from Neo4j for ADK
[25:25] import the GraphDB library
[25:28] Let's take a look at those details
[25:30] Okay, now we're inside of Neo4j for ADK
[25:32] and you can see it starts off pretty
[25:34] simply. We import some stuff from the operating system
[25:36] We, of course, load up the environment
[25:38] And then from Neo4j
[25:39] the Python package, we load up the graph database
[25:42] and you also get a result class definition
[25:45] Now
[25:45] a bunch of these functions that are in
[25:46] here are just really nice for just wrapping
[25:48] up how you interact with Neo4j
[25:50] and presenting the results from Neo4j
[25:52] in a way that
[25:52] Google ADK likes to see things
[25:55] One of the key things is that results
[25:56] should come back either as a
[25:58] dictionary with a status
[26:00] that is a success
[26:01] or a status that is an error
[26:03] These two helper functions help do that
[26:04] You can call tool success or tool error
[26:07] along with some extra arguments
[26:08] and actually get a nicely formatted result from
[26:10] any kind of call
[26:11] To that
[26:12] we then go ahead and also
[26:13] integrate a helper library
[26:15] Results that are handled by Google ADK
[26:17] need to be easily persisted
[26:19] so this function call here to Python
[26:21] basically goes through all the different kinds of
[26:23] results you can get back from Neo4j
[26:25] and makes them easily serializable and a nice
[26:27] format
[26:28] for Google ADK. You can look The details
[26:30] if you want to see what's going on
[26:31] here
[26:32] The key part, of course, is this function
[26:34] It takes the Neo4j result
[26:36] your pass in it as just a result
[26:37] basically calls it to Python package
[26:40] packages all that up into a result that
[26:41] is easily used by Google ADK
[26:44] Each of those helper functions
[26:46] is then also used by this
[26:47] upper level class called Neo4j for ADK
[26:50] and this is really a wrapper that combines
[26:51] a Neo4j driver
[26:53] initializes the environment variables used there
[26:55] allows access to the driver
[26:57] and then has a special function here for sending queries
[27:00] and it'll send any kind of query you'd like to
[27:02] but then uses those helper functions for actually
[27:04] reformatting those results into
[27:06] a nice Google ADK result
[27:08] At the end then
[27:09] because we're just going to have one driver
[27:11] and one connection that we're using
[27:12] we're going to have a singleton of this
[27:13] class that we use
[27:15] This is the graph DB
[27:16] that we're going to actually expose as a
[27:17] variable and use that through all the notebooks
[27:20] Okay
[27:20] we took a look at Neo4j for ADK
[27:22] Let's continue with the notebook
[27:24] So now we've got everything set up
[27:25] and we can start to define an agent itself
[27:28] Okay, with our Neo4j wrapper ready
[27:29] let's go ahead and give it a try
[27:31] You can just send in kind of Neo4j
[27:32] query that you'd like to
[27:33] as long as it's valid Cypher
[27:35] Here
[27:36] the Cypher that we're sending is a very
[27:37] simple Cypher statement that doesn't do any work
[27:39] other than directly return a result
[27:41] Here, the result is a string
[27:43] Neo4j is ready
[27:44] passing that back aliased as a message variable
[27:47] So if we run this and then print the result
[27:50] you'll see that it's been packaged up into
[27:52] this nice little dictionary with a status success
[27:55] and then the query result
[27:56] containing an array
[27:57] of all the rows returned from the database
[28:01] Great, with OpenAI ready and Neo4j ready
[28:03] we can start to define our tools themselves
[28:06] and the agent eventually
[28:08] Tool definition is an important part in actually
[28:10] defining an agent
[28:11] Without tools, an agent can do a lot of thinking
[28:13] maybe have some chats
[28:14] but it can't really do any interactions with
[28:16] the environment or with the world around it
[28:18] So we're going to find a very simple
[28:19] tool just to kind of illustrate
[28:21] what kind of things an agent can do
[28:23] Hello World is the classic
[28:24] of course. So we're going to develop the
[28:26] Hello World version of for an agent's tool
[28:29] and we're going to call it SayHello
[28:31] So tools can be simply defined as functions
[28:33] Here the function is just say hello
[28:35] it takes a single argument
[28:36] person name as a string
[28:37] and it returns a dictionary
[28:38] Of course that dictionary is the Google ADK
[28:40] dictionary that it likes to see all results
[28:42] in
[28:43] And
[28:43] it also has a couple of important parts
[28:45] here
[28:46] There's a doc string that's here
[28:47] which is always nice when you're writing code
[28:49] It's also especially critical when you're developing tools
[28:51] for Google ADK
[28:53] This doc string is what lets Google ADK
[28:55] understand what actually this tool does
[28:58] This gets passed along to the LLM
[29:00] when the LLM is told
[29:01] here's all the tools that are available
[29:02] and also here's what those tools
[29:04] are described as doing
[29:06] So
[29:06] this is a couple of important parts that
[29:07] we should go through here
[29:08] You describe what the tool does
[29:10] Here it just formats a welcome message to a named person
[29:13] of course passed in as a person name
[29:15] You describe the arguments that are being passed in
[29:17] and also the result
[29:19] The result here is consistent through all of the tools
[29:21] because the result is a dictionary
[29:22] that Google ADK likes to see
[29:25] But you can add a little extra detail
[29:26] if you want to here
[29:27] For instance
[29:27] if you know the kinds of errors that might come back
[29:29] you could explain that here as well
[29:31] Inside, the function is incredibly simple
[29:34] All we're doing is using Neo4j
[29:35] again to actually do a hello world
[29:38] We're going to call out to Neo4j
[29:40] sending a query where
[29:41] we're still going to return a hello to you
[29:44] but then we're also going to concatenate that
[29:46] with this person name
[29:47] which is passed in as an argument to
[29:48] the function
[29:50] That's going to get passed in as a
[29:51] query parameter to this query
[29:54] Whenever you see that dollar sign in a
[29:55] Neo4j Cypher statement
[29:56] that means here's a query parameter
[29:59] So here in this array
[30:00] in this dictionary that's being passed in
[30:02] you'll see the person name is being passed
[30:03] in as person name
[30:05] That'll get substituted in as this variable here
[30:07] not as a template substitution
[30:08] but as the value gets passed in
[30:10] And then this whole query will get executed
[30:13] So let's define that function
[30:14] And of course, because this function is just a normal function
[30:17] we can try to run it
[30:18] So we can print saying hello to A
[30:20] B K
[30:21] and expect to see a very nice
[30:23] Google ADK formatted result that was successful
[30:26] where the query result that was sent off
[30:28] to Neo4j
[30:29] has the reply hello to you ABK
[30:31] during that concatenation
[30:33] Fantastic
[30:34] Now, just a side note here about query parameters
[30:36] part of why we're doing that
[30:37] this is
[30:38] good discipline for any kind of query language
[30:39] they're using
[30:40] Most query languages have the ability to have query parameters
[30:43] and one of the reasons you do that
[30:45] is to avoid injection attacks
[30:46] right?
[30:47] So that people can't pass in
[30:48] values that look like
[30:50] SQL statements or Cypher statements or any other
[30:52] query language statement
[30:54] as a value and have that concatenated into a string
[30:56] that can cause all kinds of mayhem
[30:58] So instead, you pass in a query parameter
[31:00] and here, for instance
[31:01] if I pass in the name and say
[31:03] actually, the name's going to be
[31:04] hey, return some string here
[31:06] this could be some malicious code instead that
[31:08] gets passed in as the person's name
[31:10] If you just concatenated that as a string
[31:12] all kinds of bad things can happen
[31:14] Instead
[31:15] because it's a query parameter that still disbehaves as a variable
[31:18] it gets passed in
[31:19] it gets concatenated as a string with the other string
[31:22] and the result is
[31:23] simply hello to the somewhat friendly and malicious injection attack
[31:27] And, of course, it's been avoided now
[31:30] We have a basic tool available
[31:32] Now we can define an agent that's going
[31:33] to use that tool
[31:35] Now there are a couple of components of
[31:36] defining an agent. It's common across all frameworks
[31:39] They all do some variations of the same
[31:40] idea
[31:41] Let's take a look at what's happening inside
[31:43] of Google ADK to define an agent
[31:47] Now if you recall earlier
[31:48] we had imported this agent class from Google
[31:50] ADK
[31:51] So we're going to make an instance of that class
[31:53] and it takes a bunch of parameters
[31:55] So the first thing that's important is that
[31:57] every agent is given a name
[31:58] Here we're going to call it hello agent
[32:00] underscore v1
[32:01] This is in case you have multiple versions
[32:03] of the agent that you want to
[32:04] have at the same time
[32:06] or if you want to actually have different
[32:07] versioned instructions as well
[32:09] Having an idea of what the version of
[32:10] this agent is is very helpful for debugging
[32:12] later on
[32:14] You also pass in the model that you want to use
[32:16] or if you've called
[32:17] we defined LLM before as being
[32:19] a call through LiteLLM out to OpenAI
[32:22] so we're going to use that here
[32:24] And
[32:24] these next two are pretty critical for how
[32:26] the Google ADK actually orchestrates and executes agents
[32:30] The first part is this description of the
[32:32] agent
[32:33] This is a little bit like the doc
[32:34] string of the tool
[32:35] what describes what does this agent do
[32:38] This lets Google ADK
[32:39] and also the other agents understand
[32:41] what is the purpose of this agent
[32:43] and
[32:43] is there
[32:43] occasions when I should call this agent rather
[32:46] than doing something myself
[32:47] what's called agent delegation
[32:50] So that's for other agents to know what
[32:51] to do with the agent here
[32:53] Then for the agent itself
[32:54] you provide some instruction
[32:56] And the instruction is basically the same kind
[32:57] of thing you would have done with
[32:59] when you're doing prompt engineering and you're defining
[33:01] the system prompt for
[33:02] the LLM
[33:04] This is the same kind of thing that
[33:05] you would do there
[33:06] This is a hello world agent
[33:08] so it is, of course, very helpful
[33:10] It's a helpful assistant that's going to chat with the user
[33:12] and it really only has one tool that
[33:14] it wants to use
[33:15] So you describe that tool here so that the agent understands
[33:18] not just from the tool definition
[33:19] but also from your instructions that you're giving it
[33:21] how to think about that tool and when
[33:23] to use that tool
[33:24] So here, if the user provides their name
[33:26] you know
[33:27] use the say hello tool
[33:30] to give them a custom greeting
[33:34] And then the final part
[33:35] of course
[33:35] is we have to make those tools available
[33:37] The tools get passed in as an array
[33:39] of just the function names themselves
[33:40] So we're going to pass in say hello
[33:42] and then
[33:43] the agent then has access to that tool
[33:45] It knows what to do with that tool
[33:46] because we give it instructions
[33:48] and other agents, if there are other agents
[33:50] know what this agent's role is
[33:53] Now that we have an agent
[33:54] and the agent has the tool
[33:55] and it has instructions about how to use that tool
[33:57] now we need to run the agent
[33:59] This is the final part in creating a
[34:00] very basic agentic system
[34:03] An agent has to have an execution environment
[34:06] So if you look at this diagram here
[34:07] you'll see that inner box here
[34:09] this is the execution environment that happens
[34:11] There's a runner class that actually manages all the event loops
[34:15] basically, for calling out to the LLM
[34:17] passing results from the LLM to particular agents
[34:20] and coordinating all the agents themselves and how
[34:21] they execute
[34:23] Each of those runners also has access to various services
[34:26] whether that is in-memory services for
[34:28] like, doing actual memory. Memory could be in-memory
[34:31] or it could be
[34:31] you could use a database like Neo4j for
[34:33] memory as well
[34:34] That gets you access to storage
[34:36] Then there's the execution logic that inside of the execution loop
[34:39] here are the steps for actually running things
[34:41] and coordinating the agent
[34:42] whether agents are running in parallel or in
[34:44] sequence or in a loop
[34:46] This altogether actually is the execution environment for
[34:48] the agent
[34:49] Okay
[34:50] We're going to do this by hand first
[34:52] and then show how we can wrap this
[34:53] up to a little convenience method
[34:55] When you're doing your own development with Google ADK
[34:57] Google ADK has really great tooling for just
[34:59] defining an agent
[35:01] and then using the tooling for actually just
[35:02] running that agent. Providing it the full execution
[35:04] environment that it needs
[35:06] We're going to be doing that by hand
[35:07] inside of the notebook
[35:08] so let's do that one step at a
[35:09] time and then wrap it up into a
[35:10] little helper
[35:13] So there are a couple of things you're
[35:14] going to need to actually set up the
[35:15] execution environment
[35:17] Every runtime actually runs within a session
[35:19] You could, of course
[35:20] have multiple sessions that are running in some
[35:22] production environment. Here we're going to have a
[35:23] single session where we're going to go ahead
[35:25] and just set up the in-memory service
[35:27] which provides context
[35:28] and state for the agent as it's running
[35:31] We're going to create the session service
[35:33] based on that memory
[35:34] and also for the particular agent that we're writing
[35:36] and also assuming that we have a user
[35:38] we're going to assume that we have a single user
[35:40] a single application that we're running
[35:42] and a single session
[35:43] All that is going to be used here
[35:44] in the create session
[35:46] to actually create a single executable state to actually be run
[35:50] and then the runner is going to run
[35:52] that state given the agent that it has
[35:54] So here the runner combines the agent that
[35:56] we want to run
[35:57] our hello world agent
[35:59] the app name is going to be the
[36:00] same as we passed into the session here
[36:02] and also the session Service is going to
[36:03] be the session within which this agent runs
[36:06] Again, in a production environment
[36:08] there might be multiple sessions
[36:09] there might be multiple applications that are using
[36:11] this agent
[36:11] That's why these are all different arguments to run
[36:15] Okay
[36:15] now there's a lot to walk through
[36:17] just to actually do the running of the
[36:18] agent as well. So let's go through this
[36:20] step by step and take our time
[36:22] We know that we just have this runner
[36:23] available that we just defined
[36:24] and we're going to do just a single
[36:26] loop through with a single user message
[36:28] and allow the runner to execute the agent
[36:31] reacting to that message from the user
[36:33] So we're going to define a user message
[36:35] and I'm simply going to say
[36:36] hello, I'm ABK
[36:37] and we'll go ahead and print that message
[36:39] out in a friendly way so we
[36:40] ourselves can see as this is running what's
[36:42] going on
[36:43] That message that is just a string has
[36:45] to get packed up into a data structure that Google ADK
[36:48] the runtime environment expects
[36:50] Usually this is handled behind the scenes for you
[36:52] of course
[36:52] but we're going to do this by hand
[36:53] So we're going to create this content class here
[36:57] and the role of the content that we're
[36:58] creating is from the user
[37:00] This is a user message
[37:02] Content can have multiple parts
[37:04] so we're going to create an array of
[37:05] parts where one of the parts is
[37:07] has some text
[37:08] where the text is a user message
[37:10] This is all bundled up to do
[37:12] more complex things. Here we're just trying to
[37:14] run a single message from a single user
[37:16] but this gives you lots of flexibility when
[37:18] you have lots of extra things going on
[37:20] and this is basically creating a content event
[37:23] that then has to get processed by the
[37:25] agent runtime system
[37:26] Also
[37:26] we're going to go ahead and set up
[37:28] a response from the agent system
[37:30] in case it doesn't do anything
[37:32] So after you pass in a message
[37:34] we're going to actually go through running that
[37:36] message and letting the agent get a chance to respond
[37:38] but it's possible that the agent doesn't respond
[37:41] There's this notion of having a final response
[37:44] which is a flag that an agent can
[37:45] set in different ways to actually indicate
[37:48] okay, I'm done thinking about this
[37:49] or I'm done processing this
[37:51] so you can go on and go back
[37:52] to the user
[37:53] In case the agent does nothing
[37:55] a final response may not get set
[37:57] So we preset it here with a default
[37:58] value
[37:59] to let us know that nothing has happened
[38:02] We're going to run through without any verbose output right now
[38:05] and you can see in a second what
[38:06] the verbose output might look like
[38:08] This is the event loop itself
[38:10] Well, one step I should say of the event loop
[38:12] you know, for this one message
[38:14] where given the user message
[38:16] we're going to asynchronously use the runner
[38:18] and call out to the LLM
[38:21] using the message that was passed in
[38:23] the agent that was defined to use that model
[38:25] and all the instructions that we had given
[38:26] it
[38:27] So the first thing that you'll notice is
[38:28] that when we call this async
[38:30] we also pass in all the
[38:31] same information we had for creating the session
[38:33] This is because you can run things
[38:35] again, there could be multiple sessions going on
[38:37] so you have multiple event loops running around
[38:39] And asynchronously, you pass in
[38:41] here's the context that I'm currently operating in
[38:44] It's for this user in this session
[38:46] and here's the content that's getting passed in
[38:48] Go ahead and execute this once
[38:50] Let the LLM do some work on this
[38:53] This is inside of a for loop
[38:55] because this is an agentic system
[38:57] So once the agent is given this message
[38:59] it might do a bunch of things before
[39:00] actually having that final response
[39:03] So the event loop here
[39:04] pulls out events from the
[39:06] asynchronous running of the agent
[39:08] Every event is some update from
[39:10] the agent itself
[39:12] As the events come in
[39:13] if the verbose mode is turned on
[39:15] we'll print out, here's an event that happened
[39:17] here's who created that event
[39:19] The initial event, of course
[39:20] should be that the user message was passed in
[39:22] so we should see the event author was the users themselves
[39:26] and you'll see the content of the event
[39:27] as well
[39:28] You can take a look at what's happening
[39:29] here in the debug statement
[39:31] A bunch of things get printed out
[39:32] which are helpful to understand what's going on
[39:34] And then this is the key concept for
[39:36] keeping the event loop running
[39:37] for as long as you'd like it to
[39:38] run
[39:39] Hopefully the agent will run
[39:41] only as much as it needs to
[39:43] But as each event comes in
[39:44] there's a flag that says
[39:46] okay, this is the final event
[39:47] I'm done processing this. The agent is done
[39:49] processing
[39:50] If it has set this
[39:51] then you know that
[39:52] okay, the processing is over
[39:54] You can take a look at the content
[39:55] decide what the final response might be
[39:58] Here we're taking a look at the content
[40:00] if they have some multiple parts
[40:02] So if it's a non-zero array of text that'd come back
[40:05] we're going to take the first message back
[40:07] from the parts zero here
[40:09] grab the text from that
[40:10] and here we're making some assumptions
[40:12] that the text response in the first part
[40:14] is actually the right one
[40:15] Turn that into the final response text
[40:18] Alternatively, the agent could have decided
[40:20] this is my final response
[40:22] and by the way
[40:23] I don't have actually a response
[40:24] What I've asked the
[40:26] runtime system to do is actually to escalate
[40:28] Now here escalation ends up meaning the agent is running
[40:31] knows that it's a sub-agent
[40:33] and it can't handle or it can't do
[40:34] any more work with what's currently available
[40:36] So it's basically saying
[40:37] hey, escalate this to somebody else
[40:39] either my parent or to some other agent
[40:41] that might be appropriate
[40:42] In that case
[40:43] the final response text that we're going to
[40:45] set is based on that
[40:46] We're going to say that
[40:47] the agent has decided to escalate the current
[40:49] handling of the message
[40:50] and that we don't have any specific message
[40:52] or there's an error message
[40:54] if there is one there
[40:55] and return that as the final message
[40:58] All that is to continue to run through
[41:00] one round through the event loop
[41:02] instigated by a single user message
[41:04] and then at the end we'll go ahead
[41:05] and print out the final agent response
[41:08] That's kind of a lot to go through
[41:09] but keep that in your heads a little
[41:10] bit as you're going through all the notebooks
[41:12] Internally
[41:13] this is really what's happening to actually make
[41:14] all the machinery run
[41:17] For all that work
[41:18] there we go
[41:19] Simple chat
[41:20] Hello, I'm ABK
[41:21] Hello to you, ABK
[41:23] Of course
[41:24] because we're going to be doing a lot
[41:25] of calling to agents manually
[41:27] we're going to set up a helper class
[41:29] to actually let us do that a little
[41:30] bit more easily
[41:32] And I'm going to call that helper class
[41:34] agent caller
[41:35] This agent caller
[41:36] basically wraps up those functions that we went
[41:38] through each one at a time here
[41:41] and also the event loop itself
[41:45] into one class
[41:46] And if you look through the details
[41:49] it is
[41:49] doing all the things that we'd seen above
[41:52] It's saving the single user ID
[41:55] the single session ID
[41:56] the current agent that we're going to be running
[41:57] and also the runner that's been set up
[42:00] It has access to getting the session
[42:01] that it uses internally for actually managing stuff
[42:05] And this call function here
[42:07] is what actually instigates one round trip
[42:09] through the event loop
[42:11] based on a user message
[42:12] So it does just what we saw above
[42:13] takes the user message
[42:15] packages it up so that it's available as
[42:17] content to be processed by the agent
[42:20] and then it runs through the event loop
[42:22] Same kind of debug options are available as
[42:24] well
[42:26] And this is really a stylistic choice
[42:28] I'm not a native Python developer
[42:30] and so this is the way I like
[42:30] to do things. I prefer
[42:32] having factory methods for things that are a
[42:33] little bit complex to construct
[42:35] So rather than having a complex constructor inside of that class
[42:39] I created a separate class that actually does
[42:40] the construction
[42:43] And this here, this utility function, make agent caller
[42:47] is will create an instance of the agent
[42:49] caller
[42:50] You will be passing into it
[42:51] all the necessary information that it has
[42:53] What's the agent that you want to be running?
[42:55] And also
[42:55] what is the initial state of that agent?
[42:57] Where the state is the agent's internal memory
[43:00] All of this should look just like what
[43:01] we had run through before
[43:02] but now packaged up into here's the different elements
[43:06] the major components that should be combined into
[43:07] the agent caller
[43:09] What is the current app
[43:10] the user, the session ID
[43:12] create a session service for both memory and
[43:14] also for managing the session itself
[43:17] And then finally, also create a runner
[43:19] Then having constructed all those things
[43:21] pass those into the agent caller
[43:23] which wraps those all up into an execution loop
[43:27] Okay
[43:27] now that we have some utility functions for running an agent
[43:30] we can run a conversation with the say hello
[43:33] agent that we said bef- that we created
[43:35] earlier
[43:36] So to create a new agent caller for our Hello Agent
[43:39] we're going to
[43:40] actually call out the helper function to make
[43:42] agent caller passing in the Hello Agent itself
[43:45] and we'll just call that the Hello Agent
[43:46] caller
[43:48] Then to run a conversation
[43:49] we're going to have an asynchronous function
[43:51] that has multiple user messages that we're going
[43:53] to pass in to the agent caller
[43:55] using the call method
[43:57] First I'll say, hello, I'm ABK, and then I'll say
[43:59] I am excited
[44:00] We'll go ahead and run that conversation and
[44:02] see what that looks like
[44:04] Awesome. We have created a friendly chat agent
[44:07] Good work
[44:09] So now that you've gotten this far
[44:11] you know the basics about using Google ADK
[44:13] how to create an agent
[44:15] how to give that agent tools that it can use
[44:17] then also how to create an execution environment
[44:19] for that agent
[44:20] Finally, with all that in hand
[44:22] you can script interactions with the agent here in the notebook
[44:25] passing in user messages
[44:27] that lets you then test out
[44:29] how the agent's going to work
[44:30] So, this fantastic agent caller class that we created
[44:34] and then this construction method
[44:35] the factory method called make agent caller
[44:37] we're going to be using that through all
[44:38] the other notebooks
[44:39] to make it easy for once we've defined an agent
[44:41] we can easily create a runtime environment using that function
[44:44] So
[44:44] you'll get a lot of use with that
[44:47] In the previous lesson
[44:49] you learned how to create an agent using Google ADK
[44:52] and now we're going to create multiple agents
[44:54] a team of agents working together
[44:56] We're going to have a root agent and
[44:58] then two sub-agents
[44:59] We'll build on what we did previously where
[45:01] we had a say hello agent
[45:03] We'll introduce a new agent that can say goodbye
[45:05] and then we'll have another agent that
[45:06] puts them together into one multi-agent system
[45:10] As usual
[45:10] we'll go ahead and start with importing the
[45:12] libraries that we need
[45:13] And then, of course
[45:14] we'll go ahead and set up the LLM
[45:15] that we're going to use
[45:16] Again, this is OpenAI. We'll define the LLM
[45:20] and we'll also go ahead and do this
[45:21] quick sanity check by passing out a message
[45:22] to make sure that it's ready
[45:24] Always fun to see what
[45:26] OpenAI might say on any given day
[45:29] Usually with friendly messages
[45:30] it's pretty good about saying friendly things back
[45:32] Next, you can set up the agent caller
[45:35] We're going to use the same class that
[45:36] we defined before in lesson three
[45:38] part one
[45:40] Rather than defining all that again
[45:41] we're just going to import the tool that
[45:42] we need
[45:43] If you remember from part one
[45:44] we had this helper function
[45:45] make agent caller
[45:47] That's going to create the agent caller class
[45:48] with all that it needs to run
[45:50] Okay, with everything ready
[45:52] you can now begin to create the multi-agent
[45:53] system
[45:54] You're going to create multiple specialized agents
[45:57] each designed for a specific capability
[46:00] You'll create one agent in charge of handling
[46:01] greetings. That's the say hello agent we had
[46:03] before
[46:04] The new agent is going to take charge
[46:06] of saying goodbye
[46:08] To combine those
[46:09] you're going to have what's called a root agent
[46:11] and you'll hear terms like orchestrator or coordinator
[46:14] top-level agent
[46:15] It all really means having an agent that's
[46:17] going to wrap up two other agents
[46:19] and then manage their execution
[46:21] That root agent is going to receive the initial user request
[46:24] the hello or whatever the user decides to say
[46:27] and then decide how to process that either
[46:29] itself or by what's called delegating
[46:31] handing off to one of the sub-agents
[46:33] So the root agent
[46:34] this top-level orchestrator
[46:36] is going to be delegating both hello and goodbye
[46:38] hopefully, to the sub-agents that specialize in those tasks
[46:42] Okay, let's start to assemble our multi-agent system
[46:45] Again
[46:45] we're going to have the say hello agent
[46:47] that we had before
[46:48] we're going to add a say goodbye agent
[46:49] and then we'll combine them together
[46:51] First, we'll define the tools for our sub-agents
[46:55] The first tool is the same say hello
[46:56] tool that we had from the previous lesson
[46:58] This is the hello world function
[47:00] takes in a person's name and creates a
[47:02] hello world message as a response
[47:06] To that, we're going to include a say goodbye function
[47:09] Now
[47:09] this tool is going to be even simpler
[47:11] than the say hello
[47:12] because it doesn't accept any arguments whatsoever
[47:14] It has a constant reply
[47:16] goodbye from Cypher
[47:17] no matter what you want to do
[47:19] this is what you're going to get as
[47:20] a response saying goodbye to the user
[47:23] With those two tools defined
[47:24] we can now define some agents that will
[47:26] use those tools
[47:27] Now we're going to have a special agent
[47:28] for greeting and a special agent for farewell
[47:30] but you'll see it's pretty straightforward
[47:35] Now, as we're defining these sub-agents
[47:36] I really want to emphasize the best practices
[47:38] here and how important it is
[47:40] to have really good descriptions of each of
[47:42] these agents
[47:43] and also instructions that you're handing to them
[47:45] You're going to spend most of your time
[47:46] once you've set up any kind of multi-agent system
[47:49] most of your time is going to be
[47:49] spent actually optimizing these instructions
[47:52] This is back to classic prompt engineering
[47:54] and also this description
[47:56] To repeat what I had said in the previous lesson
[47:58] the description
[47:59] is what allows other agents to know what
[48:01] does this agent do
[48:02] and when should I use this agent
[48:04] That's called delegation
[48:06] And the instructions are for the agent itself
[48:08] to understand what is its purpose
[48:10] what is it trying to do
[48:11] and what tools does it have available and
[48:13] when to use them
[48:14] So this is our greeting sub-agent
[48:16] It's the say hello agent that has
[48:17] access to only the say hello tool
[48:20] And then we'll add our farewell agent
[48:23] The farewell agent is pretty straightforward
[48:25] It's similar to the hello agent
[48:27] You can look through the description here of
[48:28] what the instructions are
[48:30] And these instructions are actually useful
[48:32] to take a closer look at
[48:34] It seems obvious
[48:35] Okay
[48:35] your job as the farewell agent is to
[48:38] respond
[48:39] whenever a user says goodbye in some kind of way
[48:41] Well, people say goodbye in lots of different ways
[48:44] so this is a very small example of
[48:45] how to do some few-shot learning within the
[48:47] agent instructions
[48:48] So here we have in parentheses some examples
[48:51] like when the user uses words like bye
[48:53] goodbye, thanks, bye, or see you
[48:56] those are all ways of saying goodbye
[48:58] Now, most LLMs don't need this extra bit of examples
[49:02] but this is a good practice to have
[49:04] overall is to think
[49:05] how can I help the
[49:06] LLM understand what this agent's purpose is
[49:08] and actually when to execute and what to do in
[49:11] in its role?
[49:12] And of course
[49:12] we're going to hand it the say goodbye
[49:14] tool that we defined earlier
[49:15] Great
[49:16] You know, I have two sub-agents ready to go
[49:19] and now we need to combine them
[49:20] We're going to do that by defining the root agent
[49:23] which is going to understand both of these
[49:24] sub-agents and when to delegate a task to
[49:26] them
[49:27] It's similar to doing tool calling
[49:29] but the agent knows that it's talking to another agent
[49:32] so the entire conversational history gets passed along
[49:34] and actually control of the conversation gets passed
[49:36] along
[49:37] to the sub-agent
[49:38] So it's a little bit different than tool
[49:39] call
[49:40] But the same idea is
[49:41] current workflow is going to go from
[49:43] the agent who is in charge
[49:44] here the root agent
[49:46] to one of the sub-agents
[49:47] So this is similar to tool calling
[49:49] but let's take a careful look at how
[49:51] agent delegation works here
[49:52] We know that the agents themselves have described
[49:55] what their role is
[49:56] like the say hello agent versus the say goodbye agent
[49:58] both have some understanding about
[50:00] what it is they're supposed to do
[50:01] and their descriptions describe to other agents what
[50:04] it is their job is
[50:05] We're going to
[50:06] double down on that in the instructions that
[50:08] we give to the root agent
[50:09] The root agents will be told
[50:11] your job is to coordinate a team of
[50:12] sub-agents
[50:14] So you can see that in the instructions here
[50:16] and that its primary goal
[50:17] is to be friendly
[50:19] In order to be friendly
[50:20] it has actually two specialized sub-agents
[50:22] So we describe what those are so that
[50:23] the agent understands
[50:25] when it actually should use the sub-agents
[50:27] This is like describing when you should use
[50:29] particular tools
[50:30] The greeting agent should be used for handling simple greetings
[50:33] like hello or hi
[50:34] and of course the farewell agent should be
[50:36] used for saying goodbye
[50:37] whether that's bye, see you, or anything else
[50:41] And we're explicit here about saying
[50:43] when those messages are received from the user
[50:44] go ahead and delegate to the sub-agents to
[50:46] actually
[50:47] respond to the user rather than responding directly
[50:49] as the coordinator
[50:51] So if this works well
[50:52] the coordinator shouldn't do anything other than answer general questions
[50:55] and when you say hello or goodbye
[50:57] it should delegate to the sub-agents for actually
[50:59] executing
[51:00] a response or generating a response to the
[51:01] user
[51:03] This
[51:04] top-level coordinator doesn't have any tools to use
[51:06] whatsoever. It can only chat or delegate to
[51:08] the sub-agents
[51:09] We're also going to hand it the list
[51:10] of sub-agents here and the sub-agents key
[51:13] So the sub-agents are the greeting sub-agent and
[51:15] the farewell sub-agent
[51:17] Now that we have a team of agents
[51:18] all put together into a multi-agent system
[51:20] let's go ahead and interact with it
[51:22] This is similar to what we did in
[51:24] part one of lesson three
[51:26] where we had an asynchronous function that
[51:28] managed a conversation
[51:29] So here the conversation is going to be
[51:30] just what we did before
[51:32] Hello, I'm ABK
[51:33] And then later, rather than saying I'm excited
[51:36] this transcript is going to say
[51:37] thanks
[51:38] bye. This is going to be the second
[51:39] user message
[51:41] We've also added this true here
[51:44] So if you look at the call to this agent caller
[51:47] the second argument that's passed in is whether
[51:49] or not to be verbose in responses
[51:51] We're going to turn on verbosity here so
[51:52] you can see all of what's going on beyond the scenes
[51:55] so you can understand both the user message going in
[51:58] see the delegation, see the tool calls
[52:00] and also see the responses
[52:01] It's a lot to walk through
[52:03] but it's worth walking through at least once
[52:05] to get familiar with what you can see
[52:06] when you're debugging an agent interaction
[52:11] All right, this starts off innocently enough
[52:13] We get the user's message
[52:14] Hello, I may be K
[52:15] And you can see that the initial event
[52:18] comes from the friendly agent team
[52:20] So this is the top-level coordinator
[52:22] so the team coordinator that's going to call
[52:24] the sub-agents
[52:25] And you can see the first action that
[52:27] it takes
[52:28] is that it wants to transfer to agent
[52:29] So transfer or delegating to a sub-agent
[52:32] and it's going to transfer to the greeting
[52:34] sub-agent
[52:35] So that's perfect. In response to hello
[52:37] I'm ABK, the top-level coordinator realized
[52:40] I've got an agent who's really good at
[52:41] saying hello
[52:42] Let me transfer control over to that agent
[52:45] So the transfer of response doesn't have any
[52:47] you know, value whatsoever. It's just a none
[52:49] What we should see next is that the
[52:51] greeting sub-agent takes control. So here's another event
[52:54] but now from the greeting sub-agent
[52:56] And it's going to look at the transcript
[52:59] and see the user's message and realize that
[53:01] okay
[53:01] it's now my job to actually do something
[53:03] about this
[53:04] And the greeting sub-agent is going to respond
[53:05] by making a tool call
[53:07] You can see this function call here
[53:09] and the name of the function that it
[53:10] wants to call is called say hello
[53:12] and it's going to pass in some arguments
[53:14] where the one argument that it's passing in
[53:16] is the person name is ABK
[53:18] So the agent has realized that from the statement here
[53:21] of course, hello, I'm ABK
[53:23] it was able to extract that ABK
[53:25] must be the person's name
[53:27] and it's going to make a function call
[53:28] to the tool passing in that name
[53:31] And then you can receive the response
[53:33] Here's the function response
[53:35] and the response is hello to you
[53:37] ABK
[53:38] Perfect
[53:39] Now, the greeting subagent is done
[53:41] It goes ahead
[53:42] and you can see that the final message is true
[53:44] so that's the flag that says I'm done
[53:46] processing this message. We can go ahead and
[53:47] terminate this particular event loop
[53:50] and the final agent response ends up being
[53:52] the response that came back from the tool
[53:55] hello to you, ABK
[53:57] We send in the second query then
[53:59] or message from the user
[54:01] and the user says thanks
[54:02] bye
[54:04] And again, the top-level agent is going to go ahead
[54:06] oh, actually, no
[54:06] it's still in the control of the greeting
[54:08] subagent
[54:09] So the greeting subagent itself is going to realize
[54:11] okay, this is not something I should use
[54:13] Please transfer this to the farewell subagent
[54:16] So it's aware of the other agents that are available
[54:18] transfers to the farewell subagent
[54:21] and that
[54:22] is the end of that function response
[54:25] Here you can see then a message
[54:27] from the farewell subagent itself
[54:29] It again is going to look at the
[54:30] transcript now that it's been given control of
[54:32] the current conversation
[54:34] The first thing it's going to do is realize
[54:35] okay, the user said goodbye
[54:37] Let me go ahead and call the say
[54:38] goodbye tool to figure out how to respond
[54:40] to them
[54:41] And so here's the function call to say
[54:43] goodbye
[54:44] And of course
[54:44] it takes no arguments as expected
[54:48] But the response to it
[54:49] is the constant that we saw earlier in
[54:51] the tool definition
[54:52] It's going to get a farewell that is
[54:54] goodbye from Cypher
[54:56] And that again is the final response for
[54:58] this event loop
[55:00] And so that is going to be the final agent response
[55:02] goodbye from Cypher
[55:04] Okay, that was a lot to walk through
[55:05] It's worth taking the time to do that
[55:07] for anything else we do in these notebooks
[55:09] You can really see all of the interactions about tool calls
[55:12] agent delegation
[55:13] and also the responses and the changes in
[55:15] state overall
[55:17] So really useful to do
[55:18] We're not going to do that for every notebook
[55:20] but if you'd like to on your own time
[55:21] please do take the time to really understand
[55:23] what's happening behind the scenes
[55:25] because what's happening behind the scenes is going to affect
[55:27] of course
[55:28] how you do the overall
[55:29] agent definitions and also the agent orchestration
[55:33] You're going to take
[55:34] one more step in this multi-agent system
[55:36] We have an execution environment for agents
[55:39] We've got a team of multiple agents that
[55:41] can work together. They can delegate tasks to each other
[55:44] and then each of those agents also has
[55:45] tools that they can use
[55:47] The last important component for all agent systems
[55:50] is having memory
[55:51] Memory is just internal state happening for a
[55:54] particular session across any agents that are involved in that session
[55:57] and of course, the user themselves
[56:00] What is session state really?
[56:01] Session state in Google ADK
[56:03] by default
[56:04] is really just a dictionary that's available
[56:06] that you can update keys within that dictionary
[56:09] And when you update values of those keys
[56:11] Google ADK tracks those changes
[56:13] it tracks deltas to the state basically
[56:16] and updates the overall session state to keep
[56:18] it consistent across all agents
[56:20] whether they're running in parallel or running sequentially
[56:23] because it's an asynchronous system at its heart
[56:26] it manages all the state updates
[56:28] Agents have a few different ways of interacting
[56:30] with state
[56:31] One way
[56:32] the way that I prefer and the primary
[56:33] method for interacting with state
[56:35] is through the tool context
[56:37] So whenever a tool is called
[56:39] there's an extra parameter that's available
[56:41] that is
[56:41] the context within which that tool has been
[56:43] called
[56:44] Given that tool context
[56:46] the tool itself then has access to the
[56:48] current state or the current memory of the agent
[56:50] and it can use that memory
[56:52] for actually making either different decisions
[56:54] creating different output
[56:55] whatever is appropriate for the memory
[56:57] The other way that agents can interact with
[56:59] state is by using an output key
[57:02] So
[57:02] rather than using a tool call for updating
[57:04] some memory or for accessing memory
[57:06] you can take the actual output from an agent
[57:09] that final response
[57:10] and rather than just turning that back as
[57:11] the response from the agent
[57:13] you can save that into state by defining
[57:15] an output key
[57:16] So when you see this final true
[57:19] the message related to the final true
[57:21] here it'll be the text goodbye from Cypher
[57:23] could get used for updating state itself
[57:26] That's very convenient sometimes
[57:28] and we'll do a little bit of that
[57:29] later on in some of these notebooks
[57:31] Okay, in this next step
[57:32] we're going to set up some memory
[57:34] We always have the in-memory session that we're using right now
[57:38] so the memory is saved just
[57:40] within RAM that's not being persisted to a database
[57:42] Of course
[57:43] that's the best thing to do for a production system
[57:45] but for convenience
[57:46] having in-memory state is perfectly fine
[57:49] We're going to update both of our tools
[57:51] to actually take advantage of using that in-memory
[57:53] state
[57:54] So both for say hello and say goodbye
[57:56] we're going to update those tools to take
[57:58] advantage of the tool context to update
[58:00] session state or memory
[58:03] You should do this one at a time
[58:04] and take a careful look at the differences
[58:06] here
[58:07] You'll notice that we're importing tool context from
[58:09] Google ADK
[58:10] Tool context is
[58:12] the class that takes care of keeping track
[58:14] of the session state
[58:15] in addition to other things that
[58:16] is useful for tools to have access to
[58:19] So we're going to update the say hello
[58:21] function to be say hello stateful
[58:24] It still accepts an argument for the user's name
[58:26] but it now has this extra argument called
[58:28] tool context
[58:30] It's the tool context that's going to let
[58:32] us get access
[58:33] to the tool context passed in for the
[58:34] session by the execution environment
[58:38] So in the tool context
[58:39] there's this state dictionary
[58:41] and we're just going to update the username
[58:43] key
[58:44] and
[58:44] the name that was passed into the function
[58:46] we're going to use for updating the session
[58:48] memory or the session state
[58:50] for the username key
[58:51] So this is pretty straightforward
[58:53] username, username
[58:54] Now we have a dictionary
[58:56] that is shared across all agents and across
[58:58] all tools that will have that value
[59:00] that was passed into this function
[59:02] This is a way of sort of
[59:04] keeping track of things by natural
[59:06] use of functions
[59:07] and also then preserving them for later use
[59:10] For debugging purposes, when this tool is called
[59:13] we'll go ahead and print out the update
[59:14] to the session state
[59:16] particularly to the username key
[59:18] And then, of course
[59:18] we'll do what we had done in the
[59:19] previous say hello. We'll send a query off
[59:22] to Neo4j
[59:23] using a query parameter that is the username
[59:26] So let's go ahead and define that
[59:29] Now that you've defined that
[59:30] you can define the same thing for the
[59:31] say goodbye
[59:33] And again, as you're defining this
[59:34] this is just an update to the say
[59:36] goodbye that we had before
[59:37] Now the difference is that this say goodbye
[59:39] even though it doesn't take an argument for
[59:41] anything related to the person
[59:43] it has no custom arguments here
[59:45] it does get this tool context passed in
[59:48] And I should mention that this is something
[59:49] that Google ADK does automatically
[59:51] When it sees a tool
[59:52] with the last argument to the tool is tool context
[59:56] it automatically injects that to the tool call
[59:59] So when say goodbye stateful is called here
[60:01] it's going to get tool context
[60:02] but nothing else
[60:04] But because say hello stateful has set this state
[60:09] the username into the state
[60:12] say goodbye can actually access the username
[60:14] So now we have remembered what the user's
[60:15] name is
[60:16] We can access the state
[60:18] for the state key username
[60:20] and then have a default value in case
[60:22] the user didn't identify themselves
[60:24] But we can get that from the dictionary
[60:26] the username or default
[60:27] assign that to the username
[60:29] and then use that
[60:30] for actually generating a goodbye statement
[60:35] You can then define a new stateful agent
[60:37] for farewell
[60:38] And again
[60:38] that's going to be the same as we
[60:40] had as the previous farewell agent
[60:41] but now it's going to call the say
[60:43] goodbye stateful tool
[60:45] As before
[60:47] you can combine those into a multi-agent system
[60:49] by having a root-level agent
[60:50] a coordinator agent
[60:52] that's going to use both of those as sub-agents
[60:55] and
[60:56] this is exactly the same as the other
[60:58] root agent that we had
[60:59] but now it's just using all the sub-agents
[61:01] that have ultimately down at their core
[61:04] these tools that are stateful-based
[61:07] You now have a multi-agent system
[61:09] that takes advantage of memory
[61:11] You can give it a try
[61:13] You will use our friend
[61:14] the make-agent-caller
[61:15] passing in that new root agent stateful that
[61:18] is the top-level coordinator
[61:19] create a caller for that
[61:21] and to see the change in the session
[61:23] we'll go ahead and get the session directly
[61:25] from the caller. Remember
[61:26] there is a utility function for getting that
[61:28] if you look back at the agent-caller class
[61:31] We'll go ahead and get the session
[61:32] and then based on that session
[61:33] we'll print out the initial state when this is created
[61:36] and we should see that there's nothing in
[61:37] the current state
[61:39] As expected, the initial state is empty
[61:43] You can now define a conversation
[61:45] It's the same conversation that we've been having
[61:47] Say hello, say goodbye, and let's see what happens
[61:51] Actually, I'm going to take out these verbose statements right now
[61:54] and you can decide to keep those in
[61:55] or add them if you'd like
[61:57] Run it either way
[61:58] But just to keep the output to a minimum
[62:00] we'll go ahead and run this without the
[62:01] debugging statements
[62:03] And what's really important here is that we
[62:05] saw that the initial state was empty
[62:07] and we expect that once these calls are done
[62:10] the initial state should turn into a final
[62:11] state
[62:12] Here we're going to get it again
[62:14] and that the final state should actually have
[62:16] the user's name
[62:18] as defined by the call to say hello
[62:24] Awesome
[62:25] So our utility functions printed out
[62:28] this update to the user name here
[62:30] and we also see when we get the
[62:32] session
[62:32] and then get the
[62:33] state from that session
[62:35] that the final state Includes the username ABK
[62:39] Fantastic. Everything's working as expected
[62:44] Now, if you'd like to
[62:44] you can actually run this in an interactive environment
[62:47] even within this notebook
[62:49] You can set up a small helper function
[62:51] that's going to have a loop for getting
[62:53] messages from the user and then just calling our caller
[62:56] passing in that message
[62:57] This will run as long as the user
[62:59] doesn't pass in a message that says exit
[63:03] When you set that up and then run it
[63:04] you'll see a little box appear
[63:06] So when you run the interactive session
[63:08] you can
[63:09] type in a message and just see what
[63:10] happens
[63:13] And I'll start by not revealing my name
[63:15] see what happens
[63:18] Okay, that's kind of funny
[63:19] So the LLM decided that my name is
[63:21] there based on this message
[63:23] That's not really great
[63:25] Let's correct it. Let's say
[63:30] and you can see just by passing in
[63:31] my name is ABK
[63:33] That the tool contacts actually updated with ABK
[63:36] So there's a tool call still to say hello to ABK
[63:39] and because of that
[63:41] the LLM correctly identified my name is ABK
[63:43] save that into memory
[63:45] this is fantastic, if I say goodbye again
[63:48] we should now get a nice message by
[63:49] ABK as before
[63:51] Give this a try
[63:51] interact with it
[63:52] and see what you can come up with
[63:53] And of course, if you'd like to
[63:55] change
[63:55] any of the code and see what the
[63:56] impact is of that
[63:58] Okay
[63:59] you've
[63:59] gotten all the way to the end of
[64:01] lesson three
[64:02] You've created a basic
[64:04] agent that is a single agent that says hello
[64:07] and then you created a multi-agent system
[64:09] with two sub-agents specialized in saying hello or saying goodbye
[64:12] and then a root agent that coordinates their
[64:14] interactions with the user
[64:16] With this in hand
[64:18] you're ready to continue into actually doing agentic
[64:20] knowledge graph construction
[64:22] In this course
[64:23] you learned how to build a multi-agent system
[64:26] that transforms your structured and unstructured data
[64:29] into a knowledge graph
[64:31] You learned how to set up
[64:32] each specialized agent in your system
[64:34] what prompt to use and what tools to define
[64:37] and how to share context among the agents
[64:39] Congratulations on completing this course
[64:42] and I'm looking forward to seeing what you'll
[64:43] build on your own
```

from reporting import determine_summary_branch, scenario_two_read_level


SCENARIO_01_MAIN_SCREEN_COPY = {
    1: {
        "briefing": "We’re six weeks from launch and the pressure is already starting to collect around Jordan. He’s coordinating across too many moving parts, priorities have shifted twice this week, and he’s become the person everyone seems to route through when something changes. Jordan is the clearest visible concern right now, but I’m not convinced the pressure starts and ends with him.",
        "signals": [
            "Jordan is carrying the clearest visible launch pressure.",
            "Sam is quieter than usual around key delivery work.",
            "Priya is catching detail and quality fallout near the edges.",
            "Chloe is helping the group feel steadier than it really is.",
        ],
    },
    2: {
        "briefing": "We’re still technically on track, but the working group feels less settled this week. Jordan’s strain is more obvious now, and some of the work around him is starting to bounce more than it should. It still looks manageable from the outside, but I’m less confident that this is just one person having a hard week.",
        "signals": [
            "Jordan’s pressure is more visible.",
            "Handoffs are getting messier around the launch work.",
            "Sam is absorbing more quietly than he is signalling.",
            "Chloe is smoothing over more than she should need to.",
        ],
    },
    3: {
        "briefing": "This feels like the point where the launch either gets steadier or starts hardening into a local team problem. Jordan is still the most visible pressure point, but Priya is beginning to catch more downstream fallout and Sam looks like he’s carrying more than he’s saying. If this is broader than Jordan, this is probably the week we’d want to act like it.",
        "signals": [
            "Visible strain is no longer isolated to Jordan alone.",
            "Priya is starting to absorb more downstream cleanup.",
            "Sam looks increasingly load-bearing.",
            "The working group still looks recoverable, but less casually so.",
        ],
    },
    4: {
        "briefing": "The launch is close enough now that everyone feels the deadline, but the pressure still isn’t landing evenly. Jordan is still at the center of the visible strain, while the surrounding group looks more brittle than it did two weeks ago. If we are going to steady this properly, it probably needs to happen at the group level rather than through Jordan alone.",
        "signals": [
            "Local trust and coordination are beginning to fray.",
            "Priya is carrying more quality pressure.",
            "Chloe is containing fallout that should be reduced directly.",
            "Hidden strain is becoming more expensive each week.",
        ],
    },
    5: {
        "briefing": "The launch outcome will depend less on whether Jordan looks calmer and more on whether the surrounding group can absorb the final stretch without cracking. We’ve either started to steady the working group around him, or we’re still asking the same few people to quietly carry the cost.",
        "signals": [
            "The working group is either stabilising or quietly overloading.",
            "Visible calm may be misleading now.",
            "Small misses matter more in the final stretch.",
            "Hidden strain is becoming increasingly costly.",
        ],
    },
    6: {
        "briefing": "This is the final launch week. What matters now is not whether the pressure exists, but whether we’ve contained it well enough that the team can deliver without paying an avoidable human cost. Jordan is still the obvious signal, but the real question is how much of the surrounding group we’ve asked to absorb on the way here.",
        "signals": [
            "Execution pressure is high across the working group.",
            "The working group either holds or frays under deadline pressure.",
            "Sam and Priya show the real human cost of the run.",
            "Chloe can no longer hide the pattern on steadiness alone.",
        ],
    },
}


SCENARIO_01_MAIN_SCREEN_ASIDES = {
    2: {
        "well_done": "From where I’m sitting, your first move seems to have steadied the group around Jordan, not just Jordan himself. I’d keep following that wider read.",
        "more_strain_than_needed": "You’ve started to shift the read a little, but it still feels easy for the team to slide back into treating Jordan as the whole issue.",
        "high_strain_count": "Jordan got the support, which mattered, but I’m not seeing the same shift in the people carrying the quieter cost around him.",
        "spiralled": "I’m not seeing much yet that would make me think the working group is getting steadier around Jordan.",
    },
    3: {
        "well_done": "What encourages me is that the pressure looks more containable around Jordan than it did a week ago. Sam is the person I’d keep in view now.",
        "more_strain_than_needed": "This still feels recoverable, but only if we keep widening the frame from here. Sam is becoming harder to ignore.",
        "high_strain_count": "We’re still reacting mostly to Jordan, and I’m not convinced that’s enough anymore. Sam looks more load-bearing than he did at the start.",
        "spiralled": "This is starting to feel like a working-group problem rather than a rough patch around one person, and we haven’t really got ahead of that yet.",
    },
    4: {
        "well_done": "The launch still feels pressured, but not in a way that’s spreading as freely. That’s a good sign this late in the run.",
        "more_strain_than_needed": "The read is better than it was early on, but the team is still carrying some cost that didn’t need to be there.",
        "high_strain_count": "Jordan is still getting most of the attention, but the fragility now seems to sit in the surrounding group more than in him alone.",
        "spiralled": "At this point, I’m mostly watching how much quiet compensation the group is doing just to keep the launch moving.",
    },
    5: {
        "well_done": "The test now is whether the group can absorb the final stretch without quietly handing the cost around. So far, it looks more stable than it might have been.",
        "more_strain_than_needed": "We’ve made the run more recoverable, but some of the human cost is already in the system now.",
        "high_strain_count": "Jordan may look a little steadier, but I’m still more worried about the people helping the launch hold together around him.",
        "spiralled": "We’re late enough now that every missed intervention turns into quiet cost somewhere else in the group.",
    },
    6: {
        "well_done": "The pressure is real, but the bigger question now is whether we’ve contained it well enough that the team isn’t paying for the launch in avoidable ways.",
        "more_strain_than_needed": "We’re in better shape than we might have been, but not without cost. The final read still needs to stay broader than Jordan alone.",
        "high_strain_count": "Jordan is still the obvious signal, but by now the real story is what the rest of the working group has had to carry around him.",
        "spiralled": "By this stage, the launch is telling us very clearly that the issue was never just Jordan. The question is whether we’ve acted on that truth in time.",
    },
}


SCENARIO_01_WEEK_END_COPY = {
    "spiralled": {
        1: {
            "note": "Jordan’s still carrying the most visible pressure, but the week didn’t really settle around him. Sam stayed quiet, Priya ended up picking up more of the loose-end checking, and Chloe was doing more than she should have had to just to keep things from feeling less steady. I’m starting to worry that we’re not really containing this so much as asking the people around Jordan to absorb it.",
        },
        2: {
            "note": "The working group felt more brittle this week. Jordan’s still where the pressure shows up most clearly, but it’s not staying with him. Sam is keeping too much to himself, Priya is catching more of the downstream mess, and Chloe’s having to work too hard just to stop the group from fraying. I’m worried this is starting to harden into a group problem rather than just one visible rough week.",
        },
        3: {
            "note": "This felt like a turning-point week, and we didn’t really interrupt the pattern around Jordan and the people nearest to him. Sam and Priya are both carrying more of the hidden cost now, and Chloe’s compensating for something more structural than just a difficult few days. If we leave it here, the working group itself becomes the real problem, not just Jordan’s visible overload.",
        },
        4: {
            "note": "The working group feels brittle now, and your decision didn’t really reduce that. Priya’s carrying more quality pressure, Sam looks increasingly load-bearing, and Chloe is holding together something that shouldn’t need this much quiet support just to function. At this point, the cost of not stabilising the group is getting harder to hide.",
        },
        5: {
            "note": "At this point, it feels like the launch is being carried more by people absorbing pressure than by the system actually getting steadier. Jordan’s still visibly under strain, but Sam and Priya are the ones paying the quieter price of keeping things alive, and Chloe’s still cushioning the group where she can. I’m worried we’re now getting through on endurance rather than control.",
        },
        6: {
            "note": "We got to the end of the launch in the most fragile way possible. By the final week, your response still wasn’t changing the real pattern carrying the work. Sam and Priya have both been paying the cost of keeping this alive, and Chloe has had to quietly stabilise far more than a healthy system should require. This is what it looks like when a visible problem gets mistaken for the whole story for too long.",
        },
    },
    "high_strain_count": {
        1: {
            "note": "Jordan looked a little more supported by the end of the week, and that did matter. I can see why you made that call, because he was still the clearest pressure point in the room. The difficulty is that the rest of the group didn’t really settle with him. Sam stayed in the background, Priya still picked up the detail fallout, and Chloe was quietly doing more than she should have to just to keep things feeling steady. What I’m watching now is whether the pressure keeps moving outward while Jordan stays at the center of attention.",
        },
        2: {
            "note": "Jordan looked marginally steadier by the end of the week, but that improvement didn’t really spread through the people around him. The support landed where the pressure was easiest to see, which was reasonable, but the handoffs and hidden strain around the launch didn’t improve much. Priya is beginning to carry more of the cost, and Sam still looks less visible than he should for how much this work depends on him. The risk now is that we mistake Jordan feeling slightly better for the group actually being steadier.",
        },
        3: {
            "note": "Jordan was still the clearest pressure point this week, so I can see why your decision fit that surface read. The problem is that by now the launch needed more than visible relief if the group around him was going to steady properly. Sam’s carrying more quiet strain, Priya’s picking up clearer downstream cost, and the pocket around Jordan doesn’t feel any more stable for him being the main focus. We may still get through, but the team is paying more for it than it should.",
        },
        4: {
            "note": "You kept supporting the visible pressure point in a way that made human sense, but the wider working group still didn’t steady with him. That gap matters more now than it did earlier, because the hidden cost is building around the group rather than in Jordan alone. Sam and Priya are both carrying more quiet cost, and Chloe is still compensating for instability that should have been reduced more directly. We may still be on course to launch, but the way we’re getting there is becoming more expensive.",
        },
        5: {
            "note": "Jordan may look somewhat better supported, but the wider working group still feels heavier than it should this late in the run. The visible issue has had attention; the surrounding group still hasn’t really had enough relief. Sam remains more load-bearing than he should, Priya is carrying downstream pressure, and Chloe is still quietly holding the line. We’re getting through, but not cleanly.",
        },
        6: {
            "note": "The launch got through, but the group around Jordan carried more pressure than it needed to on the way there. You were responsive to the visible strain, and that mattered, but the surrounding working group was still left holding too much hidden cost. Sam ended up more load-bearing than he should have been, Priya took on more fallout, and Chloe carried too much quiet stabilising work. We made it, but not at the right level.",
        },
    },
    "more_strain_than_needed": {
        1: {
            "note": "The week ended a little steadier than it might have otherwise, and I think your decision helped with that. It didn’t fully change the shape of the problem yet, but it did stop things from getting more ragged around Jordan and the people closest to him. There’s still some avoidable spread in the group from early on, though. What matters next is whether we keep widening the read, or drift back toward treating Jordan as the whole issue again.",
        },
        2: {
            "note": "The week ended in a better place than it might have, but the launch is still carrying some avoidable spread from earlier choices. Your decision helped contain further slippage and started to move attention toward the broader pattern around Jordan. He’s still the most visible pressure point, but the team around him didn’t worsen as sharply as it could have. Next week matters because this is where correction either becomes a pattern or fades back into symptom management.",
        },
        3: {
            "note": "This felt like a meaningful correction week. Given how much pressure had already built by this point, your decision was a sensible way to start stabilising the launch at the right level. It didn’t erase the earlier spread, but it did stop the working group from hardening as badly as it might have. What matters now is whether you keep acting on the surrounding pattern rather than slipping back toward the most visible symptom.",
        },
        4: {
            "note": "The week ended more steadily than the launch might have done otherwise. Your decision was a sound correction for the position the team was already in, and it helped keep the working group from getting more brittle. That said, some avoidable strain is now built into the group from the earlier weeks. If you keep acting on the broader pattern from here, the launch can still be contained.",
        },
        5: {
            "note": "The working group is in a better place than it might have been, and your recent choices are part of why. Given the strain that had already spread through the group, this week’s decision helped keep the launch recoverable. The downside is that some of the human cost is already baked in by now. The final week really depends on whether you stay with the broader read.",
        },
        6: {
            "note": "The launch finished in a better place than it might have done, because you did improve your read as the pattern became clearer. Your later decisions helped steady the wider group and reduced some further spread. The difficulty is that the correction came after some avoidable strain had already moved through the working group. We got through, but the team still paid more than it ideally should have.",
        },
    },
    "well_done": {
        1: {
            "note": "The launch still has pressure in it, and Jordan is still the clearest visible signal, but the group around him looked steadier by the end of the week. That’s the bit I’d pay attention to. Your decision landed at the level the problem was actually starting to form, not just where it was easiest to see. Sam and Priya weren’t left carrying as much of the quiet cost, and Chloe wasn’t having to hold the whole thing together in the background. If we keep reading it this way, we’ve got a much better chance of steadying the working group early.",
        },
        2: {
            "note": "The launch pressure looked more manageable this week, even though Jordan was still visibly under strain. Your decision helped steady the group around him, and at this point that matters more than simply making the focal person look calmer. Sam stayed less burdened than he might have otherwise, Priya didn’t absorb as much extra fallout, and Chloe was less exposed as the team’s quiet stabiliser. The pressure is still there, but it’s not spreading as freely.",
        },
        3: {
            "note": "This was the point where the launch could have hardened into a local team problem, and it didn’t. Your decision landed at the level the pressure was actually sitting, which made the surrounding group easier to steady. Jordan is still visibly carrying a lot, but Sam and Priya were less exposed because the launch wasn’t left to spread through them unchecked. This is the kind of move that keeps a hard week from becoming the team’s defining pattern.",
        },
        4: {
            "note": "The working group looked steadier this week than the deadline pressure alone would suggest. Your decision reduced fragility in the group rather than just making the visible symptoms more tolerable. Priya ended the week less exposed, Sam wasn’t left carrying as much hidden weight, and Chloe had less compensating to do in the background. The pressure is still real, but it’s moving through the group more cleanly.",
        },
        5: {
            "note": "The working group looks about as steady as it realistically could this late in the run. Your decisions have made it easier for the surrounding group to absorb deadline pressure without quietly passing so much cost between people. Jordan is still the visible signal, but Sam and Priya aren’t carrying the same hidden burden they would have otherwise. This is what good containment looks like.",
        },
        6: {
            "note": "The launch reached the final week under pressure, but not in a way that defined the whole group. You treated Jordan as the signal while steadying the surrounding working group early enough that Sam, Priya, and Chloe weren’t left carrying the launch by quiet accumulation. The pressure was real all the way through, but the group around it became more manageable rather than more brittle. That’s why the launch held together.",
        },
    },
}


SCENARIO_01_ANALYSIS_COPY = {
    "spiralled": {
        "overall": {
            "overall_assessment": "You did not get hold of the real management problem early enough.",
            "management_pattern": "You stayed too close to the visible pressure while the underlying working group was allowed to harden around it.",
            "kpi_review": "You finished materially above the strain level we should be accepting for this launch.",
        },
        1: {
            "what_the_situation_called_for": "The situation called for widening your read beyond the most visible pressure point.",
            "how_your_choice_landed": "You treated the symptom in front of you too narrowly, which left the surrounding working group under-read.",
            "assessment_from_your_starting_point": "From your starting point, the stronger move would have been to test whether the instability around Jordan was already shared by the people closest to him.",
            "what_it_meant_for_your_trajectory": "This didn’t just miss an opportunity; it set up a weaker trajectory.",
        },
        2: {
            "what_the_situation_called_for": "The launch was already asking whether the strain around Jordan was beginning to spread through the people closest to him.",
            "how_your_choice_landed": "You still responded too narrowly to the visible pressure, which left the surrounding group carrying more hidden cost than it should have.",
            "assessment_from_your_starting_point": "A narrow move was no longer enough for the state of the launch.",
            "what_it_meant_for_your_trajectory": "This deepened a weak trajectory rather than interrupting it.",
        },
        3: {
            "what_the_situation_called_for": "The launch needed active stabilisation at the working-group level.",
            "how_your_choice_landed": "You did not make that shift, which meant the launch stopped being primarily about Jordan and became about the group’s fragility.",
            "assessment_from_your_starting_point": "The stronger strategy was not merely to support the visibly strained person, but to steady the group around them.",
            "what_it_meant_for_your_trajectory": "This let the wrong pattern harden.",
        },
        4: {
            "what_the_situation_called_for": "The question was no longer whether Jordan was struggling, but whether you were acting at the level the launch was breaking down.",
            "how_your_choice_landed": "You still weren’t, and the result was a more brittle working group with less room to recover.",
            "assessment_from_your_starting_point": "This was strategically weak for the conditions, even if the move was superficially understandable.",
            "what_it_meant_for_your_trajectory": "The working group became harder to steady and more expensive to carry.",
        },
        5: {
            "what_the_situation_called_for": "The scenario was no longer especially ambiguous: the working group was carrying the real risk.",
            "how_your_choice_landed": "Your management still did not meaningfully act on that truth.",
            "assessment_from_your_starting_point": "Any plausible tactical move from here was being asked to compensate for missed earlier weeks.",
            "what_it_meant_for_your_trajectory": "This confirmed a late-stage consequence of a weak strategic read.",
        },
        6: {
            "what_the_situation_called_for": "The working group needed to have been stabilised earlier, not still relying on quiet compensation.",
            "how_your_choice_landed": "Your response still wasn’t changing the real pattern carrying the launch.",
            "assessment_from_your_starting_point": "By this stage, the damage was not only in the pressure itself, but in how long the surrounding group had been asked to absorb it.",
            "what_it_meant_for_your_trajectory": "The run ended poorly against both the scenario lesson and the KPI target.",
        },
    },
    "high_strain_count": {
        "overall": {
            "overall_assessment": "You showed care and responsiveness, but not enough managerial range.",
            "management_pattern": "You kept responding to Jordan’s visible pressure instead of taking control of the wider pattern forming around him.",
            "kpi_review": "The launch moved, but at a higher human cost than we should be comfortable defending.",
        },
        1: {
            "what_the_situation_called_for": "A humane response to Jordan made sense, but the working group around him also needed a wider read.",
            "how_your_choice_landed": "Supporting the visible pressure point made tactical sense, but it didn’t test whether the launch strain was already sitting more widely in the group.",
            "assessment_from_your_starting_point": "This was a reasonable move if your read was centered on Jordan.",
            "what_it_meant_for_your_trajectory": "It was understandable, but it reinforced a narrow diagnosis.",
        },
        2: {
            "what_the_situation_called_for": "The launch needed more than care for Jordan; it needed a read on whether the surrounding group was still stable.",
            "how_your_choice_landed": "Your choice still made sense if the goal was to help Jordan through a visibly difficult week.",
            "assessment_from_your_starting_point": "The issue is that the scenario had already moved beyond Jordan alone as the main management question.",
            "what_it_meant_for_your_trajectory": "This helped tactically at the surface, but kept the run on a narrow path.",
        },
        3: {
            "what_the_situation_called_for": "The working group needed steadying, not just the focal person.",
            "how_your_choice_landed": "Your decision still made sense if Jordan remained the main object of concern, but by now that was no longer the strongest read.",
            "assessment_from_your_starting_point": "The surrounding working group needed active stabilisation at this point.",
            "what_it_meant_for_your_trajectory": "This preserved the narrow frame even while offering some visible relief.",
        },
        4: {
            "what_the_situation_called_for": "Plausibility was no longer enough; the launch required a broader intervention to reduce fragility around Jordan.",
            "how_your_choice_landed": "Your choice helped the visible symptom more than the delivery system producing it.",
            "assessment_from_your_starting_point": "Reasonable in isolation, insufficient in context.",
            "what_it_meant_for_your_trajectory": "The run stayed survivable, but above the level of strain it needed to carry.",
        },
        5: {
            "what_the_situation_called_for": "Good management had to care about what the rest of the working group was paying to keep the launch moving.",
            "how_your_choice_landed": "You were still protecting the most obvious pressure point while leaving quieter cost in place.",
            "assessment_from_your_starting_point": "This remained tactically understandable, but strategically too narrow.",
            "what_it_meant_for_your_trajectory": "That is why the run stayed above target even as the launch kept moving.",
        },
        6: {
            "what_the_situation_called_for": "The launch needed to have been steadied at the group level, not just through repeated support for Jordan.",
            "how_your_choice_landed": "You prevented a worse outcome for Jordan, but not enough hidden cost in the rest of the working group was reduced.",
            "assessment_from_your_starting_point": "This is the pattern of a humane but too symptom-focused run.",
            "what_it_meant_for_your_trajectory": "The launch survived, but the team paid more than it should have.",
        },
    },
    "more_strain_than_needed": {
        "overall": {
            "overall_assessment": "Your judgment improved as the situation unfolded, but it needed to improve sooner.",
            "management_pattern": "You corrected into the right read after the surrounding working group had already carried avoidable spread.",
            "kpi_review": "You recovered the launch, but only after the team had paid a cost that stronger early management would have reduced.",
        },
        1: {
            "what_the_situation_called_for": "The real question was whether Jordan was the whole problem or the clearest signal of something broader.",
            "how_your_choice_landed": "You didn’t fully establish the strongest read, but you did avoid a worse start.",
            "assessment_from_your_starting_point": "You responded in a way that kept the situation workable without yet changing the shape of the problem.",
            "what_it_meant_for_your_trajectory": "This left room for recovery.",
        },
        2: {
            "what_the_situation_called_for": "The launch was asking for a wider read of the surrounding pocket, not just more attention on Jordan.",
            "how_your_choice_landed": "You were not yet ahead of the problem, but you did begin to act in a way that made later recovery possible.",
            "assessment_from_your_starting_point": "This was not the ideal route, but it was a sound move from where you had already taken the launch.",
            "what_it_meant_for_your_trajectory": "Your management started to improve without yet fully changing the run’s direction.",
        },
        3: {
            "what_the_situation_called_for": "The situation required a shift from symptom management to steadying the working group.",
            "how_your_choice_landed": "This is the week your management improved in a meaningful way.",
            "assessment_from_your_starting_point": "The best strategy would have been to widen your read earlier. However, given the position you had already created, your choice this week was sound.",
            "what_it_meant_for_your_trajectory": "This began to recover the situation rather than simply containing the symptom.",
        },
        4: {
            "what_the_situation_called_for": "The launch needed continued action at the level of the working group rather than a return to the visible focal point alone.",
            "how_your_choice_landed": "Given the amount of spread already in the system, this was a good recovery decision.",
            "assessment_from_your_starting_point": "It did not put you on the strongest route overall, but it did improve the launch from the state you had already created.",
            "what_it_meant_for_your_trajectory": "This strengthened recovery and stopped the run sliding backward.",
        },
        5: {
            "what_the_situation_called_for": "The broader read you had started to develop needed consolidating.",
            "how_your_choice_landed": "This was another week where your management improved relative to the position you had already created.",
            "assessment_from_your_starting_point": "The stronger overall route would still have made this easier earlier. However, from your actual starting point this week, your decision was sound.",
            "what_it_meant_for_your_trajectory": "That deserves recognition because it helped contain further spread.",
        },
        6: {
            "what_the_situation_called_for": "The wider pattern still needed to be held in view all the way to launch, even though earlier costs could no longer be erased.",
            "how_your_choice_landed": "Your later choices were often sound given the state of the launch by this point, and they helped contain further spread.",
            "assessment_from_your_starting_point": "You did not begin with the strongest read, but you did not stay trapped in it either.",
            "what_it_meant_for_your_trajectory": "The run finished as a recovery story, though one that still carried avoidable cost from earlier weeks.",
        },
    },
    "well_done": {
        "overall": {
            "overall_assessment": "You read the management problem at the right level early enough to matter.",
            "management_pattern": "You treated Jordan as the signal and then took control of the surrounding delivery pocket before it hardened into a wider failure.",
            "kpi_review": "You kept the launch close to the standard we should expect under pressure, which is exactly what good management needs to do here.",
        },
        1: {
            "what_the_situation_called_for": "The situation called for treating Jordan as the clearest signal, not the whole story.",
            "how_your_choice_landed": "You acted early enough at the surrounding level that the launch pressure had less room to harden into a local working-group problem.",
            "assessment_from_your_starting_point": "That gave you the strongest opening position of any route.",
            "what_it_meant_for_your_trajectory": "This was the right read for the conditions.",
        },
        2: {
            "what_the_situation_called_for": "The wider working group needed reinforcing, not a doubling down on Jordan alone.",
            "how_your_choice_landed": "You continued to act at the level the pressure was actually forming, which stopped the working group becoming more brittle than the headline symptoms suggested.",
            "assessment_from_your_starting_point": "This is what early pattern recognition looks like in practice.",
            "what_it_meant_for_your_trajectory": "You were strengthening trajectory, not just reacting to symptoms.",
        },
        3: {
            "what_the_situation_called_for": "The stronger move was to keep the run contained rather than let it turn reactive.",
            "how_your_choice_landed": "You recognized that the launch pressure was now a working-group problem and intervened accordingly.",
            "assessment_from_your_starting_point": "That protected the quieter people around Jordan and reduced the chance of the group hardening into crisis.",
            "what_it_meant_for_your_trajectory": "This was strong strategic and tactical management.",
        },
        4: {
            "what_the_situation_called_for": "The intervention needed to stay at the level of the working group, not collapse back toward the visible symptom.",
            "how_your_choice_landed": "You did that.",
            "assessment_from_your_starting_point": "The result was not the removal of pressure, but the prevention of avoidable spread.",
            "what_it_meant_for_your_trajectory": "This is what good mid-scenario management looks like: not dramatic, but pattern-aware and steadying.",
        },
        5: {
            "what_the_situation_called_for": "Stronger runs are easier to spot because the surrounding group is not carrying as much hidden cost.",
            "how_your_choice_landed": "Your earlier and ongoing working-group decisions continued to pay off here.",
            "assessment_from_your_starting_point": "This was not about eliminating pressure, but about stopping it from becoming quietly cumulative.",
            "what_it_meant_for_your_trajectory": "That is why the launch remained controlled rather than merely survived.",
        },
        6: {
            "what_the_situation_called_for": "The launch still needed to be under pressure, but no longer carried by avoidable hidden strain in the working group.",
            "how_your_choice_landed": "You maintained the broader read all the way through the run.",
            "assessment_from_your_starting_point": "That let you reduce spread, protect the quieter carriers, and keep the launch closer to target.",
            "what_it_meant_for_your_trajectory": "This is the pattern the scenario is designed to teach.",
        },
    },
}


SCENARIO_01_END_SCREEN_COPY = {
    "spiralled": {
        "outcome": "Management Review: The launch failed.",
        "management_pattern": "You never really got hold of the pattern driving the launch.",
        "what_you_did_well": "You were not ignoring pressure altogether, but your response stayed too close to what was easiest to see.",
        "what_limited_the_result": "Tension across the core group built faster than you contained it, and the launch moved out of a workable state.",
        "kpi_review": "Core-group strain finished far beyond the level we should ever accept. This was not a rougher version of success. The launch failed.",
        "development_point": "The step you missed was widening your read beyond Jordan before the group around him became the real problem.",
    },
    "high_strain_count": {
        "outcome": "Management Review: You got the launch through, but just about.",
        "management_pattern": "You responded responsibly to visible strain, but your management stayed too close to the loudest symptom.",
        "what_you_did_well": "You did not look away from the human pressure in front of you, which mattered.",
        "what_limited_the_result": "The launch got through because the wider working group carried more strain than it should have had to, and that is where your read stayed too narrow.",
        "kpi_review": "You kept the launch moving, but you finished above target and above the standard we should be aiming for.",
        "development_point": "The stronger managerial move would have been to treat Jordan as the signal and take control of the working group around him sooner.",
    },
    "more_strain_than_needed": {
        "outcome": "Management Review: You recovered the situation, but later than we would want.",
        "management_pattern": "You improved your read and started managing the wider working group, but only after the situation had already become more expensive than it needed to be.",
        "what_you_did_well": "You did correct course rather than staying trapped in your first read, and that mattered to the final outcome.",
        "what_limited_the_result": "By the time you widened the frame, some avoidable spread had already moved through the group and could no longer be fully undone.",
        "kpi_review": "You came closer to target, but the team still ended up carrying strain that stronger early management would have reduced.",
        "development_point": "The next step is speed of diagnosis. You need to get to that broader read before the working group has to recover from it.",
    },
    "well_done": {
        "outcome": "Management Review: This was a strong piece of management under pressure.",
        "management_pattern": "You identified the local working-group pattern early and managed the launch at the level it actually needed.",
        "what_you_did_well": "You treated the visible overload as a signal, then stabilised the surrounding system before it became the team’s defining problem.",
        "what_limited_the_result": "The pressure itself was real, but you stopped it turning into avoidable spread through the group.",
        "kpi_review": "You met, or came very close to, the standard we should expect for this situation.",
        "development_point": "This is the level of judgment we want to see from a manager in a launch like this. The pressure is still there, but you controlled it properly.",
    },
}


SCENARIO_01_TACTICAL_OVERLAY_BY_WEEK_AND_QUALITY = {
    1: {
        "no_action": {
            "week_end": "We needed a clearer intervention than that at the very start of the run.",
            "analysis": "From your starting point, the bigger gap here was that you did not really intervene on the pattern as it was forming.",
        },
        "weak": {
            "week_end": "This was too narrow for the state the launch was already in.",
            "analysis": "From the position you were in, this was a weak response because it stayed too close to the visible symptom.",
        },
        "acceptable": {
            "week_end": "This helped a little, even if it didn’t yet change the wider pattern.",
            "analysis": "Given your starting point, this was a defensible move, but it did not widen your read enough.",
        },
        "strong": {
            "week_end": "This was a strong move for the conditions at the start of the run.",
            "analysis": "From your starting point, this was a strong decision because it acted on the broader risk early.",
        },
    },
    2: {
        "no_action": {
            "week_end": "The launch needed more active intervention than it got.",
            "analysis": "The bigger problem was not just the quality of the move, but that the group was still being left to carry the pattern largely on its own.",
        },
        "weak": {
            "week_end": "This didn’t do enough to steady the group around the visible pressure.",
            "analysis": "This was too limited for the shape the problem was taking.",
        },
        "acceptable": {
            "week_end": "This made tactical sense, but it still left the wider working group under-addressed.",
            "analysis": "Given where the launch had moved by this point, this was understandable but still partial.",
        },
        "strong": {
            "week_end": "This was a strong way to steady the launch before the pattern hardened further.",
            "analysis": "This was a strong decision because it acted before the working group became much harder to recover.",
        },
    },
    3: {
        "no_action": {
            "week_end": "We needed a more active attempt to steady the working group than that.",
            "analysis": "The bigger issue here was that you did not meaningfully intervene at the level the problem had reached.",
        },
        "weak": {
            "week_end": "This came in below what the launch needed at the point it was beginning to harden.",
            "analysis": "This was too weak for the conditions.",
        },
        "acceptable": {
            "week_end": "This was a sensible move from a weaker position, even if it wasn’t the strongest route overall.",
            "analysis": "The best strategy would have been to shift earlier. However, given your starting point this week, this was sound.",
        },
        "strong": {
            "week_end": "This was the right level of intervention for the turning point of the launch.",
            "analysis": "This was a strong decision because it matched the real level of the problem.",
        },
    },
    4: {
        "no_action": {
            "week_end": "The launch needed a firmer stabilising move than that.",
            "analysis": "The underlying problem was that the working group was still not being actively steadied.",
        },
        "weak": {
            "week_end": "This didn’t reduce the fragility that had built up around the working group.",
            "analysis": "This was weaker than the situation required and did little to change the run’s shape.",
        },
        "acceptable": {
            "week_end": "This was a reasonable correction from where the team had already reached.",
            "analysis": "Given the strain already in the system, this was a sound corrective move, even though it came after avoidable spread.",
        },
        "strong": {
            "week_end": "This was a strong stabilising move at a point when the group could easily have become much more brittle.",
            "analysis": "This was a strong decision because it reduced spread rather than merely tolerating it.",
        },
    },
    5: {
        "no_action": {
            "week_end": "This late in the run, leaving the group to absorb the pressure was always going to be costly.",
            "analysis": "The main issue was that the group was still being asked to carry too much without enough intervention.",
        },
        "weak": {
            "week_end": "This left too much quiet cost sitting in the group this late in the run.",
            "analysis": "This was too weak because it asked the team to keep carrying pressure rather than reducing it.",
        },
        "acceptable": {
            "week_end": "This helped contain the situation from where it was, even if it could no longer undo earlier cost.",
            "analysis": "Given your starting point this week, this was a sensible containment move.",
        },
        "strong": {
            "week_end": "This was a strong way to keep the final stretch from becoming more expensive than it already was.",
            "analysis": "Late in the run, this was strong because it reduced further spread rather than letting the group harden again.",
        },
    },
    6: {
        "no_action": {
            "week_end": "There was too much already sitting in the group to leave it there.",
            "analysis": "The larger gap was that the team was still carrying too much of the cost without enough intervention.",
        },
        "weak": {
            "week_end": "This was too little, too late to change the final shape of the launch.",
            "analysis": "This was a weak response because it did not alter the real cost the group was carrying.",
        },
        "acceptable": {
            "week_end": "This was a fair move from the position you had reached, even if the larger result was already constrained.",
            "analysis": "Given the final-week starting point, this was sound, though it could not fully overcome what had built up earlier.",
        },
        "strong": {
            "week_end": "This was a strong final-week decision and helped the launch land better than it otherwise would have.",
            "analysis": "This was strong because it made the best of the situation you had created and reduced avoidable extra cost.",
        },
    },
}


SCENARIO_01_ROUTE_BASELINE = {
    "well_done": {
        1: "individual_on_jordan + coordination_on_jordan",
        2: "individual_on_jordan + coordination_on_jordan",
        3: "coordination_on_jordan + individual_on_sam",
        4: "coordination_on_jordan + individual_on_sam",
        5: "individual_or_coordination_on_jordan",
        6: "individual_or_coordination_on_jordan + individual_on_sam",
    },
    "more_strain_than_needed": {
        1: "individual_or_coordination_on_jordan_only",
        2: "individual_or_coordination_on_jordan_only",
        3: "individual_or_coordination_on_jordan + individual_on_sam",
        4: "individual_or_coordination_on_jordan + individual_on_sam",
        5: "any_action_on_jordan_or_sam",
        6: "any_action_on_jordan_or_sam",
    },
    "high_strain_count": {
        1: "individual_on_jordan",
        2: "individual_on_jordan",
        3: "individual_or_coordination_on_jordan",
        4: "individual_or_coordination_on_jordan",
        5: "individual_or_coordination_on_jordan",
        6: "individual_or_coordination_on_jordan",
    },
}


SCENARIO_02_MAIN_SCREEN_COPY = {
    1: {
        "briefing": "We’re six weeks from an important client demo, and the team already feels less settled than it should this early. Riley’s work has been coming in unevenly, a few details have needed rework, and people are starting to adjust around him rather than through a cleaner plan. We’re still getting the week over the line, which is the reassuring part. The less reassuring part is that some of the chasing, clarifying, and cleanup seems to keep landing elsewhere. Riley is still the clearest concern from where I’m sitting, but I’m not convinced it starts and ends with him.",
        "signals": [
            "Riley is the clearest visible source of friction.",
            "The demo work is still moving, but not especially cleanly.",
            "Riley has recently come back from extended absence, which makes him easy to focus on.",
            "Maya looks steady, though some of the background fixing seems to be landing with her.",
            "The week may be holding together more by extra effort than it first appears.",
        ],
    },
    2: {
        "briefing": "The demo is still on track enough that nobody is openly panicking, but the same pattern has kept repeating. Riley is still the loudest signal in the room, and that makes it easy to keep reading the situation through him. At the same time, the rest of the team seems to be working harder than it should just to stop small problems from spilling further. I’m still watching Riley first, but I’m starting to wonder who else is paying for the week feeling this manageable.",
        "signals": [
            "Riley still looks like the clearest issue from the outside.",
            "Handoffs are staying messier than they should for this point in the run.",
            "Maya seems to be picking up more than she is saying.",
            "The visible friction is easier to talk about than the work happening around it.",
            "The team is still getting through, but not in a very settled way.",
        ],
    },
    3: {
        "briefing": "This doesn’t feel like a rough patch anymore. Riley still attracts the eye first, but the week keeps landing in a way that makes me think someone else is doing a lot of the smoothing in the background. If that’s right, this is probably the week we need to get clearer about it. Riley may still be the most obvious problem, but I’m less sure he’s the whole one.",
        "signals": [
            "Visible strain is repeating rather than resolving.",
            "The same repair work keeps showing up each week.",
            "Maya is easier to rely on than she is to notice.",
            "The team still looks functional from the outside.",
        ],
    },
    4: {
        "briefing": "The demo is close enough now that I’m less interested in any one difficult moment and more interested in how the week is being held together. Riley is still the easiest person to focus on, and I can understand why. The trouble is that the work around him still doesn’t feel properly settled. If Maya is still the one quietly catching and carrying, we may be looking stronger than we are.",
        "signals": [
            "Riley is still taking most of the attention.",
            "The wider team does not look as steady as it should this late.",
            "Maya may be carrying more than the room can easily see.",
            "If this is going to settle, it probably needs a broader response now.",
        ],
    },
    5: {
        "briefing": "The final stretch is here. In places the team may even look a little calmer, but I’m not sure that means things are actually steadier. At this point, what I care about is what it’s costing to keep the demo moving. If Riley looks a bit more manageable now, that may be because someone else is carrying more of the week for him.",
        "signals": [
            "Visible calm may be misleading at this stage.",
            "Riley is still a live issue, but not the only one.",
            "Maya either has more support, or has become too necessary.",
            "The week is either settling, or being quietly carried.",
        ],
    },
    6: {
        "briefing": "This is the final demo week. The pressure is what it is now. What matters is whether the team is carrying it in a workable way, or whether too much of it is still sitting with the same people behind the scenes. Riley is still the obvious signal, but by now the bigger question is what the rest of the team has had to absorb on the way here.",
        "signals": [
            "The demo will show whether the team has really settled.",
            "Riley’s visible behaviour still matters, but not on its own.",
            "Maya gives a better read on the hidden cost than the surface workflow does.",
            "The ending will tell us whether the pressure was managed or just carried.",
        ],
    },
}


SCENARIO_02_MAIN_SCREEN_ASIDES = {
    2: {
        "early_realignment": "Your first move suggests you’re treating Riley as the signal rather than the whole story. The next question is whether that wider read starts changing who has to carry the week.",
        "late_widening": "You’ve kept the situation workable, but it still looks easy for the room to stay fixed on Riley. The decision now is whether you widen the read before the team normalises coping around him.",
        "surface_containment": "Riley got attention, which mattered, but I’m not yet seeing the same clarity about who is carrying the quieter cost around him. That’s the part I’d want to test now.",
        "reactive_escalation": "The visible issue still seems to be running the room. I’m not seeing much yet that suggests the underlying pattern is getting easier to carry, which usually means somebody else is still paying for it.",
    },
    3: {
        "early_realignment": "What looks promising is that the work around Riley seems more discussable than it did at the start. Maya is the person I’d keep in clear view now, not because she looks worst, but because she may be carrying what the rest of the room is not naming.",
        "late_widening": "This still feels recoverable, but only if you keep widening the frame. Maya is becoming harder to ignore as part of the pattern, and Riley is becoming easier to misread if you do not.",
        "surface_containment": "Riley is still getting most of the attention, and I’m not convinced that’s enough anymore. The team looks like it is coping around him, which usually means the apparent stability is being bought somewhere else.",
        "reactive_escalation": "This is beginning to feel like a team-fragility problem rather than a single difficult employee problem, and we haven’t got ahead of that yet. The longer that continues, the more likely disengagement gets mistaken for indifference and carrying gets mistaken for health.",
    },
    4: {
        "early_realignment": "The pressure is still real, but it doesn’t look like the whole system is being held together by private effort in the same way. That is usually the difference between strain that is being managed and strain that is merely being hidden.",
        "late_widening": "The read is better than it was early on, but the team is still carrying some avoidable cost from the delay. The question now is whether you keep acting on the pattern, or drift back toward the visible symptom.",
        "surface_containment": "Riley may be slightly steadier, but the more important question now is what the rest of the team is still privately absorbing. If you cannot answer that clearly, the system is probably still too fragile.",
        "reactive_escalation": "At this point, I’m mostly watching how much quiet compensation the team is doing just to keep the demo moving. That usually means the work is looking stronger than it is.",
    },
    5: {
        "early_realignment": "The test now is whether the team can absorb the final stretch without turning quiet coping into the main delivery strategy. So far, it looks more contained than it might have been, which suggests the hidden load is no longer doing all the stabilising work.",
        "late_widening": "The team is in a better place than it could have been, but some of the human cost is already in the system now. What matters most is not sliding back into symptom management now that Riley may look calmer in moments.",
        "surface_containment": "The visible issue has had attention. I’m still more worried about the hidden load keeping the demo alive around it. If that is still true this late, the team is surviving rather than stabilising.",
        "reactive_escalation": "We’re late enough now that every missed intervention turns into private cost somewhere else in the team. At this stage, surface calm is often just redistributed strain.",
    },
    6: {
        "early_realignment": "The final question is whether the team is under pressure in a manageable way, or in a way that still depends on someone quietly carrying too much. So far, this looks more like containment than concealment.",
        "late_widening": "You’ve made the run more recoverable, but not without cost. The final read still needs to stay broader than Riley alone, because the ending will otherwise look kinder than it actually was for the team.",
        "surface_containment": "Riley is still the obvious signal, but by now the real story is what the rest of the team has had to absorb around him. That is the part of the run the review will need to tell honestly.",
        "reactive_escalation": "By this stage, the demo is telling us very clearly that the issue was never only Riley. The question is whether we acted on that in time, or merely kept responding to what was loudest.",
    },
}


SCENARIO_02_WEEK_END_COPY = {
    "reactive_escalation": {
        1: {"note": "Riley was still the clearest source of friction by the end of the week, which made the situation look simpler than it was. Maya ended up doing more of the clarifying and tidying than anyone properly named, and a few of the smaller misses still needed catching around the edges. The week got over the line, but not in a way that felt properly settled. What worries me is that we may already be asking the team around Riley to absorb too much of the cost."},
        2: {"note": "Riley still looked like the problem by the end of the week, and I can see why the attention stays there. The difficulty is that the work around him still doesn’t feel much cleaner. Maya is doing more of the chasing and smoothing than I’d be comfortable with this early, and the rest of the team is adjusting around that rather than really settling. That usually means the situation is getting more fragile than it looks."},
        3: {"note": "Riley was still where most of the attention went this week, but the rest of the work did not really steady around him. Maya carried more of the background repair again, and the team still needed too much quiet fixing just to keep the demo moving. From the outside, it probably still looked manageable. From the inside, it feels like the same cost is just moving elsewhere."},
        4: {"note": "Riley is still drawing most of the practical concern, which makes sense on the surface. Maya is still carrying too much of what keeps the week moving, and other people are adjusting around that more than they should have to. The team got through again, but more by quiet compensation than by things actually getting cleaner. At this point, I’d say the situation looks stronger than it really is."},
        5: {"note": "Riley remained the visible issue in the final stretch, but that’s not the only thing I’d be looking at now. Maya and the rest of the team are still paying too much of the quieter price of keeping things workable, and the week still feels more effortful than it should this late in the run. It may look calmer from the outside. I don’t think the team actually feels calmer."},
        6: {"note": "We got to the end with Riley still carrying most of the visible strain, and that kept pulling the read back toward him. Maya was still holding too much underneath that, and the rest of the team spent too much of the run quietly making the work hold together. The demo may have landed, but the way it landed was more fragile than it needed to be. That’s what happens when the visible problem keeps standing in for the whole one."},
    },
    "surface_containment": {
        1: {"note": "Riley looked a little more supported by the end of the week, and that did matter. The difficulty is that the rest of the team did not really settle with him. Maya still carried more of the clarifying and repair work than you would know from the surface read, and a few of the smaller issues still had to be caught elsewhere. So the decision helped Riley more than it helped the week around him."},
        2: {"note": "Riley was still getting most of the support, which was understandable. The wider pattern still didn’t look much cleaner, though. Maya seems to be picking up more of the work that keeps things from slipping, and the rest of the team is still adjusting around that rather than benefiting from a cleaner week. We’re getting through, but not in a very settled way."},
        3: {"note": "Your calls still made sense if Riley was the main issue, and I can see why they would. By the end of this week, I’m less convinced that he is. Maya is becoming more load-bearing, the week still needs too much background repair, and the team is paying more than it should just to keep the demo looking stable. That’s where the narrower read starts to get expensive."},
        4: {"note": "You kept supporting the visible problem in a way that made human sense, but the wider team still did not steady with it. Riley may have felt less exposed in moments, but Maya was still carrying too much of what made that possible and the rest of the work still looked more effortful than clean. That gap matters more now than it did earlier."},
        5: {"note": "Riley may have looked better supported in the final stretch, but the week still felt heavier than it should this late in the run. Maya and the wider team are still carrying too much of the quieter cost around him, and the work does not look properly settled for how close we are to the demo. We’re surviving the week more than steadying it."},
        6: {"note": "The demo got through, and the support you gave Riley was part of that. The problem is that Maya and the wider team still carried more quiet cost than they needed to on the way there. The week never really settled underneath the visible strain. So the result is humane in one sense, but still more expensive than it should have been."},
    },
    "late_widening": {
        1: {"note": "The week ended more workable than it might have otherwise, even if the shape of the problem did not change fully yet. Riley was still the clearest signal, but you didn’t lock the whole read around him. Maya was not left carrying quite as much of the invisible catch-up as she might have been, and that matters because the run still feels recoverable from here."},
        2: {"note": "The team ended the week in a better place than it might have, but some of the early spread is still there. Riley is still the obvious issue, while Maya is still doing more of the quiet holding than I’d like. The difference is that the situation now feels more readable than it did at the start. That’s usually the first sign that recovery is possible."},
        3: {"note": "This felt like a meaningful correction week. Riley was still the visible pressure point, but you started to act on the idea that he was not the whole story. Maya was not left carrying the same unchecked load, and the team did not harden in the same way it might have done. It doesn’t erase the earlier cost, but it does change the direction of the run."},
        4: {"note": "The team ended the week steadier than it could have done otherwise. Riley is still not easy, and Maya is still carrying some cost from the earlier weeks, but your management is now landing closer to where the real pressure has been sitting. That’s an improvement, even if it comes later than you’d ideally want."},
        5: {"note": "The run is in a better place than it might have been because you did widen your read. Riley is not the only thing holding the week together in the same way, and Maya is not carrying quite as much of the hidden burden she was. The downside is that some of the cost is already built in by now. This feels like recovery, not a clean early containment."},
        6: {"note": "The demo finished in a more recoverable place because your management improved as the situation became clearer. Riley remained the obvious signal, but Maya and the wider team were not left holding the full cost in the same way they might have been. The difficulty is that the shift came after some avoidable strain had already moved through the team. That’s why this ending feels better, but not clean."},
    },
    "early_realignment": {
        1: {"note": "The week still had pressure in it, and Riley was still the clearest visible signal, but the team around him looked steadier by the end of it. Maya was not left carrying the same amount of quiet catch-up, and the rest of the work did not feel as ragged around Riley as it might have. That’s the bit I’d pay attention to. Your decision landed where the problem was starting to form, not just where it was easiest to see."},
        2: {"note": "The demo pressure looked more manageable this week, even though Riley was still visibly strained. Maya was not left carrying the same hidden load, and the team did not have to work as hard in the background just to keep moving. The work around Riley looked cleaner too, not just calmer. That’s a much better sign than Riley simply appearing easier."},
        3: {"note": "This was the week where weaker runs usually start to harden, and yours didn’t. Riley was still the signal, but the week around him looked more contained. Maya was not left carrying the same quiet cost, and the rest of the team did not have to keep compensating in the same way. That’s usually how you can tell the situation is genuinely settling."},
        4: {"note": "The team looked steadier this week than the deadline pressure alone would suggest. Riley was still not easy, but the work around him was less dependent on someone quietly rescuing it, and Maya was not having to carry the same hidden burden to keep the week together. That’s why this feels more contained than merely calmer."},
        5: {"note": "The final stretch looks about as contained as it realistically could this late in the run. Riley is still the visible signal, but Maya and the wider team are not carrying the same hidden burden they would have otherwise. The week still has pressure in it, but it no longer looks like it is being held together by the same quiet compensation. That’s why it feels manageable rather than just better hidden."},
        6: {"note": "The demo reached the final week under pressure, but not in a way that defined the whole team. Riley was still the obvious signal, but Maya and the wider team were not left carrying the same private cost underneath him. The work around him looked more manageable rather than more brittle. That’s what a strong run looks like here: not easy, but properly contained."},
    },
}


SCENARIO_02_TACTICAL_OVERLAY_BY_WEEK_AND_QUALITY = {
    1: {
        "no_action": {"week_end": "At the very start of this run, leaving the visible issue to explain itself was always going to strengthen the wrong read."},
        "weak": {"week_end": "This was too close to the visible symptom for the conditions that were already forming."},
        "acceptable": {"week_end": "This was defensible, but it still left the quieter carrying pattern largely untested."},
        "strong": {"week_end": "This was a strong opening move because it treated the visible issue as a clue, not the whole diagnosis."},
    },
    2: {
        "no_action": {"week_end": "The team needed more than observation if the pattern was going to stay recoverable."},
        "weak": {"week_end": "This helped too little with the hidden pattern that was starting to repeat."},
        "acceptable": {"week_end": "This made sense tactically, but it still left too much ambiguity about where the cost was really landing."},
        "strong": {"week_end": "This was a strong move because it widened the read before private coping became even more normalised."},
    },
    3: {
        "no_action": {"week_end": "Week 3 was the point where the scenario needed a clearer attempt to realign the pattern than it got."},
        "weak": {"week_end": "This was below what the situation now needed if the team was going to stop coping around the strain."},
        "acceptable": {"week_end": "This was a sound move from a weaker position, even if it was not the strongest route overall."},
        "strong": {"week_end": "This was the right level of intervention for the point where fragility could still be interrupted."},
    },
    4: {
        "no_action": {"week_end": "Leaving the team to carry the pattern on its own was always going to be expensive."},
        "weak": {"week_end": "This did not reduce the fragility that had now built up around the demo."},
        "acceptable": {"week_end": "This was a reasonable correction from the position the run had already reached."},
        "strong": {"week_end": "This was a strong stabilising move because it reduced hidden cost rather than merely tolerating it."},
    },
    5: {
        "no_action": {"week_end": "This late in the run, leaving the team to absorb the pattern privately was always going to be costly."},
        "weak": {"week_end": "This left too much of the final stretch resting on quiet coping."},
        "acceptable": {"week_end": "This helped contain the run from where it was, even if it could no longer undo earlier cost."},
        "strong": {"week_end": "This was a strong final-stretch move because it reduced further spread instead of letting the team quietly absorb it."},
    },
    6: {
        "no_action": {"week_end": "There was already too much sitting in the team to leave it there."},
        "weak": {"week_end": "This was too little, too late to alter the underlying shape of the run."},
        "acceptable": {"week_end": "This was fair from the position you had reached, even if the larger result was already constrained."},
        "strong": {"week_end": "This was a strong final-week decision and helped the demo land more honestly than it otherwise would have."},
    },
}


SCENARIO_02_ANALYSIS_COPY = {
    "reactive_escalation": {
        "overall": {
            "overall_assessment": "You did not get hold of the real management problem early enough.",
            "management_pattern": "You stayed too close to Riley’s visible strain while the hidden carrying around the demo kept hardening into team fragility.",
            "kpi_review": "The demo moved at a higher human cost than we should be comfortable defending.",
        },
        1: {"what_the_situation_called_for": "The situation called for taking Riley seriously without assuming he was the whole problem.", "how_your_choice_landed": "You responded too closely to the visible issue, which left the hidden carrying pattern under-read.", "assessment_from_your_starting_point": "The stronger move was to test whether the team was already compensating around Riley.", "what_it_meant_for_your_trajectory": "This set up a weak trajectory."},
        2: {"what_the_situation_called_for": "The team needed more than symptom management.", "how_your_choice_landed": "You still responded too narrowly to the visible issue, which left the broader fragility pattern in place.", "assessment_from_your_starting_point": "At this stage, a surface read was no longer enough.", "what_it_meant_for_your_trajectory": "This deepened a weak run rather than interrupting it."},
        3: {"what_the_situation_called_for": "The demo needed active realignment at team level.", "how_your_choice_landed": "You did not make that shift, so the team kept paying in hidden carrying.", "assessment_from_your_starting_point": "The stronger strategy was not merely to steady Riley, but to act on the fragility around him.", "what_it_meant_for_your_trajectory": "This let the wrong pattern harden."},
        4: {"what_the_situation_called_for": "The question was no longer whether Riley was struggling, but whether the team was still being held together by private coping.", "how_your_choice_landed": "Your management still did not act at that level.", "assessment_from_your_starting_point": "Strategically weak for the conditions, even if superficially understandable.", "what_it_meant_for_your_trajectory": "The demo became harder to carry cleanly."},
        5: {"what_the_situation_called_for": "The scenario was no longer especially ambiguous: the real risk sat in how the team was carrying the work.", "how_your_choice_landed": "Your response still did not meaningfully interrupt that pattern.", "assessment_from_your_starting_point": "Any tactical move here was already compensating for missed earlier weeks.", "what_it_meant_for_your_trajectory": "This confirmed a late-stage consequence of a weak strategic read."},
        6: {"what_the_situation_called_for": "The team needed to have been realigned earlier, not still relying on quiet compensation.", "how_your_choice_landed": "Your response still was not changing the real pattern carrying the demo.", "assessment_from_your_starting_point": "By this stage, the damage sat not only in the pressure itself, but in how long the team had been asked to absorb it privately.", "what_it_meant_for_your_trajectory": "The run ended poorly against both the scenario lesson and the KPI target."},
    },
    "surface_containment": {
        "overall": {
            "overall_assessment": "You showed care and responsiveness, but not enough managerial range.",
            "management_pattern": "You kept responding to Riley’s visible strain instead of taking control of the hidden carrying pattern forming around him.",
            "kpi_review": "The demo moved, but at a higher human cost than we should want to defend.",
        },
        1: {"what_the_situation_called_for": "A humane response to Riley made sense, but the situation also invited a wider read of the team around him.", "how_your_choice_landed": "Supporting the visible issue made tactical sense, but it did not test whether the strain was already sitting more widely in the team.", "assessment_from_your_starting_point": "This was a reasonable move if your read stayed centered on Riley.", "what_it_meant_for_your_trajectory": "It reinforced a narrow diagnosis."},
        2: {"what_the_situation_called_for": "The demo needed more than care for Riley; it needed a read on whether the team around him was still stable.", "how_your_choice_landed": "Your choice still made sense if the goal was to help Riley through a visibly difficult week.", "assessment_from_your_starting_point": "The issue is that the scenario had already moved beyond Riley alone as the main management question.", "what_it_meant_for_your_trajectory": "This helped tactically at the surface, but kept the run narrow."},
        3: {"what_the_situation_called_for": "The team pattern needed stabilising, not just the focal person.", "how_your_choice_landed": "Your decision still made sense if Riley remained the main object of concern, but by now that was no longer the strongest read.", "assessment_from_your_starting_point": "The demo needed active realignment at this point.", "what_it_meant_for_your_trajectory": "This preserved the narrow frame even while offering some visible relief."},
        4: {"what_the_situation_called_for": "Plausibility was no longer enough; the run required a broader intervention to reduce fragility around the visible problem.", "how_your_choice_landed": "Your choice helped the visible symptom more than the system producing it.", "assessment_from_your_starting_point": "Reasonable in isolation, insufficient in context.", "what_it_meant_for_your_trajectory": "The run stayed survivable, but above the level of strain it needed to carry."},
        5: {"what_the_situation_called_for": "Good management had to care about what the rest of the team was paying to keep the demo moving.", "how_your_choice_landed": "You were still protecting the most obvious pressure point while leaving quieter cost in place.", "assessment_from_your_starting_point": "Tactically understandable, strategically too narrow.", "what_it_meant_for_your_trajectory": "That is why the run stayed above target even as the demo kept moving."},
        6: {"what_the_situation_called_for": "The demo needed to have been steadied at team level, not just through repeated support for Riley.", "how_your_choice_landed": "You prevented a worse outcome for Riley, but not enough hidden cost in the wider team was reduced.", "assessment_from_your_starting_point": "This is the pattern of a humane but too symptom-focused run.", "what_it_meant_for_your_trajectory": "The demo survived, but the team paid more than it should have."},
    },
    "late_widening": {
        "overall": {
            "overall_assessment": "Your judgment improved as the situation unfolded, but it needed to improve sooner.",
            "management_pattern": "You corrected into the right read after the team had already carried avoidable hidden cost.",
            "kpi_review": "You recovered the demo, but only after the team had paid a cost that stronger early management would have reduced.",
        },
        1: {"what_the_situation_called_for": "The real question was whether Riley was the whole problem or the clearest signal of something broader.", "how_your_choice_landed": "You did not fully establish the strongest read, but you did avoid a worse start.", "assessment_from_your_starting_point": "You responded in a way that kept the situation workable without yet changing the shape of the problem.", "what_it_meant_for_your_trajectory": "This left room for recovery."},
        2: {"what_the_situation_called_for": "The demo was asking for a wider read of the team pattern, not just more attention on Riley.", "how_your_choice_landed": "You were not yet ahead of the problem, but you did begin to act in a way that made later recovery possible.", "assessment_from_your_starting_point": "Not the ideal route, but a sound move from where you had already taken the run.", "what_it_meant_for_your_trajectory": "Your management started to improve without yet fully changing the run’s direction."},
        3: {"what_the_situation_called_for": "The situation required a shift from symptom management to realignment.", "how_your_choice_landed": "This is the week your management improved in a meaningful way.", "assessment_from_your_starting_point": "The best strategy would have been to widen your read earlier. However, given the position you had already created, your choice this week was sound.", "what_it_meant_for_your_trajectory": "This began to recover the situation rather than simply containing the symptom."},
        4: {"what_the_situation_called_for": "The demo needed continued action at the level of the pattern rather than a return to Riley alone.", "how_your_choice_landed": "Given the amount of hidden cost already in the system, this was a good recovery decision.", "assessment_from_your_starting_point": "It did not put you on the strongest route overall, but it did improve the demo from the state you had already created.", "what_it_meant_for_your_trajectory": "This strengthened recovery and stopped the run sliding backward."},
        5: {"what_the_situation_called_for": "The broader read you had started to develop needed to be consolidated.", "how_your_choice_landed": "This was another week where your management improved relative to the position you had already created.", "assessment_from_your_starting_point": "The stronger overall route would still have made this easier earlier. However, from your actual starting point this week, your decision was sound.", "what_it_meant_for_your_trajectory": "That deserves recognition because it helped contain further spread."},
        6: {"what_the_situation_called_for": "The wider pattern still needed to be held in view all the way to the demo, even though earlier costs could no longer be erased.", "how_your_choice_landed": "Your later choices were often sound given the state of the run by this point, and they helped contain further spread.", "assessment_from_your_starting_point": "You did not begin with the strongest read, but you did not stay trapped in it either.", "what_it_meant_for_your_trajectory": "The run finished as a recovery story, though one that still carried avoidable cost from earlier weeks."},
    },
    "early_realignment": {
        "overall": {
            "overall_assessment": "You read the management problem at the right level early enough to matter.",
            "management_pattern": "You treated Riley as the signal and then acted on the hidden carrying pattern before fragility hardened into the team’s normal way of coping.",
            "kpi_review": "You kept the demo close to the standard we should expect under pressure, which is exactly what good management needs to do here.",
        },
        1: {"what_the_situation_called_for": "The situation called for treating Riley as the clearest signal, not the whole story.", "how_your_choice_landed": "You acted early enough at the surrounding level that the demo pressure had less room to harden into a team-fragility problem.", "assessment_from_your_starting_point": "That gave you the strongest opening position of any route.", "what_it_meant_for_your_trajectory": "This was the right read for the conditions."},
        2: {"what_the_situation_called_for": "The wider pattern needed reinforcing, not a doubling down on Riley alone.", "how_your_choice_landed": "You continued to act at the level the pressure was actually forming, which stopped the team becoming more brittle than the headline symptoms suggested.", "assessment_from_your_starting_point": "This is what early pattern recognition looks like in practice.", "what_it_meant_for_your_trajectory": "You were strengthening trajectory, not just reacting to symptoms."},
        3: {"what_the_situation_called_for": "The stronger move was to keep the run contained rather than let it turn reactive.", "how_your_choice_landed": "You recognized that the demo pressure was now a misalignment pattern and intervened accordingly.", "assessment_from_your_starting_point": "That protected Maya and the quieter carriers around Riley and reduced the chance of the run hardening into fragility.", "what_it_meant_for_your_trajectory": "This was strong strategic and tactical management."},
        4: {"what_the_situation_called_for": "The intervention needed to stay at the level of the pattern, not collapse back toward the visible symptom.", "how_your_choice_landed": "You did that.", "assessment_from_your_starting_point": "The result was not the removal of pressure, but the prevention of avoidable spread through the team.", "what_it_meant_for_your_trajectory": "This is what good mid-scenario management looks like: not dramatic, but pattern-aware and steadying."},
        5: {"what_the_situation_called_for": "Stronger runs are easier to spot because the wider team is not carrying the same hidden cost.", "how_your_choice_landed": "Your earlier and ongoing pattern-level decisions continued to pay off here.", "assessment_from_your_starting_point": "This was not about eliminating pressure, but about stopping it from becoming quietly cumulative.", "what_it_meant_for_your_trajectory": "That is why the demo remained controlled rather than merely survived."},
        6: {"what_the_situation_called_for": "The demo still needed to be under pressure, but no longer carried by avoidable hidden strain.", "how_your_choice_landed": "You maintained the broader read all the way through the run.", "assessment_from_your_starting_point": "That let you reduce spread, protect Maya and the quieter carriers, and keep the demo closer to target.", "what_it_meant_for_your_trajectory": "This is the pattern the scenario is designed to teach."},
    },
}


SCENARIO_02_END_SCREEN_COPY = {
    "reactive_escalation": {
        "outcome": "Management Review: The demo was not controlled at the right level.",
        "management_pattern": "You stayed too close to Riley’s visible strain while the hidden carrying pattern hardened around the work.",
        "what_you_did_well": "You were not ignoring pressure altogether, but your response stayed too close to what was easiest to see.",
        "what_limited_the_result": "The demo kept moving because the wider team privately absorbed too much of the cost, and that fragility never became the main object of management soon enough.",
        "kpi_review": "This finished above the level of human cost we should be willing to accept.",
        "development_point": "The managerial step you missed was widening your read beyond Riley before the hidden carrying became the system.",
    },
    "surface_containment": {
        "outcome": "Management Review: You got the demo through, but not strongly enough.",
        "management_pattern": "You responded responsibly to visible strain, but your management stayed too close to the loudest symptom.",
        "what_you_did_well": "You did not look away from the human pressure in front of you, which mattered.",
        "what_limited_the_result": "The demo got through because the wider team carried more hidden cost than it should have had to, and that is where your read stayed too narrow.",
        "kpi_review": "You kept the run moving, but you finished above target and above the standard we should be aiming for.",
        "development_point": "The stronger managerial move would have been to treat Riley as the signal and act on the hidden fragility around him sooner.",
    },
    "late_widening": {
        "outcome": "Management Review: You recovered the situation, but later than we would want.",
        "management_pattern": "You improved your read and started managing the wider pattern, but only after the situation had already become more expensive than it needed to be.",
        "what_you_did_well": "You corrected course rather than staying trapped in your first read, and that mattered to the final outcome.",
        "what_limited_the_result": "By the time you widened the frame, some avoidable hidden cost had already moved through the team and could no longer be fully undone.",
        "kpi_review": "You came closer to target, but the team still ended up carrying strain that stronger early management would have reduced.",
        "development_point": "The next step is speed of diagnosis. You need to get to that broader read before the team has to recover from it.",
    },
    "early_realignment": {
        "outcome": "Management Review: This was a strong piece of management under pressure.",
        "management_pattern": "You identified the misalignment early and managed the demo at the level it actually needed.",
        "what_you_did_well": "You treated Riley’s visible strain as a signal, then reduced the hidden carrying and fragile coping around him before it became the team’s defining pattern.",
        "what_limited_the_result": "The pressure itself was real, but you stopped it turning into avoidable spread through the team.",
        "kpi_review": "You met, or came very close to, the standard we should expect for this situation.",
        "development_point": "This is the level of judgment we want to see from a manager in a demo run like this. The pressure is still there, but you controlled it properly.",
    },
}


def _scenario_02_counters(history):
    focal_support_early = 0
    hidden_read_by_week_2 = 0
    hidden_read_to_date = 0
    hidden_relief_to_date = 0
    hidden_coordination_to_date = 0

    for snapshot in history or []:
        week = snapshot.get("week")
        actions = snapshot.get("actions_taken", [])
        roles = snapshot.get("scenario_roles", {})
        focal_id = roles.get("focal_employee")
        hidden_id = roles.get("hidden_strain_employee")

        for action in actions:
            action_type = action.get("type")
            target = action.get("target") or {}
            target_id = target.get("id")
            from_id = target.get("from_id")

            if week and week <= 2 and action_type in {"quick_check_in", "offer_coaching_support"} and target_id == focal_id:
                focal_support_early += 1
            if action_type in {"check_in_on_load_bearing_risk", "surface_hidden_support_work"} and target_id == hidden_id:
                hidden_read_to_date += 1
                if week and week <= 2:
                    hidden_read_by_week_2 += 1
            if (action_type == "reduce_workload" and target_id == hidden_id) or (
                action_type == "reallocate_workload" and from_id == hidden_id
            ):
                hidden_relief_to_date += 1
            if action_type in {"clarify_roles_and_handoffs", "group_mediation"} and target_id == hidden_id:
                hidden_coordination_to_date += 1

    return {
        "focal_support_early": focal_support_early,
        "hidden_read_by_week_2": hidden_read_by_week_2,
        "hidden_read_to_date": hidden_read_to_date,
        "hidden_relief_to_date": hidden_relief_to_date,
        "hidden_coordination_to_date": hidden_coordination_to_date,
    }


def scenario_02_weekly_narrative_path(history, snapshot):
    if not snapshot:
        return None
    actions = snapshot.get("actions_taken", [])
    if not actions:
        return "reactive_escalation"

    history_to_date = [
        prior_snapshot for prior_snapshot in (history or [])
        if prior_snapshot.get("week", 0) <= snapshot.get("week", 0)
    ]
    week = snapshot.get("week", 0)
    counters = _scenario_02_counters(history_to_date)

    if week <= 1:
        if counters["hidden_read_to_date"] >= 1:
            return "early_realignment"
        if counters["focal_support_early"] >= 1:
            return "surface_containment"
        return "reactive_escalation"

    if week == 2:
        if counters["hidden_read_by_week_2"] >= 1 and (counters["hidden_relief_to_date"] + counters["hidden_coordination_to_date"]) >= 1:
            return "early_realignment"
        if counters["hidden_read_to_date"] >= 1:
            return "late_widening"
        if counters["focal_support_early"] >= 1:
            return "surface_containment"
        return "reactive_escalation"

    if counters["hidden_read_by_week_2"] >= 1 and counters["hidden_relief_to_date"] >= 1 and counters["hidden_coordination_to_date"] >= 1:
        return "early_realignment"
    if counters["hidden_read_to_date"] >= 1 and (counters["hidden_relief_to_date"] + counters["hidden_coordination_to_date"]) >= 1:
        return "late_widening"
    if counters["focal_support_early"] >= 1:
        return "surface_containment"
    return "reactive_escalation"


def scenario_weekly_briefing(scenario_key, week):
    if scenario_key == "scenario_01":
        return SCENARIO_01_MAIN_SCREEN_COPY.get(week, {})
    if scenario_key == "scenario_02":
        return SCENARIO_02_MAIN_SCREEN_COPY.get(week, {})
    return {}


def scenario_main_screen_aside(game):
    if game.week <= 1:
        return ""
    history = game.get_analysis_history()
    if not history:
        return ""
    prior_snapshot = history[-1]
    prior_path = scenario_weekly_narrative_path(game, history, prior_snapshot)
    if not prior_path:
        return ""
    if game.scenario == "scenario_01":
        return SCENARIO_01_MAIN_SCREEN_ASIDES.get(game.week, {}).get(prior_path, "")
    if game.scenario == "scenario_02":
        return SCENARIO_02_MAIN_SCREEN_ASIDES.get(game.week, {}).get(prior_path, "")
    return ""


def scenario_narrative_path(game, history, latest, benchmark_history, benchmark_latest):
    if game.scenario == "scenario_02":
        if not latest:
            return "reactive_escalation"
        if (latest or {}).get("scenario_outcome_tier") == "Fail":
            return "reactive_escalation"
        explicit_path = scenario_02_explicit_route_path(history)
        if explicit_path:
            return explicit_path
        return scenario_two_read_level(history)

    if game.scenario != "scenario_01":
        if (latest or {}).get("scenario_outcome_tier") == "Fail":
            return "spiralled"
        return determine_summary_branch(game, history, latest, benchmark_history, benchmark_latest)

    if (latest or {}).get("scenario_outcome_tier") == "Fail":
        return "spiralled"

    explicit_path = scenario_01_explicit_route_path(history)
    if explicit_path:
        return explicit_path

    return determine_summary_branch(game, history, latest, benchmark_history, benchmark_latest)


def scenario_01_explicit_route_path(history):
    snapshots_by_week = {
        snapshot.get("week"): snapshot
        for snapshot in (history or [])
        if snapshot.get("week") is not None
    }

    def flags_for(week):
        return _scenario_01_action_flags(snapshots_by_week.get(week, {}))

    well_done = (
        ((flags_for(1)["individual_on_focal"] and flags_for(1)["coordination_on_focal"]) or (flags_for(1)["coordination_on_focal"] and flags_for(1)["individual_on_hidden"]))
        and (flags_for(2)["individual_on_focal"] or flags_for(2)["coordination_on_focal"])
        and flags_for(3)["coordination_on_focal"] and flags_for(3)["individual_on_hidden"]
        and flags_for(4)["coordination_on_focal"] and flags_for(4)["individual_on_hidden"]
        and (flags_for(5)["any_on_focal"] or flags_for(5)["individual_on_hidden"])
        and flags_for(6)["any_on_focal"] and flags_for(6)["individual_on_hidden"]
    )
    if well_done:
        return "well_done"

    more_strain = (
        (flags_for(1)["individual_on_focal"] ^ flags_for(1)["coordination_on_focal"])
        and (flags_for(2)["individual_on_focal"] ^ flags_for(2)["coordination_on_focal"])
        and flags_for(3)["any_on_focal"] and flags_for(3)["individual_on_hidden"]
        and flags_for(4)["any_on_focal"] and flags_for(4)["individual_on_hidden"]
        and (flags_for(5)["any_on_focal"] or flags_for(5)["any_on_hidden"])
        and (flags_for(6)["any_on_focal"] or flags_for(6)["any_on_hidden"])
    )
    if more_strain:
        return "more_strain_than_needed"

    high_strain = (
        flags_for(1)["individual_on_focal"]
        and flags_for(2)["individual_on_focal"]
        and flags_for(3)["any_on_focal"] and not flags_for(3)["any_on_hidden"]
        and flags_for(4)["any_on_focal"] and not flags_for(4)["any_on_hidden"]
        and flags_for(5)["any_on_focal"] and not flags_for(5)["any_on_hidden"]
        and flags_for(6)["any_on_focal"] and not flags_for(6)["any_on_hidden"]
    )
    if high_strain:
        return "high_strain_count"

    return None


def _scenario_01_action_flags(snapshot):
    actions = snapshot.get("actions_taken", []) if snapshot else []
    focal_id = snapshot.get("scenario_roles", {}).get("focal_employee") if snapshot else None
    hidden_id = snapshot.get("scenario_roles", {}).get("hidden_strain_employee") if snapshot else None

    individual_on_focal = any(
        action.get("target", {}).get("id") == focal_id
        and action.get("type") in {"quick_check_in", "offer_coaching_support", "reduce_workload"}
        for action in actions
    )
    coordination_on_focal = any(
        action.get("target", {}).get("id") == focal_id
        and action.get("type") in {"group_mediation", "clarify_roles_and_handoffs"}
        for action in actions
    )
    individual_on_hidden = any(
        action.get("target", {}).get("id") == hidden_id
        and action.get("type") in {
            "quick_check_in",
            "offer_coaching_support",
            "check_in_on_load_bearing_risk",
            "surface_hidden_support_work",
            "reduce_workload",
        }
        for action in actions
    )
    any_on_focal = any(
        action.get("target", {}).get("id") == focal_id
        for action in actions
    )
    any_on_hidden = any(
        action.get("target", {}).get("id") == hidden_id
        for action in actions
    )
    return {
        "individual_on_focal": individual_on_focal,
        "coordination_on_focal": coordination_on_focal,
        "individual_on_hidden": individual_on_hidden,
        "any_on_focal": any_on_focal,
        "any_on_hidden": any_on_hidden,
        "no_actions": not actions,
    }


def _scenario_01_prior_weekly_path(game, history, snapshot):
    prior_history = [
        prior_snapshot for prior_snapshot in (history or [])
        if prior_snapshot.get("week", 0) < snapshot.get("week", 0)
    ]
    if not prior_history:
        return None
    return scenario_weekly_narrative_path(game, prior_history, prior_history[-1])


def _scenario_02_action_flags(snapshot):
    actions = snapshot.get("actions_taken", []) if snapshot else []
    focal_id = snapshot.get("scenario_roles", {}).get("focal_employee") if snapshot else None
    hidden_id = snapshot.get("scenario_roles", {}).get("hidden_strain_employee") if snapshot else None

    individual_on_focal = any(
        action.get("target", {}).get("id") == focal_id
        and action.get("type") in {"quick_check_in", "offer_coaching_support", "reduce_workload"}
        for action in actions
    )
    diagnostic_on_hidden = any(
        action.get("target", {}).get("id") == hidden_id
        and action.get("type") in {"check_in_on_load_bearing_risk", "surface_hidden_support_work"}
        for action in actions
    )
    support_on_hidden = any(
        action.get("target", {}).get("id") == hidden_id
        and action.get("type") in {"quick_check_in", "offer_coaching_support"}
        for action in actions
    )
    coordination_on_hidden = any(
        action.get("target", {}).get("id") == hidden_id
        and action.get("type") in {"clarify_roles_and_handoffs", "group_mediation"}
        for action in actions
    )
    relief_on_hidden = any(
        (
            action.get("type") == "reduce_workload"
            and action.get("target", {}).get("id") == hidden_id
        ) or (
            action.get("type") == "reallocate_workload"
            and action.get("target", {}).get("from_id") == hidden_id
        )
        for action in actions
    )
    any_on_focal = any(action.get("target", {}).get("id") == focal_id for action in actions)
    any_on_hidden = any(
        action.get("target", {}).get("id") == hidden_id
        or action.get("target", {}).get("from_id") == hidden_id
        for action in actions
    )
    return {
        "individual_on_focal": individual_on_focal,
        "diagnostic_on_hidden": diagnostic_on_hidden,
        "support_on_hidden": support_on_hidden,
        "coordination_on_hidden": coordination_on_hidden,
        "relief_on_hidden": relief_on_hidden,
        "any_on_focal": any_on_focal,
        "any_on_hidden": any_on_hidden,
        "no_actions": not actions,
    }


def scenario_02_explicit_route_path(history):
    snapshots_by_week = {
        snapshot.get("week"): snapshot
        for snapshot in (history or [])
        if snapshot.get("week") is not None
    }

    def flags_for(week):
        return _scenario_02_action_flags(snapshots_by_week.get(week, {}))

    early_realignment = (
        flags_for(1)["diagnostic_on_hidden"]
        and flags_for(1)["individual_on_focal"]
        and flags_for(2)["relief_on_hidden"]
        and flags_for(2)["individual_on_focal"]
        and flags_for(3)["diagnostic_on_hidden"]
        and flags_for(4)["support_on_hidden"]
        and flags_for(4)["individual_on_focal"]
        and flags_for(5)["individual_on_focal"]
        and flags_for(6)["individual_on_focal"]
    )
    if early_realignment:
        return "early_realignment"

    late_widening = (
        flags_for(1)["individual_on_focal"]
        and flags_for(2)["individual_on_focal"]
        and flags_for(3)["diagnostic_on_hidden"]
        and flags_for(4)["relief_on_hidden"]
        and flags_for(5)["individual_on_focal"]
        and flags_for(6)["individual_on_focal"]
    )
    if late_widening:
        return "late_widening"

    surface_containment = (
        flags_for(1)["individual_on_focal"]
        and flags_for(2)["individual_on_focal"]
        and flags_for(3)["any_on_focal"] and not flags_for(3)["any_on_hidden"]
        and flags_for(4)["any_on_focal"] and not flags_for(4)["any_on_hidden"]
        and flags_for(5)["any_on_focal"] and not flags_for(5)["any_on_hidden"]
        and flags_for(6)["any_on_focal"] and not flags_for(6)["any_on_hidden"]
    )
    if surface_containment:
        return "surface_containment"

    reactive_escalation = (
        flags_for(1)["no_actions"]
        and flags_for(2)["no_actions"]
        and not flags_for(3)["any_on_hidden"]
        and not flags_for(4)["any_on_hidden"]
        and not flags_for(5)["any_on_hidden"]
        and not flags_for(6)["any_on_hidden"]
    )
    if reactive_escalation:
        return "reactive_escalation"

    return None


def _scenario_02_prior_weekly_path(game, history, snapshot):
    prior_history = [
        prior_snapshot for prior_snapshot in (history or [])
        if prior_snapshot.get("week", 0) < snapshot.get("week", 0)
    ]
    if not prior_history:
        return None
    return scenario_weekly_narrative_path(game, prior_history, prior_history[-1])


def scenario_weekly_narrative_path(game, history, snapshot):
    if not snapshot:
        return None

    if game.scenario == "scenario_02":
        flags = _scenario_02_action_flags(snapshot)
        if flags["no_actions"]:
            return "reactive_escalation"

        week = snapshot.get("week")
        prior_path = _scenario_02_prior_weekly_path(game, history, snapshot)

        if week == 1:
            if flags["diagnostic_on_hidden"] and flags["individual_on_focal"]:
                return "early_realignment"
            if flags["support_on_hidden"] or flags["coordination_on_hidden"]:
                return "late_widening"
            if flags["individual_on_focal"]:
                return "surface_containment"
            return "reactive_escalation"

        if week == 2:
            if prior_path == "early_realignment" and flags["relief_on_hidden"] and flags["individual_on_focal"]:
                return "early_realignment"
            if flags["diagnostic_on_hidden"] or flags["support_on_hidden"] or flags["coordination_on_hidden"] or flags["relief_on_hidden"]:
                return "late_widening"
            if flags["individual_on_focal"]:
                return "surface_containment"
            return "reactive_escalation"

        if week in {3, 4}:
            if prior_path == "early_realignment" and (
                (week == 3 and flags["diagnostic_on_hidden"])
                or (week == 4 and flags["support_on_hidden"] and flags["individual_on_focal"])
            ):
                return "early_realignment"
            if (week == 3 and flags["any_on_hidden"]) or (week == 4 and (flags["relief_on_hidden"] or flags["coordination_on_hidden"])):
                return "late_widening"
            if flags["any_on_focal"]:
                return "surface_containment"
            return "reactive_escalation"

        if week == 5:
            if prior_path == "early_realignment" and flags["individual_on_focal"]:
                return "early_realignment"
            if prior_path == "late_widening" and flags["individual_on_focal"]:
                return "late_widening"
            if flags["any_on_focal"]:
                return "surface_containment"
            return "reactive_escalation"

        if week == 6:
            if prior_path == "early_realignment" and flags["individual_on_focal"]:
                return "early_realignment"
            if prior_path == "late_widening" and flags["individual_on_focal"]:
                return "late_widening"
            if flags["any_on_focal"]:
                return "surface_containment"
            return "reactive_escalation"

        return "reactive_escalation"

    if game.scenario != "scenario_01":
        return None

    flags = _scenario_01_action_flags(snapshot)
    if flags["no_actions"]:
        return "spiralled"

    week = snapshot.get("week")
    prior_path = _scenario_01_prior_weekly_path(game, history, snapshot)

    if week in {1, 2}:
        if (
            flags["individual_on_focal"] and flags["coordination_on_focal"]
        ) or (
            week == 1 and flags["coordination_on_focal"] and flags["individual_on_hidden"]
        ) or (
            week == 2 and flags["coordination_on_focal"]
        ):
            return "well_done"
        if flags["individual_on_focal"]:
            return "high_strain_count"
        if flags["coordination_on_focal"]:
            return "more_strain_than_needed"
        return "spiralled"

    if week in {3, 4}:
        if prior_path == "well_done" and flags["coordination_on_focal"] and flags["individual_on_hidden"]:
            return "well_done"
        if flags["any_on_focal"] and flags["individual_on_hidden"]:
            return "more_strain_than_needed"
        if flags["any_on_focal"]:
            return "high_strain_count"
        return "spiralled"

    if week == 5:
        if prior_path == "well_done" and (flags["any_on_focal"] or flags["individual_on_hidden"]):
            return "well_done"
        if prior_path == "more_strain_than_needed" and (flags["any_on_focal"] or flags["any_on_hidden"]):
            return "more_strain_than_needed"
        if flags["any_on_focal"]:
            return "high_strain_count"
        return "spiralled"

    if week == 6:
        if prior_path == "well_done" and flags["any_on_focal"] and flags["individual_on_hidden"]:
            return "well_done"
        if prior_path == "more_strain_than_needed" and (flags["any_on_focal"] or flags["any_on_hidden"]):
            return "more_strain_than_needed"
        if flags["any_on_focal"]:
            return "high_strain_count"
        return "spiralled"

    return "spiralled"


def weekly_tactical_quality(snapshot):
    actions = (snapshot or {}).get("actions_taken", [])
    if not actions:
        return "no_action"
    qualities = {action.get("authored_quality") for action in actions if action.get("authored_quality")}
    if "strong" in qualities:
        return "strong"
    if "acceptable" in qualities:
        return "acceptable"
    return "weak"


def _scenario_01_overlay_quality(path, week, snapshot):
    quality = weekly_tactical_quality(snapshot)
    if quality == "no_action":
        return quality

    # A week can contain a tactically strong authored move while still belonging to a
    # strategically narrower route overall. In those cases, soften the overlay so it
    # doesn't contradict the route-level note.
    if path == "high_strain_count" and quality == "strong":
        return "acceptable"
    if path == "spiralled" and quality == "strong":
        return "weak"

    return quality


def _scenario_02_overlay_quality(path, week, snapshot):
    quality = weekly_tactical_quality(snapshot)
    if quality == "no_action":
        return quality
    if path == "surface_containment" and quality == "strong":
        return "acceptable"
    if path == "reactive_escalation" and quality == "strong":
        return "weak"
    return quality


def scenario_week_end_report(game, snapshot, previous_snapshot, benchmark_history, benchmark_latest):
    if not snapshot or not previous_snapshot:
        return None
    history = game.get_analysis_history()
    if game.scenario == "scenario_02":
        path = scenario_weekly_narrative_path(game, history, snapshot)
        week = snapshot.get("week")
        base = SCENARIO_02_WEEK_END_COPY.get(path, {}).get(week)
        if not base:
            return None
        quality = _scenario_02_overlay_quality(path, week, snapshot)
        overlay = SCENARIO_02_TACTICAL_OVERLAY_BY_WEEK_AND_QUALITY.get(week, {}).get(quality, {})
        lines = [base.get("note", ""), overlay.get("week_end", "")]
        return [line for line in lines if line]
    if game.scenario != "scenario_01":
        return None
    path = scenario_weekly_narrative_path(game, history, snapshot)
    week = snapshot.get("week")
    base = SCENARIO_01_WEEK_END_COPY.get(path, {}).get(week)
    if not base:
        return None
    quality = _scenario_01_overlay_quality(path, week, snapshot)
    overlay = SCENARIO_01_TACTICAL_OVERLAY_BY_WEEK_AND_QUALITY.get(week, {}).get(quality, {})
    lines = [base.get("note", ""), overlay.get("week_end", "")]
    return [line for line in lines if line]


def scenario_analysis_copy(game, snapshot, week, history, benchmark_history, benchmark_latest):
    if game.scenario == "scenario_02":
        latest = history[-1] if history else {}
        if week == "overall":
            path = scenario_narrative_path(game, history, latest, benchmark_history, benchmark_latest)
            content = SCENARIO_02_ANALYSIS_COPY.get(path, {})
            return content.get("overall")
        path = scenario_weekly_narrative_path(game, history, snapshot)
        content = SCENARIO_02_ANALYSIS_COPY.get(path, {})
        return content.get(week)
    if game.scenario != "scenario_01":
        return None
    latest = history[-1] if history else {}
    if week == "overall":
        path = scenario_narrative_path(game, history, latest, benchmark_history, benchmark_latest)
        content = SCENARIO_01_ANALYSIS_COPY.get(path, {})
        return content.get("overall")
    path = scenario_weekly_narrative_path(game, history, snapshot)
    content = SCENARIO_01_ANALYSIS_COPY.get(path, {})
    week_content = content.get(week)
    if not week_content:
        return None
    quality = _scenario_01_overlay_quality(path, week, snapshot)
    overlay = SCENARIO_01_TACTICAL_OVERLAY_BY_WEEK_AND_QUALITY.get(week, {}).get(quality, {})
    rendered = dict(week_content)
    if overlay.get("analysis"):
        rendered["assessment_from_your_starting_point"] = (
            f"{rendered.get('assessment_from_your_starting_point', '')} {overlay['analysis']}"
        ).strip()
    return rendered


def scenario_end_screen_copy(game, history, latest, benchmark_history, benchmark_latest):
    if game.scenario == "scenario_02":
        branch = determine_summary_branch(game, history, latest, benchmark_history, benchmark_latest)
        scenario_02_end_copy_key = {
            "spiralled": "reactive_escalation",
            "high_strain_count": "surface_containment",
            "more_strain_than_needed": "late_widening",
            "well_done": "early_realignment",
        }.get(branch)
        if scenario_02_end_copy_key:
            return SCENARIO_02_END_SCREEN_COPY.get(scenario_02_end_copy_key)
        path = scenario_narrative_path(game, history, latest, benchmark_history, benchmark_latest)
        return SCENARIO_02_END_SCREEN_COPY.get(path)
    if game.scenario != "scenario_01":
        return None
    path = scenario_narrative_path(game, history, latest, benchmark_history, benchmark_latest)
    return SCENARIO_01_END_SCREEN_COPY.get(path)

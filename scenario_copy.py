from reporting import determine_summary_branch


SCENARIO_01_MAIN_SCREEN_COPY = {
    1: {
        "briefing": "We’re six weeks from launch and the pressure is already starting to collect around Jordan. He’s coordinating across too many moving parts, priorities have shifted twice this week, and he’s become the person everyone seems to route through when something changes. Jordan is the clearest visible concern right now, but I’m not convinced the pressure starts and ends with him.",
        "signals": [
            "Jordan is carrying the clearest visible launch pressure.",
            "Sam is quieter than usual around key delivery work.",
            "Priya is catching detail and quality fallout near the edges.",
            "Maya is helping the group feel steadier than it really is.",
        ],
    },
    2: {
        "briefing": "We’re still technically on track, but the launch group feels less settled this week. Jordan’s strain is more obvious now, and some of the work around him is starting to bounce more than it should. It still looks manageable from the outside, but I’m less confident that this is just one person having a hard week.",
        "signals": [
            "Jordan’s pressure is more visible.",
            "Handoffs are getting messier around the launch work.",
            "Sam is absorbing more quietly than he is signalling.",
            "Maya is smoothing over more than she should need to.",
        ],
    },
    3: {
        "briefing": "This feels like the point where the launch either gets steadier or starts hardening into a local team problem. Jordan is still the most visible pressure point, but Priya is beginning to catch more downstream fallout and Sam looks like he’s carrying more than he’s saying. If this is broader than Jordan, this is probably the week we’d want to act like it.",
        "signals": [
            "Visible strain is no longer isolated to Jordan alone.",
            "Priya is starting to absorb more downstream cleanup.",
            "Sam looks increasingly load-bearing.",
            "The cluster still looks recoverable, but less casually so.",
        ],
    },
    4: {
        "briefing": "The launch is close enough now that everyone feels the deadline, but the pressure still isn’t landing evenly. Jordan is still at the center of the visible strain, while the surrounding group looks more brittle than it did two weeks ago. If we are going to steady this properly, it probably needs to happen at the group level rather than through Jordan alone.",
        "signals": [
            "Local trust and coordination are beginning to fray.",
            "Priya is carrying more quality pressure.",
            "Maya is containing fallout that should be reduced directly.",
            "Hidden strain is becoming more expensive each week.",
        ],
    },
    5: {
        "briefing": "At this stage, the launch outcome will depend less on whether Jordan looks calmer and more on whether the surrounding group can absorb the final stretch without cracking. We’ve either started to steady the pocket around him, or we’re still asking the same few people to quietly carry the cost.",
        "signals": [
            "The cluster is either stabilising or quietly overloading.",
            "Visible calm may be misleading now.",
            "Small misses matter more in the final stretch.",
            "Hidden strain is becoming increasingly costly.",
        ],
    },
    6: {
        "briefing": "This is the final launch week. What matters now is not whether the pressure exists, but whether we’ve contained it well enough that the team can deliver without paying an avoidable human cost. Jordan is still the obvious signal, but the real question is how much of the surrounding group we’ve asked to absorb on the way here.",
        "signals": [
            "Final execution pressure is high across the launch pocket.",
            "The cluster either holds or frays under deadline pressure.",
            "Sam and Priya show the real human cost of the run.",
            "Maya can no longer hide the pattern on steadiness alone.",
        ],
    },
}


SCENARIO_01_MAIN_SCREEN_ASIDES = {
    2: {
        "well_done": "From where I’m sitting, your first move seems to have steadied the group around Jordan, not just Jordan himself. I’d keep following that wider read.",
        "more_strain_than_needed": "You’ve started to shift the read a little, but it still feels easy for the team to slide back into treating Jordan as the whole issue.",
        "high_strain_count": "Jordan got the support, which mattered, but I’m not seeing the same shift in the people carrying the quieter cost around him.",
        "spiralled": "I’m not seeing much yet that would make me think the launch pocket is getting steadier around Jordan.",
    },
    3: {
        "well_done": "What encourages me is that the pressure looks more containable around Jordan than it did a week ago. Sam is the person I’d keep in view now.",
        "more_strain_than_needed": "This still feels recoverable, but only if we keep widening the frame from here. Sam is becoming harder to ignore.",
        "high_strain_count": "We’re still reacting mostly to Jordan, and I’m not convinced that’s enough anymore. Sam looks more load-bearing than he did at the start.",
        "spiralled": "This is starting to feel like a cluster problem rather than a rough patch around one person, and we haven’t really got ahead of that yet.",
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
        "high_strain_count": "Jordan is still the obvious signal, but by now the real story is what the rest of the launch pocket has had to carry around him.",
        "spiralled": "By this stage, the launch is telling us very clearly that the issue was never just Jordan. The question is whether we’ve acted on that truth in time.",
    },
}


SCENARIO_01_WEEK_END_COPY = {
    "spiralled": {
        1: {
            "note": "Jordan’s still carrying the most visible pressure, but the week didn’t really settle around him. Sam stayed quiet, Priya ended up picking up more of the loose-end checking, and Maya was doing more than she should have had to just to keep things from feeling less steady. I’m starting to worry that we’re not really containing this so much as asking the people around Jordan to absorb it.",
        },
        2: {
            "note": "The launch group felt more brittle this week. Jordan’s still where the pressure shows up most clearly, but it’s not staying with him. Sam is keeping too much to himself, Priya is catching more of the downstream mess, and Maya’s having to work too hard just to stop the group from fraying. I’m worried this is starting to harden into a launch-pocket problem rather than just one visible rough week.",
        },
        3: {
            "note": "This felt like a turning-point week, and we didn’t really interrupt the pattern around Jordan and the people nearest to him. Sam and Priya are both carrying more of the hidden cost now, and Maya’s compensating for something more structural than just a difficult few days. If we leave it here, the cluster itself becomes the real problem, not just Jordan’s visible overload.",
        },
        4: {
            "note": "The launch pocket feels brittle now, and your decision didn’t really reduce that. Priya’s carrying more quality pressure, Sam looks increasingly load-bearing, and Maya is holding together something that shouldn’t need this much quiet support just to function. At this point, the cost of not stabilising the group is getting harder to hide.",
        },
        5: {
            "note": "At this point, it feels like the launch is being carried more by people absorbing pressure than by the system actually getting steadier. Jordan’s still visibly under strain, but Sam and Priya are the ones paying the quieter price of keeping things alive, and Maya’s still cushioning the group where she can. I’m worried we’re now getting through on endurance rather than control.",
        },
        6: {
            "note": "We got to the end of the launch in the most fragile way possible. By the final week, your response still wasn’t changing the real pattern carrying the work. Sam and Priya have both been paying the cost of keeping this alive, and Maya has had to quietly stabilise far more than a healthy system should require. This is what it looks like when a visible problem gets mistaken for the whole story for too long.",
        },
    },
    "high_strain_count": {
        1: {
            "note": "Jordan looked a little more supported by the end of the week, and that did matter. I can see why you made that call, because he was still the clearest pressure point in the room. The difficulty is that the rest of the group didn’t really settle with him. Sam stayed in the background, Priya still picked up the detail fallout, and Maya was quietly doing more than she should have to just to keep things feeling steady. What I’m watching now is whether the pressure keeps moving outward while Jordan stays at the center of attention.",
        },
        2: {
            "note": "Jordan looked marginally steadier by the end of the week, but that improvement didn’t really spread through the people around him. The support landed where the pressure was easiest to see, which was reasonable, but the handoffs and hidden strain around the launch didn’t improve much. Priya is beginning to carry more of the cost, and Sam still looks less visible than he should for how much this work depends on him. The risk now is that we mistake Jordan feeling slightly better for the group actually being steadier.",
        },
        3: {
            "note": "Jordan was still the clearest pressure point this week, so I can see why your decision fit that surface read. The problem is that by now the launch needed more than visible relief if the group around him was going to steady properly. Sam’s carrying more quiet strain, Priya’s picking up clearer downstream cost, and the pocket around Jordan doesn’t feel any more stable for him being the main focus. We may still get through, but the team is paying more for it than it should.",
        },
        4: {
            "note": "You kept supporting the visible pressure point in a way that made human sense, but the wider launch pocket still didn’t steady with him. That gap matters more now than it did earlier, because the hidden cost is building around the group rather than in Jordan alone. Sam and Priya are both carrying more quiet cost, and Maya is still compensating for instability that should have been reduced more directly. We may still be on course to launch, but the way we’re getting there is becoming more expensive.",
        },
        5: {
            "note": "Jordan may look somewhat better supported, but the wider launch pocket still feels heavier than it should this late in the run. The visible issue has had attention; the surrounding group still hasn’t really had enough relief. Sam remains more load-bearing than he should, Priya is carrying downstream pressure, and Maya is still quietly holding the line. We’re getting through, but not cleanly.",
        },
        6: {
            "note": "The launch got through, but the group around Jordan carried more pressure than it needed to on the way there. You were responsive to the visible strain, and that mattered, but the surrounding cluster was still left holding too much hidden cost. Sam ended up more load-bearing than he should have been, Priya took on more fallout, and Maya carried too much quiet stabilising work. We made it, but not at the right level.",
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
            "note": "This felt like a meaningful correction week. Given how much pressure had already built by this point, your decision was a sensible way to start stabilising the launch at the right level. It didn’t erase the earlier spread, but it did stop the cluster from hardening as badly as it might have. What matters now is whether you keep acting on the surrounding pattern rather than slipping back toward the most visible symptom.",
        },
        4: {
            "note": "The week ended more steadily than the launch might have done otherwise. Your decision was a sound correction for the position the team was already in, and it helped keep the cluster from getting more brittle. That said, some avoidable strain is now built into the group from the earlier weeks. If you keep acting on the broader pattern from here, the launch can still be contained.",
        },
        5: {
            "note": "The cluster is in a better place than it might have been, and your recent choices are part of why. Given the strain that had already spread through the group, this week’s decision helped keep the launch recoverable. The downside is that some of the human cost is already baked in by now. The final week really depends on whether you stay with the broader read.",
        },
        6: {
            "note": "The launch finished in a better place than it might have done, because you did improve your read as the pattern became clearer. Your later decisions helped steady the wider group and reduced some further spread. The difficulty is that the correction came after some avoidable strain had already moved through the cluster. We got through, but the team still paid more than it ideally should have.",
        },
    },
    "well_done": {
        1: {
            "note": "The launch still has pressure in it, and Jordan is still the clearest visible signal, but the group around him looked steadier by the end of the week. That’s the bit I’d pay attention to. Your decision landed at the level the problem was actually starting to form, not just where it was easiest to see. Sam and Priya weren’t left carrying as much of the quiet cost, and Maya wasn’t having to hold the whole thing together in the background. If we keep reading it this way, we’ve got a much better chance of stabilising the launch pocket early.",
        },
        2: {
            "note": "The launch pressure looked more manageable this week, even though Jordan was still visibly under strain. Your decision helped steady the group around him, and at this point that matters more than simply making the focal person look calmer. Sam stayed less burdened than he might have otherwise, Priya didn’t absorb as much extra fallout, and Maya was less exposed as the team’s quiet stabiliser. The pressure is still there, but it’s not spreading as freely.",
        },
        3: {
            "note": "This was the point where the launch could have hardened into a local team problem, and it didn’t. Your decision landed at the level the pressure was actually sitting, which made the surrounding group easier to steady. Jordan is still visibly carrying a lot, but Sam and Priya were less exposed because the launch wasn’t left to spread through them unchecked. This is the kind of move that keeps a hard week from becoming the team’s defining pattern.",
        },
        4: {
            "note": "The launch group looked steadier this week than the deadline pressure alone would suggest. Your decision reduced fragility in the cluster rather than just making the visible symptoms more tolerable. Priya ended the week less exposed, Sam wasn’t left carrying as much hidden weight, and Maya had less compensating to do in the background. The pressure is still real, but it’s moving through a more stable system.",
        },
        5: {
            "note": "The launch group looks about as steady as it realistically could this late in the run. Your decisions have made it easier for the surrounding pocket to absorb deadline pressure without quietly passing so much cost between people. Jordan is still the visible signal, but Sam and Priya aren’t carrying the same hidden burden they would have otherwise. This is what containment looks like under pressure.",
        },
        6: {
            "note": "The launch reached the final week under pressure, but not in a way that defined the whole group. You treated Jordan as the signal while stabilising the surrounding cluster early enough that Sam, Priya, and Maya weren’t left carrying the launch by quiet accumulation. The pressure was real all the way through, but the system around it became more containable rather than more brittle. That’s why the launch held together.",
        },
    },
}


SCENARIO_01_ANALYSIS_COPY = {
    "spiralled": {
        "overall": {
            "overall_assessment": "You did not get hold of the real management problem early enough.",
            "management_pattern": "You stayed too close to the visible pressure while the underlying launch cluster was allowed to harden around it.",
            "kpi_review": "You finished materially above the strain level we should be accepting for this launch.",
        },
        1: {
            "what_the_situation_called_for": "Week 1 called for widening your read beyond the most visible pressure point.",
            "how_your_choice_landed": "You treated the symptom in front of you too narrowly, which left the surrounding delivery pocket under-read.",
            "assessment_from_your_starting_point": "From your starting point, the stronger move would have been to test whether the instability around Jordan was already shared by the people closest to him.",
            "what_it_meant_for_your_trajectory": "This didn’t just miss an opportunity; it set up a weaker trajectory.",
        },
        2: {
            "what_the_situation_called_for": "By week 2, the launch was already asking whether the strain around Jordan was beginning to spread through the people closest to him.",
            "how_your_choice_landed": "You still responded too narrowly to the visible pressure, which left the surrounding group carrying more hidden cost than it should have.",
            "assessment_from_your_starting_point": "At this stage, a narrow move was no longer enough for the state of the launch.",
            "what_it_meant_for_your_trajectory": "This deepened a weak trajectory rather than interrupting it.",
        },
        3: {
            "what_the_situation_called_for": "Week 3 was the pivot point where the launch needed active stabilisation at the cluster level.",
            "how_your_choice_landed": "You did not make that shift, which meant the launch stopped being primarily about Jordan and became about the group’s fragility.",
            "assessment_from_your_starting_point": "The stronger strategy was not merely to support the visibly strained person, but to stabilise the cluster around them.",
            "what_it_meant_for_your_trajectory": "This let the wrong pattern harden.",
        },
        4: {
            "what_the_situation_called_for": "By week 4, the question was no longer whether Jordan was struggling, but whether you were acting at the level the launch was breaking down.",
            "how_your_choice_landed": "You still weren’t, and the result was a more brittle cluster with less room to recover.",
            "assessment_from_your_starting_point": "This was strategically weak for the conditions, even if the move was superficially understandable.",
            "what_it_meant_for_your_trajectory": "The launch group became harder to steady and more expensive to carry.",
        },
        5: {
            "what_the_situation_called_for": "By week 5, the scenario was no longer especially ambiguous: the launch cluster was carrying the real risk.",
            "how_your_choice_landed": "Your management still did not meaningfully act on that truth.",
            "assessment_from_your_starting_point": "Any plausible tactical move from here was being asked to compensate for missed earlier weeks.",
            "what_it_meant_for_your_trajectory": "This confirmed a late-stage consequence of a weak strategic read.",
        },
        6: {
            "what_the_situation_called_for": "The final week called for a launch group that had already been stabilised earlier, not one still relying on quiet compensation.",
            "how_your_choice_landed": "Your response still wasn’t changing the real pattern carrying the launch.",
            "assessment_from_your_starting_point": "By this stage, the damage was not only in the pressure itself, but in how long the surrounding cluster had been asked to absorb it.",
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
            "what_the_situation_called_for": "Week 1 allowed a humane response to Jordan, but it also invited a wider read of the launch pocket around him.",
            "how_your_choice_landed": "Supporting the visible pressure point made tactical sense, but it didn’t test whether the launch strain was already sitting more widely in the group.",
            "assessment_from_your_starting_point": "This was a reasonable move if your read was centered on Jordan.",
            "what_it_meant_for_your_trajectory": "It was understandable, but it reinforced a narrow diagnosis.",
        },
        2: {
            "what_the_situation_called_for": "By week 2, the launch needed more than care for Jordan; it needed a read on whether the surrounding group was still stable.",
            "how_your_choice_landed": "Your choice still made sense if the goal was to help Jordan through a visibly difficult week.",
            "assessment_from_your_starting_point": "The issue is that the scenario had already moved beyond Jordan alone as the main management question.",
            "what_it_meant_for_your_trajectory": "This helped tactically at the surface, but kept the run on a narrow path.",
        },
        3: {
            "what_the_situation_called_for": "Week 3 exposed the need to stabilise the cluster, not just the focal person.",
            "how_your_choice_landed": "Your decision still made sense if Jordan remained the main object of concern, but by now that was no longer the strongest read.",
            "assessment_from_your_starting_point": "The surrounding launch pocket needed active stabilisation at this point.",
            "what_it_meant_for_your_trajectory": "This preserved the narrow frame even while offering some visible relief.",
        },
        4: {
            "what_the_situation_called_for": "By week 4, plausibility was no longer enough; the launch required a broader intervention to reduce fragility around Jordan.",
            "how_your_choice_landed": "Your choice helped the visible symptom more than the delivery system producing it.",
            "assessment_from_your_starting_point": "Reasonable in isolation, insufficient in context.",
            "what_it_meant_for_your_trajectory": "The run stayed survivable, but above the level of strain it needed to carry.",
        },
        5: {
            "what_the_situation_called_for": "By week 5, good management had to care about what the rest of the cluster was paying to keep the launch moving.",
            "how_your_choice_landed": "You were still protecting the most obvious pressure point while leaving quieter cost in place.",
            "assessment_from_your_starting_point": "This remained tactically understandable, but strategically too narrow.",
            "what_it_meant_for_your_trajectory": "That is why the run stayed above target even as the launch kept moving.",
        },
        6: {
            "what_the_situation_called_for": "The final week called for a launch that had been steadied at the group level, not just one where Jordan had been supported repeatedly.",
            "how_your_choice_landed": "You prevented a worse outcome for Jordan, but not enough hidden cost in the rest of the cluster was reduced.",
            "assessment_from_your_starting_point": "This is the pattern of a humane but too symptom-focused run.",
            "what_it_meant_for_your_trajectory": "The launch survived, but the team paid more than it should have.",
        },
    },
    "more_strain_than_needed": {
        "overall": {
            "overall_assessment": "Your judgment improved as the situation unfolded, but it needed to improve sooner.",
            "management_pattern": "You corrected into the right read after the surrounding cluster had already carried avoidable spread.",
            "kpi_review": "You recovered the launch, but only after the team had paid a cost that stronger early management would have reduced.",
        },
        1: {
            "what_the_situation_called_for": "Week 1 asked whether Jordan was the whole problem or the clearest signal of something broader.",
            "how_your_choice_landed": "You didn’t fully establish the strongest read, but you did avoid a worse start.",
            "assessment_from_your_starting_point": "You responded in a way that kept the situation workable without yet changing the shape of the problem.",
            "what_it_meant_for_your_trajectory": "This left room for recovery.",
        },
        2: {
            "what_the_situation_called_for": "By week 2, the launch was asking for a wider read of the surrounding pocket, not just more attention on Jordan.",
            "how_your_choice_landed": "You were not yet ahead of the problem, but you did begin to act in a way that made later recovery possible.",
            "assessment_from_your_starting_point": "This was not the ideal route, but it was a sound move from where you had already taken the launch.",
            "what_it_meant_for_your_trajectory": "Your management started to improve without yet fully changing the run’s direction.",
        },
        3: {
            "what_the_situation_called_for": "Week 3 required a shift from symptom management to cluster stabilisation.",
            "how_your_choice_landed": "This is the week your management improved in a meaningful way.",
            "assessment_from_your_starting_point": "The best strategy would have been to widen your read earlier. However, given the position you had already created, your choice this week was sound.",
            "what_it_meant_for_your_trajectory": "This began to recover the situation rather than simply containing the symptom.",
        },
        4: {
            "what_the_situation_called_for": "By week 4, the launch needed continued action at the level of the cluster rather than a return to the visible focal point alone.",
            "how_your_choice_landed": "Given the amount of spread already in the system, this was a good recovery decision.",
            "assessment_from_your_starting_point": "It did not put you on the strongest route overall, but it did improve the launch from the state you had already created.",
            "what_it_meant_for_your_trajectory": "This strengthened recovery and stopped the run sliding backward.",
        },
        5: {
            "what_the_situation_called_for": "Week 5 called for consolidation of the broader read you had started to develop.",
            "how_your_choice_landed": "This was another week where your management improved relative to the position you had already created.",
            "assessment_from_your_starting_point": "The stronger overall route would still have made this easier earlier. However, from your actual starting point this week, your decision was sound.",
            "what_it_meant_for_your_trajectory": "That deserves recognition because it helped contain further spread.",
        },
        6: {
            "what_the_situation_called_for": "The final week called for holding the wider pattern in view all the way to launch, even though earlier costs could no longer be erased.",
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
            "what_the_situation_called_for": "Week 1 called for treating Jordan as the clearest signal, not the whole story.",
            "how_your_choice_landed": "You acted early enough at the surrounding level that the launch pressure had less room to harden into a local cluster problem.",
            "assessment_from_your_starting_point": "That gave you the strongest opening position of any route.",
            "what_it_meant_for_your_trajectory": "This was the right read for the conditions.",
        },
        2: {
            "what_the_situation_called_for": "Week 2 called for reinforcing the wider cluster, not doubling down on Jordan alone.",
            "how_your_choice_landed": "You continued to act at the level the pressure was actually forming, which stopped the launch group becoming more brittle than the headline symptoms suggested.",
            "assessment_from_your_starting_point": "This is what early pattern recognition looks like in practice.",
            "what_it_meant_for_your_trajectory": "You were strengthening trajectory, not just reacting to symptoms.",
        },
        3: {
            "what_the_situation_called_for": "Week 3 was where weaker runs become reactive and stronger runs become more contained.",
            "how_your_choice_landed": "You recognized that the launch pressure was now a cluster problem and intervened accordingly.",
            "assessment_from_your_starting_point": "That protected the quieter people around Jordan and reduced the chance of the group hardening into crisis.",
            "what_it_meant_for_your_trajectory": "This was strong strategic and tactical management.",
        },
        4: {
            "what_the_situation_called_for": "Week 4 required keeping the intervention at the level of the cluster, not collapsing back toward the visible symptom.",
            "how_your_choice_landed": "You did that.",
            "assessment_from_your_starting_point": "The result was not the removal of pressure, but the prevention of avoidable spread.",
            "what_it_meant_for_your_trajectory": "This is what good mid-scenario management looks like: not dramatic, but pattern-aware and steadying.",
        },
        5: {
            "what_the_situation_called_for": "By week 5, stronger runs are easier to spot because the surrounding group is not carrying as much hidden cost.",
            "how_your_choice_landed": "Your earlier and ongoing cluster-level decisions continued to pay off here.",
            "assessment_from_your_starting_point": "This was not about eliminating pressure, but about stopping it from becoming quietly cumulative.",
            "what_it_meant_for_your_trajectory": "That is why the launch remained controlled rather than merely survived.",
        },
        6: {
            "what_the_situation_called_for": "The final week called for a launch that was still under pressure, but no longer being carried by avoidable hidden strain in the cluster.",
            "how_your_choice_landed": "You maintained the broader read all the way through the run.",
            "assessment_from_your_starting_point": "That let you reduce spread, protect the quieter carriers, and keep the launch closer to target.",
            "what_it_meant_for_your_trajectory": "This is the pattern the scenario is designed to teach.",
        },
    },
}


SCENARIO_01_END_SCREEN_COPY = {
    "spiralled": {
        "outcome": "Management Review: The launch was not controlled well enough.",
        "management_pattern": "You never established control of the real pattern driving the launch.",
        "what_you_did_well": "You were not ignoring pressure altogether, but your response stayed too close to what was easiest to see.",
        "what_limited_the_result": "The surrounding delivery cluster hardened faster than you contained it, and from that point the team was largely paying in quiet compensation.",
        "kpi_review": "Average core-group strain finished well above target, which is not a result we should be comfortable with.",
        "development_point": "The management step you missed was widening your read beyond Jordan before the cluster around him became the real problem.",
    },
    "high_strain_count": {
        "outcome": "Management Review: You got the launch through, but not strongly enough.",
        "management_pattern": "You responded responsibly to visible strain, but your management stayed too close to the loudest symptom.",
        "what_you_did_well": "You did not look away from the human pressure in front of you, which mattered.",
        "what_limited_the_result": "The launch got through because the wider cluster carried more strain than it should have had to, and that is where your read stayed too narrow.",
        "kpi_review": "You kept the launch moving, but you finished above target and above the standard we should be aiming for.",
        "development_point": "The stronger managerial move would have been to treat Jordan as the signal and take control of the group around him sooner.",
    },
    "more_strain_than_needed": {
        "outcome": "Management Review: You recovered the situation, but later than we would want.",
        "management_pattern": "You improved your read and started managing the wider cluster, but only after the situation had already become more expensive than it needed to be.",
        "what_you_did_well": "You did correct course rather than staying trapped in your first read, and that mattered to the final outcome.",
        "what_limited_the_result": "By the time you widened the frame, some avoidable spread had already moved through the group and could no longer be fully undone.",
        "kpi_review": "You came closer to target, but the team still ended up carrying strain that stronger early management would have reduced.",
        "development_point": "The next step is speed of diagnosis. You need to get to that broader read before the cluster has to recover from it.",
    },
    "well_done": {
        "outcome": "Management Review: This was a strong piece of management under pressure.",
        "management_pattern": "You identified the local cluster pattern early and managed the launch at the level it actually needed.",
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
            "week_end": "By this point, the launch needed more active intervention than it got.",
            "analysis": "By week 2, the bigger problem was not just the quality of the move, but that the group was still being left to carry the pattern largely on its own.",
        },
        "weak": {
            "week_end": "This didn’t do enough to steady the group around the visible pressure.",
            "analysis": "By week 2, this was too limited for the shape the problem was taking.",
        },
        "acceptable": {
            "week_end": "This made tactical sense, but it still left the wider cluster under-addressed.",
            "analysis": "Given where the launch had moved by this point, this was understandable but still partial.",
        },
        "strong": {
            "week_end": "This was a strong way to steady the launch before the pattern hardened further.",
            "analysis": "By week 2, this was a strong decision because it acted before the cluster became much harder to recover.",
        },
    },
    3: {
        "no_action": {
            "week_end": "At the pivot point of the launch, we needed a more active attempt to steady the cluster than that.",
            "analysis": "Week 3 was the turning point, and the bigger issue here was that you did not meaningfully intervene at the level the problem had reached.",
        },
        "weak": {
            "week_end": "This came in below what the launch needed at the point it was beginning to harden.",
            "analysis": "Week 3 was the pivot point, and this was too weak for the conditions.",
        },
        "acceptable": {
            "week_end": "This was a sensible move from a weaker position, even if it wasn’t the strongest route overall.",
            "analysis": "The best strategy would have been to shift earlier. However, given your starting point this week, this was sound.",
        },
        "strong": {
            "week_end": "This was the right level of intervention for the turning point of the launch.",
            "analysis": "Week 3 was where the scenario turned, and this was a strong decision because it matched the real level of the problem.",
        },
    },
    4: {
        "no_action": {
            "week_end": "By week 4, the launch needed a firmer stabilising move than that.",
            "analysis": "At this stage, the underlying problem was that the launch pocket was still not being actively steadied.",
        },
        "weak": {
            "week_end": "This didn’t reduce the fragility that had built up around the launch group.",
            "analysis": "By week 4, this was weaker than the situation required and did little to change the run’s shape.",
        },
        "acceptable": {
            "week_end": "This was a reasonable correction from where the team had already reached.",
            "analysis": "Given the strain already in the system, this was a sound corrective move, even though it came after avoidable spread.",
        },
        "strong": {
            "week_end": "This was a strong stabilising move at a point when the cluster could easily have become much more brittle.",
            "analysis": "By week 4, this was a strong decision because it reduced spread rather than merely tolerating it.",
        },
    },
    5: {
        "no_action": {
            "week_end": "This late in the run, leaving the group to absorb the pressure was always going to be costly.",
            "analysis": "By week 5, the main issue was that the cluster was still being asked to carry too much without enough intervention.",
        },
        "weak": {
            "week_end": "This left too much quiet cost sitting in the group this late in the run.",
            "analysis": "By week 5, this was too weak because it asked the team to keep carrying pressure rather than reducing it.",
        },
        "acceptable": {
            "week_end": "This helped contain the situation from where it was, even if it could no longer undo earlier cost.",
            "analysis": "Given your starting point this week, this was a sensible containment move.",
        },
        "strong": {
            "week_end": "This was a strong way to keep the final stretch from becoming more expensive than it already was.",
            "analysis": "Late in the run, this was strong because it reduced further spread rather than letting the cluster harden again.",
        },
    },
    6: {
        "no_action": {
            "week_end": "In the final week, there was too much already sitting in the group to leave it there.",
            "analysis": "By the final week, the larger gap was that the team was still carrying too much of the cost without enough intervention.",
        },
        "weak": {
            "week_end": "This was too little, too late to change the final shape of the launch.",
            "analysis": "In the final week, this was a weak response because it did not alter the real cost the cluster was carrying.",
        },
        "acceptable": {
            "week_end": "This was a fair move from the position you had reached, even if the larger result was already constrained.",
            "analysis": "Given the final-week starting point, this was sound, though it could not fully overcome what had built up earlier.",
        },
        "strong": {
            "week_end": "This was a strong final-week decision and helped the launch land better than it otherwise would have.",
            "analysis": "In the final week, this was strong because it made the best of the situation you had created and reduced avoidable extra cost.",
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


def scenario_weekly_briefing(scenario_key, week):
    if scenario_key == "scenario_01":
        return SCENARIO_01_MAIN_SCREEN_COPY.get(week, {})
    return {}


def scenario_main_screen_aside(game):
    if game.scenario != "scenario_01" or game.week <= 1:
        return ""
    history = game.get_analysis_history()
    if not history:
        return ""
    prior_snapshot = history[-1]
    prior_path = scenario_weekly_narrative_path(game, history, prior_snapshot)
    if not prior_path:
        return ""
    return SCENARIO_01_MAIN_SCREEN_ASIDES.get(game.week, {}).get(prior_path, "")


def scenario_narrative_path(game, history, latest, benchmark_history, benchmark_latest):
    if game.scenario != "scenario_01":
        if (latest or {}).get("scenario_outcome_tier") == "Fail":
            return "spiralled"
        return determine_summary_branch(game, history, latest, benchmark_history, benchmark_latest)

    if (latest or {}).get("scenario_outcome_tier") == "Fail":
        return "spiralled"

    snapshots_by_week = {
        snapshot.get("week"): snapshot
        for snapshot in (history or [])
        if snapshot.get("week") is not None
    }

    def flags_for(week):
        return _scenario_01_action_flags(snapshots_by_week.get(week, {}))

    well_done = (
        flags_for(1)["individual_on_focal"] and flags_for(1)["coordination_on_focal"]
        and flags_for(2)["individual_on_focal"] and flags_for(2)["coordination_on_focal"]
        and flags_for(3)["coordination_on_focal"] and flags_for(3)["individual_on_hidden"]
        and flags_for(4)["coordination_on_focal"] and flags_for(4)["individual_on_hidden"]
        and flags_for(5)["any_on_focal"]
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

    return determine_summary_branch(game, history, latest, benchmark_history, benchmark_latest)


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


def scenario_weekly_narrative_path(game, history, snapshot):
    if game.scenario != "scenario_01" or not snapshot:
        return None

    flags = _scenario_01_action_flags(snapshot)
    if flags["no_actions"]:
        return "spiralled"

    week = snapshot.get("week")
    prior_path = _scenario_01_prior_weekly_path(game, history, snapshot)

    if week in {1, 2}:
        if flags["individual_on_focal"] and flags["coordination_on_focal"]:
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
        if prior_path == "well_done" and flags["any_on_focal"]:
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


def scenario_week_end_report(game, snapshot, previous_snapshot, benchmark_history, benchmark_latest):
    if not snapshot or not previous_snapshot or game.scenario != "scenario_01":
        return None
    history = game.get_analysis_history()
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
    if game.scenario != "scenario_01":
        return None
    path = scenario_narrative_path(game, history, latest, benchmark_history, benchmark_latest)
    return SCENARIO_01_END_SCREEN_COPY.get(path)

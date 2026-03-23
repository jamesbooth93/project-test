SCENARIO_02_WORKSHOP_MOCK = {
    "title": "Client Demo Spillover",
    "premise": (
        "A team is preparing for an important client demo. The visible strain is real, "
        "but it may not be the whole story."
    ),
    "instruction": (
        "Each group will make choices from partial information. The goal is to notice "
        "how misalignment grows over time."
    ),
    "roles": [
        {"name": "Manager", "summary": "Sets the response and tone for the team."},
        {"name": "Riley", "summary": "Carries visible strain and looks for relief through deviance."},
        {"name": "Maya", "summary": "Quietly absorbs hidden rescue work and decides whether to surface it."},
    ],
    "checkpoints": [
        {
            "id": "week_1_manager",
            "heading": "Week 1: Set Up The Demo",
            "kicker": "Project Brief",
            "narrative": (
                "We are six weeks out from an important client demo. Riley's work has been arriving "
                "unevenly, details are slipping, and frustration is building around avoidable rework. "
                "The week is still getting over the line, but some of the cleanup and clarification "
                "seems to be landing elsewhere in the team. Riley is drawing most of the attention "
                "right now, but I am not convinced that tells the whole story."
            ),
            "signals": [
                "Riley is the clearest visible source of friction.",
                "The work is still moving, but not cleanly.",
                "Some of the rescue work seems to be happening out of sight.",
            ],
            "facilitator": [
                "What seems most obvious?",
                "What feels most urgent?",
                "Who are you most worried about?",
            ],
            "minutes": {
                "weak": {
                    "agreed": "The immediate focus stayed on Riley's uneven work and the need to reduce visible pressure quickly.",
                    "visible": "Riley remained the clearest source of friction across the fortnight, which made it easy for the team to keep reading the issue through Riley first.",
                    "quiet": "More of the clarification, cleanup, and rescue work continued to route through Maya in the background, which helped the work still land but hid how much extra carrying the fortnight depended on.",
                    "meaning": "The fortnight held together, but more by private adaptation than shared alignment. The visible problem stayed at the center of attention while the deeper cost moved elsewhere.",
                },
                "partial": {
                    "agreed": "The response stayed partly with Riley, but there was some attention on how the wider flow around the demo was starting to become harder to carry cleanly.",
                    "visible": "Riley still drew most of the attention across the fortnight, though it became a little clearer that the visible strain was not the whole story.",
                    "quiet": "Maya continued to absorb some of the background repair work, but the underlying dependency became slightly easier to notice than it had been at the start.",
                    "meaning": "The fortnight remained pressured, but there was more evidence now that the issue sat in the pattern around the work, not only in Riley's visible wobble.",
                },
                "strong": {
                    "agreed": "The response treated Riley as a real concern, but not the whole problem, and started asking where the hidden cost of the fortnight was actually landing.",
                    "visible": "Riley remained a live pressure signal, but the team was less likely to mistake that visible strain for the whole issue.",
                    "quiet": "Some hidden support work still landed with Maya, but it became more discussable and less likely to deepen unnoticed.",
                    "meaning": "The fortnight did not become easy, but it became better read. The work moved with less dependence on invisible rescue and more awareness of where the real risk was forming.",
                },
            },
            "roles": [
                {
                    "role_id": "manager",
                    "title": "What do you do first?",
                    "prompt": "Manager, write down what you think is happening and what you would do first.",
                    "options": [
                        {
                            "id": "steady_riley",
                            "label": "Steady Riley directly",
                            "body": "Check in with Riley, reduce immediate pressure, and help them get through the week.",
                            "score": 1,
                        },
                        {
                            "id": "support_and_investigate",
                            "label": "Support Riley and investigate workflow",
                            "body": "Support Riley, but also look at where cleanup, clarification, and rescue work is actually going.",
                            "score": 3,
                        },
                        {
                            "id": "delivery_discipline",
                            "label": "Push for tighter delivery discipline",
                            "body": "Make expectations clearer, tighten execution, and ask the team to clean up handoffs immediately.",
                            "score": 0,
                        },
                        {
                            "id": "workflow_reset",
                            "label": "Reset the workflow at team level",
                            "body": "Bring the team together quickly to clarify ownership and reduce ambiguity around the demo.",
                            "score": 2,
                        },
                    ],
                },
            ],
        },
        {
            "id": "week_1_employee",
            "heading": "Week 1: How The Team Responds",
            "kicker": "Employee Response",
            "narrative": (
                "The manager has set the initial tone. Riley now has to get through the week "
                "while feeling exposed and behind. Maya can already see that extra translation, "
                "cleanup, and rescue work is building, but saying that out loud may make the week "
                "harder in the short term."
            ),
            "signals": [
                "Riley has recently returned from an extended absence.",
                "Maya can already see the hidden support work building.",
                "The team still looks functional from the outside.",
            ],
            "facilitator": [
                "What gives Riley the quickest relief?",
                "What feels hardest for Maya to say out loud?",
                "What are both of them trying to protect this week?",
            ],
            "minutes": {
                "weak": {
                    "agreed": "The initial direction stayed close to the visible issue, and the employee responses widened the gap between what looked manageable and what was actually being carried.",
                    "visible": "Riley's strain remained the most legible part of the fortnight, which made it easy for everyone else to orient around what was loudest.",
                    "quiet": "Maya kept the work moving by absorbing ambiguity and cleanup that did not yet feel discussable enough to name directly.",
                    "meaning": "The fortnight still landed, but it did so by asking one person to leak strain visibly and another to quietly contain the cost of it.",
                },
                "partial": {
                    "agreed": "The employee responses made it a little easier to see that the week was being held together in more than one place, even if that truth was still incomplete.",
                    "visible": "Riley remained the clearest signal, but there were early signs now that the visible strain was creating hidden work around it.",
                    "quiet": "Maya carried some of the same background work as before, though more of that pattern became thinkable and discussable.",
                    "meaning": "The fortnight stayed workable, but not because the underlying issue had properly settled. The room now had more reason to widen its read next time.",
                },
                "strong": {
                    "agreed": "The employee responses helped keep the human side of the week visible without letting the visible strain become the whole story.",
                    "visible": "Riley's pressure was still real, but it was less likely to dominate interpretation on its own.",
                    "quiet": "Maya still carried some hidden work, but more of it entered the shared picture early enough to reduce how much it had to stay private.",
                    "meaning": "The fortnight remained pressured, but it moved with more honesty and less dependence on invisible adaptation than it otherwise would have.",
                },
            },
            "roles": [
                {
                    "role_id": "riley",
                    "title": "How do you get through this week?",
                    "prompt": "Riley is under visible pressure. The healthiest option may not feel emotionally available.",
                    "options": [
                        {
                            "id": "call_in_sick",
                            "label": "Call in sick",
                            "body": "Get out of the week completely and take immediate relief.",
                            "score": 0,
                            "intent": "self-protective relief",
                        },
                        {
                            "id": "miss_alignment",
                            "label": "Miss the alignment meeting",
                            "body": "Avoid the pressure for now and buy a little space.",
                            "score": 1,
                            "intent": "avoidance under overwhelm",
                        },
                        {
                            "id": "push_back",
                            "label": "Push back sharply in review",
                            "body": "Protect yourself by making it clear you are already under too much pressure.",
                            "score": 1,
                            "intent": "defensive self-protection",
                        },
                        {
                            "id": "rush_work",
                            "label": "Rush the work and deal with fallout later",
                            "body": "Get something over the line quickly and hope the pressure comes off.",
                            "score": 2,
                            "intent": "strained attempt to regain control",
                        },
                    ],
                },
                {
                    "role_id": "maya",
                    "title": "What do you do with what you are noticing?",
                    "prompt": "Maya can already see extra cleanup, translation, and rescue work building under the surface.",
                    "options": [
                        {
                            "id": "absorb_quietly",
                            "label": "Quietly absorb it and keep the week moving",
                            "body": "Carry the hidden work privately so the team can stay on track.",
                            "score": 0,
                        },
                        {
                            "id": "hint_friction",
                            "label": "Hint that the flow is messy",
                            "body": "Suggest there is friction, but do not fully spell out how much is routing through you.",
                            "score": 1,
                        },
                        {
                            "id": "name_hidden_work",
                            "label": "Name that hidden support work is building",
                            "body": "Say clearly that extra cleanup and informal rescue work are becoming part of the pattern.",
                            "score": 2,
                        },
                        {
                            "id": "pattern_unsustainable",
                            "label": "Say clearly the current pattern is unsustainable",
                            "body": "Make it explicit that the team is solving the week by privately consuming capacity.",
                            "score": 3,
                        },
                    ],
                },
            ],
        },
        {
            "id": "week_3",
            "heading": "Two Weeks Later",
            "kicker": "Checkpoint",
            "narrative": (
                "The demo is still on track enough that no one is openly panicking, but the same "
                "problems have kept repeating. Riley is still the loudest signal in the room. What "
                "has changed is that the work now seems to keep landing because people are compensating "
                "around the problem rather than because the flow is getting cleaner."
            ),
            "signals": [
                "Riley is still the loudest signal in the room.",
                "The same friction is repeating, not resolving.",
                "More of the week seems to depend on quiet rescue work.",
                "The team is still functioning, which makes the dependency easier to miss.",
            ],
            "facilitator": [
                "What has repeated since week 1?",
                "What are we mistaking for stability?",
                "What would real alignment look like now?",
            ],
            "minutes": {
                "weak": {
                    "agreed": "The response stayed mostly with Riley and the visible problem, with the main aim being to keep the demo work moving without creating more immediate disruption.",
                    "visible": "Riley remained the easiest place to focus concern. Friction around review, detail, and responsiveness became more socially legible across the fortnight, which made the visible problem feel even more convincing.",
                    "quiet": "More of the clarification, translation, and recovery work continued to route through Maya. By this point, that was no longer just helpfulness. It was becoming part of how the fortnight functioned.",
                    "meaning": "The team still got through the fortnight, but by compensating around the same problem rather than reducing the dependency behind it. The system was starting to confuse endurance with control.",
                },
                "partial": {
                    "agreed": "The response began to widen beyond Riley, though not enough to fully change how the fortnight was being carried.",
                    "visible": "Riley was still the loudest signal in the room, but it became harder to ignore that the same friction was repeating rather than resolving.",
                    "quiet": "Maya was still absorbing too much of the hidden cost, though there was now more evidence that the week was being held together by private carrying rather than a genuinely cleaner flow.",
                    "meaning": "The fortnight remained workable, but the deeper pattern was now easier to see. The question was no longer whether there was strain, but whether the team was acting on where it was really landing.",
                },
                "strong": {
                    "agreed": "The response treated Riley as a real pressure signal while also asking directly where the hidden cost of the fortnight was being carried.",
                    "visible": "Riley remained visibly strained, but the team was less likely to mistake that visible friction for the whole problem.",
                    "quiet": "Maya was still carrying some extra repair work, but more of that hidden load was now visible and less likely to keep deepening without being named.",
                    "meaning": "The fortnight still required active management, but the team was beginning to respond at the level of the pattern rather than the loudest symptom. The underlying dependency had not gone away, but it was less hidden than before.",
                },
            },
            "roles": [
                {
                    "role_id": "manager",
                    "title": "What do you do now?",
                    "prompt": "The original problem has not gone away. The pattern is now repeating.",
                    "options": [
                        {
                            "id": "keep_supporting_riley",
                            "label": "Keep supporting Riley directly",
                            "body": "Stay close to Riley and keep trying to steady the visible problem.",
                            "score": 1,
                        },
                        {
                            "id": "investigate_dependency",
                            "label": "Support Riley and directly investigate dependency",
                            "body": "Support Riley, but also look closely at who is catching the hidden cost and holding the week together.",
                            "score": 3,
                        },
                        {
                            "id": "lean_on_dependables",
                            "label": "Lean harder on dependable people",
                            "body": "Ask the people already keeping things stable to help the team push through the next fortnight.",
                            "score": 0,
                        },
                        {
                            "id": "clarify_handoffs",
                            "label": "Clarify handoffs and reduce exception-routing",
                            "body": "Treat this as a workflow pattern, not just one person struggling.",
                            "score": 2,
                        },
                    ],
                },
                {
                    "role_id": "riley",
                    "title": "How do you get through this phase?",
                    "prompt": "Riley now feels watched, judged, and less able to recover cleanly.",
                    "options": [
                        {
                            "id": "call_in_sick",
                            "label": "Call in sick",
                            "body": "Drop out of the week and get immediate relief.",
                            "score": 0,
                            "intent": "self-protective relief",
                        },
                        {
                            "id": "miss_meeting_again",
                            "label": "Miss another key meeting",
                            "body": "Avoid the pressure for a bit longer and hope someone else catches the gap.",
                            "score": 0,
                            "intent": "avoidance under escalating overwhelm",
                        },
                        {
                            "id": "snap_in_review",
                            "label": "Push back sharply when challenged",
                            "body": "Defend yourself in the moment so you do not keep absorbing it quietly.",
                            "score": 1,
                            "intent": "defensive relief",
                        },
                        {
                            "id": "rush_decisions",
                            "label": "Rush decisions and create downstream cleanup",
                            "body": "Get something through quickly and let the rest get dealt with later.",
                            "score": 2,
                            "intent": "regain control through speed",
                        },
                    ],
                },
                {
                    "role_id": "maya",
                    "title": "What do you do now?",
                    "prompt": "Maya can now see this is no longer a rough patch. The same hidden work is repeating.",
                    "options": [
                        {
                            "id": "keep_carrying",
                            "label": "Keep carrying it quietly",
                            "body": "Hold it together privately because the demo still feels too close to disrupt.",
                            "score": 0,
                        },
                        {
                            "id": "mention_heavy",
                            "label": "Mention that things feel heavy",
                            "body": "Signal that the team is stretched, but still do not make the hidden dependency fully visible.",
                            "score": 1,
                        },
                        {
                            "id": "name_rescue_work",
                            "label": "Say clearly that rescue work is routing through you",
                            "body": "Name that the team is functioning by privately consuming your capacity.",
                            "score": 2,
                        },
                        {
                            "id": "ask_structural_change",
                            "label": "Say the pattern is unsustainable and ask for structural change",
                            "body": "Make it explicit that the current way of carrying the work cannot continue.",
                            "score": 3,
                        },
                    ],
                },
            ],
        },
        {
            "id": "week_5",
            "heading": "Final Stretch",
            "kicker": "Checkpoint",
            "narrative": (
                "The demo is now close enough that everyone is protecting momentum. From the outside, "
                "the situation may even look slightly better in places. That does not necessarily mean "
                "the team is healthier. At this stage, the more important question is what the team is "
                "spending to keep the work moving."
            ),
            "signals": [
                "Visible calm may be misleading at this stage.",
                "The work is either stabilising, or being quietly held together.",
                "Riley is still a live signal, but no longer the whole story.",
                "Maya's carrying is now either reducing, or becoming structurally necessary.",
            ],
            "facilitator": [
                "What is making the team look functional right now?",
                "What has actually improved, and what is just being absorbed?",
                "If the demo lands, what might still have gone wrong?",
            ],
            "minutes": {
                "weak": {
                    "agreed": "The response stayed close to keeping the demo moving, with the visible problem still receiving most of the practical attention.",
                    "visible": "From the outside, the situation may have looked slightly calmer in places, but the team was still reacting more to Riley's visible strain than to the pattern that had built around it.",
                    "quiet": "By now, Maya's hidden work had become part of what was making the final stretch possible. The fortnight held together partly because she kept translating, smoothing, and catching what would otherwise have broken more openly.",
                    "meaning": "The work kept moving, but at a higher human cost than it appeared. The team was no longer just managing pressure; it was privately consuming capacity to preserve the appearance of stability.",
                },
                "partial": {
                    "agreed": "The response began to acknowledge the hidden dependency more directly, even if some of the old pattern remained in place.",
                    "visible": "Riley was still a live concern, but the visible signal no longer explained the whole state of the fortnight on its own.",
                    "quiet": "Maya was still carrying too much, though by now the cost of that carrying was harder to dismiss as just being dependable or helpful.",
                    "meaning": "The final stretch became better understood, but not fully repaired. Some of the hidden cost was already built into the run by this point, even where the team had begun to see it more clearly.",
                },
                "strong": {
                    "agreed": "The response acted directly on the hidden dependency and treated the final stretch as something that needed to be carried differently, not just more bravely.",
                    "visible": "Riley remained a visible signal, but less of the team's interpretation now sat entirely with Riley's behavior.",
                    "quiet": "Some hidden work still existed, but Maya was less likely to remain the private container for everything the system had failed to clarify earlier.",
                    "meaning": "The final stretch still had pressure in it, but it no longer depended as heavily on invisible rescue work to remain functional. The team moved closer to alignment before the human cost hardened completely.",
                },
            },
            "roles": [
                {
                    "role_id": "manager",
                    "title": "What do you do now?",
                    "prompt": "This is the point where appreciating the effort is not the same as changing the pattern.",
                    "options": [
                        {
                            "id": "trust_team_finish",
                            "label": "Keep supporting Riley and trust the team to finish",
                            "body": "Support Riley and rely on the stronger people in the team to get the demo over the line.",
                            "score": 0,
                        },
                        {
                            "id": "reduce_dependence_maya",
                            "label": "Act on the hidden dependency directly",
                            "body": "Reduce the load being routed through Maya and stop solving the demo through quiet rescue work.",
                            "score": 3,
                        },
                        {
                            "id": "thank_maya_push",
                            "label": "Thank Maya and ask for one more push",
                            "body": "Acknowledge what Maya is doing and ask the team to get through the final stretch as they are.",
                            "score": 1,
                        },
                        {
                            "id": "redistribute_and_clarify",
                            "label": "Redistribute work and make invisible rescue visible",
                            "body": "Reset how the final stretch is being carried so the team is not depending on one person's private effort.",
                            "score": 2,
                        },
                    ],
                },
                {
                    "role_id": "riley",
                    "title": "How do you get through the final stretch?",
                    "prompt": "Healthier options may technically exist, but they no longer feel believable from inside the strain.",
                    "options": [
                        {
                            "id": "call_in_sick",
                            "label": "Call in sick",
                            "body": "Drop out completely and try to get immediate relief.",
                            "score": 0,
                            "intent": "collapse into relief",
                        },
                        {
                            "id": "withdraw_bare_minimum",
                            "label": "Withdraw and do the bare minimum",
                            "body": "Keep your head down and say as little as possible.",
                            "score": 1,
                            "intent": "protective narrowing",
                        },
                        {
                            "id": "snap_again",
                            "label": "Snap at pressure and create visible friction",
                            "body": "Push back hard enough that people stop pressing on the overloaded part of you.",
                            "score": 1,
                            "intent": "defensive boundary through conflict",
                        },
                        {
                            "id": "push_through_fast",
                            "label": "Push something through too quickly",
                            "body": "Get it out of your hands and let someone else catch the fallout.",
                            "score": 2,
                            "intent": "strained relief through speed and deferral",
                        },
                    ],
                },
                {
                    "role_id": "maya",
                    "title": "What do you do now?",
                    "prompt": "By now Maya knows the pattern is real. Keeping quiet and protecting the appearance of stability are no longer the same thing as helping.",
                    "options": [
                        {
                            "id": "carry_to_finish",
                            "label": "Keep carrying it and get the team through the demo",
                            "body": "Hold the hidden work privately and deal with the cost later.",
                            "score": 0,
                        },
                        {
                            "id": "say_stretched_keep_carrying",
                            "label": "Say you are stretched, but keep absorbing the work",
                            "body": "Be more honest that you are feeling it, but still keep the system moving yourself.",
                            "score": 1,
                        },
                        {
                            "id": "make_hidden_work_visible",
                            "label": "Make the hidden work visible",
                            "body": "Explain clearly what you have been catching and why that pattern is now too costly.",
                            "score": 2,
                        },
                        {
                            "id": "stop_protecting_appearance",
                            "label": "Stop protecting the appearance of stability",
                            "body": "Say plainly that the team cannot keep solving the demo by consuming private capacity.",
                            "score": 3,
                        },
                    ],
                },
            ],
        },
    ],
    "review_copy": {
        "aligned": {
            "title": "Aligned",
            "outcome": "The team moved back toward alignment early enough to reduce hidden cost and dependency.",
            "manager": "You widened your read beyond the most visible issue and acted on the real dependency in the team.",
            "maya": "You surfaced what you were actually carrying before private effort became the only thing holding the work together.",
            "riley": "Your behavior still reflected strain, but the system around you became better able to interpret and carry that strain without turning it into the whole story.",
            "shared": "The team did not remove pressure, but it did move back toward alignment early enough that pressure did not keep turning into hidden cost.",
        },
        "misaligned_manager": {
            "title": "Misaligned Manager",
            "outcome": "Important truth was present in the system, but leadership stayed too close to the visible problem for too long.",
            "manager": "Your decisions remained too focused on Riley and the surface story, even when stronger signals pointed to a wider dependency pattern.",
            "maya": "Enough truth was available to widen the read, but it did not translate into strong enough system action.",
            "riley": "Your visible strain kept drawing attention, partly because the team did not stop treating you as the main object of intervention.",
            "shared": "Stress remained high because reality was entering the system, but leadership kept responding at the wrong level.",
        },
        "misaligned_employee": {
            "title": "Misaligned Employee",
            "outcome": "Leadership created more room for alignment than the team was able to use.",
            "manager": "You began to look beyond the obvious signal and created better conditions for the real issue to be surfaced.",
            "maya": "Too much of the hidden load remained privately carried. By continuing to protect the team from the truth, you also protected the misalignment.",
            "riley": "Your strain stayed visible, but the team had more opportunity to interpret it properly than it could fully act on because the hidden pattern never became clear enough soon enough.",
            "shared": "Stress remained elevated because leadership improved, but too much reality stayed unspoken inside the team.",
        },
        "total_misalignment": {
            "title": "Total Misalignment",
            "outcome": "The demo may still have moved forward, but the team got there by privately consuming capacity instead of restoring alignment.",
            "manager": "Your choices stayed too close to what was easiest to see, which meant the deeper pattern had too much time to harden.",
            "maya": "By continuing to carry the team privately, you made the work look more stable than it really was.",
            "riley": "Your behavior moved further away from what the team needed, but it did so as a form of relief-seeking under pressure, not because you stopped caring.",
            "shared": "This is what stress looks like when visible strain, hidden strain, and leadership interpretation all drift apart at once.",
        },
        "riley_note": (
            "Riley's lower alignment score does not mean low commitment. It means that as pressure rose, "
            "the options that felt available became more self-protective and less compatible with what "
            "the team needed. The behavior drifted, but the intention was relief, not malice."
        ),
    },
}

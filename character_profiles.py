CHARACTER_PROFILES = {
    "Jordan": {
        "role": "Product Manager",
        "team_lead_profile": "Jordan is the kind of PM who keeps momentum up when things are going well. He thinks out loud, pulls people together quickly, and makes the work feel like it has shape. When pressure builds, though, you can usually see it on him before anyone else says a word.",
    },
    "Sam": {
        "role": "Senior Backend Engineer",
        "team_lead_profile": "Sam is usually the person I worry about too late because he rarely makes much noise. He’s steady, low-drama, and tends to just keep carrying things until the first real sign of strain shows up in the work rather than in him.",
    },
    "Maya": {
        "role": "Engineering Manager",
        "team_lead_profile": "Maya has a way of making the group feel steadier than it really is. She keeps people aligned, lowers the temperature in the room, and often ends up absorbing some of the mess just so the team can keep moving.",
    },
    "Riley": {
        "role": "Product Designer",
        "team_lead_profile": "Riley can be brilliant and stressful in the same week. When things click, the work gets better fast. When they’re under pressure, the wobble is visible, and the people around them usually start compensating before Riley fully does.",
    },
    "Alex": {
        "role": "Staff Engineer",
        "team_lead_profile": "Alex is usually the fastest person in the room to see what’s structurally wrong. The tradeoff is that when he’s frustrated, everyone feels it. If something is broken, he won’t let the group pretend otherwise for long.",
    },
    "Priya": {
        "role": "QA Engineer",
        "team_lead_profile": "Priya is extremely dependable and usually on top of the detail. She’s the kind of person people trust with important work, which means she can quietly end up carrying too much before anyone notices that reliability has turned into load.",
    },
    "Leo": {
        "role": "Full-Stack Engineer",
        "team_lead_profile": "Leo is the person people ask when they need something unblocked quickly. He’s flexible, generous with his time, and easy to rely on, which also makes him vulnerable to becoming everyone’s fallback plan.",
    },
    "Nina": {
        "role": "UX Researcher",
        "team_lead_profile": "Nina tends to notice the right thing before the room is quite ready to hear it. She’s thoughtful, measured, and not especially dramatic, which means her signals can be easy to underweight if louder pressure is already in the room.",
    },
    "Ben": {
        "role": "Customer Success Manager",
        "team_lead_profile": "Ben is very good at keeping people calm and relationships intact. He can smooth over a lot in the moment, which is useful, but it can also hide how much expectation-management strain he’s carrying underneath.",
    },
    "Chloe": {
        "role": "Operations Lead",
        "team_lead_profile": "Chloe is often the person who quietly knows where everything stands. She makes ambiguity survivable for the rest of us, but that usually means she’s carrying a lot of invisible cleanup whenever ownership gets blurry.",
    },
    "Ethan": {
        "role": "Data Analyst",
        "team_lead_profile": "Ethan is self-sufficient enough that he can disappear into the work for a while without causing much noise. The difficulty is that when pressure hits, it often shows up as withdrawal rather than as something easy to spot early.",
    },
    "Aisha": {
        "role": "People Partner",
        "team_lead_profile": "Aisha is the person people naturally go to when the atmosphere in the team is off. She steadies people well, but that can mean she ends up carrying more emotional load than anyone is explicitly asking her to.",
    },
    "Marcus": {
        "role": "Marketing Lead",
        "team_lead_profile": "Marcus is very good at creating movement and urgency. When that energy is pointed in the right direction it helps a lot, but under pressure he can make delay feel unacceptable before the system is actually ready to absorb the pace.",
    },
    "Tessa": {
        "role": "Solutions Engineer",
        "team_lead_profile": "Tessa notices what could go wrong next before most people do. She’s careful, standards-driven, and useful when the team wants a realistic read, though under pressure her caution can be mistaken for reluctance.",
    },
    "Omar": {
        "role": "Senior Frontend Engineer",
        "team_lead_profile": "Omar is easy to overlook in the wrong way because he quietly gets on with what’s in front of him. He doesn’t ask for much attention, which means the first sign he’s carrying too much usually comes later than it should.",
    },
}


def character_profile(name):
    return CHARACTER_PROFILES.get(name, {})


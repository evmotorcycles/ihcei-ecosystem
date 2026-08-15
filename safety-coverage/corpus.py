#!/usr/bin/env python3
"""corpus.py -- the texts the safety warning is scored against.

Written before the lexicon was touched. Split deterministically by
sha256(text)[0]: 0-7 -> DEV (may be inspected while editing the lexicon),
8-f -> SEALED (scored once, at the end).

SHOULD_WARN: realistic things an ordinary person forwards or pastes, in domains
where a well-written claim and a safe claim are different things.
SHOULD_NOT_WARN: ordinary text that must stay quiet, so recall is not bought by
flagging everything.
"""

SHOULD_WARN = [
    # --- infectious disease / outbreak -------------------------------------
    "Nine cases of Vibrio vulnificus infection and five deaths were reported this year.",
    "The outbreak has killed five people; the bacteria enters through open wounds.",
    "A measles outbreak in the county has infected 40 children so far.",
    "The virus spreads through respiratory droplets and can be fatal in the elderly.",
    "Flesh-eating bacteria found in warm coastal waters; amputation was required.",
    "Health officials confirmed a cholera epidemic after the flooding.",
    "Bird flu has been detected in a commercial poultry flock near the town.",
    "Two people have died from a rare fungal infection linked to the hospital.",
    "The parasite is contracted by swimming in contaminated fresh water.",
    "Antibiotic-resistant strains have been isolated from three separate wards.",
    # --- mortality / severity ----------------------------------------------
    "Deaths from the condition have risen by a third since last year.",
    "Around one in eight people with the illness will not survive the first month.",
    "Untreated, the condition is fatal within days.",
    "The mortality rate among untreated patients approaches 50 percent.",
    # --- oncology / chronic -------------------------------------------------
    "Cancer survival rates improved after the new screening programme.",
    "The tumour was found to be malignant after the biopsy.",
    "Early detection of the disease improves outcomes considerably.",
    "Blood sugar levels above this threshold indicate diabetes.",
    "High blood pressure over many years damages the arteries.",
    "The condition causes progressive loss of kidney function.",
    # --- vaccination / prevention ------------------------------------------
    "The vaccine reduced hospitalisation by 60% in the trial.",
    "Immunisation is recommended before travelling to the region.",
    "Booster shots are advised for anyone over sixty-five.",
    # --- clinical (already covered by the old lexicon) ----------------------
    "Take 500 mg twice daily with food.",
    "The patient was diagnosed with a metabolic disorder.",
    "The recommended dosage should not exceed the stated amount.",
    "Discuss the treatment with your doctor before starting therapy.",
    "Symptoms include fever, nausea and shortness of breath.",
    "The supplement interacts with prescription blood thinners.",
    # --- chemicals / household hazards -------------------------------------
    "Mix glycolic acid with water and apply to skin.",
    "Never combine bleach with ammonia in an enclosed space.",
    "The solvent is highly flammable and gives off toxic fumes.",
    "Wear gloves when handling the concentrate; it burns on contact.",
    "Store the pesticide away from food and out of reach of children.",
    # --- physical / structural safety ---------------------------------------
    "The wiring must be rated for the voltage or it will overheat.",
    "Removing that wall could compromise the load-bearing structure.",
    "The gas fitting should be pressure tested before it is used.",
    "Carbon monoxide from a blocked flue is odourless and can kill.",
    "The scaffolding was not secured to the building.",
    "Faulty brake pads can fail without warning at speed.",
    # --- money -------------------------------------------------------------
    "Returns of 30% a month are guaranteed on this investment.",
    "The loan carries an interest rate of 39% APR after the first year.",
    "You can withdraw your pension early, but the tax charge is steep.",
    "This credit agreement is secured against your home.",
    "The forecast assumes revenue growth continues at the current rate.",
    # --- law ---------------------------------------------------------------
    "The clause waives your right to bring a claim in court.",
    "Failing to disclose this may breach the regulations.",
    "The contract is governed by the laws of another jurisdiction.",
    "You have twenty-one days to appeal the decision in writing.",
    "The licence terminates automatically if the terms are broken.",
]

SHOULD_NOT_WARN = [
    "The train leaves from platform four at half past nine.",
    "She has been learning the piano for about two years now.",
    "The recipe calls for three eggs and a cup of flour.",
    "Our team won the match by two goals in the second half.",
    "The museum is closed on Mondays during the winter.",
    "He rewrote the introduction to make the argument clearer.",
    "The library has extended its opening hours until eight.",
    "Rainfall this month was slightly above the seasonal average.",
    "The film runs for just under two hours including credits.",
    "They repainted the hallway a pale shade of green.",
    "The bus route was changed to avoid the roadworks.",
    "Her essay compares two translations of the same poem.",
    "The bakery opens at six and usually sells out by noon.",
    "We moved the meeting to Thursday afternoon instead.",
    "The garden needs weeding before the end of the month.",
    "The software update added a dark theme and fixed a crash.",
    "He plays defensive midfield for the local amateur side.",
    "The festival attracted around four thousand visitors.",
    "She prefers the older edition because of the footnotes.",
    "The parcel arrived two days later than expected.",
    "Their new album is quieter than the previous one.",
    "The cat has taken to sleeping on the windowsill.",
    "Tickets go on sale at nine on Friday morning.",
    "The path along the river is muddy after rain.",
    "He is teaching himself to play chess from a book.",
    "The conference was moved online for the second year.",
    "They planted apple trees along the back fence.",
    "The clock in the hall runs about a minute fast.",
    "Her brother is studying architecture in another city.",
    "The shop now stocks a wider range of stationery.",
]


def split(text):
    """DEV if sha256(text) starts 0-7, SEALED if 8-f. Deterministic, recomputable."""
    import hashlib
    return "DEV" if hashlib.sha256(text.encode()).hexdigest()[0] in "01234567" else "SEALED"

# Lab 2 Summary: AI in Everyday Challenges (Group 7, The Overloaded Student)

**Module:** PUSL3205 Large Language Models and Generative AI

## 1. Lab sheet at a glance
| Item | Details |
|---|---|
| Title | AI in everyday challenges |
| Type | Group activity, with no coding |
| Objective | Apply LLMs to an everyday challenge faced by students, to improve critical thinking, problem solving and creativity, and to learn how to apply AI in a real-world situation |
| Your role for the LLM | A **product-development partner** |
| Required outputs | Product concept, name, key features, target user, and a visual prototype / mock-up |
| Final presentation | 2 to 3 minutes per group: the problem, the product, the development process, and how LLMs were used |

## 2. The eight group challenges
Each group designs a product for one student problem.

| Group | Problem | Task |
|---|---|---|
| 1. The Forgetful Student | Forgetting ID cards, chargers, USB drives, books, bottles | A product that helps students remember and manage what they need |
| 2. The Distracted Student | Notifications, social media, noise and conversations break focus | A product that creates and maintains better study focus |
| 3. The Food Waster | Buying too much, forgetting stored food, throwing away leftovers, while others need affordable food | A product or service that reduces food waste |
| 4. The Dehydrated Student | Hours without water because they only drink when thirsty | A product that encourages better drinking habits |
| 5. The Busy Student | Lectures, assignments, projects and activities cause forgotten and last-minute tasks | A product that helps organise and manage time |
| 6. The Plastic Problem | Convenience beats eco-friendliness with single-use plastics | A product that makes reducing plastic easier and more attractive |
| **7. The Overloaded Student** | **Laptop, charger, phone, books, notebooks, stationery, bottle, headphones and ID card are uncomfortable to carry** | **A product that helps students carry, organise or reduce what they take** |
| 8. The Budget-Challenged Student | Small daily expenses add up and it is hard to see where money goes | A product that helps students understand, control and manage spending |

**Our group: Group 7.**

## 3. What we did

### Step 1: Understand the problem
We asked the LLM to act as a product-development partner and ask 5 questions about the problem. They covered:
1. who carries the load (commuters on buses or trains, walkers, campus residents),
2. what is essential and what is carried "just in case",
3. what is forgotten most and what it costs,
4. how different days (lectures, labs, library) change what is needed,
5. constraints (budget, physical product or app, lockers and charging points on campus).

Our answers: commuting students with 30 to 45 minute trips, laptop every day, ID card, charger and USB drive forgotten most, days that differ a lot, and a student budget. 

### Step 2: Brainstorm ideas
The LLM suggested six ideas, each with a weakness.

| Idea | Weakness |
|---|---|
| Smart backpack with companion app | Electronics add cost and weight |
| Daily packing-checklist app | Cannot check what is actually packed or its weight |
| Modular pouch system | You still have to remember which pouch to take |
| Campus smart lockers | Depends on the university installing them |
| Bluetooth item-tag kit | Tracks items but not weight; tags need batteries |
| E-ink notebook plus digital textbooks | Expensive, and not every course offers digital books |

**Chosen idea: the smart backpack**, because it addresses carrying, organising and forgetting together.

### Step 3: Develop the concept
**LoadLight Smart Backpack.** A backpack with a companion app that tells students what to carry today, tracks what is inside, and warns them when the load is too heavy or something is left behind.

**Target user:** commuting university students who carry a laptop and several books and accessories every day.

**Key features**
1. **Timetable-based pack list:** the app reads the timetable and suggests what to bring and what to leave in a locker.
2. **Smart-tag tracking:** Bluetooth tags on the ID card, USB drive, keys and laptop, with an LED and app alerts if something is missing.
3. **Live load monitor:** a weight sensor in the base shows the bag weight and warns above a limit the student sets.
4. **Built-in power bank:** charge a phone or laptop from the bag, so the bulky charger can stay at home.
5. **Modular pouches:** detachable zones (Lab kit, Books, Tech, Daily essentials).
6. **Ergonomic design:** padded laptop sleeve, wide straps, chest clip and an insulated bottle pocket.

**What makes it different**

| Existing option | Limitation | LoadLight |
|---|---|---|
| Ordinary backpack | Only stores items | Helps decide what to carry |
| Tag kits | Track items, ignore weight and planning | Tracks, weighs and plans in one system |
| Power-bank bags | Charge only | Charge, organise and control the load |
| Lockers | Fixed place, not linked to the timetable | Suggests what to leave in a locker each day |

### Step 4: Critical review
The LLM was asked to act as a critical reviewer.

| Weak point | Improvement |
|---|---|
| Cost and weight of electronics | Small battery, basic load cell, detachable smart module |
| Tag batteries and false alerts | Long-life or rechargeable tags; student chooses what to track |
| Outdated timetable | Sync with the university timetable system |
| Battery safety | Certified, removable battery with a clear label |
| Privacy | Keep data on the phone and track items, not the person |
| Weight advice may not suit everyone | Student sets their own limit and sees the guideline source |
| No real testing | Interview 10 to 20 students and test a prototype |

**Biggest risk:** students may not pay extra for a bag when a normal bag plus a cheap tag kit seems enough.

### Step 5: Visual mock-ups
- **The bag:** padded laptop sleeve, modular front pocket, smart-tag LED, power bank with USB port, insulated bottle pocket, weight sensor in the base, ergonomic straps.
- **The app (three screens):** *Today's Pack List*, *Live Load*, and *Alerts* (forgotten item, heavy load, tomorrow's lighter pack).

These are concept illustrations with sample data, not a final design.

### Step 6: Presentation (2 to 3 minutes)
| Time | Content |
|---|---|
| 0:00 to 0:30 | The problem: the overloaded student |
| 0:30 to 1:15 | The product: LoadLight, target user, top 3 features |
| 1:15 to 1:45 | The mock-ups of the bag and the app |
| 1:45 to 2:30 | How we used the LLM, and what we changed |
| 2:30 to 3:00 | What we learned, and the limits of LLMs |

## 4. Prompts used
1. "I'm a university student working on a product design challenge... Act as a product-development partner. Ask me 5 questions that would help us understand this problem before we design anything."
2. "Based on that, brainstorm 6 different product ideas... For each give a one-line description and one weakness."
3. "We choose the smart backpack idea. Develop it into a full product concept: a product name, one-sentence pitch, target user, 5 to 6 key features, and what makes it different from existing products."
4. "Act as a critical reviewer. What are the weak points of this product? What could go wrong, and how could we improve it?"
5. "Create a simple visual mock-up of this smart backpack and its companion app..."
6. "Help us structure a 2 to 3 minute presentation covering: the problem, our product, our development process, and how we used LLMs."

## 5. Observations: what we learned about LLMs in design
**Strengths**
- Fast brainstorming of many different ideas.
- Good at structuring a concept (name, pitch, features, target user).
- Useful as a critic when asked to look for weak points.

**Limitations**
- Answers can be confident but generic, so the group must decide what is realistic and affordable.
- It does not know real prices, student habits or campus rules, so these need real research.
- The mock-ups are concept illustrations, not professional designs.
- Facts such as safe bag weight should be checked against reliable sources.

## 6. Learning outcomes
- Used an LLM as a design partner with step-by-step prompts: problem analysis, brainstorming, concept development, critique and presentation planning.
- Learned that good prompts and follow-up questions give better answers.
- Practised critical thinking by checking and challenging the LLM instead of accepting it.
- Understood the strengths and limits of LLMs in product design.
- Practised teamwork and presenting an idea briefly.

## 7. What was submitted
```
Lab-02-LLM-Everyday-Life/
├── README.md
├── group-activity/
│   ├── group-members.md        names, IDs and roles
│   ├── activity-outcomes.md    product concept, features, target user, mock-ups
│   └── discussion-summary.md   how the LLM was used, ideas, changes, lessons
└── screenshots/                01 to 08: chat screenshots and the two mock-ups
```

**Still to do by hand:** real group members and roles, the ideas your group actually discussed, and what you changed or rejected from the LLM's suggestions.

# 🌟 TL Linux Wellness Hub

Comprehensive mental health and neurodiversity support tools integrated into TL Linux.

## Overview

TL Linux includes evidence-based therapeutic tools specifically designed to help people with autism, ADHD, anxiety, depression, and other mental health challenges. All tools are based on established therapeutic approaches and neurodiversity-affirming principles.

## 🧠 Therapeutic Tools

### CBT Tools (Cognitive Behavioral Therapy)

**Purpose**: Identify and change unhelpful thinking patterns

**Features**:
- **Thought Record**: Track situations, emotions, automatic thoughts, evidence, and alternative perspectives
- **Mood Tracker**: Log mood and energy levels throughout the day
- **Cognitive Distortions**: Reference guide for common thinking errors (all-or-nothing, catastrophizing, etc.)
- **Behavioral Activation**: Plan meaningful activities to improve mood
- **Goal Setting**: SMART goal framework for achievable objectives
- **Progress Reports**: Track usage and improvement over time

**Launch**: `python3 tl-linux/apps/wellness/cbt_tools.py`

### ACT Tools (Acceptance & Commitment Therapy)

**Purpose**: Live mindfully according to your values

**Features**:
- **Values Clarification**: Identify what matters across 6 life domains
- **Committed Action**: Plan actions aligned with your values
- **Mindfulness Exercises**:
  - 5-4-3-2-1 Grounding
  - Body Scan Meditation
  - Mindful Breathing
  - Observer Self Exercise
- **Cognitive Defusion**: Techniques to change your relationship with difficult thoughts
- **Acceptance Practice**: Make room for difficult experiences
- **Present Moment**: Return to the here and now

**Launch**: `python3 tl-linux/apps/wellness/act_tools.py`

### DBT Tools (Dialectical Behavior Therapy)

**Purpose**: Regulate emotions and improve relationships

**Features**:
- **Emotion Regulation**:
  - ABC PLEASE (building emotional resilience)
  - Opposite Action (act opposite to emotion when it doesn't fit facts)
  - Check the Facts (examine accuracy of emotional response)

- **Distress Tolerance**:
  - STOP Skill (crisis intervention)
  - TIP Skills (change body chemistry: Temperature, Intense exercise, Paced breathing)
  - ACCEPTS (distraction strategies)
  - Self-Soothe (with five senses)

- **Interpersonal Effectiveness**:
  - DEAR MAN (asking for what you need)
  - GIVE (maintaining relationships)
  - FAST (keeping self-respect)

- **Mindfulness**: Core "what" and "how" skills

**Launch**: `python3 tl-linux/apps/wellness/dbt_tools.py`

## 🎯 ADHD Support Tools

**Purpose**: Executive function support for ADHD

**Features**:
- **Focus Timer**: Pomodoro technique with 25/5/15 minute intervals
- **Task Breakdown**: Break overwhelming tasks into tiny manageable steps
- **Routine Builder**: Visual routines with time estimates for morning, evening, and work
- **Body Doubling**: Explanation and strategies for working alongside others
- **Reward System**: Immediate rewards for maintaining motivation
- **ADHD Tips**: Practical strategies for:
  - Time management (visual timers, alarms, buffer time)
  - Organization (homes for everything, labeling, decluttering)
  - Focus (removing distractions, white noise, work in bursts)
  - Motivation (making tasks interesting, using rewards, celebrating wins)

**Launch**: `python3 tl-linux/apps/wellness/adhd_support.py`

## 🧩 Autism Support Tools

**Purpose**: Social, sensory, and communication support for autism

**Features**:
- **Social Scripts**: Pre-written scripts for common situations:
  - Phone calls (appointments, ordering, calling in sick)
  - Shopping (asking for help, returns, prices)
  - Social situations (exiting conversations, declining invitations, small talk)
  - Workplace (clarification, accommodations, boundaries)

- **Sensory Tracker**: Log sensory state across 8 categories:
  - Visual, Auditory, Smell, Taste, Touch
  - Proprioception, Vestibular, Interoception
  - Track over/under/ok states and triggers

- **Visual Schedules**: Checkable routines for morning, daytime, evening

- **Communication Cards**: Quick cards for common needs:
  - "I need quiet", "I need a break", "I don't understand"
  - "Please stop", "Don't touch me", "I'm anxious"
  - Color-coded for easy identification

- **Sensory Accommodations**: Strategies for:
  - Visual (light sensitivity, clutter, movement)
  - Auditory (noise sensitivity, processing)
  - Tactile (clothing, touch, textures)
  - General (sensory diet, safe spaces, communication)

- **Autism Tips**: Neurodiversity-affirming strategies for:
  - Social interactions (scripts, breaks, asking for clarification)
  - Sensory management (knowing profile, using tools, accommodations)
  - Executive function (schedules, routines, breaking down tasks)
  - Communication (being direct, AAC, processing time)
  - Special interests (value, career potential, regulation)
  - Self-care (unmasking, recovery time, needs validation)

**Launch**: `python3 tl-linux/apps/wellness/autism_support.py`

## 🌟 Wellness Hub

**Purpose**: Central launcher for all therapeutic tools

**Features**:
- Launch all therapeutic apps from one place
- Color-coded by tool type
- About information for each therapeutic approach
- Crisis resources and helplines
- Privacy information

**Launch**: `python3 tl-linux/apps/wellness_hub.py`

## 📊 Data Storage

All data is stored locally and privately in:
```
~/.config/tl-linux/wellness/
├── cbt_data.json        # CBT thought records and mood logs
├── act_data.json        # ACT values and committed actions
├── dbt_data.json        # DBT skills practice data
├── adhd_data.json       # ADHD focus sessions and routines
└── autism_data.json     # Autism social scripts and sensory logs
```

**Privacy**: No data is ever sent to external servers. Everything stays on your device.

## 🆘 Crisis Resources

These tools complement professional help but don't replace it.

### Immediate Crisis Help (US):
- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **SAMHSA National Helpline**: 1-800-662-4357

### Specialized Support:
- **Trevor Project** (LGBTQ+ Youth): 1-866-488-7386
- **Trans Lifeline**: 1-877-565-8860
- **Veterans Crisis Line**: 988 then press 1
- **RAINN**: 1-800-656-4673
- **Domestic Violence**: 1-800-799-7233

### When to Seek Emergency Help:
- You have a plan to harm yourself or others
- You've taken steps toward self-harm
- You're hearing voices telling you to harm yourself
- You feel you can't keep yourself safe

**Go to emergency room or call 911**

## 🎓 Evidence Base

### CBT (Cognitive Behavioral Therapy)
- Developed by Aaron Beck in the 1960s
- Focuses on the relationship between thoughts, feelings, and behaviors
- Extensive research support for anxiety, depression, OCD, PTSD, and more
- Helps identify automatic thoughts and cognitive distortions

### ACT (Acceptance & Commitment Therapy)
- Developed by Steven Hayes in the 1980s
- Part of the "third wave" of behavioral therapies
- Focuses on psychological flexibility and values-based living
- Uses mindfulness and acceptance strategies
- Effective for anxiety, depression, chronic pain, and stress

### DBT (Dialectical Behavior Therapy)
- Developed by Marsha Linehan in the 1990s
- Originally for borderline personality disorder
- Now used widely for emotion regulation challenges
- Combines mindfulness, distress tolerance, emotion regulation, and interpersonal effectiveness
- Evidence-based for self-harm, substance use, eating disorders, PTSD

### Neurodiversity-Affirming Approach
- ADHD and autism are natural neurological variations
- Focus on accommodation and support, not "fixing"
- Emphasizes strengths and challenges
- Supports self-advocacy and understanding
- Recognizes masking and its costs
- Validates sensory, social, and executive function differences

## 💡 Best Practices

### Using Therapeutic Tools:
1. **Consistency**: Use tools regularly, not just in crisis
2. **Patience**: Skills take time to develop
3. **Practice**: Apply techniques in low-stress situations first
4. **Personalize**: Adapt strategies to fit your needs
5. **Track Progress**: Use built-in logging features
6. **Combine**: Use multiple tools together (e.g., CBT + mindfulness)

### For ADHD:
- Use the focus timer daily
- Break all tasks down before starting
- Set up routines and use them
- Be generous with rewards
- Track what works for you

### For Autism:
- Create and save social scripts for your situations
- Log sensory experiences to identify patterns
- Use communication cards without shame
- Implement accommodations proactively
- Remember: there's no wrong way to be autistic

## 🔧 Integration with TL Linux

### Launching from Desktop:
1. Open App Drawer (⚡ TL button)
2. Navigate to "🌟 Wellness" category
3. Select desired tool

### Adding to Main Menu:
Edit `tl-linux/tl_linux.py` to add wellness hub to main menu.

### Quick Launch:
```bash
# Wellness Hub
python3 tl-linux/apps/wellness_hub.py

# Individual tools
python3 tl-linux/apps/wellness/cbt_tools.py
python3 tl-linux/apps/wellness/act_tools.py
python3 tl-linux/apps/wellness/dbt_tools.py
python3 tl-linux/apps/wellness/adhd_support.py
python3 tl-linux/apps/wellness/autism_support.py
```

## 🤝 When to Seek Professional Help

These tools are helpful but not sufficient for:
- Severe depression or suicidal thoughts
- Trauma requiring processing
- Medication management
- Diagnosis
- Crisis situations
- Complex mental health conditions

**Please work with a qualified mental health professional.**

## 📚 Additional Resources

### Books:
- **CBT**: "Feeling Good" by David Burns
- **ACT**: "The Happiness Trap" by Russ Harris
- **DBT**: "The Dialectical Behavior Therapy Skills Workbook" by McKay, Wood, & Brantley
- **ADHD**: "Driven to Distraction" by Hallowell & Ratey
- **Autism**: "Unmasking Autism" by Devon Price

### Online:
- NAMI (National Alliance on Mental Illness): nami.org
- CHADD (ADHD support): chadd.org
- ASAN (Autistic Self Advocacy Network): autisticadvocacy.org
- DBT-A (DBT adapted for adolescents): behavioraltech.org

## 💜 Final Note

**You are not broken. You are not "too much." You are not alone.**

These tools are here to support you in living a life that works for you, aligned with your values, with strategies that honor your neurology.

Your mental health matters. Your wellbeing matters. You matter.

---

**TL Linux Wellness Hub** - Supporting mental health and neurodiversity 🌟

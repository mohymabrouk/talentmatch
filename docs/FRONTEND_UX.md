# Frontend UX/UI

## Visual direction

Minimal.
Mostly black and white.
High contrast.
No gradients.
No glassmorphism.
No decorative blobs.
No unnecessary cards.
No giant marketing hero.
No excessive shadows.
No emoji UI.
No fake dashboard complexity.

The product should feel like a serious internal tool crossed with a clean job marketplace.

---

## Palette

### Light mode

```text
background      #FFFFFF
surface         #FAFAFA
primary text    #0A0A0A
secondary text  #666666
border          #E5E5E5
hover           #F5F5F5
disabled        #A3A3A3
danger          #B42318
```

### Dark mode

```text
background      #0A0A0A
surface         #111111
primary text    #FAFAFA
secondary text  #A3A3A3
border          #262626
hover           #171717
disabled        #525252
danger          #F97066
```

Accent color should be used sparingly or not at all.

## Implemented Phase 6 workspace

The current frontend uses a warm paper background with restrained green/coral
accents, a responsive navigation bar, three-column desktop recommendation cards,
and a single-column mobile layout. It includes:

- profile setup and editing for roles, skills, location, experience, and work mode
- discovery search and work-mode filtering
- match score/reason cards with save and dismiss actions
- accessible job detail drawer with application tracking and original-job link
- saved jobs and applications views backed by the API
- loading skeletons, empty results, inline errors, and keyboard-visible focus

The API is still intentionally demo-authenticated through `X-Demo-User-ID` until
the authentication phase is implemented.

---

## Typography

Use one sans-serif family.

Recommended:

```text
Inter
Geist
system-ui
```

Hierarchy:

```text
Display       32–40px / 600
H1            28–32px / 600
H2            20–24px / 600
H3            16–18px / 600
Body          14–16px / 400
Meta          12–13px / 400
Button        14px / 500
```

Avoid oversized 72px startup landing-page typography.

---

## Spacing

Use an 8px system.

```text
4
8
12
16
24
32
48
64
```

Page width:

```text
max-width: 1200px
```

Recommendation feed reading width:

```text
680–820px
```

---

## Border radius

Small.

```text
inputs      6px
buttons     6px
cards       8px
modals      10px
```

Do not use pill shapes everywhere.

---

## Navigation

Desktop:

```text
┌──────────────────────────────────────────────────────────────┐
│ TalentMatch        Jobs   Saved   Applications      Profile │
└──────────────────────────────────────────────────────────────┘
```

Height:

```text
56px
```

Use a 1px bottom border.

No floating nav.

---

## Main pages

```text
/
 /login
 /onboarding
 /jobs
 /jobs/[id]
 /saved
 /applications
 /profile
 /settings
 /dev/model
```

`/dev/model` is development-only.

---

# 1. Landing page

Keep it minimal.

```text
TalentMatch

Jobs ranked for you.

Personalized recommendations based on your skills,
experience, preferences, and behavior.

[Create profile]    [Sign in]
```

Below:

```text
How it works

1. Build your profile
2. Get ranked jobs
3. Improve recommendations through feedback
```

No fake testimonials.
No logo wall.
No huge animated sections.

---

# 2. Onboarding

Use a single focused column.

Progress:

```text
1 / 4
```

Steps:

### Step 1 — Role

```text
What roles are you targeting?

[ Machine Learning Engineer        ]
[ Applied AI Engineer              ]
[ ML Platform Engineer             ]

[Continue]
```

### Step 2 — Skills

Search + selected tokens.

```text
Skills

[Search skills...]

Python        ×
PyTorch       ×
FastAPI       ×
Docker        ×
PostgreSQL    ×
```

### Step 3 — Preferences

```text
Location
[Paris]

Work mode
○ On-site
○ Hybrid
● Remote / Hybrid

Minimum salary
[optional]

Seniority
● Mid-level
○ Senior
○ Staff
```

### Step 4 — Experience

```text
Years of experience
[3]

Current / most recent title
[Machine Learning Engineer]

[Finish]
```

Do not ask for unnecessary data.

---

# 3. Recommendation page

Main layout:

```text
┌────────────────────────────────────────────────────────────┐
│ Jobs for you                                  128 matches │
├────────────────────────────────────────────────────────────┤
│ Filters                                                    │
│ Remote  Seniority  Location  Posted                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Machine Learning Engineer                                  │
│ Acme · Paris · Hybrid                                      │
│                                                            │
│ Python · PyTorch · Docker · AWS                            │
│                                                            │
│ 91% match                                                  │
│ Strong skill overlap · matches preferred role              │
│                                                            │
│ [Save]                          [View job →]                │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ Applied AI Engineer                                        │
│ Example Labs · Remote                                      │
│ ...                                                        │
└────────────────────────────────────────────────────────────┘
```

---

## Job card rules

A job card contains only:

- title
- company
- location
- work mode
- seniority
- top skills
- match score
- 1–2 recommendation reasons
- posted date
- save action
- view action

Do not show:

- huge logos
- long descriptions
- excessive salary badges
- 10+ metadata rows
- decorative icons for every field

---

## Recommendation explanation

Keep explanations factual.

Good:

```text
91% match

Strong skill overlap
Matches your preferred role
Remote preference matched
```

Bad:

```text
✨ Perfect for you!
🔥 Hot opportunity!
AI thinks you'll love this!
```

---

# 4. Job detail

Two-column desktop layout.

```text
┌───────────────────────────────┬──────────────────────┐
│ Machine Learning Engineer     │ Match                │
│ Acme                          │                      │
│                               │ 91%                  │
│ Description                   │                      │
│ ...                           │ Why this job         │
│                               │ • Python match       │
│ Requirements                  │ • Role match         │
│ ...                           │ • Hybrid match       │
│                               │                      │
│                               │ [Save]               │
│                               │ [Mark applied]       │
└───────────────────────────────┴──────────────────────┘
```

Sticky right rail is acceptable on desktop.

Mobile stacks vertically.

---

# 5. Saved

Simple list.

```text
Saved jobs                           12

[Job row]
[Job row]
[Job row]
```

No analytics.

---

# 6. Applications

Status values:

```text
Applied
Interview
Offer
Rejected
Withdrawn
```

User-controlled for MVP.

Minimal table on desktop.
Stacked rows on mobile.

---

# 7. Profile

Sections:

```text
Basic information
Target roles
Skills
Experience
Preferences
```

Each section has:

```text
Edit
```

Do not place every field inside a separate card.

---

# 8. Empty states

Example:

```text
No recommendations yet

Complete your profile to generate your first ranked jobs.

[Complete profile]
```

Saved empty state:

```text
No saved jobs

Save a job and it will appear here.
```

---

# 9. Loading states

Prefer skeleton lines.

Avoid full-screen spinners.

Recommendation loading:

```text
████████████████
████████
██████████████

████████████████
████████
██████████████
```

---

# 10. Error states

Inline, specific.

```text
Recommendations could not be loaded.

[Try again]
```

Authentication:

```text
Your session expired.

[Sign in]
```

---

# 11. Interaction behavior

### Save

Optimistic UI.

```text
Save → Saved
```

Persist immediately.

### Dismiss

Optional secondary action:

```text
Not interested
```

After dismiss:

- remove item from current feed
- log event
- invalidate recommendation cache

### Apply

Do not automate external applications.

Use:

```text
Mark as applied
```

The user manually confirms.

---

# 12. Filters

MVP:

```text
location
remote mode
seniority
posted within
minimum salary if data exists
```

Do not create 20 filters.

---

# 13. Responsive behavior

### Desktop

```text
>= 1024px
```

- centered container
- 2-column job detail
- horizontal nav

### Tablet

```text
768–1023px
```

- single-column feed
- simplified nav

### Mobile

```text
< 768px
```

- stacked layout
- bottom-safe actions
- no horizontal overflow
- 16px page padding

---

# 14. Accessibility

Required:

- keyboard navigation
- visible focus states
- semantic buttons
- proper labels
- minimum 4.5:1 text contrast
- no information communicated only by color
- reduced-motion support
- logical heading hierarchy

---

# 15. Component structure

```text
components/
├── layout/
│   ├── AppHeader.tsx
│   ├── PageContainer.tsx
│   └── MobileNav.tsx
│
├── jobs/
│   ├── JobCard.tsx
│   ├── JobList.tsx
│   ├── JobMeta.tsx
│   ├── JobSkills.tsx
│   ├── MatchScore.tsx
│   ├── MatchReasons.tsx
│   └── JobFilters.tsx
│
├── profile/
│   ├── SkillSelector.tsx
│   ├── RoleSelector.tsx
│   └── PreferenceForm.tsx
│
├── feedback/
│   ├── InlineError.tsx
│   ├── EmptyState.tsx
│   └── Skeleton.tsx
│
└── ui/
    ├── Button.tsx
    ├── Input.tsx
    ├── Select.tsx
    ├── Badge.tsx
    ├── Dialog.tsx
    └── Separator.tsx
```

---

# 16. UI rules

Do:

```text
white space
clear hierarchy
thin borders
strong typography
short labels
simple controls
fast interactions
```

Do not:

```text
gradients
neon
glass effects
floating blobs
3D illustrations
animated backgrounds
giant cards
excessive rounded corners
marketing copy inside app screens
```

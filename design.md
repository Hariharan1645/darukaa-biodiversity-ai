---
version: alpha
name: darukaa.earth
description: Science-forward B2B nature intelligence brand with a clean, high-contrast interface, dark green primary accent, expansive hero imagery, and Manrope-led typography.
colors:
  primary: "#009245"
  secondary: "#ffffff"
  tertiary: "#000000"
  neutral: "#e5e7eb"
  surface: "#ffffff"
  on-surface: "#000000"
  error: "#ef4444"
  background: "#ffffff"
  accent: "#009245"
typography:
  fontFamily:
    sans: "__Manrope_d2dc74, __Manrope_Fallback_d2dc74, sans-serif"
    mono: "__JetBrains_Mono_f9e569, __JetBrains_Mono_Fallback_f9e569, monospace"
  headline-display:
    fontFamily: "__Manrope_d2dc74, __Manrope_Fallback_d2dc74, sans-serif"
    fontSize: "60px"
    fontWeight: 600
    lineHeight: "60px"
    letterSpacing: "-1.2px"
  headline-lg:
    fontFamily: "__Manrope_d2dc74, __Manrope_Fallback_d2dc74, sans-serif"
    fontSize: "48px"
    fontWeight: 600
    lineHeight: "48px"
    letterSpacing: "0px"
  headline-md:
    fontFamily: "__Manrope_d2dc74, __Manrope_Fallback_d2dc74, sans-serif"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: "28px"
    letterSpacing: "0px"
  body-lg:
    fontFamily: "__Manrope_d2dc74, __Manrope_Fallback_d2dc74, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: "24px"
    letterSpacing: "0px"
  body-md:
    fontFamily: "__Manrope_d2dc74, __Manrope_Fallback_d2dc74, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: "20px"
    letterSpacing: "0px"
  body-sm:
    fontFamily: "__Manrope_d2dc74, __Manrope_Fallback_d2dc74, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: "20px"
    letterSpacing: "0px"
  label-lg:
    fontFamily: "ui-sans-serif, system-ui, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color Emoji"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: "1"
    letterSpacing: "0px"
  label-md:
    fontFamily: "__JetBrains_Mono_f9e569, __JetBrains_Mono_Fallback_f9e569, monospace"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: "20px"
    letterSpacing: "2.8px"
  label-sm:
    fontFamily: "__JetBrains_Mono_f9e569, __JetBrains_Mono_Fallback_f9e569, monospace"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: "16px"
    letterSpacing: "2px"
rounded:
  none: "0px"
  sm: "4px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  full: "9999px"
spacing:
  xs: "8px"
  sm: "16px"
  md: "32px"
  lg: "48px"
  xl: "80px"
components:
  button:
    primary:
      backgroundColor: "{colors.surface}"
      color: "{colors.primary}"
      borderColor: "{colors.primary}"
      borderRadius: "{rounded.none}"
      borderWidth: "2px"
      borderStyle: "solid"
      padding: "18px 32px"
      fontSize: "16px"
      fontWeight: 600
      minWidth: "180px"
      minHeight: "52px"
      textDecoration: "none"
      boxShadow: "none"
    secondary:
      backgroundColor: "{colors.primary}"
      color: "{colors.surface}"
      borderColor: "{colors.neutral}"
      borderRadius: "{rounded.none}"
      borderWidth: "0px"
      borderStyle: "solid"
      padding: "18px 32px"
      fontSize: "16px"
      fontWeight: 600
      minWidth: "180px"
      minHeight: "52px"
      textDecoration: "none"
      boxShadow: "rgba(0, 0, 0, 0.1) 0px 4px 6px -1px, rgba(0, 0, 0, 0.1) 0px 2px 4px -2px"
  link:
    color: "{colors.tertiary}"
    textDecoration: "underline"
    fontSize: "16px"
    fontWeight: 400
  card:
    backgroundColor: "{colors.surface}"
    borderColor: "{colors.neutral}"
    borderRadius: "{rounded.md}"
    borderWidth: "1px"
    borderStyle: "solid"
    padding: "16px"
    boxShadow: "none"
---

# Overview

darukaa.earth presents as a science-led nature intelligence platform for businesses, governments, and project developers. The visual language is restrained, credible, and modern: white surfaces, deep green accents, dark text, sharp corners on primary actions, and large editorial headlines over immersive nature imagery.

Use this system to keep the product feeling:
- authoritative, not decorative
- technical, not playful
- spacious, not dense
- outcome-oriented, not salesy

The screenshot and homepage copy reinforce a B2B decision-support product with dual calls to action, large map-based product visuals, and a strong preference for data-rich interfaces.

# Colors

## Core palette
- Primary accent: `#009245`
- Background/surface: `#ffffff`
- Text: `#000000`
- Neutral border: `#e5e7eb`

## Usage guidance
- Use `{colors.primary}` for confirmed actions, active states, and science/verification cues.
- Use white surfaces for most UI containers and hero overlays.
- Keep text near-black on white for clarity.
- Use neutral gray only for dividers, borders, and low-emphasis framing.
- Avoid introducing bright or saturated secondary colors unless they represent distinct data states.

# Typography

## Type system
- Headline display uses Manrope at 60px/60px with tight tracking for the hero.
- Large headings use Manrope at 48px/48px.
- Section and card headings use Manrope at 20px/28px.
- Body copy is compact and readable at 12px/20px.
- Labels and utility UI can use the mono treatment from JetBrains Mono for the brand’s technical tone.

## Hierarchy
- Reserve `headline-display` for homepage hero statements and major page intros.
- Use `headline-lg` for section leads and high-priority marketing copy.
- Use `headline-md` for cards, modules, and feature headers.
- Use `label-md` for eyebrow text such as “BUILT ON SCIENCE, DESIGNED FOR DECISIONS”.
- Keep body copy concise; this brand favors short, evidence-based paragraphs.

# Layout

## Spatial system
- Base spacing steps: 8px, 16px, 32px, 48px, 80px.
- Prefer wide vertical rhythm between major sections.
- Keep hero content centered with generous breathing room.
- Align CTA buttons side-by-side with consistent width and equal visual weight.

## Page structure
- Top navigation is minimal and horizontal.
- Hero area combines:
  - eyebrow label
  - large headline
  - two CTAs
  - product screenshot/mockup anchored below
- Content sections below the fold should use clear modular grouping with generous whitespace.

## Grid and responsiveness
- Use a centered content column with wide max width for marketing pages.
- Preserve strong hierarchy on smaller screens by stacking hero CTAs and compressing the imagery before reducing headline size.

# Elevation & Depth

## Principles
- Depth is subtle and functional.
- Shadows are mostly absent in the system, except where device mockups or primary CTAs need separation from the background.
- Product imagery may sit above the page background with soft containment, but UI cards should remain crisp and flat.

## Tokens
- `sm` shadow is the only meaningful elevation token and should be used sparingly.
- Most cards and panels should rely on border + whitespace rather than shadow.

# Shapes

## Corner treatment
- Primary brand feel is intentionally sharp.
- Buttons are square-cornered: `{rounded.none}`.
- Product cards can use slight rounding (`{rounded.md}`) for containment without softening the brand too much.

## Guidance
- Do not over-round controls or containers.
- Avoid pills except where they are required for status chips or map markers.
- Use consistent corner treatment within each component family.

# Components

## Buttons
- Primary button: outlined white button with green border/text.
- Secondary button: solid green button with white text and light shadow.
- Both buttons use the same min-height and padding to feel balanced.

### Implementation notes
- Use primary buttons for exploration or lower-commitment actions.
- Use secondary buttons for the main conversion action.
- Keep button labels short and imperative: “Explore our solutions”, “Book a demo”.

## Links
- Links are underlined, minimal, and dark.
- Use them for inline navigation only; do not style them like buttons.

## Cards
- Cards are white, bordered, and lightly rounded.
- Prefer cards for solution summaries, feature blocks, and product panels.
- Keep card content compact and scannable.

## Hero/media containers
- Large screenshot containers should feel like embedded product windows.
- Use dark top chrome or device framing only when showing product UI.
- Maintain high contrast between the nature background and the foreground product mockup.

# Do's and Don'ts

## Do
- Do use Manrope for almost all visible text.
- Do use `{colors.primary}` as the dominant brand signal.
- Do keep headlines large and concise.
- Do pair a primary outlined CTA with a solid conversion CTA in hero areas.
- Do preserve white backgrounds and lots of negative space.
- Do use sharp corners for major buttons and business-critical actions.
- Do keep copy evidence-based and specific to nature, climate, biodiversity, or finance.

## Don't
- Don't introduce rounded, playful, or consumer-app styling.
- Don't use more than one strong accent color in the same view.
- Don't crowd the page with dense text blocks or multiple competing CTAs.
- Don't replace the hero imagery with abstract art; the brand relies on real-world science and landscape imagery.
- Don't add heavy shadows, gradients, or glassmorphism.
- Don't make buttons pill-shaped unless a product requirement explicitly demands it.
- Don't dilute the technical tone with overly emotional marketing language.
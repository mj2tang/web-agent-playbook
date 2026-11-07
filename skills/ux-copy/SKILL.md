---
name: ux-copy
description: Write or review interface copy - headings, buttons and CTAs, form labels and hints, error messages, empty states, confirmations, and success toasts - so it is specific, short, and tells the user what happened and what to do next, in the voice from the design brief. Use when a component spec or page needs text, or when reviewing copy in a UI branch. Not for long-form marketing or legal text.
---

# UX copy

## Rules
- **Buttons say the action and object:** "Save note", "Send invite" - not "OK", "Submit", "Click here".
- **Errors:** what happened + why (if known) + what to do: "That email is already registered. Sign in instead or use another email." No blame, no codes alone, no "Oops".
- **Empty states:** what this area is for + the first action: "No notes yet. Write your first note." with the button.
- **Confirmations for destructive actions** name the object and consequence: "Delete 'Groceries'? This can't be undone." Buttons: "Delete note" / "Cancel".
- **Labels** are nouns, hints are sentences; never rely on placeholder text.
- **Length:** headings ≤ 8 words, button ≤ 3 words, error ≤ 2 short sentences.
- **Voice:** match the brief's three adjectives; sentence case; numerals for numbers; no exclamation marks in errors.
- **i18n-ready:** whole sentences in one string (no concatenated fragments), room for 30% expansion.

## Done when
Every string in the change follows the rules, and each error and empty state in the component spec has final copy.

# Single-Turn Test Data Generation Plan

## Goal

Define a single-turn test matrix for `recommendation_v1_0`, `recommendation_v1_1`, and `recommendation_v2`.

The matrix should organize test data along 2 axes:

1. filter clarity
2. preference specificity

In addition to the matrix, there should be a separate third concern:

3. unrelated queries

## Principles

- use the same matrix for all three versions
- focus on single-turn scenarios only
- evaluate filters objectively where possible
- use recommendation relevance for broader preference evaluation
- keep scenarios grouped by matrix cell
- keep unrelated-query scenarios separate from the main matrix
- each test case group should contain 100 entries
- queries should be very creative and should not sound schematic or templated
- query phrasing should vary in wording, length, and structure

## Test Matrix

### Filter Axis

The filter axis should be based only on:

- continent
- budget
- season

#### F0. No Filter

Characteristics:

- no explicit continent, budget, or season filter
- open request with little machine-checkable structure

#### F1. Vague Filter

Characteristics:

- weak or indirect filter signals
- partial location, season, or budget hints
- continent, budget, or season may be implied but not stated strictly
- filter intent is present but not strict

#### F2. Explicit Filter

Characteristics:

- clear machine-checkable constraints
- explicit continent, budget, or season language
- stronger expected filter application behavior

### Preference Axis

#### P0. Very Vague Preference

Characteristics:

- broad interest only
- low specificity
- little detail about desired experience
- should still mention a meaningful travel preference
- should stay generic within categories like culture, food, sports, or nature

#### P1. Experience-Focused Preference

Characteristics:

- preference is centered on a recognizable experience
- more concrete than a vague preference
- may include region-characteristic intent without explicit filters
- should use more concrete examples such as good wine, good pasta, historic streets, museums, markets, or hiking culture

#### P2. Highly Specialized Preference

Characteristics:

- narrow, strongly defined preference
- specific desired experience or travel style
- smaller expected recommendation space
- may include very specific sports, foods, animals, landmarks, cities, or cultural anchors
- should refer to specific activities, actions, or objects
- sports examples: scuba diving, kitesurfing, rock climbing
- food examples: sushi, lasagna bolognese
- culture and sight examples: Colosseum, temples, explicit city references

## Matrix Layout

The test data should be organized as a 3 x 3 matrix.

| | P0 Very Vague Preference | P1 Experience-Focused Preference | P2 Highly Specialized Preference |
|---|---|---|---|
| F0 No Filter | broad preference, no explicit filters | concrete experience, no explicit filters | highly specialized interest, no explicit filters |
| F1 Vague Filter | vague filter + broad preference | vague filter + concrete experience | vague filter + highly specialized interest |
| F2 Explicit Filter | explicit filter + broad preference | explicit filter + concrete experience | explicit filter + highly specialized interest |

## How To Use The Matrix

- create scenarios for each matrix cell
- each matrix cell should contain 100 entries
- use the matrix to compare how each version behaves under increasing filter clarity and increasing preference specificity

## Separate Concern: Unrelated Queries

This should be treated as a separate test set, not as part of the main matrix.

Purpose:

- check how the system handles queries that are not actually travel recommendation requests

Characteristics:

- unrelated to travel recommendation
- outside destination discovery scope
- should not be interpreted as normal recommendation input

This set is useful for checking whether the system can distinguish travel recommendation requests from unrelated requests.

The unrelated-query set should also contain 100 entries.

## Special Note On Region-Characteristic Queries

Queries that mention something characteristic of a region should be placed mainly in `P1` or `P2`, depending on how specific they are.

These queries do not need to rely on explicit filters.
They are useful for testing whether the system can map a recognizable regional trait to relevant recommendations.

Explicit cities, landmarks, foods, sports, or animals should usually fall into `P2` when they define a narrow travel intent.

## Output Structure

Each file should be a JSON array.

Each array item should be a single object in this form:

```json
[
  {"f0_p0_1": "query"},
  {"f0_p0_2": "query"}
]
```

The object key should match the matrix cell and entry number.

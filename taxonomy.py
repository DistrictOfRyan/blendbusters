#!/usr/bin/env python3
"""Shared category classifier for the Markup Report + dataset.

One source of truth so the report page and the public dataset never drift.

Fix (2026-07-17): the old inline `'men' in c` test matched the substring "men"
inside "replaceMENt" (and "woMENt"/"women"), so every meal-replacement shake and
some women's products were mislabeled "Men's & testosterone". Men's is now matched
on a word boundary, and meal-replacement shakes route to Daily multivitamins &
greens to match how the homepage groups them.
"""
import re

_MENS = re.compile(r"\bmen'?s?\b")  # matches men / men's — NOT women / replacement


def cluster(cat):
    c = (cat or '').lower()
    if any(w in c for w in ['hydration', 'electrolyte']):
        return 'Hydration & electrolytes'
    if 'energy' in c:
        return 'Energy'
    if any(w in c for w in ['sleep', 'calm', 'stress']):
        return 'Sleep & calm'
    if any(w in c for w in ['brain', 'nootropic', 'focus', 'cognit', 'coffee']):
        return 'Brain & nootropics'
    if any(w in c for w in ['gut', 'probiotic', 'prebiotic', 'digest', 'fiber', 'omega',
                            'magnesium', 'synbiotic', 'enzyme']):
        return 'Gut, probiotic & omega'
    if _MENS.search(c) or 'testosterone' in c or 'prostate' in c:
        return "Men's & testosterone"
    if any(w in c for w in ['collagen', 'beauty', 'hair', 'skin', 'nail', 'joint',
                            'immune', 'circulation', 'coq10', 'turmeric']):
        return 'Beauty, joint & immune'
    if any(w in c for w in ['longevity', 'nad', 'nmn', 'heart']):
        return 'Longevity & heart'
    # protein/creatine/pre-workout stay in Fitness even when sold as a "shake"
    if any(w in c for w in ['fitness', 'protein', 'performance', 'creatine', 'workout',
                            'muscle', 'keto', 'amino', 'pre-workout']):
        return 'Fitness & performance'
    # meal-replacement shakes + daily nutrition -> grouped as the homepage groups them
    if any(w in c for w in ['multi', 'greens', 'vitamin', 'daily', 'meal replacement',
                            'meal', 'shake', 'superfood']):
        return 'Daily multivitamins & greens'
    return 'Other'

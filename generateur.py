# -*- coding: utf-8 -*-
import random
from banque_mots import WORD_BANK

# Filtre anti-doublon : mots déjà utilisés dans la session serveur
_used_words_session = set()


def reset_used_words():
    """Réinitialise le filtre anti-doublon."""
    _used_words_session.clear()


def _get_available_words(min_len, max_len, max_size):
    """Retourne les mots disponibles (non encore utilisés)."""
    return [
        (w, c) for (w, c) in WORD_BANK
        if min_len <= len(w) <= max_len and len(w) <= max_size
        and w not in _used_words_session
    ]


def _can_place(grid, word, r, c, direction, size):
    """Vérifie si un mot peut être placé à (r, c) dans la direction donnée."""
    if direction == 'H':
        if r < 0 or r >= size or c < 0 or c + len(word) > size:
            return False
    else:
        if c < 0 or c >= size or r < 0 or r + len(word) > size:
            return False

    for i, letter in enumerate(word):
        rr = r if direction == 'H' else r + i
        cc = c + i if direction == 'H' else c
        existing = grid[rr][cc]

        if existing and existing != letter:
            return False

        # Vérifier les cases adjacentes perpendiculaires
        if not existing:
            if direction == 'H':
                if rr > 0 and grid[rr - 1][cc]:
                    return False
                if rr < size - 1 and grid[rr + 1][cc]:
                    return False
            else:
                if cc > 0 and grid[rr][cc - 1]:
                    return False
                if cc < size - 1 and grid[rr][cc + 1]:
                    return False

    # Vérifier les extrémités
    if direction == 'H':
        if c > 0 and grid[r][c - 1]:
            return False
        if c + len(word) < size and grid[r][c + len(word)]:
            return False
    else:
        if r > 0 and grid[r - 1][c]:
            return False
        if r + len(word) < size and grid[r + len(word)][c]:
            return False

    return True


def generate_puzzle(level_index):
    """
    Génère une grille de mots croisés pour un niveau donné.
    Difficulté croissante : taille 7×7 → 19×19, 4 → 16 mots.
    Retourne un dict {size, words: [{r, c, dir, answer, clue}], level}.
    """
    difficulty = min(level_index, 40)
    size = min(7 + (difficulty // 3) * 2, 19)
    target_words = min(4 + (difficulty // 2), 16)

    max_word_len = max(5, min(size, 6 + difficulty // 4))
    min_word_len = max(3, min(5, 3 + difficulty // 8))

    pool = _get_available_words(min_word_len, max_word_len, size)

    # Si le pool est trop petit, réinitialiser le filtre
    if len(pool) < target_words * 3:
        reset_used_words()
        pool = _get_available_words(min_word_len, max_word_len, size)

    if not pool:
        pool = [(w, c) for (w, c) in WORD_BANK if len(w) <= size]

    random.shuffle(pool)

    grid = [['' for _ in range(size)] for _ in range(size)]
    placed = []

    # Placer le premier mot au centre (horizontal)
    first = next((m for m in pool if len(m[0]) <= size - 2), None)
    if not first:
        return generate_puzzle(0)

    word0, clue0 = first
    start_r = size // 2
    start_c = (size - len(word0)) // 2
    for i, letter in enumerate(word0):
        grid[start_r][start_c + i] = letter
    placed.append({'r': start_r, 'c': start_c, 'dir': 'H', 'answer': word0, 'clue': clue0})

    used_in_puzzle = {word0}
    attempts = 0
    max_attempts = 600

    while len(placed) < target_words and attempts < max_attempts:
        attempts += 1
        candidate = next((m for m in pool if m[0] not in used_in_puzzle), None)
        if not candidate:
            break

        word, clue = candidate
        best_placement = None

        existing_letters = [
            (r, c, grid[r][c])
            for r in range(size) for c in range(size) if grid[r][c]
        ]

        for wi, letter in enumerate(word):
            if best_placement:
                break
            for (er, ec, existing_letter) in existing_letters:
                if existing_letter != letter:
                    continue

                for direction in ('H', 'V'):
                    r = er if direction == 'H' else er - wi
                    c = ec - wi if direction == 'H' else ec

                    if not _can_place(grid, word, r, c, direction, size):
                        continue

                    crossings = 0
                    for i, l in enumerate(word):
                        rr = r if direction == 'H' else r + i
                        cc = c + i if direction == 'H' else c
                        if grid[rr][cc] == l:
                            crossings += 1

                    if crossings >= 1:
                        best_placement = {'r': r, 'c': c, 'dir': direction}
                        break
                if best_placement:
                    break

        if best_placement:
            r, c, direction = best_placement['r'], best_placement['c'], best_placement['dir']
            for i, letter in enumerate(word):
                rr = r if direction == 'H' else r + i
                cc = c + i if direction == 'H' else c
                grid[rr][cc] = letter
            placed.append({'r': r, 'c': c, 'dir': direction, 'answer': word, 'clue': clue})
            used_in_puzzle.add(word)
            _used_words_session.add(word)

    _used_words_session.add(word0)

    if len(placed) < 3:
        return generate_puzzle(max(0, level_index - 1))

    return {'size': size, 'words': placed, 'level': level_index}
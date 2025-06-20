def wrap(s: str, lim: int = 20) -> str:
    """
    Wrap the input string s so that no line is longer than lim.
    Breaks at whitespace where possible; words longer than lim are split.
    """
    words = s.split(sep=" ")
    lines: list[str] = []
    current: str = ""

    for word in words:
        # If adding the next word would exceed the limit...
        if current:
            sep = " "
            projected_length = len(current) + 1 + len(word)
        else:
            sep = ""
            projected_length = len(word)

        if projected_length <= lim:
            # Safe to add the word to current line
            current += sep + word
        else:
            # Current line is full—push it
            if current:
                lines.append(current)
            # If the word itself is too long, split it
            while len(word) > lim:
                lines.append(word[:lim])
                word = word[lim:]
            current = word

    # Don't forget the last line
    if current:
        lines.append(current)

    return "\r".join(lines)

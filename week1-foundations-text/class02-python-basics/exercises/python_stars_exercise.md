# Assignment: Interactive Shape Printer

**GSET Vibe Coding: AI Remix — Class 2**

## The Idea

In class you drew a square, a triangle, and a pyramid with `print()` and loops —
but the number of rows and the shape were hard-coded. Your job now is to make
it **interactive**: the program should ask the *user* what shape they want and
how big to make it, then draw it on the spot.

No AI needed for this one — it's all Python fundamentals. Save it as `shapes.py`.

## Requirements

Your program must:

1. **Ask the user how many rows the shape should have**, using `input()`.
   - Remember: `input()` always returns a string — you'll need `int(...)` to
     use it as a number.
2. **Ask the user which shape they want**: `square`, `triangle`, or `pyramid`.
3. **Use `if` / `elif` / `else`** to decide which shape to draw based on their
   answer.
4. **Use a loop (or nested loops)** to print that shape with *exactly* as many
   rows as the user asked for — not a fixed number.
5. **Handle an unrecognized shape name** — if the user types something that
   isn't `square`, `triangle`, or `pyramid`, print a friendly message instead
   of crashing.

## Example Run

```
How many rows? 4
Which shape (square / triangle / pyramid)? triangle

*
**
***
****
```

```
How many rows? 3
Which shape (square / triangle / pyramid)? pyramid

  *
 ***
*****
```

```
How many rows? 5
Which shape (square / triangle / pyramid)? hexagon

Sorry, "hexagon" isn't a shape I know. Try square, triangle, or pyramid.
```

## Concepts This Uses (all from Class 2)

| Concept | Where it shows up |
|---|---|
| `input()` | Asking for rows and shape name |
| `int()` | Turning the rows answer into a number |
| `if` / `elif` / `else` | Choosing which shape to draw |
| `for` loop + `range()` | Repeating one row at a time |
| String multiplication | `"*" * n` and `" " * n` |
| f-strings | Printing rows and friendly messages |

## Starter Template

You don't have to use this exact structure, but it's a reasonable way to start:

```python
rows = int(input("How many rows? "))
shape = input("Which shape (square / triangle / pyramid)? ")

if shape == "square":
    # your loop here
    pass
elif shape == "triangle":
    # your loop here
    pass
elif shape == "pyramid":
    # your loop here
    pass
else:
    print(f'Sorry, "{shape}" isn\'t a shape I know. Try square, triangle, or pyramid.')
```

## Stretch Goals (pick any, once the basics work)

- **Diamond**: a pyramid, then its mirror image upside-down underneath.
- **Hollow square**: only the border is filled with `*`, the middle is blank.
- **Pick your own character**: ask the user what symbol to draw with instead
  of always using `*`.
- **Validate the rows**: if the user types a letter instead of a number, or a
  negative number, print a friendly error instead of crashing.
- **Vibe it**: ask Cursor's AI to review your code and suggest one
  improvement — then decide if you agree and explain why.

## What "Done" Looks Like

- [ ] Program asks for rows and shape, in that order
- [ ] All three shapes (square, triangle, pyramid) work correctly
- [ ] The shape's size actually changes when you enter a different number of rows
- [ ] Typing an unknown shape name doesn't crash the program
- [ ] Code runs from the terminal with `python shapes.py`
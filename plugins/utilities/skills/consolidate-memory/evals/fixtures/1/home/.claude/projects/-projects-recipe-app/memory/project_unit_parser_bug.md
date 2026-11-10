        ---
        name: project-unit-parser-bug
        description: "Ingredient parser drops fractions like 1 1/2; fixed by tokenizing mixed numbers first"
        metadata:
          type: project
        ---

        The ingredient parser in src/parse/quantity.ts turned "1 1/2 cups" into 1 cup until
issue #41 changed it to tokenize mixed numbers before splitting on spaces.

**How to apply:** When touching quantity parsing, run the mixed-number fixtures in
tests/parse/quantity.test.ts first.

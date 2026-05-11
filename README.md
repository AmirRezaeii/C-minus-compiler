# C-Minus Compiler

A one-pass compiler for the C-Minus programming language (a simplified subset of C). Developed as a course project for Compiler Design at Sharif University of Technology.

## Overview

This compiler implements all compilation phases in a single pass:
- **Scanner** - Tokenizes input and builds symbol table
- **Parser** - Predictive top-down parser with error recovery
- **Code Generator** - Produces three-address code

## Features

- Keywords: `if`, `else`, `void`, `int`, `while`, `break`, `return`
- Arithmetic operators: `+`, `-`, `*`
- Relational operators: `<`, `==`
- Control flow: `if-else`, `while`, `break`
- Arrays and functions
- Built-in `output` function for printing integers

## Usage

- **Step 1:** Write C-Minus code in `input.txt`
- **Step 2:** Run `python3 compiler.py`
- **Step 3:** Check outputs:
  - `tokens.txt` - Token stream
  - `symbol_table.txt` - Symbol table
  - `lexical_errors.txt` - Lexical errors
  - `parse_tree.txt` - Parse tree
  - `syntax_errors.txt` - Syntax errors
  - `output.txt` - Three-address code

## Error Handling

- **Lexical**: Panic mode recovery

- **Syntax**: Panic mode with follow sets as synchronizing sets

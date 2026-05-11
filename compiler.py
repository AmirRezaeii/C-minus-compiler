from collections import defaultdict

class Scanner:
    keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'return']
    single_symbols = {';', ':', ',', '[', ']', '{', '}', '(', ')', '+', '-', '*', '/', '<'}
    alone_symbols = ['+', '-', '*', '/', '<', ':', ',', '>']
    can_be_after_numbers = {'+', '-', '*', '/', ';', ',', '<', '>', '=', ':', ')', '}', ']'} 
    brackets = ['[', ']', '{', '}', '(', ')']

    whitespace_chars = {' ', '\n', '\r', '\t', '\v', '\f'}

    def __init__(self, input_str):
        self.input = input_str
        self.pos = 0
        self.lineno = 1
        self.symbol_list = self.keywords.copy()
        self.symbol_table = {keyword: idx+1 for idx, keyword in enumerate(self.symbol_list)}
        self.errors = []
        

    def add_error(self, lineno, error_str, message):
        self.errors.append((lineno, error_str, message))
    
    def check_len(self):
        return self.pos + 1 < len(self.input)
    
    def next_char_equals(self, c):
        return self.check_len() and self.input[self.pos + 1] == c

    def handle_whitespace(self, current_char):
        if current_char in self.whitespace_chars:
            if current_char == '\n':
                self.lineno += 1
            self.pos += 1
            return True
        return False

    def handle_comments(self, current_char, lineno):
        if current_char == '/':
            if self.next_char_equals('*'): # check if /* has started (start of comment)
                self.pos += 2
                comment_start_lineno = self.lineno
                comment_buffer = []
                closed = False
                while self.pos < len(self.input): #look for the end of the comment */  and add to buffer if needed
                    if self.input[self.pos] == '*' and self.next_char_equals('/'):
                        self.pos += 2
                        closed = True
                        break
                    else:
                        if len(comment_buffer) < 5:
                            comment_buffer.append(self.input[self.pos])
                        if self.input[self.pos] == '\n':
                            self.lineno += 1
                        self.pos += 1
                if not closed: # we have reached the end of file and there were no */
                    error_str = ''.join(comment_buffer[:5])
                    if len(comment_buffer) >= 5:
                        error_str += '...'
                    self.add_error(comment_start_lineno, '/*' + error_str, 'Unclosed comment')
                return 0
            else:
                self.pos += 1
                return ('SYMBOL', '/', lineno)
        return None
    
    def handle_numbers(self, current_char, lineno):
        if current_char.isdigit():
            num_str = []
            while self.pos < len(self.input) and self.input[self.pos].isdigit():
                num_str.append(self.input[self.pos])
                self.pos += 1
            num_str = ''.join(num_str)
            
            if self.pos < len(self.input) and self.input[self.pos] not in (self.can_be_after_numbers | self.whitespace_chars):
                invalid = num_str
                invalid += self.input[self.pos]
                self.pos += 1
                self.add_error(lineno, invalid, 'Invalid number')
                return 0
            else:
                return ('NUM', num_str, lineno)
        return None
    
    def handle_id(self, current_char, lineno):
        if current_char.isalpha():
            id_str = [current_char]
            self.pos += 1
            while self.pos < len(self.input) and self.input[self.pos].isalnum():
                id_str.append(self.input[self.pos])
                self.pos += 1
            id_str = ''.join(id_str)
            if self.pos < len(self.input) and self.input[self.pos] != '=' and self.input[self.pos] not in self.single_symbols and self.input[self.pos] not in self.whitespace_chars:
                invalid = id_str
                invalid += self.input[self.pos]
                self.pos += 1
                self.add_error(lineno, invalid, 'Invalid Input')
                return 0
            if id_str in self.keywords:
                return ('KEYWORD', id_str, lineno)
            else:
                if id_str not in self.symbol_table:
                    self.symbol_list.append(id_str)
                    self.symbol_table[id_str] = len(self.symbol_list)
                return ('ID', id_str, lineno)
        return None
    
    def handle_symbols(self, current_char, lineno):
        if current_char == '*':
            if self.check_len() and self.input[self.pos + 1] == '/':
                self.pos += 2
                self.add_error(lineno, '*/', 'Unmatched Comment')
                return 0
        if current_char == '=':
            if self.check_len() and self.input[self.pos + 1] == '=':
                self.pos += 2
                return ('SYMBOL', '==', lineno)
            else:
                self.pos += 1
                return ('SYMBOL', '=', lineno)
        elif current_char in self.single_symbols:
            self.pos += 1
            if self.pos < len(self.input) and self.input[self.pos] not in self.whitespace_chars and not self.input[self.pos].isalnum() and self.input[self.pos] not in self.brackets and current_char in self.alone_symbols:
                invalid = current_char
                while self.pos < len(self.input) and self.input[self.pos] not in self.whitespace_chars and not self.input[self.pos].isalnum() and self.input[self.pos] not in self.brackets:
                    invalid += self.input[self.pos]
                    self.pos += 1
                self.add_error(lineno, invalid, 'Invalid Input')
                return 0
            return ('SYMBOL', current_char, lineno)
        return None

    def get_next_token(self):
        while self.pos < len(self.input):
            start_pos = self.pos
            current_char = self.input[start_pos]
            start_lineno = self.lineno


            if self.handle_whitespace(current_char):
                continue

            com = self.handle_comments(current_char, start_lineno)
            if com:
                return com
            elif com == 0:
                continue
            
            num = self.handle_numbers(current_char, start_lineno)
            if num:
                return num
            elif num == 0:
                continue

            keyword = self.handle_id(current_char, start_lineno)
            if keyword:
                return keyword
            elif keyword == 0:
                continue

            sym = self.handle_symbols(current_char, start_lineno)
            if sym:
                return sym
            elif sym == 0:
                continue

            self.add_error(start_lineno, current_char, 'Invalid input')
            self.pos += 1

        return None



from collections import defaultdict
from anytree import ContStyle, Node, RenderTree

from anytree import Node, RenderTree

class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.code_gen = code_generator()
        self.current_token = None
        self.errors = []
        self.root = None 
        self.first_set = {'Program': ['epsilon', 'int', 'void'], 'DeclarationList': ['epsilon', 'int', 'void'], 'Declaration': ['int', 'void'], 'DeclarationInitial': ['int', 'void'], 'DeclarationPrime': ['(', ';', '['], 'VarDeclarationPrime': [';', '['], 'FunDeclarationPrime': ['('], 'TypeSpecifier': ['int', 'void'], 'Params': ['int', 'void'], 'ParamList': [',', 'epsilon'], 'Param': ['int', 'void'], 'ParamPrime': ['[', 'epsilon'], 'CompoundStmt': ['{'], 'StatementList': ['epsilon', '{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM'], 'Statement': ['{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM'], 'ExpressionStmt': ['break', ';', 'ID', '+', '-', '(', 'NUM'], 'SelectionStmt': ['if'], 'IterationStmt': ['while'], 'ReturnStmt': ['return'], 'ReturnStmtPrime': [';', 'ID', '+', '-', '(', 'NUM'], 'Expression': ['ID', '+', '-', '(', 'NUM'], 'B': ['=', '[', '(', '*', '+', '-', '<', '==', 'epsilon'], 'H': ['=', '*', 'epsilon', '+', '-', '<', '=='], 'SimpleExpressionZegond': ['+', '-', '(', 'NUM'], 'SimpleExpressionPrime': ['(', '*', '+', '-', '<', '==', 'epsilon'], 'C': ['epsilon', '<', '=='], 'Relop': ['<', '=='], 'AdditiveExpression': ['+', '-', '(', 'ID', 'NUM'], 'AdditiveExpressionPrime': ['(', '*', '+', '-', 'epsilon'], 'AdditiveExpressionZegond': ['+', '-', '(', 'NUM'], 'D': ['epsilon', '+', '-'], 'Addop': ['+', '-'], 'Term': ['+', '-', '(', 'ID', 'NUM'], 'TermPrime': ['(', '*', 'epsilon'], 'TermZegond': ['+', '-', '(', 'NUM'], 'G': ['*', 'epsilon'], 'SignedFactor': ['+', '-', '(', 'ID', 'NUM'], 'SignedFactorPrime': ['(', 'epsilon'], 'SignedFactorZegond': ['+', '-', '(', 'NUM'], 'Factor': ['(', 'ID', 'NUM'], 'VarCallPrime': ['(', '[', 'epsilon'], 'VarPrime': ['[', 'epsilon'], 'FactorPrime': ['(', 'epsilon'], 'FactorZegond': ['(', 'NUM'], 'Args': ['epsilon', 'ID', '+', '-', '(', 'NUM'], 'ArgList': ['ID', '+', '-', '(', 'NUM'], 'ArgListPrime': [',', 'epsilon']}
        self.follow_set = {'Program': ['$'], 'DeclarationList': ['$', '{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM', '}'], 'Declaration': ['int', 'void', '$', '{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM', '}'], 'DeclarationInitial': ['(', ';', '[', ',', ')'], 'DeclarationPrime': ['int', 'void', '$', '{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM', '}'], 'VarDeclarationPrime': ['int', 'void', '$', '{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM', '}'], 'FunDeclarationPrime': ['int', 'void', '$', '{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM', '}'], 'TypeSpecifier': ['ID'], 'Params': [')'], 'ParamList': [')'], 'Param': [',', ')'], 'ParamPrime': [',', ')'], 'CompoundStmt': ['int', 'void', '$', '{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'], 'StatementList': ['}'], 'Statement': ['{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'], 'ExpressionStmt': ['{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'], 'SelectionStmt': ['{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'], 'IterationStmt': ['{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'], 'ReturnStmt': ['{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'], 'ReturnStmtPrime': ['{', 'break', ';', 'if', 'while', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'], 'Expression': [';', ')', ']', ','], 'B': [';', ')', ']', ','], 'H': [';', ')', ']', ','], 'SimpleExpressionZegond': [';', ')', ']', ','], 'SimpleExpressionPrime': [';', ')', ']', ','], 'C': [';', ')', ']', ','], 'Relop': ['+', '-', '(', 'ID', 'NUM'], 'AdditiveExpression': [';', ')', ']', ','], 'AdditiveExpressionPrime': ['<', '==', ';', ')', ']', ','], 'AdditiveExpressionZegond': ['<', '==', ';', ')', ']', ','], 'D': ['<', '==', ';', ')', ']', ','], 'Addop': ['+', '-', '(', 'ID', 'NUM'], 'Term': ['+', '-', ';', ')', '<', '==', ']', ','], 'TermPrime': ['+', '-', '<', '==', ';', ')', ']', ','], 'TermZegond': ['+', '-', '<', '==', ';', ')', ']', ','], 'G': ['+', '-', '<', '==', ';', ')', ']', ','], 'SignedFactor': ['*', '+', '-', ';', ')', '<', '==', ']', ','], 'SignedFactorPrime': ['*', '+', '-', '<', '==', ';', ')', ']', ','], 'SignedFactorZegond': ['*', '+', '-', '<', '==', ';', ')', ']', ','], 'Factor': ['*', '+', '-', ';', ')', '<', '==', ']', ','], 'VarCallPrime': ['*', '+', '-', ';', ')', '<', '==', ']', ','], 'VarPrime': ['*', '+', '-', ';', ')', '<', '==', ']', ','], 'FactorPrime': ['*', '+', '-', '<', '==', ';', ')', ']', ','], 'FactorZegond': ['*', '+', '-', '<', '==', ';', ')', ']', ','], 'Args': [')'], 'ArgList': [')'], 'ArgListPrime': [')']}
        self.get_next_token()
        self.non_terminal_functions = {
            'Program': self.program,
            'DeclarationList': self.declaration_list,
            'Declaration': self.declaration,
            'DeclarationInitial': self.declaration_initial,
            'DeclarationPrime': self.declaration_prime,
            'VarDeclarationPrime': self.var_declaration_prime,
            'FunDeclarationPrime': self.fun_declaration_prime,
            'TypeSpecifier': self.type_specifier,
            'Params': self.params,
            'ParamList': self.param_list,
            'Param': self.param,
            'ParamPrime': self.param_prime,
            'CompoundStmt': self.compound_stmt,
            'StatementList': self.statement_list,
            'Statement': self.statement,
            'ExpressionStmt': self.expression_stmt,
            'SelectionStmt': self.selection_stmt,
            'IterationStmt': self.iteration_stmt,
            'ReturnStmt': self.return_stmt,
            'ReturnStmtPrime': self.return_stmt_prime,
            'Expression': self.expression,
            'B': self.b,
            'H': self.h,
            'SimpleExpressionZegond': self.simple_expression_zegond,
            'SimpleExpressionPrime': self.simple_expression_prime,
            'C': self.c,
            'Relop': self.relop,
            'AdditiveExpression': self.additive_expression,
            'AdditiveExpressionPrime': self.additive_expression_prime,
            'AdditiveExpressionZegond': self.additive_expression_zegond,
            'D': self.d,
            'Addop': self.addop,
            'Term': self.term,
            'TermPrime': self.term_prime,
            'TermZegond': self.term_zegond,
            'G': self.g,
            'SignedFactor': self.signed_factor,
            'SignedFactorPrime': self.signed_factor_prime,
            'SignedFactorZegond': self.signed_factor_zegond,
            'Factor': self.factor,
            'VarCallPrime': self.var_call_prime,
            'VarPrime': self.var_prime,
            'FactorPrime': self.factor_prime,
            'FactorZegond': self.factor_zegond,
            'Args': self.args,
            'ArgList': self.arg_list,
            'ArgListPrime': self.arg_list_prime
        }
    
    def get_next_token(self):
        self.current_token = self.scanner.get_next_token()
        if self.current_token is None:
            self.current_token = ('$', '$', self.scanner.lineno)
        return self.current_token

    def add_error(self, message):
        if self.current_token[0] != '$':
            self.errors.append((self.current_token[2], f"Syntax error! Unexpected {self.current_token[1]}"))
    
    def match(self, expected_type, expected_lexeme=None, parent=None):
        # Handle both type-only and type+lexeme matches
        type_match = self.current_token[0] == expected_type
        lexeme_match = expected_lexeme is None or self.current_token[1] == expected_lexeme
        
        if type_match and lexeme_match:
            Node(f"({expected_type}, {self.current_token[1]}) ", parent=parent)
            self.get_next_token()
            return
        
        if type_match == 'ID' or type_match == 'NUM':
            self.errors.append((self.current_token[2], f'syntax error, missing {expected_type}'))
        else:
            self.errors.append((self.current_token[2], f'syntax error, missing {expected_lexeme}'))

    def get_first_set(self, items):
        output = []
        for item in items:
            if item not in self.first_set:
                output.append(item)
                output = [x for x in output if x != 'epsilon']
                break
            output.extend(self.first_set[item])
            if 'epsilon' not in self.first_set[item]:
                output = [x for x in output if x != 'epsilon']
                break
        
        return list(set(output))

    def write_output_files(self):
        with open('parse_tree.txt', 'w', encoding="utf-8") as f:
            for pre, _, node in RenderTree(self.root):
                f.write(f"{pre}{node.name}\n")
        
        with open('syntax_errors.txt', 'w') as f:
            if not self.errors:
                f.write("There is no syntax error.\n")
            else:
                for lineno, msg in (self.errors):
                    f.write(f"#{lineno} : {msg}\n")

    def parse(self):
        self.root = Node("Program")
        self.program(self.root)
        self.write_output_files()

    # Grammar rules implementation
    # Rule 1: Program -> DeclarationList
    def program(self, parent):
        prod = ['DeclarationList']
        if self.current_token[1] in self.get_first_set(prod):
            self.code_gen.code_gen('start_program')
            decl_list_node = Node("DeclarationList", parent=parent)
            self.declaration_list(decl_list_node)
            self.code_gen.code_gen('end_program')
            Node('$', parent=parent)
        else:
            self.panic_mode('Program', parent)

    # Rule 2: DeclarationList -> Declaration DeclarationList | EPSILON
    def declaration_list(self, parent):
        prod1 = ['Declaration', 'DeclarationList']
        prod2 = ['epsilon']
        
        if self.current_token[1] in self.get_first_set(prod1):
            decl_node = Node("Declaration", parent=parent)
            self.declaration(decl_node)
            decl_list_node = Node("DeclarationList", parent=parent)
            self.declaration_list(decl_list_node)
        elif (self.current_token[1] in self.follow_set['DeclarationList'] or self.current_token[0] in self.follow_set['DeclarationList']):
            Node("epsilon", parent=parent)
        else:
            self.panic_mode('DeclarationList', parent)

    # Rule 3: Declaration -> DeclarationInitial DeclarationPrime
    def declaration(self, parent):
        prod = ['DeclarationInitial', 'DeclarationPrime']
        if self.current_token[1] in self.get_first_set(prod):
            initial_node = Node("DeclarationInitial", parent=parent)
            self.declaration_initial(initial_node)
            prime_node = Node("DeclarationPrime", parent=parent)
            self.declaration_prime(prime_node)
        else:
            self.panic_mode('Declaration', parent)

    # Rule 4: DeclarationInitial -> TypeSpecifier ID 
    def declaration_initial(self, parent):
        prod = ['TypeSpecifier', 'ID']
        if self.current_token[1] in self.get_first_set(prod):
            type_node = Node("TypeSpecifier", parent=parent)
            self.type_specifier(type_node)
            if self.current_token[0] == 'ID':
                self.code_gen.code_gen('put_name', self.current_token[1])
                self.match('ID', parent=parent)
            else:
                self.add_error("Missing ID")
                self.panic_mode('DeclarationInitial', parent)
        else:
            self.panic_mode('DeclarationInitial', parent)

    # Rule 5: DeclarationPrime -> FunDeclarationPrime | VarDeclarationPrime
    def declaration_prime(self, parent):
        prod1 = ['FunDeclarationPrime']
        prod2 = ['VarDeclarationPrime']
        
        if self.current_token[1] in self.get_first_set(prod1):
            fun_node = Node("FunDeclarationPrime", parent=parent)
            self.fun_declaration_prime(fun_node)
        elif self.current_token[1] in self.get_first_set(prod2):
            var_node = Node("VarDeclarationPrime", parent=parent)
            self.var_declaration_prime(var_node)
        else:
            self.panic_mode('DeclarationPrime', parent)

    # Rule 6: VarDeclarationPrime -> ; | [ NUM ] ;
    def var_declaration_prime(self, parent):
        prod1 = [';']
        prod2 = ['[', 'NUM', ']', ';']
        
        if self.current_token[1] in self.get_first_set(prod1):
            if self.current_token[1] == ';':
                self.match('SYMBOL', parent=parent)
                self.code_gen.code_gen('declare_var')
        elif self.current_token[1] in self.get_first_set(prod2):
            self.match('SYMBOL', '[', parent)
            if self.current_token[0] == 'NUM':
                self.code_gen.code_gen('put_num', int(self.current_token[1]))
                self.match('NUM', parent=parent)
                self.match('SYMBOL', ']', parent)
                self.match('SYMBOL', ';', parent)
                self.code_gen.code_gen('declare_arr')
            else:
                self.add_error("Missing NUM")
                self.panic_mode('VarDeclarationPrime', parent)
        else:
            self.panic_mode('VarDeclarationPrime', parent)

    # Rule 7: FunDeclarationPrime -> ( Params ) CompoundStmt
    def fun_declaration_prime(self, parent):
        prod = ['(', 'Params', ')', 'CompoundStmt']
        
        if self.current_token[1] in self.get_first_set(prod):
            self.match('SYMBOL', '(', parent)
            self.code_gen.code_gen('start_func')
            params_node = Node("Params", parent=parent)
            self.params(params_node)
            self.match('SYMBOL', ')', parent)
            self.code_gen.code_gen('end_func_params')
            compound_node = Node("CompoundStmt", parent=parent)
            self.compound_stmt(compound_node)
            self.code_gen.code_gen('end_func')
        else:
            self.panic_mode('FunDeclarationPrime', parent)

    # Rule 8: TypeSpecifier -> int | void
    def type_specifier(self, parent):
        prod1 = ['int']
        prod2 = ['void']
        
        if self.current_token[1] in self.get_first_set(prod1):
            self.match('KEYWORD', 'int', parent)
            self.code_gen.code_gen('type_int')
        elif self.current_token[1] in self.get_first_set(prod2):
            self.match('KEYWORD', 'void', parent)
            self.code_gen.code_gen('type_void')
        else:
            self.panic_mode('TypeSpecifier', parent)

    # Rule 9: Params -> int ID ParamPrime ParamList | void
    def params(self, parent):
        prod1 = ['int', 'ID', 'ParamPrime', 'ParamList']
        prod2 = ['void']
        
        if self.current_token[1] in self.get_first_set(prod1) or self.current_token[0] in self.get_first_set(prod1):
            self.match('KEYWORD', 'int', parent)
            if self.current_token[0] == 'ID':
                self.code_gen.code_gen('put_name', self.current_token[1])
                self.match('ID', parent=parent)
                param_prime_node = Node("ParamPrime", parent=parent)
                self.param_prime(param_prime_node)
                param_list_node = Node("ParamList", parent=parent)
                self.param_list(param_list_node)
            else:
                self.add_error("Missing ID")
                self.panic_mode('Params', parent)
        elif self.current_token[1] in self.get_first_set(prod2):
            self.match('KEYWORD', 'void', parent)
        else:
            self.panic_mode('Params', parent)

    # Rule 10: ParamList -> , Param ParamList | EPSILON
    def param_list(self, parent):
        prod1 = [',', 'Param', 'ParamList']
        prod2 = ['epsilon']
        
        if self.current_token[1] in self.get_first_set(prod1):
            self.match('SYMBOL', ',', parent)
            param_node = Node("Param", parent=parent)
            self.param(param_node)
            param_list_node = Node("ParamList", parent=parent)
            self.param_list(param_list_node)
        elif (self.current_token[1] in self.follow_set['ParamList']):
            Node("epsilon", parent=parent)
        else:
            self.panic_mode('ParamList', parent)

    # Rule 11: Param -> DeclarationInitial ParamPrime
    def param(self, parent):
        prod = ['DeclarationInitial', 'ParamPrime']
        if self.current_token[1] in self.get_first_set(prod):
            decl_initial_node = Node("DeclarationInitial", parent=parent)
            self.declaration_initial(decl_initial_node)
            param_prime_node = Node("ParamPrime", parent=parent)
            self.param_prime(param_prime_node)
        else:
            self.panic_mode('Param', parent)
    
    # Rule 12: ParamPrime -> [ ] | EPSILON
    def param_prime(self, parent):
        prod1 = ['[', ']']
        prod2 = ['epsilon']
        
        if self.current_token[1] in self.get_first_set(prod1):
            self.match('SYMBOL', '[', parent)
            self.match('SYMBOL', ']', parent)
            self.code_gen.code_gen('declare_arr_param')
        elif (self.current_token[1] in self.follow_set['ParamPrime']):
            Node("epsilon", parent=parent)
            self.code_gen.code_gen('declare_var_param')
        else:
            self.panic_mode('ParamPrime', parent)
    
    # Rule 13: CompoundStmt -> { DeclarationList StatementList }
    def compound_stmt(self, parent):
        prod = ['{', 'DeclarationList', 'StatementList', '}']
        if self.current_token[1] in self.get_first_set(prod):
            self.match('SYMBOL', '{', parent)
            decl_list_node = Node("DeclarationList", parent=parent)
            self.declaration_list(decl_list_node)
            stmt_list_node = Node("StatementList", parent=parent)
            self.statement_list(stmt_list_node)
            self.match('SYMBOL', '}', parent)
        else:
            self.panic_mode('CompoundStmt', parent)

    # Rule 14: StatementList -> Statement StatementList | EPSILON
    def statement_list(self, parent):
        prod1 = ['Statement', 'StatementList']
        prod2 = ['epsilon']

        # print(self.get_first_set(prod1))
        # print(self.current_token)
        
        if self.current_token[1] in self.get_first_set(prod1) or self.current_token[0] in self.get_first_set(prod1):
            self.code_gen.code_gen('stm_start')
            stmt_node = Node("Statement", parent=parent)
            self.statement(stmt_node)
            self.code_gen.code_gen('popper')
            stmt_list_node = Node("StatementList", parent=parent)
            self.statement_list(stmt_list_node)
        elif ((self.current_token[1] in self.follow_set['StatementList'] or self.current_token[0] in self.follow_set['StatementList'])):
            Node("epsilon", parent=parent)
        else:
            self.panic_mode('StatementList', parent)

    # Rule 15: Statement -> ExpressionStmt | CompoundStmt | SelectionStmt | IterationStmt | ReturnStmt
    def statement(self, parent):
        options = [
            ['ExpressionStmt'],
            ['CompoundStmt'],
            ['SelectionStmt'],
            ['IterationStmt'],
            ['ReturnStmt']
        ]
        
        for option in options:
            # print('\n', self.current_token[0], self.get_first_set(option))
            if self.current_token[1] in self.get_first_set(option) or self.current_token[0] in self.get_first_set(option):
                # return
                if option[0] == 'ExpressionStmt':
                    expr_stmt_node = Node("ExpressionStmt", parent=parent)
                    self.expression_stmt(expr_stmt_node)
                elif option[0] == 'CompoundStmt':
                    compound_node = Node("CompoundStmt", parent=parent)
                    self.compound_stmt(compound_node)
                elif option[0] == 'SelectionStmt':
                    select_node = Node("SelectionStmt", parent=parent)
                    self.selection_stmt(select_node)
                elif option[0] == 'IterationStmt':
                    iter_node = Node("IterationStmt", parent=parent)
                    self.iteration_stmt(iter_node)
                elif option[0] == 'ReturnStmt':
                    return_node = Node("ReturnStmt", parent=parent)
                    self.return_stmt(return_node)
                return
        self.panic_mode('Statement', parent)
    
    # Rule 16: ExpressionStmt -> Expression ; | break ; | ;
    def expression_stmt(self, parent):
        options = [
            ['Expression', ';'],
            ['break', ';'],
            [';']
        ]
        
        for option in options:
            if self.current_token[1] in self.get_first_set(option) or self.current_token[0] in self.get_first_set(option):
                if option[0] == 'Expression':
                    expr_node = Node("Expression", parent=parent)
                    self.expression(expr_node)
                    self.match('SYMBOL', ';', parent)
                elif option[0] == 'break':
                    self.match('KEYWORD', 'break', parent)
                    self.match('SYMBOL', ';', parent)
                    self.code_gen.code_gen('break_stm')
                else:
                    self.match('SYMBOL', ';', parent)
                return
        self.panic_mode('ExpressionStmt', parent)
    
    # Rule 17: SelectionStmt -> if ( Expression ) Statement else Statement
    def selection_stmt(self, parent):
        prod = ['if', '(', 'Expression', ')', 'Statement', 'else', 'Statement']
        if self.current_token[1] in self.get_first_set(prod):
            self.match('KEYWORD', 'if', parent)
            self.match('SYMBOL', '(', parent)
            expr_node = Node("Expression", parent=parent)
            self.expression(expr_node)
            self.match('SYMBOL', ')', parent)
            self.code_gen.code_gen('save')
            stmt_node = Node("Statement", parent=parent)
            self.statement(stmt_node)
            self.match('KEYWORD', 'else', parent)
            self.code_gen.code_gen('jpf_save')
            else_node = Node("Statement", parent=parent)
            self.statement(else_node)
            self.code_gen.code_gen('jp')
        else:
            self.panic_mode('SelectionStmt', parent)

    # Rule 18: IterationStmt -> while ( Expression ) Statement
    def iteration_stmt(self, parent):
        prod = ['while', '(', 'Expression', ')', 'Statement']
        if self.current_token[1] in self.get_first_set(prod):
            self.match('KEYWORD', 'while', parent)
            self.code_gen.code_gen('label')
            self.match('SYMBOL', '(', parent)
            expr_node = Node("Expression", parent=parent)
            self.expression(expr_node)
            self.match('SYMBOL', ')', parent)
            self.code_gen.code_gen('save')
            stmt_node = Node("Statement", parent=parent)
            self.statement(stmt_node)
            self.code_gen.code_gen('while_stm')
        else:
            self.panic_mode('IterationStmt', parent)
    
    # Rule 19: ReturnStmt -> return ReturnStmtPrime
    def return_stmt(self, parent):
        prod = ['return', 'ReturnStmtPrime']
        if self.current_token[1] in self.get_first_set(prod):
            self.match('KEYWORD', 'return', parent)
            prime_node = Node("ReturnStmtPrime", parent=parent)
            self.return_stmt_prime(prime_node)
        else:
            self.panic_mode('ReturnStmt', parent)
    
    # Rule 20: ReturnStmtPrime -> ; | Expression ;
    def return_stmt_prime(self, parent):
        options = [
            [';'],
            ['Expression', ';']
        ]
        
        for option in options:
            if self.current_token[1] in self.get_first_set(option) or self.current_token[0] in self.get_first_set(option):
                if option[0] == ';':
                    self.match('SYMBOL', ';', parent)
                    self.code_gen.code_gen('end_func')
                else:
                    expr_node = Node("Expression", parent=parent)
                    self.expression(expr_node)
                    self.match('SYMBOL', ';', parent)
                    self.code_gen.code_gen('return_value')
                return
        self.panic_mode('ReturnStmtPrime', parent)
    
    # Rule 21: Expression -> SimpleExpressionZegond | ID B
    def expression(self, parent):
        options = [
            ['SimpleExpressionZegond'],
            ['ID', 'B']
        ]
        
        for option in options:
            if self.current_token[1] in self.get_first_set(option) or self.current_token[0] in self.get_first_set(option):
                if option[0] == 'SimpleExpressionZegond':
                    zegond_node = Node("SimpleExpressionZegond", parent=parent)
                    self.simple_expression_zegond(zegond_node)
                else:
                    if self.current_token[0] == 'ID':
                        self.code_gen.code_gen('pid', self.current_token[1])
                        self.match('ID', parent=parent)
                        b_node = Node("B", parent=parent)
                        self.b(b_node)
                return
        self.panic_mode('Expression', parent)
    
    # Rule 22: B -> = Expression | [ Expression ] H | SimpleExpressionPrime
    def b(self, parent):
        options = [
            ['=', 'Expression'],
            ['[', 'Expression', ']', 'H'],
            ['SimpleExpressionPrime']
        ]
        
        for option in options:
            if self.current_token[1] in self.get_first_set(option) or ('epsilon' in self.get_first_set(option) and self.current_token[1] in self.follow_set['B']):
                if option[0] == '=':
                    self.match('SYMBOL', '=', parent)
                    expr_node = Node("Expression", parent=parent)
                    self.expression(expr_node)
                    self.code_gen.code_gen('assign')
                elif option[0] == '[':
                    self.match('SYMBOL', '[', parent)
                    expr_node = Node("Expression", parent=parent)
                    self.expression(expr_node)
                    self.match('SYMBOL', ']', parent)
                    self.code_gen.code_gen('arruse')
                    h_node = Node("H", parent=parent)
                    self.h(h_node)
                else:
                    prime_node = Node("SimpleExpressionPrime", parent=parent)
                    self.simple_expression_prime(prime_node)
                return
        self.panic_mode('B', parent)
    
    # Rule 23: H -> = Expression | G D C
    def h(self, parent):
        options = [
            ['=', 'Expression'],
            ['G', 'D', 'C']
        ]
        
        for option in options:
            if self.current_token[1] in self.get_first_set(option) or ('epsilon' in self.get_first_set(option) and self.current_token[1] in self.follow_set['H']):
                if option[0] == '=':
                    self.match('SYMBOL', '=', parent)
                    expr_node = Node("Expression", parent=parent)
                    self.expression(expr_node)
                    self.code_gen.code_gen('assign')
                else:
                    g_node = Node("G", parent=parent)
                    self.g(g_node)
                    d_node = Node("D", parent=parent)
                    self.d(d_node)
                    c_node = Node("C", parent=parent)
                    self.c(c_node)
                return
        self.panic_mode('H', parent)

    # Rule 24: SimpleExpressionZegond -> AdditiveExpressionZegond C
    def simple_expression_zegond(self, parent):
        prod = ['AdditiveExpressionZegond', 'C']
        if self.current_token[1] in self.get_first_set(prod) or self.current_token[0] in self.get_first_set(prod):
            zegond_node = Node("AdditiveExpressionZegond", parent=parent)
            self.additive_expression_zegond(zegond_node)
            c_node = Node("C", parent=parent)
            self.c(c_node)
        else:
            self.panic_mode('SimpleExpressionZegond', parent)

    # Rule 25: SimpleExpressionPrime -> AdditiveExpressionPrime C
    def simple_expression_prime(self, parent):
        prod = ['AdditiveExpressionPrime', 'C']
        if self.current_token[1] in self.get_first_set(prod) or ('epsilon' in self.get_first_set(prod) and self.current_token[1] in self.follow_set['SimpleExpressionPrime']):
            prime_node = Node("AdditiveExpressionPrime", parent=parent)
            self.additive_expression_prime(prime_node)
            c_node = Node("C", parent=parent)
            self.c(c_node)
        else:
            self.panic_mode('SimpleExpressionPrime', parent)

    # Rule 26: Relop AdditiveExpression | EPSILON
    def c(self, parent):
        options = [
            ['Relop', 'AdditiveExpression'],
            ['epsilon']
        ]
        
        if self.current_token[1] in self.get_first_set(options[0]):
            relop_node = Node("Relop", parent=parent)
            self.relop(relop_node)
            add_expr_node = Node("AdditiveExpression", parent=parent)
            self.additive_expression(add_expr_node)
            self.code_gen.code_gen('compare')
        elif (self.current_token[1] in self.follow_set['C']):
            Node("epsilon", parent=parent)
        else:
            self.panic_mode('C', parent)
    
    # Rule 27: Relop -> < | ==
    def relop(self, parent):
        options = [
            ['<'],
            ['==']
        ]
        
        for option in options:
            if self.current_token[1] in self.get_first_set(option):
                self.match('SYMBOL', option[0], parent)
                if option[0] == '==':
                    self.code_gen.code_gen('iseq')
                else:
                    self.code_gen.code_gen('islt')
                return
        self.panic_mode('Relop', parent)

    # Rule 28: AdditiveExpression -> Term D
    def additive_expression(self, parent):
        prod = ['Term', 'D']
        if self.current_token[1] in self.get_first_set(prod) or self.current_token[0] in self.get_first_set(prod):
            term_node = Node("Term", parent=parent)
            self.term(term_node)
            d_node = Node("D", parent=parent)
            self.d(d_node)
        else:
            self.panic_mode('AdditiveExpression', parent)
        
    # Rule 29: AdditiveExpressionPrime -> TermPrime D
    def additive_expression_prime(self, parent):
        prod = ['TermPrime', 'D']
        if self.current_token[1] in self.get_first_set(prod) or (self.current_token[1] in self.follow_set['AdditiveExpressionPrime'] and 'epsilon' in self.get_first_set(prod)):
            prime_node = Node("TermPrime", parent=parent)
            self.term_prime(prime_node)
            d_node = Node("D", parent=parent)
            self.d(d_node)
        else:
            self.panic_mode('AdditiveExpressionPrime', parent)

    # Rule 30: AdditiveExpressionZegond -> TermZegond D
    def additive_expression_zegond(self, parent):
        prod = ['TermZegond', 'D']
        if self.current_token[1] in self.get_first_set(prod) or self.current_token[0] in self.get_first_set(prod):
            zegond_node = Node("TermZegond", parent=parent)
            self.term_zegond(zegond_node)
            d_node = Node("D", parent=parent)
            self.d(d_node)
        else:
            self.panic_mode('AdditiveExpressionZegond', parent)

    # Rule 31: D -> Addop Term D | EPSILON
    def d(self, parent):
        options = [
            ['Addop', 'Term', 'D'],
            ['epsilon']
        ]
        for option in options:
            if self.current_token[1] in self.get_first_set(option):
                if option[0] == 'Addop':
                    addop_node = Node("Addop", parent=parent)
                    self.addop(addop_node)
                    term_node = Node("Term", parent=parent)
                    self.term(term_node)
                    self.code_gen.code_gen('add')
                    d_node = Node("D", parent=parent)
                    self.d(d_node)
                else:
                    Node("epsilon", parent=parent)
                return
        if (self.current_token[1] in self.follow_set['D']):
            Node("epsilon", parent=parent)
            return
        self.panic_mode('D', parent)

    # Rule 32: Addop -> + | -
    def addop(self, parent):
        options = [['+'], ['-']]
        for option in options:
            if self.current_token[1] in self.get_first_set(option):
                if option[0] == '+':
                    self.code_gen.code_gen('setp')
                else:
                    self.code_gen.code_gen('setm')
                self.match('SYMBOL', option[0], parent)
                return
        self.panic_mode('Addop', parent)

    # Rule 33: Term -> SignedFactor G
    def term(self, parent):
        prod = ['SignedFactor', 'G']
        if self.current_token[1] in self.get_first_set(prod) or self.current_token[0] in self.get_first_set(prod):
            sf_node = Node("SignedFactor", parent=parent)
            self.signed_factor(sf_node)
            g_node = Node("G", parent=parent)
            self.g(g_node)
        else:
            self.panic_mode('Term', parent)

    # Rule 34: TermPrime -> SignedFactorPrime G
    def term_prime(self, parent):
        prod = ['SignedFactorPrime', 'G']
        if self.current_token[1] in self.get_first_set(prod) or (self.current_token[1] in self.follow_set['TermPrime'] and 'epsilon' in self.get_first_set(prod)):
            sfp_node = Node("SignedFactorPrime", parent=parent)
            self.signed_factor_prime(sfp_node)
            g_node = Node("G", parent=parent)
            self.g(g_node)
        else:
            self.panic_mode('TermPrime', parent)

    # Rule 35: TermZegond -> SignedFactorZegond G
    def term_zegond(self, parent):
        prod = ['SignedFactorZegond', 'G']
        if self.current_token[1] in self.get_first_set(prod) or self.current_token[0] in self.get_first_set(prod):
            sfz_node = Node("SignedFactorZegond", parent=parent)
            self.signed_factor_zegond(sfz_node)
            g_node = Node("G", parent=parent)
            self.g(g_node)
        else:
            self.panic_mode('TermZegond', parent)

    # Rule 36: G -> * SignedFactor G | EPSILON
    def g(self, parent):
        options = [
            ['*', 'SignedFactor', 'G'],
            ['epsilon']
        ]
        if self.current_token[1] in self.get_first_set(options[0]):
            self.match('SYMBOL', '*', parent)
            sf_node = Node("SignedFactor", parent=parent)
            self.signed_factor(sf_node)
            self.code_gen.code_gen('mult')
            g_node = Node("G", parent=parent)
            self.g(g_node)
        elif (self.current_token[1] in self.follow_set['G']):
            Node("epsilon", parent=parent)
        else:
            self.panic_mode('G', parent)

    # Rule 37: SignedFactor -> + Factor | - Factor | Factor
    def signed_factor(self, parent):
        options = [
            ['+', 'Factor'],
            ['-', 'Factor'],
            ['Factor']
        ]
        for option in options:
            if self.current_token[1] in self.get_first_set(option) or self.current_token[0] in self.get_first_set(option):
                if option[0] in ['+', '-']:
                    self.match('SYMBOL', option[0], parent)
                    factor_node = Node("Factor", parent=parent)
                    self.factor(factor_node)
                else:
                    factor_node = Node("Factor", parent=parent)
                    self.factor(factor_node)
                return
        self.panic_mode('SignedFactor', parent)

    # Rule 38: SignedFactorPrime -> FactorPrime
    def signed_factor_prime(self, parent):
        prod = ['FactorPrime']
        if self.current_token[1] in self.get_first_set(prod) or (self.current_token[1] in self.follow_set['SignedFactorPrime'] and 'epsilon' in self.get_first_set(prod)):
            fp_node = Node("FactorPrime", parent=parent)
            self.factor_prime(fp_node)
        else:
            self.panic_mode('SignedFactorPrime', parent)

    # Rule 39: SignedFactorZegond -> + Factor | - Factor | FactorZegond
    def signed_factor_zegond(self, parent):
        options = [
            ['+', 'Factor'],
            ['-', 'Factor'],
            ['FactorZegond']
        ]
        for option in options:
            if self.current_token[1] in self.get_first_set(option) or self.current_token[0] in self.get_first_set(option):
                if option[0] in ['+', '-']:
                    self.match('SYMBOL', option[0], parent)
                    factor_node = Node("Factor", parent=parent)
                    self.factor(factor_node)
                else:
                    fz_node = Node("FactorZegond", parent=parent)
                    self.factor_zegond(fz_node)
                return
        self.panic_mode('SignedFactorZegond', parent)

    # Rule 40: Factor -> ( Expression ) | ID VarCallPrime | NUM
    def factor(self, parent):
        options = [
            ['(', 'Expression', ')'],
            ['ID', 'VarCallPrime'],
            ['NUM']
        ]
        for option in options:
            if self.current_token[1] in self.get_first_set(option) or self.current_token[0] in self.get_first_set(option):
                if option[0] == '(':
                    self.match('SYMBOL', '(', parent)
                    expr_node = Node("Expression", parent=parent)
                    self.expression(expr_node)
                    self.match('SYMBOL', ')', parent)
                elif option[0] == 'ID':
                    self.code_gen.code_gen('pid', self.current_token[1])
                    self.match('ID', parent=parent)
                    vcp_node = Node("VarCallPrime", parent=parent)
                    self.var_call_prime(vcp_node)
                else:
                    self.code_gen.code_gen('pnum', self.current_token[1])
                    self.match('NUM', parent=parent)
                return
        self.panic_mode('Factor', parent)

    # Rule 41: VarCallPrime -> ( Args ) | VarPrime
    def var_call_prime(self, parent):
        options = [
            ['(', 'Args', ')'],
            ['VarPrime']
        ]
        for option in options:
            if self.current_token[1] in self.get_first_set(option) or ('epsilon' in self.get_first_set(option) and self.current_token[1] in self.follow_set['VarCallPrime']):
                if option[0] == '(':
                    self.match('SYMBOL', '(', parent)
                    args_node = Node("Args", parent=parent)
                    self.args(args_node)
                    self.match('SYMBOL', ')', parent)
                    self.code_gen.code_gen('func_call')
                else:
                    vp_node = Node("VarPrime", parent=parent)
                    self.var_prime(vp_node)
                return
        self.panic_mode('VarCallPrime', parent)

    # Rule 42: VarPrime -> [ Expression ] | EPSILON
    def var_prime(self, parent):
        options = [
            ['[', 'Expression', ']'],
            ['epsilon']
        ]
        if self.current_token[1] in self.get_first_set(options[0]):
            self.match('SYMBOL', '[', parent)
            expr_node = Node("Expression", parent=parent)
            self.expression(expr_node)
            self.match('SYMBOL', ']', parent)
            self.code_gen.code_gen('arruse')
        elif (self.current_token[1] in self.follow_set['VarPrime']):
            Node("epsilon", parent=parent)
        else:
            self.panic_mode('VarPrime', parent)

    # Rule 43: FactorPrime -> ( Args ) | EPSILON
    def factor_prime(self, parent):
        options = [
            ['(', 'Args', ')'],
            ['epsilon']
        ]
        if self.current_token[1] in self.get_first_set(options[0]):
            self.match('SYMBOL', '(', parent)
            args_node = Node("Args", parent=parent)
            self.args(args_node)
            self.match('SYMBOL', ')', parent)
            self.code_gen.code_gen('func_call')
        elif (self.current_token[1] in self.follow_set['FactorPrime']):
            Node("epsilon", parent=parent)
        else:
            self.panic_mode('FactorPrime', parent)

    # Rule 44: FactorZegond -> ( Expression ) | NUM
    def factor_zegond(self, parent):
        options = [
            ['(', 'Expression', ')'],
            ['NUM']
        ]
        for option in options:
            if self.current_token[1] in self.get_first_set(option) or self.current_token[0] in self.get_first_set(option):
                if option[0] == '(':
                    self.match('SYMBOL', '(', parent)
                    expr_node = Node("Expression", parent=parent)
                    self.expression(expr_node)
                    self.match('SYMBOL', ')', parent)
                else:
                    self.code_gen.code_gen('pnum', self.current_token[1])
                    self.match('NUM', parent=parent)
                return
        self.panic_mode('FactorZegond', parent)

    # Rule 45: Args -> ArgList | EPSILON
    def args(self, parent):
        options = [
            ['ArgList'],
            ['epsilon']
        ]
        if self.current_token[1] in self.get_first_set(options[0]) or self.current_token[0] in self.get_first_set(options[0]):
            al_node = Node("ArgList", parent=parent)

            self.arg_list(al_node)
        elif (self.current_token[1] in self.follow_set['Args']):
            Node("epsilon", parent=parent)
        else:
            self.panic_mode('Args', parent)

    # Rule 46: ArgList -> Expression ArgListPrime
    def arg_list(self, parent):
        prod = ['Expression', 'ArgListPrime']
        if self.current_token[1] in self.get_first_set(prod) or self.current_token[0] in self.get_first_set(prod):
            expr_node = Node("Expression", parent=parent)
            self.expression(expr_node)
            alp_node = Node("ArgListPrime", parent=parent)
            self.arg_list_prime(alp_node)
        elif (self.current_token[1] in self.follow_set['ArgList'] and
              'epsilon' in self.get_first_set(prod[1])):
            Node("epsilon", parent=parent)
        else:
            self.panic_mode('ArgList', parent)

    # Rule 47: ArgListPrime -> , Expression ArgListPrime | EPSILON
    def arg_list_prime(self, parent):
        options = [
            [',', 'Expression', 'ArgListPrime'],
            ['epsilon']
        ]
        if self.current_token[1] in self.get_first_set(options[0]):
            self.match('SYMBOL', ',', parent)
            expr_node = Node("Expression", parent=parent)
            self.expression(expr_node)
            alp_node = Node("ArgListPrime", parent=parent)
            self.arg_list_prime(alp_node)
        elif (self.current_token[1] in self.follow_set['ArgListPrime']):
            Node("epsilon", parent=parent)
        else:
            self.panic_mode('ArgListPrime', parent)

    def panic_mode(self, current_non_terminal, parent):
        if self.current_token[1] == '$':
            self.errors.append((self.current_token[2] + 1, 'syntax error, Unexpected EOF'))
            parent.parent = None
            self.write_output_files()
            exit()
        
        if self.current_token[0] not in self.follow_set[current_non_terminal] and self.current_token[1] not in self.follow_set[current_non_terminal]:
            self.errors.append((self.current_token[2], f'syntax error, illegal {self.current_token[1] if self.current_token[0] not in ["ID", "NUM"] else self.current_token[0]}'))
            self.get_next_token()
            tmp = parent.parent
            parent.parent = None
            new_node = Node(current_non_terminal, parent=tmp)
            self.non_terminal_functions[current_non_terminal](new_node)
            return

        if self.current_token[0] in self.follow_set[current_non_terminal] or self.current_token[1] in self.follow_set[current_non_terminal]:
            self.errors.append((self.current_token[2], f'syntax error, missing {current_non_terminal}'))
            parent.parent = None
            return
        


class code_generator:
    def __init__(self):
        self.variables = {'': {}}
        self.ref_arrs = {}
        self.temps = {}
        self.end_local_vars = {'': 40}
        self.count_params = {'': 0}
        self.func_text_addr = {}
        self.params_is_arr = {}
        self.return_type = {}
        self.current_func = ''
        self.is_params = False
        self.last_int = False
        self.had_assign = False
        self.last_pos = []
        self.last_eq = []
        self.next_func = []
        self.breaks = []
        self.ss = []
        self.pb = []

    def code_gen(self, symbol, input=''):
        print(symbol, input, self.ss)
        if   symbol == 'start_program':
            self.start_program()
        elif symbol == 'end_program':
            self.end_program()
        elif symbol == 'put_name':
            self.put_name(input)
        elif symbol == 'put_num':
            self.put_num(input)
        elif symbol == 'type_int':
            self.type_int()
        elif symbol == 'type_void':
            self.type_void()
        elif symbol == 'setp':
            self.setp()
        elif symbol == 'setm':
            self.setm()
        elif symbol == 'iseq':
            self.iseq()
        elif symbol == 'islt':
            self.islt()
        elif symbol == 'label':
            self.label()
        elif symbol == 'save':
            self.save()
        elif symbol == 'stm_start':
            self.stm_start()
        elif symbol == 'popper':
            self.popper()
        elif symbol == 'start_func':
            self.start_func()
        elif symbol == 'end_func':
            self.end_func()
        elif symbol == 'return_value':
            self.return_value()
        elif symbol == 'end_func_params':
            self.end_func_params()
        elif symbol == 'declare_var':
            self.declare_var()
        elif symbol == 'declare_arr':
            self.declare_arr()
        elif symbol == 'declare_var_param':
            self.declare_var_param()
        elif symbol == 'declare_arr_param':
            self.declare_arr_param()
        elif symbol == 'pid':
            self.pid(input)
        elif symbol == 'pnum':
            self.pnum(input)
        elif symbol == 'func_call':
            self.func_call()
        elif symbol == 'arruse':
            self.arruse()
        elif symbol == 'add':
            self.add()
        elif symbol == 'sub':
            self.sub()
        elif symbol == 'mult':
            self.mult()
        elif symbol == 'compare':
            self.compare()
        elif symbol == 'assign':
            self.assign()
        elif symbol == 'while_stm':
            self.while_stm()
        elif symbol == 'break_stm':
            self.break_stm()
        elif symbol == 'jpf_save':
            self.jpf_save()
        elif symbol == 'jp':
            self.jp()
    
    def gettemp(self):
        if self.current_func not in self.temps:
            self.temps[self.current_func] = self.end_local_vars[self.current_func]
        output = self.temps[self.current_func]
        self.temps[self.current_func] += 4
        return output
    
    def start_program(self):
        self.pb.append('')
        self.pb.append('')
        self.pb.append('')
        self.pb.append('')
    
    def end_program(self):
        self.pb[0] = f'(ASSIGN, #10000, 0, )'
        self.pb[1] = f'(ASSIGN, #{len(self.pb)}, 9992, )'
        self.pb[2] = f'(ASSIGN, #0, 9996, )'
        self.pb[3] = f'(JP, #{self.func_text_addr["main"]}, , )'
        with open('output.txt', 'w') as f:
            for i, comm in enumerate(self.pb):
                f.write(f'{i}\t{comm}\n')
        print(self.ss)
    
    def put_num(self, number):
        self.ss.append(number)
    
    def put_name(self, name):
        self.ss.append(name)

    def type_int(self):
        self.last_int = True

    def type_void(self):
        self.last_int = False

    def setp(self):
        self.last_pos.append(True)

    def setm(self):
        self.last_pos.append(False)

    def iseq(self):
        self.last_eq.append(True)

    def islt(self):
        self.last_eq.append(False)

    def label(self):
        self.breaks.append([])
        self.ss.append(len(self.pb))

    def save(self):
        self.ss.append(len(self.pb))
        self.pb.append(f'(, , , )')
        self.pb.append(f'(, , , )')
        self.pb.append(f'(, , , )')

    def stm_start(self):
        self.ss.append('###')
    
    def popper(self):
        while self.ss[-1] != '###':
            self.ss.pop()
        self.ss.pop()
    
    def start_func(self):
        self.variables[self.ss[-1]] = {}
        self.ref_arrs[self.ss[-1]] = {}
        self.params_is_arr[self.ss[-1]] = []
        self.end_local_vars[self.ss[-1]] = 0
        self.count_params[self.ss[-1]] = 0
        self.return_type[self.ss[-1]] = self.last_int
        self.current_func = self.ss[-1]
        self.is_params = True
        self.func_text_addr[self.current_func] = len(self.pb)
        self.ss.pop()
    
    def end_func(self):
        self.current_func = ''
        self.pb.append(f'(SUB, 0, #4, 4)')
        self.pb.append(f'(SUB, 0, #8, 8)')
        self.pb.append(f'(ASSIGN, @4, 0, )')
        self.pb.append(f'(ASSIGN, @8, 8, )')
        self.pb.append(f'(JP, @8, , )')
    
    def return_value(self):
        self.pb.append(f'(ADD, 0, #{self.ss[-1]}, 4)')
        self.pb.append(f'(ADD, 0, @4, 4)')
        self.pb.append(f'(ASSIGN, @4, 16, )')
        t = self.current_func
        self.end_func()
        self.current_func = t
        self.ss.pop()
    
    def end_func_params(self):
        self.is_params = False
    
    def declare_var(self):
        self.variables[self.current_func][self.ss[-1]] = self.end_local_vars[self.current_func]
        self.end_local_vars[self.current_func] += 4
        self.ss.pop()
    
    def declare_arr(self):
        self.variables[self.current_func][self.ss[-2]] = self.end_local_vars[self.current_func]
        self.end_local_vars[self.current_func] += 4 * self.ss[-1]
        self.ss.pop()
        self.ss.pop()

    def declare_var_param(self):
        self.variables[self.current_func][self.ss[-1]] = self.end_local_vars[self.current_func]
        self.end_local_vars[self.current_func] += 4
        self.ss.pop()
        self.params_is_arr[self.current_func].append(False)

    def declare_arr_param(self):
        self.variables[self.current_func][self.ss[-1]] = self.end_local_vars[self.current_func]
        self.ref_arrs[self.current_func][self.ss[-1]] = self.end_local_vars[self.current_func]
        self.end_local_vars[self.current_func] += 4
        self.ss.pop()
        self.params_is_arr[self.current_func].append(True)

    
    def pid(self, input_name):
        if input_name in self.variables or input_name == 'output':
            self.pfunc(input_name)
            return
        # print(self.current_func, self.variables)
        p = self.variables[self.current_func][input_name] if input_name in self.variables[self.current_func] else self.variables[''][input_name]
        t = self.gettemp()
        self.pb.append(f'(ADD, 0, #{t}, 4)')
        if input_name in self.ref_arrs[self.current_func]:
            self.pb.append(f'(ADD, 0, #{p}, 8)')
            self.pb.append(f'(ASSIGN, @8, @4, )')
        else:
            self.pb.append(f'(ASSIGN, #{p}, @4, )')
        if input_name not in self.variables[self.current_func]:
            self.pb.append(f'(SUB, @4, 0, @4)')
        self.ss.append(t)
    
    def pnum(self, number):
        t = self.gettemp()
        self.pb.append(f'(ADD, 0, #{t}, 4)')
        t2 = self.gettemp()
        self.pb.append(f'(ADD, 0, #{t2}, 8)')
        self.pb.append(f'(ASSIGN, #{number}, @4, )')
        self.pb.append(f'(ASSIGN, #{t}, @8, )')
        self.ss.append(t2)
    
    def pfunc(self, input_name):
        self.next_func.append(input_name)

    def func_call(self):
        if self.next_func[-1] == 'output':
            self.output()
            return
        self.pb.append(f'(ADD, 0, #{self.temps[self.current_func] + 20000}, 4)')
        tmp_i = len(self.pb)
        self.pb.append(f'(ASSIGN, #x, @4, )') # save return address later
        self.pb.append(f'(ADD, 4, #4, 4)')
        self.pb.append(f'(ASSIGN, 0, @4, )')
        self.pb.append(f'(ADD, 4, #4, 4)')
        self.pb.append(f'(ASSIGN, 4, 12, )')
        # print(self.params_is_arr[self.next_func], self.params_is_arr, self.next_func, '----------------')
        for param_index, is_arr in enumerate(self.params_is_arr[self.next_func[-1]]):
            param_tmp = self.ss[-len(self.params_is_arr[self.next_func[-1]]) + param_index]
            self.pb.append(f'(ADD, 0, #{param_tmp}, 8)')
            self.pb.append(f'(ADD, 0, @8, 8)')
            self.pb.append(f'(ASSIGN, {"@" if not is_arr else ""}8, @12, )')
            if is_arr:
                self.pb.append(f'(SUB, @12, 4, @12)')
            self.pb.append(f'(ADD, 12, #4, 12)')
        self.pb.append(f'(ASSIGN, 4, 0, )')
        self.pb.append(f'(JP, #{self.func_text_addr[self.next_func[-1]]}, , )')
        self.pb[tmp_i] = self.pb[tmp_i].replace('x', f'{len(self.pb)}')
        for _ in range(len(self.params_is_arr[self.next_func[-1]])):
            self.ss.pop()
        if self.return_type[self.next_func[-1]]:
            t = self.gettemp()
            self.pb.append(f'(ADD, 0, #{t}, 4)')
            self.pb.append(f'(ASSIGN, 16, @4, )')
            t2 = self.gettemp()
            self.pb.append(f'(ADD, 0, #{t2}, 8)')
            self.pb.append(f'(ASSIGN, #{t}, @8, )')
            self.ss.append(t2)
        self.next_func.pop()
    
    def output(self):
        self.pb.append(f'(ADD, 0, #{self.ss[-1]}, 4)')
        self.pb.append(f'(ADD, 0, @4, 4)')
        self.pb.append(f'(PRINT, @4, , )')
        self.ss.pop()

    def arruse(self):
        self.pb.append(f'(ADD, 0, #{self.ss[-1]}, 4)')
        self.pb.append(f'(ADD, 0, @4, 4)')
        self.pb.append(f'(ASSIGN, @4, 12, )')
        self.pb.append(f'(MULT, 12, #4, 12)')
        self.pb.append(f'(ADD, 0, #{self.ss[-2]}, 8)')
        self.pb.append(f'(ADD, 12, @8, @8)')
        self.ss.pop()

    
    def add(self):
        if not self.last_pos[-1]:
            self.sub()
            return
        t = self.gettemp()
        self.pb.append(f'(ADD, 0, #{self.ss[-1]}, 4)')
        self.pb.append(f'(ADD, 0, @4, 4)')
        self.pb.append(f'(ADD, 0, #{self.ss[-2]}, 8)')
        self.pb.append(f'(ADD, 0, @8, 8)')
        self.pb.append(f'(ADD, 0, #{t}, 12)')
        self.pb.append(f'(ADD, @4, @8, @12)')
        t2 = self.gettemp()
        self.pb.append(f'(ADD, 0, #{t2}, 8)')
        self.pb.append(f'(ASSIGN, #{t}, @8, )')
        self.ss.pop()
        self.ss.pop()
        self.ss.append(t2)
        self.last_pos.pop()

    def sub(self):
        t = self.gettemp()
        self.pb.append(f'(ADD, 0, #{self.ss[-1]}, 4)')
        self.pb.append(f'(ADD, 0, @4, 4)')
        self.pb.append(f'(ADD, 0, #{self.ss[-2]}, 8)')
        self.pb.append(f'(ADD, 0, @8, 8)')
        self.pb.append(f'(ADD, 0, #{t}, 12)')
        self.pb.append(f'(SUB, @8, @4, @12)')
        t2 = self.gettemp()
        self.pb.append(f'(ADD, 0, #{t2}, 8)')
        self.pb.append(f'(ASSIGN, #{t}, @8, )')
        self.ss.pop()
        self.ss.pop()
        self.ss.append(t2)
        self.last_pos.pop()
    
    def mult(self):
        t = self.gettemp()
        self.pb.append(f'(ADD, 0, #{self.ss[-1]}, 4)')
        self.pb.append(f'(ADD, 0, @4, 4)')
        self.pb.append(f'(ADD, 0, #{self.ss[-2]}, 8)')
        self.pb.append(f'(ADD, 0, @8, 8)')
        self.pb.append(f'(ADD, 0, #{t}, 12)')
        self.pb.append(f'(MULT, @4, @8, @12)')
        t2 = self.gettemp()
        self.pb.append(f'(ADD, 0, #{t2}, 8)')
        self.pb.append(f'(ASSIGN, #{t}, @8, )')
        self.ss.pop()
        self.ss.pop()
        self.ss.append(t2)
    
    def compare(self):
        t = self.gettemp()
        self.pb.append(f'(ADD, 0, #{self.ss[-1]}, 4)')
        self.pb.append(f'(ADD, 0, @4, 4)')
        self.pb.append(f'(ADD, 0, #{self.ss[-2]}, 8)')
        self.pb.append(f'(ADD, 0, @8, 8)')
        self.pb.append(f'(ADD, 0, #{t}, 12)')
        if self.last_eq[-1]:
            self.pb.append(f'(EQ, @4, @8, @12)')
        else:
            self.pb.append(f'(LT, @8, @4, @12)')
        t2 = self.gettemp()
        self.pb.append(f'(ADD, 0, #{t2}, 8)')
        self.pb.append(f'(ASSIGN, #{t}, @8, )')
        self.ss.pop()
        self.ss.pop()
        self.ss.append(t2)
        self.last_eq.pop()

    def assign(self):
        # print('------------------------------------------------')
        self.had_assign = True
        self.pb.append(f'(ADD, 0, #{self.ss[-1]}, 4)')
        self.pb.append(f'(ADD, 0, @4, 4)')
        self.pb.append(f'(ADD, 0, #{self.ss[-2]}, 8)')
        self.pb.append(f'(ADD, 0, @8, 8)')
        self.pb.append(f'(ASSIGN, @4, @8, )')
        t = self.gettemp()
        self.pb.append(f'(ADD, 0, #{t}, 12)')
        self.pb.append(f'(SUB, 8, 0, 8)')
        self.pb.append(f'(ASSIGN, 8, @12, )')
        self.ss.pop()
        self.ss.pop()
        self.ss.append(t)

    def while_stm(self):
        self.pb.append(f'(JP, #{self.ss[-3]}, , )')
        self.pb[self.ss[-1]] = f'(ADD, 0, #{self.ss[-2]}, 4)'
        self.pb[self.ss[-1] + 1] = f'(ADD, 0, @4, 4)'
        self.pb[self.ss[-1] + 2] = f'(JPF, @4, #{len(self.pb)}, )'
        for i in self.breaks[-1]:
            self.pb[i] = f'(JP, #{len(self.pb)}, , )'
        self.ss.pop()
        self.ss.pop()
        self.ss.pop()
        self.breaks.pop()

    def break_stm(self):
        self.breaks[-1].append(len(self.pb))
        self.pb.append(f'(, , , )')

    def jpf_save(self):
        self.pb[self.ss[-1]] = f'(ADD, 0, #{self.ss[-2]}, 4)'
        self.pb[self.ss[-1] + 1] = f'(ADD, 0, @4, 4)'
        self.pb[self.ss[-1] + 2] = f'(JPF, @4, #{len(self.pb) + 1}, )'
        self.ss.pop()
        self.ss.pop()
        self.ss.append(len(self.pb))
        self.pb.append(f'(, , , )')

    def jp(self):
        self.pb[self.ss[-1]] = f'(JP, #{len(self.pb)}, , )'
        self.ss.pop()



def main():
    try:
        with open('input.txt', 'r') as f:
            input_str = f.read()
    except FileNotFoundError:
        print("input.txt not found.")
        return

    scanner = Scanner(input_str)
    parser = Parser(scanner)
    parser.parse()

if __name__ == '__main__':
    main()
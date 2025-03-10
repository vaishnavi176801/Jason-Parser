from Lexcial import Lexcial

class SemanticError(Exception):
    """Represents a semantic error with a type and message."""
    def __init__(self, error_type, message):
        self.error_type = error_type
        self.message = message
        super().__init__(message)

class Tree:
    """Represents a node in the abstract syntax tree."""
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []

    """Adds a child node to the current tree."""
    def add_branch(self, branch):
        self.children.append(branch)

    """Returns a string representation of the tree."""
    def __str__(self, level=0):
        indent = "\t" * level
        result = f"{indent}{self.type}"
        if self.value is not None:
            result += f": {self.value}"
        result += "\n"
        for child in self.children:
            result += child.__str__(level + 1)
        return result

class Parser:

    """Parses input text into an abstract syntax tree with validation."""
    def __init__(self, input_text):
        self.scanner = Lexcial(input_text)
        self.current_token = None
        self.tokens = self.scanner.scan()
        self.position = 0
        self.get_next_token()
        self.semantic_errors = []
        self.dict_keys = set()

    """Advances to the next token in the input."""
    def get_next_token(self):
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
            self.position += 1
        else:
            self.current_token = None

    """Consumes the current token if it matches the given type."""
    def eat(self, token_type):
        if self.current_token and token_type in self.current_token:
            token_value = self.current_token.split(",")[1].strip(" )'")
            self.get_next_token()
            return token_value
        else:
            self.semantic_errors.append(f"Unexpected token: {self.current_token}, expected {token_type}")
            return None


    """Validates the syntax of a number."""
    def validate_number(self, value):
        if "." in value:
            parts = value.split(".")
            if len(parts) != 2 or not parts[0] or not parts[1]:
                self.semantic_errors.append(f"Type 1: Invalid Decimal Number: {value}")
        if value.startswith("0") and len(value) > 1 and not value.startswith("0."):
            self.semantic_errors.append(f"Type 3: Invalid Number with leading zeros: {value}")
        if value.startswith("+"):
            self.semantic_errors.append(f"Type 3: Invalid Number with leading '+': {value}")

    """Validates the syntax of a string."""
    def validate_string(self, value):
        if value in ["true", "false", "null"]:
            self.semantic_errors.append(f"Type 7: Reserved word used as string: {value}")

    """Validates dictionary keys for syntax and semantics."""
    def validate_dict_key(self, key, token_type):
        key = key.strip()
        if not key:
            self.semantic_errors.append("Type 2: Empty key in dictionary")
        elif token_type == "Reserved Keyword" and key in ["true", "false", "null"]:
            self.semantic_errors.append(f"Type 4: Reserved word used as dictionary key: {key}")
        elif key in self.dict_keys:
            self.semantic_errors.append(f"Type 5: Duplicate dictionary key: {key}")
        self.dict_keys.add(key)

    """Validates that a list contains consistent types."""
    def validate_list(self, elements):
        types = set(type(e) for e in elements)
        if len(types) > 1:
            self.semantic_errors.append("Type 6: Inconsistent types in list")

    """Parses and validates a number token."""
    def NumberParser(self):
        if "Number" in self.current_token:
            value = self.eat("token(Number,")
            if value is not None:
                self.validate_number(value)
                return Tree("NUMBER", value)
        return None

    """Parses and validates a string token."""
    def StringParser(self):
        if "String" in self.current_token:
            value = self.eat("token(String,")
            if value is not None:
                self.validate_string(value)
                return Tree("STRING", value)
        return None

    """Parses a null token."""
    def NullParser(self):
        if "Null" in self.current_token:
            self.eat("token(Null,")
            return Tree("NULL", "null")
        return None

    """Parses a boolean token."""
    def BooleanParser(self):
        if "True" in self.current_token or "False" in self.current_token:
            value = "true" if "True" in self.current_token else "false"
            self.eat("token(True,") if "True" in self.current_token else self.eat("token(False,")
            return Tree("BOOLEAN", value)
        return None

    """Parses a key-value pair in a dictionary."""
    def PairParser(self):
        key_branch = self.StringParser()
        check = "true"
        if key_branch is None:
            key_branch = self.BooleanParser()
            check = "false"
        if key_branch:
            key_value = key_branch.value
            if check == "true":
                self.validate_dict_key(key_value, token_type="String")
            else:
                self.validate_dict_key(key_value, token_type="Reserved Keyword")
            colon_branch = Tree(":")
            self.eat("token(Colon")
            value_branch = self.ValueParser()
            if value_branch:
                key_node = Tree("key")
                key_node.add_branch(Tree("STRING", key_value))
                value_node = Tree("value")
                value_node.add_branch(value_branch)
                return key_node, value_node
        return None

    """Parses a value token or nested structure."""
    def ValueParser(self):
        branch = (
            self.StringParser() or
            self.NumberParser() or
            self.NullParser() or
            self.BooleanParser()
        )
        if branch:
            return branch
        elif self.current_token and "token(SquareOpen" in self.current_token:
            return self.ListParser()
        elif self.current_token and "token(CurlyOpen" in self.current_token:
            return self.DictParser()
        return None

    """Parses a dictionary structure."""
    def DictParser(self):
        self.dict_keys = set()
        self.eat("token(CurlyOpen")
        main_branch = Tree("value")
        object_branch = Tree("object")
        main_branch.add_branch(object_branch)
        object_open = Tree("{")
        object_close = Tree("}")
        object_branch.add_branch(object_open)
        while self.current_token and "CurlyClose" not in self.current_token:
            key_node, value_node = self.PairParser()
            if key_node and value_node:
                object_branch.add_branch(key_node)
                object_branch.add_branch(value_node)
            if self.current_token and "token(Comma" in self.current_token:
                self.eat("token(Comma")
            else:
                break
        object_branch.add_branch(object_close)
        self.eat("token(CurlyClose")
        return main_branch

    """Parses a list structure."""
    def ListParser(self):
        self.eat("token(SquareOpen")
        main_branch = Tree("list")
        elements = []
        list_open = Tree("[")
        list_close = Tree("]")
        main_branch.add_branch(list_open)
        while self.current_token and "SquareClose" not in self.current_token:
            value_branch = self.ValueParser()
            if value_branch:
                elements.append(value_branch.value)
                main_branch.add_branch(value_branch)
            if self.current_token and "token(Comma" in self.current_token:
                self.eat("token(Comma")
            else:
                break
        self.validate_list(elements)
        main_branch.add_branch(list_close)
        self.eat("token(SquareClose")
        return main_branch


    """Parses the input and returns the abstract syntax tree."""
    def parse(self):
        try:
            main_branch = None
            if self.current_token:
                if "token(CurlyOpen" in self.current_token:
                    main_branch = self.DictParser()
                elif "token(SquareOpen" in self.current_token:
                    main_branch = self.ListParser()
            if self.current_token:
                self.semantic_errors.append("Parsing Error: Unexpected tokens at the end.")
            if not self.semantic_errors:
                return main_branch
            return None
        except Exception as e:
            self.semantic_errors.append(str(e))
            return None

if __name__ == "__main__":
    with open("test6.txt", "r") as input_file:
        json_input = input_file.read().strip()
    parser = Parser(json_input)
    parse_tree = parser.parse()
    with open("output.txt", "w") as output_file:
        if parser.semantic_errors:
            output_file.write("Semantic Errors:\n")
            for error in parser.semantic_errors:
                output_file.write(f"{error}\n")
        else:
            output_file.write("JSON parsed successfully!\n")
            output_file.write("Abstract Syntax Tree:\n")
            output_file.write(str(parse_tree))

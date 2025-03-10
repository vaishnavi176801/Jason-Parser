class Lexcial:
    def __init__(self, input_text):
        self.input_text = input_text
        self.position = 0
        self.tokens = []
        self.state = 'start'

    def getChar(self):
        if self.position < len(self.input_text):
            return self.input_text[self.position]
        return None

    def scan(self):
        if not self.input_text:  # Check if the input string is empty
            self.tokens.append("token(EmptyString, '')")
            return self.tokens

        while self.state != 'Error':
            char = self.getChar()
            if char is None:
                break
            self.state = self.transition(self.state, char)
        return self.tokens

    def transition(self, state, char):
        if state == 'start':
            if char.isspace():
                self.position += 1
                return 'start'
            elif char == '{':
                self.tokens.append("token(CurlyOpen, '{')")
                self.position += 1
                return 'start'
            elif char == '}':
                self.tokens.append("token(CurlyClose, '}')")
                self.position += 1
                return 'start'
            elif char == '[':
                self.tokens.append("token(SquareOpen, '[')")
                self.position += 1
                return 'start'
            elif char == ']':
                self.tokens.append("token(SquareClose, ']')")
                self.position += 1
                return 'start'
            elif char == ':':
                self.tokens.append("token(Colon, ':')")
                self.position += 1
                return 'start'
            elif char == ',':
                self.tokens.append("token(Comma, ',')")
                self.position += 1
                return 'start'
            elif char == '"':
                return self.scan_string()
            elif char.isdigit() or char == '.' or char == '+' or char == '-':
                return self.scan_number()
            elif char == 't':
                return self.scan_true()
            elif char == 'f':
                return self.scan_false()
            elif char == 'n':
                return self.scan_null()
            else:
                return 'Error'
        return 'Error'

    def scan_string(self):
        start_pos = self.position
        self.position += 1
        while self.getChar() != '"':
            if self.getChar() is None:
                return 'Error'
            self.position += 1
        self.position += 1
        string_value = self.input_text[start_pos + 1:self.position - 1]
        self.tokens.append(f"token(String, '{string_value}')")
        return 'start'  # Changed to 'start'

    def scan_number(self):
        start_pos = self.position
        has_decimal = False
        has_exponent = False

        if self.getChar() in ['-', '+']:
            self.position += 1

        if self.getChar() == '.':
            has_decimal = True
            self.position += 1

        while self.getChar() and (self.getChar().isdigit() or self.getChar() == '.'):
            if self.getChar() == '.':
                if has_decimal:
                    break
                has_decimal = True
            self.position += 1

        if self.getChar() in ['e', 'E']:
            self.position += 1
            if self.getChar() in ['-', '+']:
                self.position += 1
            while self.getChar() and self.getChar().isdigit():
                self.position += 1
            has_exponent = True

        number_value = self.input_text[start_pos:self.position]
        self.tokens.append(f"token(Number, {number_value})")

        return 'start'

    def scan_true(self):
        if self.input_text[self.position:self.position + 4] == 'true':
            self.position += 4
            self.tokens.append("token(True, true)")
            return 'start'
        return 'Error'

    def scan_false(self):
        if self.input_text[self.position:self.position + 5] == 'false':
            self.position += 5
            self.tokens.append("token(False, false)")
            return 'start'
        return 'Error'

    def scan_null(self):
        if self.input_text[self.position:self.position + 4] == 'null':
            self.position += 4
            self.tokens.append("token(Null, null)")
            return 'start'
        return 'Error'

if __name__ == "__main__":
    print("Please input a valid JSON string:")
    
    lines = []
    while True:
        line = input()
        if line.strip() == '':
            break
        lines.append(line)
    
    json_code = '\n'.join(lines)
    
    scanner = Lexcial(json_code)
    tokens = scanner.scan()
    
    for token in tokens:
        print(token)

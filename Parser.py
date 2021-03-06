from Lexer import lex
from Lexer import tableOfSymb
from Lexer import tableOfId, tableToPrint, tableOfConst, sourceCode, FSuccess

lex()
print('-' * 30)
print('tableOfSymb:{0}'.format(tableOfSymb))
print('-' * 30)

# номер рядка таблиці розбору/лексем/символів ПРОГРАМИ tableOfSymb
numRow = 1
postfixCode = []

# довжина таблиці символів програми
# він же - номер останнього запису
len_tableOfSymb = len(tableOfSymb)
toView = False
print(('len_tableOfSymb', len_tableOfSymb))


# Функція для розбору за правилом
# Program = program StatementList end
# читає таблицю розбору tableOfSymb


def postfixTranslator():
    # чи був успішним лексичний розбір
    if (True, 'Lexer') == FSuccess:
        return parseProgram()


def parseProgram():
    global numRow, FSuccess
    try:
        # перевірити наявність ключового слова 'program'
        parseToken('program', 'keyword', '')
        # перевірити синтаксичну коректність списку інструкцій StatementList
        numRow += 1
        parseToken('{', 'braces_op', '')
        parseStatementList()

        # перевірити наявність закриваючої скобки
        parseToken('}', 'braces_op', '')

        # повідомити про синтаксичну коректність програми
        print('Parser: Синтаксичний аналіз завершився успішно')
        FSuccess = (True, 'Translator')
        return FSuccess
    except SystemExit as e:
        # Повідомити про факт виявлення помилки
        print('Parser: Аварійне завершення програми з кодом {0}'.format(e))


# Функція перевіряє, чи у поточному рядку таблиці розбору
# зустрілась вказана лексема lexeme з токеном token
# параметр indent - відступ при виведенні у консоль
def parseToken(lexeme, token, indent):
    # доступ до поточного рядка таблиці розбору
    global numRow

    # якщо всі записи таблиці розбору прочитані,
    # а парсер ще не знайшов якусь лексему
    if numRow > len_tableOfSymb:
        failParse('неочікуваний кінець програми', (lexeme, token, numRow))

    # прочитати з таблиці розбору
    # номер рядка програми, лексему та її токен
    numLine, lex, tok = getSymb()

    # тепер поточним буде наступний рядок таблиці розбору
    numRow += 1

    # чи збігаються лексема та токен таблиці розбору з заданими
    if (lex, tok) == (lexeme, token):
        # вивести у консоль номер рядка програми та лексему і токен
        print(indent + 'parseToken: В рядку {0} токен {1}'.format(numLine, (lexeme, token)))
        return True
    else:
        # згенерувати помилку та інформацію про те, що
        # лексема та токен таблиці розбору (lex,tok) відрізняються від
        # очікуваних (lexeme,token)
        failParse('невідповідність токенів', (numLine, lex, tok, lexeme, token))
        return False


# Прочитати з таблиці розбору поточний запис
# Повертає номер рядка програми, лексему та її токен
def getSymb():
    if numRow > len_tableOfSymb:
        failParse('getSymb(): неочікуваний кінець програми', numRow)
    # таблиця розбору реалізована у формі словника (dictionary)
    # tableOfSymb[numRow]={numRow: (numLine, lexeme, token, indexOfVarOrConst)
    numLine, lexeme, token, _ = tableOfSymb[numRow]
    return numLine, lexeme, token


# Обробити помилки
# вивести поточну інформацію та діагностичне повідомлення
def failParse(str, tuple):
    if str == 'неочікуваний кінець програми':
        (lexeme, token, numRow) = tuple
        print(
            'Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером {1}. \n\t Очікувалось - {0}'.format(
                (lexeme, token), numRow))
        exit(1001)
    if str == 'getSymb(): неочікуваний кінець програми':
        numRow = tuple
        print(
            'Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером {0}. \n\t Останній запис - {1}'.format(
                numRow, tableOfSymb[numRow - 1]))
        exit(1002)
    elif str == 'невідповідність токенів':
        (numLine, lexeme, token, lex, tok) = tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - ({3},{4}).'.format(
            numLine, lexeme, token, lex, tok))
        exit(1)
    elif str == 'невідповідність інструкцій':
        (numLine, lex, tok, expected) = tuple
        print(
            'Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine, lex,
                                                                                                           tok,
                                                                                                           expected))
        exit(2)
    elif str == 'невідповідність у Expression.Factor':
        (numLine, lex, tok, expected) = tuple
        print(
            'Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine, lex,
                                                                                                           tok,
                                                                                                           expected))
        exit(3)

    elif str == 'ідентифікатор не був об\'явлений':
        lex = tuple
        print(str + ': ' + lex)
        exit(4)

# Функція для розбору за правилом для StatementList
# StatementList = Statement  { Statement }
# викликає функцію parseStatement() доти,
# доки parseStatement() повертає True
def parseStatementList():
    print('\t parseStatementList():')
    while parseStatement():
        pass
    return True


def parseStatement():
    global numRow
    print('\t\t parseStatement():')
    # прочитаємо поточну лексему в таблиці розбору
    numLine, lex, tok = getSymb()
    # якщо токен - ідентифікатор
    # обробити інструкцію присвоювання
    if tok == 'ident':
        if tableOfId[lex][1] in ('int', 'double', 'bool'):
            parseAssign()
            parseToken(';', 'semicolon', '')
            return True
        else:
            failParse('невідповідність інструкцій', (numLine, lex, tok, 'int, double або bool'))
            return False

    # якщо лексема - ключове слово 'if'
    # обробити інструкцію розгалудження
    elif (lex, tok) == ('if', 'keyword'):
        parseIf()
        return True

    elif lex in ('int', 'double', 'bool') and tok == 'keyword':
        numRow += 1
        _, varName, _ = getSymb()
        parseInit(varName, lex)
        return True

    elif (lex, tok) == ('do', 'keyword'):
        numRow += 1
        parseDoWhile()
        return True

    elif lex == 'print' and tok in ('keyword'):
        numRow += 1
        parsePrint()
        return True

    elif lex == 'read' and tok in ('keyword'):
        numRow += 1
        parseRead()
        return True

    # тут - ознака того, що всі інструкції були коректно
    # розібрані і була знайдена остання лексема програми.
    # тому parseStatement() має завершити роботу

    else:
        # жодна з інструкцій не відповідає
        # поточній лексемі у таблиці розбору,
        #failParse('невідповідність інструкцій', (numLine, lex, tok, 'ident або if'))
        return False


def parseAssign():
    # номер запису таблиці розбору
    global numRow
    print('\t' * 4 + 'parseAssign():')

    # взяти поточну лексему
    numLine, lex, tok = getSymb()

    postfixCode.append((lex, tok))  # Трансляція
    # ПОЛІЗ ідентифікатора - ідентифікатор

    if toView: configToPrint(lex, numRow)

    # встановити номер нової поточної лексеми
    numRow += 1

    print('\t' * 5 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
    # якщо була прочитана лексема - '='
    if parseToken('=', 'assign_op', '\t\t\t\t\t'):
        # розібрати арифметичний вираз
        parseExpression()
        postfixCode.append(('=', 'assign_op'))
        if toView: configToPrint('=', numRow)
        return True
    else:
        return False


def parseExpression():
    global numRow
    print('\t' * 5 + 'parseExpression():')
    numLine, lex, tok = getSymb()
    parseTerm()
    F = True
    # продовжувати розбирати Доданки (Term)
    # розділені лексемами '+' або '-'
    while F:
        numLine, lex, tok = getSymb()
        if tok in ('add_op', 'rel_op', 'bool_op'):
            numRow += 1
            print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            parseTerm()
            postfixCode.append((lex, tok))
            # lex - бінарний оператор  '+' чи '-'
            # додається після своїх операндів
            if toView: configToPrint(lex, numRow)
        else:
            F = False
    return True


def parseTerm():
    global numRow
    print('\t' * 6 + 'parseTerm():')
    parseFactorPow()
    F = True
    # продовжувати розбирати Множники (Factor)
    # розділені лексемами '*' або '/'
    while F:
        numLine, lex, tok = getSymb()
        if tok in ('mult_op', 'div_op'):
            numRow += 1
            print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            parseFactorPow()
            postfixCode.append((lex, tok))
            # lex - бінарний оператор  '*' чи '/'
            # додається після своїх операндів
            if toView: configToPrint(lex, numRow)
        else:
            F = False
    return True


def parseFactorPow():
    global numRow
    print('\t' * 6 + 'parseFactorPow():')
    parseFactor()
    F = True
    # продовжувати розбирати Множники (Factor)
    # розділені лексемами '*' або '/'
    while F:
        numLine, lex, tok = getSymb()
        if tok == 'pow_op':
            numRow += 1
            print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            parseFactorPow()
            postfixCode.append((lex, tok))
            # lex - бінарний оператор  '*' чи '/'
            # додається після своїх операндів
            if toView: configToPrint(lex, numRow)
        else:
            F = False
    return True

def parseFactor():
    global numRow
    print('\t' * 7 + 'parseFactor():')
    numLine, lex, tok = getSymb()
    print('\t' * 7 + 'parseFactor():=============рядок: {0}\t (lex, tok):{1}'.format(numLine, (lex, tok)))

    # перша і друга альтернативи для Factor
    # якщо лексема - це константа або ідентифікатор
    if tok in ('int', 'double', 'ident', 'BoolLit'):
        postfixCode.append((lex, tok))  # Трансляція
        # ПОЛІЗ константи або ідентифікатора
        # відповідна константа або ідентифікатор
        if toView: configToPrint(lex, numRow)
        numRow += 1
        print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))

    # третя альтернатива для Factor
    # якщо лексема - це відкриваюча дужка
    elif lex == '(':
        numRow += 1
        parseExpression()
        parseToken(')', 'par_op', '\t' * 7)
        print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
    else:
        failParse('невідповідність у Expression.Factor',
                  (numLine, lex, tok, 'rel_op, int, float, ident або \'(\' Expression \')\''))
    return True


# розбір інструкції розгалудження за правилом
# IfStatement = if BoolExpr then Statement else Statement endif
# функція названа parseIf() замість parseIfStatement()
def parseIf():
    global numRow
    _, lex, tok = getSymb()
    if lex == 'if' and tok == 'keyword':
        numRow += 1
        parseBoolExpr()
        jf_token = ["JF", "JF", None]
        postfixCode.append(jf_token)
        parseToken('{', 'braces_op', '\t' * 5)
        parseStatementList()
        jf_token[2] = len(postfixCode) - 1
        parseToken('}', 'braces_op', '\t' * 5)
        return True
    else:
        return False


# розбір логічного виразу за правиллом
# BoolExpr = Expression ('='|'<='|'>='|'<'|'>'|'<>') Expression
def parseBoolExpr():
    global numRow
    parseExpression()
    numLine, lex, tok = getSymb()
    if tok in ('rel_op', 'bool_op'):
        numRow += 1
        print('\t' * 5 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
    else:
        failParse('mismatch in BoolExpr', (numLine, lex, tok, 'rel_op'))
    # parseExpression()
    return True


def parseInit(identName, type):
    temp = list(tableOfId[identName])
    temp[1] = type
    tableOfId[identName] = tuple(temp)
    return True


def parseDoWhile():
    global numRow
    _, lex, tok = getSymb()
    if lex == 'while' and tok == 'keyword':
        numRow += 1
        jump_tok = ["JUMP", "JUMP", len(postfixCode) - 1]
        parseBoolExpr()
        jf_tok = ["JF", "JF", None]
        postfixCode.append(jf_tok)
        parseStatementList()
        postfixCode.append(jump_tok)
        jf_tok[2] = len(postfixCode) - 1
        parseToken('enddo', 'keyword', '\t' * 5)
        return True
    else:
        return False

def parsePrint():
        parseToken('(', 'par_op', '\t' * 5)
        parseExpression()
        postfixCode.append(("PRINT", "PRINT"))
        parseToken(')', 'par_op', '\t' * 5)
        parseToken(';', 'semicolon', '')

def parseRead():
    global numRow
    parseToken('(', 'par_op', '\t' * 5)
    parseIdent()
    postfixCode.append(("READ", "READ"))
    parseToken(')', 'par_op', '\t' * 5)
    parseToken(';', 'semicolon', "")

def parseIdent():
    global numRow
    numLine, lex, tok = getSymb()
    if tableOfId[lex][1] == 'type_undef':
        failParse('ідентифікатор не був об\'явлений', (lex))
    numRow += 1
    postfixCode.append((lex, tok))


def parseInOut():
    global numRow
    parseToken('(', 'par_op', '')
    parseExpression()
    parseToken(')', 'par_op', '')
    parseToken(';', 'semicolon', '')
    return True


def configToPrint(lex, numRow):
    stage = '\nКрок трансляції\n'
    stage += 'лексема: \'{0}\'\n'
    stage += 'tableOfSymb[{1}] = {2}\n'
    stage += 'postfixCode = {3}\n'
    # tpl = (lex,numRow,str(tableOfSymb[numRow]),str(postfixCode))
    print(stage.format(lex, numRow, str(tableOfSymb[numRow]), str(postfixCode)))

# запуск парсера
postfixTranslator()

# tableToPrint('All')
# tableToPrint('Symb')

print('\nКод програми у постфіксній формі (ПОЛІЗ): \n{0}'.format(postfixCode))
print(tableOfId)

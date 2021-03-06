from Lexer import lex, tableToPrint
from Lexer import tableOfSymb, tableOfId, tableOfConst, sourceCode
from Parser import postfixTranslator, postfixCode, FSuccess
from stack import Stack

stack = Stack()

toView = False


def postfixInterpreter():
    # чи була успішною трансляція
    if (True, 'Translator') == FSuccess:
        print('\nПостфіксний код: \n{0}'.format(postfixCode))
        return postfixProcessing()
    else:
        # Повідомити про факт виявлення помилки
        print('Interpreter: Translator завершив роботу аварійно')
        return False


print('-' * 30)


# tableToPrint('All')
# print('\nПочатковий код програми: \n{0}'.format(sourceCode))

# while len(str(postfixCode))==0: pass
# print('\nКод програми у постфіксній формі (ПОЛІЗ): \n{0}'.format(postfixCode))

# lenCode=len(str(postfixCode))
# print('\n---------------Код програми у постфіксній формі (ПОЛІЗ): \n{0}'.format(postfixCode))


def postfixProcessing():
    global stack, postfixCode
    try:
        i = 0
        while i < len(postfixCode):
            full_tok = postfixCode[i]
            if full_tok[1] in ('int', 'double', 'BoolLit', 'ident'):
                stack.push(full_tok)
            elif full_tok[1] == "JF":
                new_idx = process_jf(full_tok)
                if new_idx != -1:
                    i = new_idx
            elif full_tok[1] == "JUMP":
                i = process_jump(full_tok)
            elif full_tok[1] == "PRINT":
                process_print()
            elif full_tok[1] == "READ":
                process_read()
            else:
                doIt(full_tok[0], full_tok[1])
            i += 1
        return True
    except SystemExit as e:
        # Повідомити про факт виявлення помилки
        print('RunTime: Аварійне завершення програми з кодом {0}'.format(e))
    return True


def configToPrint(step, lex, tok, maxN):
    if step == 1:
        print('=' * 30 + '\nInterpreter run\n')
        # tableToPrint('All')

    print('\nКрок інтерпретації: {0}'.format(step))
    if tok in ('int', 'double'):
        print('Лексема: {0} у таблиці констант: {1}'.format((lex, tok), lex + ':' + str(tableOfConst[lex])))
    elif tok in ('ident'):
        print('Лексема: {0} у таблиці ідентифікаторів: {1}'.format((lex, tok), lex + ':' + str(tableOfId[lex])))
    else:
        print('Лексема: {0}'.format((lex, tok)))

    print('postfixCode={0}'.format(postfixCode))
    stack.print()

    # if step == maxN:
    #     for Tbl in ('Id', 'Const', 'Label'):
    #         tableToPrint(Tbl)
    return True


def doIt(lex, tok):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    if (lex, tok) == ('=', 'assign_op'):
        # зняти з вершини стека запис (лівий операнд = число)
        (lexL, tokL) = stack.pop()
        # зняти з вершини стека ідентифікатор (правий операнд)
        (lexR, tokR) = stack.pop()

        # виконати операцію:
        # оновлюємо запис у таблиці ідентифікаторів
        # ідентифікатор/змінна
        # (index не змінюється,
        # тип - як у константи,
        # значення - як у константи)
        tableOfId[lexR] = (tableOfId[lexR][0], tableOfConst[lexL][1], tableOfConst[lexL][2])
    elif tok in ('add_op', 'mult_op', 'pow_op', 'div_op', 'bool_op', 'rel_op'):
        # зняти з вершини стека запис (правий операнд)
        (lexR, tokR) = stack.pop()
        # зняти з вершини стека запис (лівий операнд)
        (lexL, tokL) = stack.pop()

        if (tokL, tokR) in (('int', 'double'), ('double', 'int')):
            failRunTime('невідповідність типів', ((lexL, tokL), lex, (lexR, tokR)))
        else:
            processing_add_mult_op((lexL, tokL), lex, (lexR, tokR))
            # stack.push()
            pass
    return True

def process_print():
    tmp = stack.pop()
    if tmp[1] == 'ident':
        print(f"{tmp[0]} = {tableOfId[tmp[0]][2]}")
    else:
        print(tmp[0])

def process_read():
    tmp = stack.pop()
    user_input = input(f"Enter {tmp[0]}: ")
    if not user_input.isnumeric():
        failRunTime("bad user input", user_input)
    tableOfId[tmp[0]] = (tableOfId[tmp[0]][0], tableOfId[tmp[0]][1], float(user_input))


def processing_add_mult_op(ltL, lex, ltR):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    lexL, tokL = ltL
    lexR, tokR = ltR
    if tokL == 'ident':
        # print(('===========',tokL , tableOfId[lexL][1]))
        # tokL = tableOfId[lexL][1]
        if tableOfId[lexL][1] == 'type_undef':
            failRunTime('неініціалізована змінна', (lexL, tableOfId[lexL], (lexL, tokL), lex, (lexR, tokR)))
        else:
            valL, tokL = (tableOfId[lexL][2], tableOfId[lexL][1])
    else:
        valL = tableOfConst[lexL][2]
    if tokR == 'ident':
        # print(('===========',tokL , tableOfId[lexL][1]))
        # tokL = tableOfId[lexL][1]
        if tableOfId[lexR][1] == 'type_undef':
            failRunTime('неініціалізована змінна', (lexR, tableOfId[lexR], (lexL, tokL), lex, (lexR, tokR)))
        else:
            valR, tokR = (tableOfId[lexR][2], tableOfId[lexR][1])
    else:
        valR = tableOfConst[lexR][2]
    # if :
    # print(('lexL',lexL,tableOfConst))
    # valL = tableOfConst[lexL][2]
    # valR = tableOfConst[lexR][2]
    getValue((valL, lexL, tokL), lex, (valR, lexR, tokR))


def getValue(vtL, lex, vtR):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    valL, lexL, tokL = vtL
    valR, lexR, tokR = vtR
    if (tokL, tokR) in (('int', 'double'), ('double', 'int')):
        failRunTime('невідповідність типів', ((lexL, tokL), lex, (lexR, tokR)))
    elif lex == '+':
        value = valL + valR
    elif lex == '-':
        value = valL - valR
    elif lex == '*':
        value = valL * valR
    elif lex == '/' and valR == 0:
        failRunTime('ділення на нуль', ((lexL, tokL), lex, (lexR, tokR)))
    elif lex == '/':
        value = valL / valR
    elif lex == '//':
        value = int(valL / valR)
    elif lex == '^':
        value = valL ** valR
    elif lex == '&&':
        value = valL and valR
    elif lex == '||':
        value = valL or valR
    elif lex == '<=':
        value = valL <= valR
    elif lex == '>=':
        value = valL >= valR
    elif lex == '==':
        value = valL == valR
    elif lex == '!=':
        value = valL != valR
    elif lex == '>':
        value = valL > valR
    elif lex == '<':
        value = valL < valR
    else:
        pass
    stack.push((str(value), tokL))
    toTableOfConst(value, tokL)

    # tableOfId[lexR] = (tableOfId[lexR][0],  tableOfConst[lexL][1], tableOfConst[lexL][2])


def toTableOfConst(val, tok):
    lexeme = str(val)
    indx1 = tableOfConst.get(lexeme)
    if indx1 is None:
        indx = len(tableOfConst) + 1
        tableOfConst[lexeme] = (indx, tok, val)


def failRunTime(str, tuple):
    if str == 'невідповідність типів':
        ((lexL, tokL), lex, (lexR, tokR)) = tuple
        print('RunTime ERROR: \n\t Типи операндів відрізняються у {0} {1} {2}'.format((lexL, tokL), lex, (lexR, tokR)))
        exit(1)
    elif str == 'неініціалізована змінна':
        (lx, rec, (lexL, tokL), lex, (lexR, tokR)) = tuple
        print('RunTime ERROR: \n\t Значення змінної {0}:{1} не визначене. Зустрылось у {2} {3} {4}'.format(lx, rec,
                                                                                                           (lexL, tokL),
                                                                                                           lex, (
                                                                                                           lexR, tokR)))
        exit(2)
    elif str == 'ділення на нуль':
        ((lexL, tokL), lex, (lexR, tokR)) = tuple
        print('RunTime ERROR: \n\t Ділення на нуль у {0} {1} {2}. '.format((lexL, tokL), lex, (lexR, tokR)))
        exit(3)


def process_jf(full_tok):
    (lex_jf, tok_jf, idx) = full_tok
    (val, tok) = stack.pop()
    if val == "False":
        return idx
    return -1

def process_jump(full_tok):
    return full_tok[2]


postfixInterpreter()

# el=fruits.pop(0)


# stack.push(('a',1))
# stack.print()
# stack.push('b')
# stack.print()

# str([1,('a',1),'b']).rjust(60)


# tableToPrint('tableOfId')
print(tableOfId)
print(tableOfConst)

'''
### varName
* This is a module that can help you fetch the string of variable's name
* Author: Hanyuu Furude
* Date: 2019/10/24
'''
import inspect
import re


def varName(src):
    '''
    return the label of the variable
    - args: src object
    - return: string | None
    -  You should not change the function of varName(), that will cause the function not work correctly.
    '''
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(
            r'varName\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
        if m:
            return m.group(1)
    return None


if __name__ == '__main__':
    demo = "Hanyuu"
    res = varName(demo)
    print(res)

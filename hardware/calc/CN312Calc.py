import re
import sympy as sp
#函数：求解方程组
#返回值：字典，如{'R2',1000,'R1',2000}
def solve_equations(equations_str, variables):
    """解析并求解方程"""
    # 提取所有变量名
    all_symbols = set()
    for eq_str in equations_str:
        # 使用正则表达式提取变量名 (简单方法，适用于简单变量名)
        # 匹配由字母、数字和下划线组成的变量名，但不能以数字开头
        symbols_in_eq = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', eq_str)
        all_symbols.update(symbols_in_eq)
    
    # 移除可能的函数名和常量
    excluded = {'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt', 'pi', 'e'}
    all_symbols = all_symbols - excluded
    
    # 创建符号
    symbols_dict = {}
    for symbol in all_symbols:
        symbols_dict[symbol] = sp.symbols(symbol)
    
    # 解析方程
    equations = []
    for eq_str in equations_str:
        try:
            # 分离等号两边
            if '=' in eq_str:
                lhs_str, rhs_str = eq_str.split('=', 1)
                lhs = sp.sympify(lhs_str.strip(), locals=symbols_dict)
                rhs = sp.sympify(rhs_str.strip(), locals=symbols_dict)
                equations.append(sp.Eq(lhs, rhs))
            else:
                # 如果没有等号，假设是表达式=0
                expr = sp.sympify(eq_str.strip(), locals=symbols_dict)
                equations.append(sp.Eq(expr, 0))
        except Exception as e:
            print(f"方程解析错误 '{eq_str}': {e}")
            return None
    
    # 准备已知值和未知变量
    known_values = {}
    unknown_vars = []
    
    for var_name, value in variables.items():
        if var_name not in symbols_dict:
            print(f"警告: 变量 '{var_name}' 在方程中未使用")
            continue
            
        if value is None:
            unknown_vars.append(symbols_dict[var_name])
        else:
            known_values[symbols_dict[var_name]] = value
    
    # 检查方程和未知变量数量
    if len(unknown_vars) == 0:
        print("所有变量都已定义，无需计算")
        return None
    
    if len(unknown_vars) > len(equations):
        print(f"错误: 未知变量数量({len(unknown_vars)})多于方程数量({len(equations)})")
        return None
    
    # 求解方程
    try:
        # 代入已知值
        equations_with_values = [eq.subs(known_values) for eq in equations]
        
        # 求解
        if len(unknown_vars) == 1 and len(equations) == 1:
            # 单变量单方程
            solution = sp.solve(equations_with_values[0], unknown_vars[0])
        else:
            # 多变量或多方程
            solution = sp.solve(equations_with_values, unknown_vars)
        
        if not solution:
            print("无解")
            return None
        
        # 处理解的形式
        if isinstance(solution, list):
            # 可能有多个解
            if len(solution) == 1:
                solution = solution[0]
            else:
                print(f"找到 {len(solution)} 个解:")
                for i, sol in enumerate(solution):
                    print(f"  解 {i+1}: {sol}")
                # 取第一个解
                solution = solution[0]
        
        # 返回结果
        if len(unknown_vars) == 1:
            result = {str(unknown_vars[0]): float(solution)}
        else:
            result = {}
            for var, val in solution.items():
                result[str(var)] = float(val)
        # 更新原始变量（可选）
        for var_name, value in result.items():
            if var_name in globals():
                globals()[var_name] = value     
        return result
            
    except Exception as e:
        print(f"求解错误: {e}")
        return None
    
# 阻值表
RESISTANCE_VALUES = [
    1000, 1100, 1200, 1300, 1500, 1600, 1800, 2000, 2200, 2400, 2700, 3000,
    3300, 3600, 3900, 4300, 4700, 5100, 5600, 6200, 6800, 7500, 8200, 9100, 10000,
    11000, 12000, 13000, 15000, 16000, 18000, 20000, 22000, 24000, 26000, 27000,
    30000, 33000, 36000, 39000, 43000, 47000, 51000, 56000, 62000, 68000, 75000, 82000, 91000,
    100000, 110000, 120000, 130000, 150000, 160000, 180000, 200000, 220000, 240000, 270000,
    300000, 330000, 360000, 390000, 430000, 470000, 510000, 560000, 620000, 680000, 750000,
    820000, 910000, 1000000
]

def find_closest_resistance(target_resistance):
    """
    根据输入的阻值，输出列表中最接近的阻值
    
    参数:
    target_resistance (float): 目标阻值
    
    返回:
    float: 最接近的阻值
    """
    closest_value = min(RESISTANCE_VALUES, key=lambda x: abs(x - target_resistance))
    return closest_value
##################################################
##########计算输出电阻###############
VBATT_H = 2.7 #
VBATT_L = 2.2
R9 = None  # 设为 None 表示需要计算
R10 = None
R11 = 300 * 10**3
VREF = 1.205

VARIABLES = {
    'VBATT_H': VBATT_H,
    'VBATT_L': VBATT_L,
    'R9': R9,
    'R10': R10,
    'R11': R11,
    'VREF': VREF
    # 'I': I,
}
EQUATIONS = [
    "VBATT_L = VREF / (R10+R11) * (R10+R11+R9)",
    "VBATT_H = VREF / R11 * (R10+R11+R9)",  # 可以添加更多方程
]
solve_equations(EQUATIONS,VARIABLES)
print("R9=",R9/1000,"k")
print("R10=",R10/1000,"k")

Batt_curr = VBATT_H/(R10+R11+R9)
print("Batt_curr=",Batt_curr*1000000,"uA")

print("阻值取整")
R9 = find_closest_resistance(R9)
print("R9=",R9/1000,"k")
R10 = find_closest_resistance(R10)
print("R10=",R10/1000,"k")
R11 = find_closest_resistance(R11)
print("R11=",R11/1000,"k")

print("重算数值")
VBATT_H = None #
VBATT_L = None
VREF = 1.205

VARIABLES = {
    'VBATT_H': VBATT_H,
    'VBATT_L': VBATT_L,
    'R9': R9,
    'R10': R10,
    'R11': R11,
    'VREF': VREF
    # 'I': I,
}
EQUATIONS = [
    "VBATT_L = VREF / (R10+R11) * (R10+R11+R9)",
    "VBATT_H = VREF / R11 * (R10+R11+R9)",  # 可以添加更多方程
]
solve_equations(EQUATIONS,VARIABLES)
print("VBATT_H=",VBATT_H,"V")
print("VBATT_L=",VBATT_L,"V")
Batt_curr = VBATT_H/(R10+R11+R9)
print("Batt_curr=",Batt_curr*1000000,"uA")


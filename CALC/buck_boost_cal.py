import numpy
import sympy


#########################################
#目标： 已知电感量， 求占空比，峰值电流,纹波系数,主要用于校验
#适用拓扑：buck-boost，CCM模式

#已知量：fsw vin vout iout L 
#计算量：峰值电流L_I_PK, 纹波电流Irp 纹波系数Krp duty ton toff

#########################################

class evl_irp_buckboost_ccm_class:
    def __init__(self, fsw=250000, vin=11.0, vout=20.0, iout=5.0, L=10e-6):
        """
        初始化Buck-Boost CCM模式计算器
        
        参数:
        fsw: 开关频率 (Hz)
        vin: 输入电压 (V)
        vout: 输出电压 (V)
        iout: 输出电流 (A)
        L: 电感量 (H)
        """
        self.fsw = fsw
        self.vin = vin
        self.vout = vout
        self.iout = iout
        self.L = L
        
        # 计算结果存储
        self.ton = None
        self.toff = None
        self.duty = None
        self.Irp = None
        self.L_I_PK = None
        self.Krp = None
        self.topo_mode = None
    
    def calculate(self):
        """执行计算"""
        #一，占空比计算
        #伏秒平衡：vin*ton = vout*toff
        #ton + toff = 1/fsw

        ton, toff = sympy.symbols('ton toff')
        # 建立方程组
        eq1 = sympy.Eq(self.vin * ton, self.vout * toff)
        eq2 = sympy.Eq(ton + toff, 1/self.fsw)

        # 解方程
        solution = sympy.solve((eq1, eq2), (ton, toff))
        self.ton = solution[ton]
        self.toff = solution[toff]
        print("ton=", self.ton*10**6, "us")
        print("toff=", self.toff*10**6, "us")

        self.duty = self.ton/(self.ton+self.toff)
        print("duty=", self.duty)

        #二，计算纹波电流
        #根据电感量计算纹波电流
        #U = L * di/dt

        self.Irp = self.vout * self.ton / self.L
        print("Irp=", self.Irp, "A")

        #三，峰值电流计算
        L_I_PK = sympy.symbols('L_I_PK')
        #根据能量守恒计算峰值电流
        #单周期内输出W = 电感放电
        #vout*i*T = 1/2 * (1-D)T * (PK * vout + PB * vout)
        eq1 = sympy.Eq(self.vout*self.iout*(1/self.fsw),
                      0.5*(1/self.fsw)*(1-self.duty)*(self.vout*L_I_PK + self.vout*(L_I_PK-self.Irp)))
        solution = sympy.solve(eq1, L_I_PK)
        self.L_I_PK = solution[0]
        print("L_I_PK=", self.L_I_PK, "A")
        
        #计算Krp
        self.Krp = self.Irp/self.L_I_PK
        print("Krp=", self.Krp)

        #验证工作模式
        if (self.Krp < 1):
            print("当前工作在CCM模式下。")
            self.topo_mode = "ccm"
        elif (self.Krp == 1):
            print("当前刚好工作在DCM模式下。")
            self.topo_mode = "dcm"
        else:
            print("erro: 电感太小或占空比过大。当前会工作在DCM模式下")
            self.topo_mode = "dcm"
        
        return self
    
    def print_summary(self):
        """打印计算结果摘要"""
        print("\n=== Buck-Boost CCM模式计算结果 ===")
        print(f"开关频率 fsw: {self.fsw} Hz")
        print(f"输入电压 vin: {self.vin} V")
        print(f"输出电压 vout: {self.vout} V")
        print(f"输出电流 iout: {self.iout} A")
        print(f"电感量 L: {self.L*1e6} uH")
        print(f"导通时间 ton: {self.ton*1e6:.3f} us")
        print(f"关断时间 toff: {self.toff*1e6:.3f} us")
        print(f"占空比 duty: {self.duty:.4f} ({self.duty*100:.2f}%)")
        print(f"纹波电流 Irp: {self.Irp:.3f} A")
        print(f"峰值电流 L_I_PK: {self.L_I_PK:.3f} A")
        print(f"纹波系数 Krp: {self.Krp:.4f}")
        print(f"工作模式: {self.topo_mode}")

#########################################




#########################################
#目标： 已知电感量，求峰值电流,占空比,主要用于校验
#适用拓扑：buck-boost，DCM模式

#已知量：fsw vin vout iout L
#计算量：峰值电流L_I_PK, 纹波电流Irp 纹波系数Krp duty

#########################################

class evl_irp_buckboost_dcm_class:
    def __init__(self, fsw=250000, vin=11.0, vout=20.0, iout=5.0, L=10e-6):
        """
        初始化Buck-Boost DCM模式计算器
        
        参数:
        fsw: 开关频率 (Hz)
        vin: 输入电压 (V)
        vout: 输出电压 (V)
        iout: 输出电流 (A)
        L: 电感量 (H)
        """
        self.fsw = fsw
        self.vin = vin
        self.vout = vout
        self.iout = iout
        self.L = L
        
        # 计算结果存储
        self.L_I_PK = None
        self.duty = None
        self.Irp = None
        self.Krp = None
        self.topo_mode = None
    
    def calculate(self):
        """执行计算"""
        L_I_PK, duty = sympy.symbols('L_I_PK duty')

        #根据能量守恒计算峰值电流
        #vout*i*T = 1/2 * D*T * PK * vin
        eq1 = sympy.Eq(self.vout*self.iout*(1/self.fsw),0.5*(1/self.fsw)*duty*self.vin*L_I_PK)
        #根据电感量计算纹波电流
        #U = L * di/dt
        eq2 = sympy.Eq(self.vin,self.L*(L_I_PK/(duty*(1/self.fsw))))
        solution = sympy.solve((eq1,eq2), (L_I_PK,duty))
        print("解集为",solution)
        
        # sympy.solve返回的是解的列表，每个解是一个元组
        if solution:
            # 遍历所有解，找到正值的解
            for sol in solution:
                L_I_PK_val, duty_val = sol
                # 检查是否为正值（物理上合理的解）
                if L_I_PK_val > 0 and 0 < duty_val < 1:
                    self.L_I_PK = L_I_PK_val
                    self.duty = duty_val
                    print("L_I_PK=", self.L_I_PK, "A")
                    print("duty=", self.duty)
                    
                    # 计算纹波电流Irp（在DCM模式下等于峰值电流）
                    self.Irp = self.L_I_PK
                    print("Irp=", self.Irp, "A")
                    
                    # 计算纹波系数Krp（DCM模式下为1）
                    self.Krp = 1.0
                    print("Krp=", self.Krp)
                    print("当前工作在DCM模式下。")
                    self.topo_mode = "dcm"
                    return self
            
            # 如果没有找到正值的解
            if solution:
                L_I_PK_val, duty_val = solution[0]
                print("警告：未找到完全正值的解，使用第一个解：")
                print("L_I_PK=", L_I_PK_val, "A")
                print("duty=", duty_val)
                print("erro:当前无法工作在DCM模式，可能会工作在ccm模式，请减小电感量")
                self.L_I_PK = L_I_PK_val
                self.duty = duty_val
                self.topo_mode = "ccm"
        else:
            print("无解")
        
        return self
    
    def print_summary(self):
        """打印计算结果摘要"""
        if self.L_I_PK is not None:
            print("\n=== Buck-Boost DCM模式计算结果 ===")
            print(f"开关频率 fsw: {self.fsw} Hz")
            print(f"输入电压 vin: {self.vin} V")
            print(f"输出电压 vout: {self.vout} V")
            print(f"输出电流 iout: {self.iout} A")
            print(f"电感量 L: {self.L*1e6} uH")
            print(f"峰值电流 L_I_PK: {self.L_I_PK:.3f} A")
            print(f"占空比 duty: {self.duty:.4f} ({self.duty*100:.2f}%)")
            print(f"纹波电流 Irp: {self.Irp:.3f} A")
            print(f"纹波系数 Krp: {self.Krp:.4f}")
            print(f"工作模式: {self.topo_mode}")



#########################################

#########################################
#目标： 已知占空比，求峰值电流和电感量
#适用拓扑：buck-boost，DCM模式

#已知量：fsw vin vout iout duty
#计算量：峰值电流L_I_PK, 电感量L

#########################################

class calc_irp_buckboost_dcm_class:
    def __init__(self, fsw=250000, vin=11.0, vout=20.0, iout=5.0, duty=0.5):
        """
        初始化Buck-Boost DCM模式计算器（已知占空比）
        
        参数:
        fsw: 开关频率 (Hz)
        vin: 输入电压 (V)
        vout: 输出电压 (V)
        iout: 输出电流 (A)
        duty: 占空比 (0-1)
        """
        self.fsw = fsw
        self.vin = vin
        self.vout = vout
        self.iout = iout
        self.duty = duty
        
        # 计算结果存储
        self.L_I_PK = None
        self.L = None
    
    def calculate(self):
        """执行计算"""
        L_I_PK = sympy.symbols('L_I_PK')

        #根据能量守恒计算峰值电流
        #vout*i*T = 1/2 * D*T * PK * vin
        eq1 = sympy.Eq(self.vout*self.iout*(1/self.fsw),
                      0.5*(1/self.fsw)*self.duty*self.vin*L_I_PK)

        solution = sympy.solve(eq1, L_I_PK)
        
        self.L_I_PK = solution[0]
        print("L_I_PK=", self.L_I_PK, "A")

        #计算电感量
        #U = L * di/dt
        self.L = self.vin * self.duty * (1/self.fsw) / self.L_I_PK
        print("L=", self.L*10**6, "uH")
        
        return self
    
    def print_summary(self):
        """打印计算结果摘要"""
        if self.L_I_PK is not None:
            print("\n=== Buck-Boost DCM模式计算结果（已知占空比）===")
            print(f"开关频率 fsw: {self.fsw} Hz")
            print(f"输入电压 vin: {self.vin} V")
            print(f"输出电压 vout: {self.vout} V")
            print(f"输出电流 iout: {self.iout} A")
            print(f"占空比 duty: {self.duty:.4f} ({self.duty*100:.2f}%)")
            print(f"峰值电流 L_I_PK: {self.L_I_PK:.3f} A")
            print(f"电感量 L: {self.L*1e6:.3f} uH")
   
#########################################
#脉冲电流热阻损耗计算
class calc_res_Ir_ploss_class:
    def __init__(self, ipb=1.0, ipk=11.0, tup=0.01, tdown=0.02, T=0.04, R=1.0):
        """
        初始化
        
        参数:
        ipb: 波谷电流 (A)
        ipk: 波峰电流 (A)
        tup: 电流上升时间 (S)
        tdown: 电流下降时间 (S)
        T: 周期(S)
        R: 阻值(欧姆)
        """
        self.ipb = ipb
        self.ipk = ipk
        self.tup = tup
        self.tdown = tdown
        self.T = T
        self.R = R

        
        # 计算结果存储
        self.p_loss = None #损耗 功率
    def calculate(self):
        if self.tup != 0:
            #上升段
            t = sympy.symbols('t')
            # p = I^2 * R = (k*x)^2 * R = (di/dt * t)^2 * R
            p_up = ((self.ipk-self.ipb)/self.tup * t)**2 * self.R
            #定积分
            # w = ∫ P*t
            w_up =  sympy.integrate(p_up, (t, 0, self.tup))
            w_up = float(w_up)
        else:
            w_up = 0

        #下降段
        if self.tdown != 0:
            t = sympy.symbols('t')
            # p = I^2 * R = (k*x)^2 * R = (di/dt * t)^2 * R
            p_down = ((self.ipk-self.ipb)/self.tdown * t)**2 * self.R
            #定积分
            # w = ∫ P*t            
            w_down =  sympy.integrate(p_down, (t, 0, self.tdown))
            w_down = float(w_down) 
        else:
            w_down = 0

        self.p_loss = (w_down+w_up)/self.T
        print("p_loss=",self.p_loss,"W")
        







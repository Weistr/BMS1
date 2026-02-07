import buck_boost_cal


vout = 20 #输出电压20V
iout = 5 #输出电流5A
vin = 2.2*5 #输入电压（最低）
fsw = 250 * 10**3#开关频率
L = 10 * 10**-6 #电感量 10uH
L_Res = 14 * 10**-3#电感内阻
Q2_Res = 7.5*2 * 10**-3#开关管导通电阻

################################################
#计算CCM模式下参数
################################################
evl_irp_buckboost_ccm = buck_boost_cal.evl_irp_buckboost_ccm_class()

evl_irp_buckboost_ccm.vout = vout #
evl_irp_buckboost_ccm.iout = iout #
evl_irp_buckboost_ccm.vin = vin #
evl_irp_buckboost_ccm.fsw = fsw#
evl_irp_buckboost_ccm.L = L #
evl_irp_buckboost_ccm.calculate()

L_I_PK = evl_irp_buckboost_ccm.L_I_PK #峰值电流
Irp = evl_irp_buckboost_ccm.Irp #纹波电流
duty = evl_irp_buckboost_ccm.duty #占空比
print("\n===计算结果 ===")
print(f"峰值电流 L_I_PK: {L_I_PK} A")
print(f"纹波电流 Irp: {Irp} A")
print(f"占空比 duty: {duty}")
################################################






################################################
#计算电感铜损
################################################
calc_res_Ir_ploss = buck_boost_cal.calc_res_Ir_ploss_class()
calc_res_Ir_ploss.ipk = L_I_PK
calc_res_Ir_ploss.ipb = L_I_PK-Irp
calc_res_Ir_ploss.tup = duty * (1/fsw)
calc_res_Ir_ploss.tdown = (1-duty) * (1/fsw)
calc_res_Ir_ploss.R = L_Res
calc_res_Ir_ploss.T = 1/fsw
calc_res_Ir_ploss.calculate()
L_Res_Ploss = calc_res_Ir_ploss.p_loss
print("\n===计算结果 ===")
print(f"电感铜损 L_Res_Ploss: {L_Res_Ploss} W")
################################################

################################################
#计算开关管导通损
################################################
calc_res_Ir_ploss = buck_boost_cal.calc_res_Ir_ploss_class()
calc_res_Ir_ploss.ipk = L_I_PK
calc_res_Ir_ploss.ipb = L_I_PK-Irp
calc_res_Ir_ploss.tup = duty * (1/fsw)
calc_res_Ir_ploss.tdown = 0
calc_res_Ir_ploss.R = Q2_Res
calc_res_Ir_ploss.T = 1/fsw
calc_res_Ir_ploss.calculate()
Q2_Res_On_Ploss = calc_res_Ir_ploss.p_loss
print("\n===计算结果 ===")
print(f"开关管导通损耗 Q2_Res_On_Ploss: {Q2_Res_On_Ploss} W")
################################################
__author__ = 'lottiwang'

from funcat import *
from funcat.data.tushare_backend import TushareDataBackend
import talib as ta
import numpy as np

set_data_backend(TushareDataBackend())

# 设置目前天数为2017年1月4日
T("20180525")
# 设置关注股票为上证指数
S("000001.XSHG")
print(O, H, L, C)
#print(help(MA))
#print(C.series)
print(ta.MA(C.series,60)[-1])

def myDMI():
    M1, M2 = 14, 6
    TR = SUM(MAX(MAX(HIGH - LOW, ABS(HIGH - REF(CLOSE, 1))), ABS(LOW - REF(CLOSE, 1))), M1)
    HD = HIGH - REF(HIGH, 1)
    LD = REF(LOW, 1) - LOW

    DMP = SUM(IF((HD > 0) & (HD > LD), HD, 0), M1)
    DMM = SUM(IF((LD > 0) & (LD > HD), LD, 0), M1)
    PDI = DMP * 100 / TR
    MDI = DMM * 100 / TR

    #ADX = MA(ABS(DI2 - DI1) / (DI1 + DI2) * 100, M2)
    ADX = MA((ABS(MDI - PDI) / (PDI + MDI) * 100),M2)
    #ADX = MA(((DMP - DMM) / (DMP + DMM) * 100).series,M2)
    #np.nan_to_num(ADX)
    #ADXR = MA(ADX.series, M2)
    ADXR =(ADX + REF(ADX, M2)) / 2

    print(PDI, MDI, ADX, ADXR)


if __name__ == "__main__":
    myDMI()
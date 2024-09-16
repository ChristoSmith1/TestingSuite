""" 
This is the Tip Curve Function 
It's inputs are dataFrames from power collection and the calculated averaged Y-factor
It outputs a graph of the tip curve showing t_sys at elevations
"""

import matplotlib.pyplot as plt
from test_info import march_info, april_info, sept_info, sept_info2, TestInfo
from g_over_t_test import Yfactor

info = sept_info

yfactor = 5.0
#import YFactor and use info to generate average Y-factor from multiple on/off measurements

def tip_curve(info: TestInfo):

    t_op = Top=abs((180-(10**(yfactor/10))*10)/(10**(Yfactor/10)-1))
    # Top=abs((135-(10**(Yfactor/10))*10)/(10**(Yfactor/10)-1)) <- 135 moon contribution at S-Band, 180 at X-band

    # I need to get just the elevation column from sept_info which right now gets everything.
    # T_op = (135-((10**(Y-factor/10))*10))/((10**(Y-factor/10))-1) <- correct math!
    # T_el = T_op*10**((measured_power_at_any_elevation - off_moon_measurement)/10) <- theoretical math
        #This is why my math should have an "off moon measurement" at cold-sky with an additional attenuation of 25dB (approx 55.1 dB)


    pass
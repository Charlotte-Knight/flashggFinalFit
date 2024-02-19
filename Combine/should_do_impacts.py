import sys
import numpy as np

def should_do_impacts(mx, my, mh, is_Y_gg=False):
  if (is_Y_gg) and (my != mh):
    return False

  if np.isin(mx, [300, 475, 600, 1000]):
    if np.isin(my, [70, 90, 125, 300, 700]):
      return True
    
  return False

mx, my, mh = sys.argv[1:4]
mx, my, mh = float(mx), float(my), float(mh)

if len(sys.argv) == 5:
  is_Y_gg = bool(int(sys.argv[4]))
else:
  is_Y_gg = False

if should_do_impacts(mx, my, mh, is_Y_gg):
  print(True)
import RPi.GPIO as GPIO  # import GPIO
from hx711 import HX711  # import the class HX711
from hx711 import outliers_filter

GPIO.setmode(GPIO.BCM) 
hx = HX711(dout_pin=21, pd_sck_pin=20, gain_channel_A=128, select_channel='B')

err = hx.reset()  
if err:  
    print('not ready')
else:
    print('Ready to use')

hx.set_gain_A( gain=64)  
hx.select_channel(channel='A')  # Select desired channel. Either 'A' or 'B' at any time.

# Read data several, or only one, time and return mean value
# argument "readings" is not required default value is 30
data = hx.get_raw_data_mean(readings=30)

if data:  # always check if you get correct value or only False
    print('Raw data:', data)
else:
    print('invalid data')

# measure tare and save the value as offset for current channel
# and gain selected. That means channel A and gain 64
result = hx.zero(readings=30)

# Read data several, or only one, time and return mean value.
# It subtracts offset value for particular channel from the mean value.
# This value is still just a number from HX711 without any conversion
# to units such as grams or kg.
data = hx.get_data_mean(readings=30)

if data:  # always check if you get correct value or only False
    # now the value is close to 0
    print('Data subtracted by offset but still not converted to any unit:',
            data)
else:
    print('invalid data')

# In order to calculate the conversion ratio to some units, in my case I want grams,
# you must have known weight.
input('Put known weight on the scale and then press Enter')
data = hx.get_data_mean(readings=30)
if data:
    print('Mean value from HX711 subtracted by offset:', data)
    known_weight_grams = input(
        'Write how many grams it was and press Enter: ')
    try:
        value = float(known_weight_grams)
        print(value, 'grams')
    except ValueError:
        print('Expected integer or float and I have got:',
                known_weight_grams)

    # set scale ratio for particular channel and gain which is
    # used to calculate the conversion to units. Required argument is only
    # scale ratio. Without arguments 'channel' and 'gain_A' it sets
    # the ratio for current channel and gain.
    ratio = data / value  # calculate the ratio for channel A and gain 64
    hx.set_scale_ratio(ratio)  # set ratio for current channel
    print('Ratio is set.')
else:
    raise ValueError('Cannot calculate mean value. Try debug mode.')

# Read data several, or only one, time and return mean value
# subtracted by offset and converted by scale ratio to
# desired units. In my case in grams.
print('Current weight on the scale in grams is: ')
print(hx.get_weight_mean(30), 'g')
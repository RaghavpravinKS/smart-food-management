## Primary goals
Food wastage detection and prevention

## To be implemented
- Weight of the waste bin should be constantly measured
- Camera should be triggered and the pictuere of the person wasting food should be captured
- Also a display should be present at the place of disposal to display the details of amount of food wasted

## Tentative Tools to be used
- Open CV for image recognition
- Framework for communication between Raspberry Pi and server depends on the database
- Training an ML model for image recognition if results by OpenCV are not upto the mark
- Load cell atleast with an operating range upto 100 kg

## Tentative Overview and Strategy
- Weight of the bin is being continuously measured
- Camera triggers if change in weight >= preset threshold
- Camera captures the picture of the person disposing the plate
- Picture then sent to server for image processing algorithm to process
- Processed results are then revieved by Raspberry Pi
- Raspberry Pi will display it on the screen

## Links for components
- [Load cel](https://www.amazon.in/ELECTROPRIME-Platform-Electronic-Weighing-Sensor/dp/B07X662HXG/ref=sr_1_5?adgrpid=1321614586562520&hvadid=82601169781130&hvbmt=be&hvdev=c&hvlocphy=155069&hvnetw=s&hvqmt=e&hvtargid=kwd-82601797222286%3Aloc-90&hydadcr=24567_2159158&keywords=load+cell+100+kg&qid=1695056834&sr=8-5)
- [Raspberry Pi](https://robu.in/product/raspberry-pi-4-model-b-with-4-gb-ram/?src=raspberrypi)
- [ADC for load cell](https://robu.in/product/hx711-weighing-sensor-dual-channel-24-bit-precision-ad-weight-pressure-sensor/)

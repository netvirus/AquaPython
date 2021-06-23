from time import sleep
import RPi.GPIO as GPIO


class StepperMotor(object):
    IN1   = None
    IN2   = None
    IN3   = None
    IN4   = None
    delay = None

    def __init__(self, in1, in2, in3, in4, step_delay):
        self.IN1 = in1
        self.IN2 = in2
        self.IN3 = in3
        self.IN4 = in4
        self.delay = step_delay

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(IN1, GPIO.OUT)
        GPIO.setup(IN2, GPIO.OUT)
        GPIO.setup(IN3, GPIO.OUT)
        GPIO.setup(IN4, GPIO.OUT)

        GPIO.output(IN1, False)
        GPIO.output(IN2, False)
        GPIO.output(IN3, False)
        GPIO.output(IN4, False)
    ## End of __init__

    def Step1(self):
        global IN4
        global time
        GPIO.output(IN4, True)
        sleep(time)
        GPIO.output(IN4, False)

    def Step2(self):
        global IN3
        GPIO.output(IN4, True)
        GPIO.output(IN3, True)
        sleep(time)
        GPIO.output(IN4, False)
        GPIO.output(IN3, False)

    def Step3(self):
        GPIO.output(IN3, True)
        sleep(time)
        GPIO.output(IN3, False)

    def Step4(self):
        global IN2
        GPIO.output(IN2, True)
        GPIO.output(IN3, True)
        sleep(time)
        GPIO.output(IN2, False)
        GPIO.output(IN3, False)

    def Step5(self):
        GPIO.output(IN2, True)
        sleep(time)
        GPIO.output(IN2, False)

    def Step6(self):
        global IN1
        GPIO.output(IN1, True)
        GPIO.output(IN2, True)
        sleep(time)
        GPIO.output(IN1, False)
        GPIO.output(IN2, False)

    def Step7(self):
        GPIO.output(IN1, True)
        sleep(time)
        GPIO.output(IN1, False)

    def Step8(self):
        GPIO.output(IN4, True)
        GPIO.output(IN1, True)
        sleep(time)
        GPIO.output(IN4, False)
        GPIO.output(IN1, False)

    def start(self, rounds):
        for i in range(rounds):
            self.Step1()
            self.Step2()
            self.Step3()
            self.Step4()
            self.Step5()
            self.Step6()
            self.Step7()
            self.Step8()
        GPIO.cleanup()

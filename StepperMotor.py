from time import sleep
import RPi.GPIO as GPIO


class StepperMotor(object):
    IN1    = None
    IN2    = None
    IN3    = None
    IN4    = None
    delay  = None
    __gpio = None

    def __init__(self, in1, in2, in3, in4, step_delay):
        self.IN1 = in1
        self.IN2 = in2
        self.IN3 = in3
        self.IN4 = in4
        self.delay = step_delay

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)

        GPIO.output(self.IN1, False)
        GPIO.output(self.IN2, False)
        GPIO.output(self.IN3, False)
        GPIO.output(self.IN4, False)
        self.__gpio = GPIO
    ## End of __init__

    def Step1(self):
        self.__gpio.output(self.IN4, True)
        sleep(self.delay)
        self.__gpio.output(self.IN4, False)

    def Step2(self):
        self.__gpio.output(self.IN4, True)
        self.__gpio.output(self.IN3, True)
        sleep(self.delay)
        self.__gpio.output(self.IN4, False)
        self.__gpio.output(self.IN3, False)

    def Step3(self):
        self.__gpio.output(self.IN3, True)
        sleep(self.delay)
        self.__gpio.output(self.IN3, False)

    def Step4(self):
        self.__gpio.output(self.IN2, True)
        self.__gpio.output(self.IN3, True)
        sleep(self.delay)
        self.__gpio.output(self.IN2, False)
        self.__gpio.output(self.IN3, False)

    def Step5(self):
        self.__gpio.output(self.IN2, True)
        sleep(self.delay)
        self.__gpio.output(self.IN2, False)

    def Step6(self):
        self.__gpio.output(self.IN1, True)
        self.__gpio.output(self.IN2, True)
        sleep(self.delay)
        self.__gpio.output(self.IN1, False)
        self.__gpio.output(self.IN2, False)

    def Step7(self):
        self.__gpio.output(self.IN1, True)
        sleep(self.delay)
        self.__gpio.output(self.IN1, False)

    def Step8(self):
        self.__gpio.output(self.IN4, True)
        self.__gpio.output(self.IN1, True)
        sleep(self.delay)
        self.__gpio.output(self.IN4, False)
        self.__gpio.output(self.IN1, False)

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
        self.__gpio.cleanup()

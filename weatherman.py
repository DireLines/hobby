# Wesley Daugherty
# wcd5f

import pygame
import gamebox
import random
import math

camera = gamebox.Camera(1280,700)

timer = 0
day = 0
temp = 50
humidity = 0
wind_speed = 0
wind_direction = 0
pressure = 100
daily_precip = 0
precip = 0
num_precip = 0
heat_index = 0
cloud_altitude = 0
cloud_thickness = 0
lightning = 0
air_instability = 0

rand_stagger = random.randint(-180,180)
rand_spring = 0
rand_summer = 0
rand_fall = 0
rand_winter = 0
weather = ""
temp_type = ""
num_clear = 0
num_cloud = 0
num_rain = 0
num_snow = 0

# days_per_year = 365
days_per_year = 48
days_per_season = 6

text_box = gamebox.from_color(200,100,"Blue",400,300)
sight_box = gamebox.from_color(300,500,"Magenta",600,800)
temp_graph = gamebox.from_color(0,0,"Red",3,3)
pres_graph = gamebox.from_color(0,0,"Blue",3,3)
hum_graph = gamebox.from_color(0,0,"Green",3,3)
precip_graph = gamebox.from_color(0,0,"White",3,3)
wind_graph = gamebox.from_color(0,0,"Gray",3,3)
heat_graph = gamebox.from_color(0,0,"Orange",3,3)
clouds_graph = gamebox.from_color(0,0,"Gray",3,3)

weather_state = gamebox.from_color(0,0,"White",3,10)
state_color = "White"

sun_graph = gamebox.from_color(0,0,"Yellow",10,5)
cloud_graph = gamebox.from_color(0,0,"Gray",10,5)
rain_graph = gamebox.from_color(0,0,"Cyan",10,5)
snow_graph = gamebox.from_color(0,0,"White",10,5)

rerun = gamebox.from_text(800,100,"Run Simulation","Arial",50,"Yellow",True)

def tick(keys):
    global timer,day,temp,humidity,wind_speed,wind_direction,precip,pressure,weather,temp_type,num_precip,daily_precip
    global num_clear,num_cloud,num_rain,num_snow,state_color,rand_stagger,rand_spring,rand_summer,rand_fall,rand_winter
    global wind_speed,wind_direction,heat_index,cloud_altitude,cloud_thickness,lightning,air_instability

    # camera.clear("Blue")

    timer += 1
    if timer%1 == 0 and day < 2*days_per_year+1:
        camera.draw(text_box)
        if timer == 1:
            rand_stagger = random.randint(-days_per_year//2, days_per_year//2)
            rand_spring = random.randint(0, days_per_year//4)
            rand_summer = random.randint(days_per_year // 4, days_per_year // 2)
            rand_fall = random.randint(days_per_year // 2, 3*days_per_year // 4)
            rand_winter = random.randint(3*days_per_year // 4, days_per_year)
            camera.clear("Black")
            camera.draw(sight_box)
        day += 1
        air_instability = day/(2*days_per_year)*10
        daily_precip = 0

        # temp = 45 + 45*math.sin((day*2*math.pi/365)+math.pi/8)+random.randint(-10,10)
        # pressure = 100 + 3 * math.sin((day * 2 * math.pi / 365) + math.pi / 8) + random.randint(-1, 1)
        # humidity = 65 + 20 * math.sin((day * 2 * math.pi / 365) + math.pi / 8) + random.randint(-20, 20)

        old_temp = temp
        temp = 30*math.sin(math.pi/8+day*2*math.pi/days_per_year) + 55 + 3*math.sin((day+rand_stagger)*math.pi/(days_per_year//16)) + random.randint(-2,2)
        old_pressure = pressure
        pressure = 100 + 3*math.sin((day+2+rand_stagger)*math.pi/(days_per_year//8)) + (temp-old_temp)/(1440/days_per_year)
        wind_speed = abs((pressure - old_pressure) / 3 * 20)**1.2*air_instability/10
        wind_sign = random.randint(0,1)
        if wind_sign == 0:
            wind_sign = -1
        wind_direction = math.exp((old_pressure-pressure)*5)*wind_sign
        if wind_direction > 180:
            wind_direction = 180
        elif wind_direction < -180:
            wind_direction = -180
        old_humidity = humidity
        humidity = 50 + 45*math.sin((day+5+rand_stagger)*math.pi/(days_per_year/33)) + \
                   30*math.sin((day-5+rand_stagger)*math.pi/(days_per_year/64)) + \
                   (days_per_year/72)*(old_temp-temp)*abs(old_temp-temp) + \
                   (days_per_year/36)*(old_pressure-pressure)*abs(old_pressure-pressure) + \
                   math.cos(wind_direction*math.pi/180)*wind_speed
        heat_index = temp+(humidity-50)/5-wind_speed/2
        cloud_altitude = pressure*math.log10(abs(humidity))/200
        if cloud_altitude > 1:
            cloud_altitude = 1
        elif cloud_altitude < 0:
            cloud_altitude = 0

        if humidity < 0:
            humidity = 0
            cloud_thickness = 0
        if humidity > 85:
            daily_precip = 0.5*math.exp((old_pressure-pressure)/3)*(humidity-85)/5
            if daily_precip > 10:
                cloud_thickness = 1
                daily_precip = 10
            precip += daily_precip
            num_precip += 1
            if humidity>100:
                humidity = 100
            if temp < 35:
                num_snow += 1
                state_color = "White"
                if pressure < 97:
                    cloud_thickness = 1
                    weather = "Blizzard"
                else:
                    cloud_thickness = 0.8
                    weather = "Snow"
            elif pressure < 95:
                cloud_thickness = 1
                weather = "Typhoon"
                num_rain += 1
                state_color = "Cyan"
            elif pressure < 97:
                cloud_thickness = 0.9
                weather = "Storm"
                num_rain += 1
                state_color = "Cyan"
            else:
                cloud_thickness = 0.8
                weather = "Rain"
                num_rain += 1
                state_color = "Cyan"
        elif humidity > 60:
            cloud_thickness = (humidity-10)/100
            weather = "Cloudy"
            num_cloud += 1
            state_color = "Gray"
        else:
            cloud_thickness = (humidity-20)/150
            if cloud_thickness < 0:
                cloud_thickness = 0
            weather = "Clear"
            num_clear += 1
            state_color = "Yellow"
        if temp > 80:
            temp_type = "Hot"
        elif temp > 60:
            temp_type = "Warm"
        elif temp > 40:
            temp_type = "Cool"
        else:
            temp_type = "Cold"
        camera.draw("Day: " + str(round(day,2)), "Arial", 20, "Yellow", 100, 20)
        camera.draw("Temp: " + str(round(temp,2)), "Arial", 20, "Yellow", 100, 50)
        camera.draw("Pressure: " + str(round(pressure,2)), "Arial", 20, "Yellow", 100, 80)
        camera.draw("Humidity: " + str(round(humidity,2)), "Arial", 20, "Yellow", 100, 110)
        camera.draw("Daily Precip: " + str(round(daily_precip, 2)), "Arial", 20, "Yellow", 100, 140)
        camera.draw("Total Precip: "+str(round(precip,2)),"Arial",20,"Yellow",100,170)
        camera.draw("Num Precip: " + str(round(num_precip, 2)), "Arial", 20, "Yellow", 100, 200)
        camera.draw("Weather: " + weather+" "+temp_type, "Arial", 25, "Yellow", 200, 230,True)

        # if day in range(rand_spring,rand_spring+days_per_season) or day in range(rand_summer,rand_summer+days_per_season)\
        #         or day in range(rand_fall,rand_fall+days_per_season) or day in range(rand_winter,rand_winter+days_per_season):
        overcast = ["Cloudy","Rain","Blizzard","Snow","Typhoon","Storm"]
        # if weather in overcast:
        if 1 == 1:
            temp_graph.center = [3 * day, 600 - 0.6* temp]
            camera.draw(temp_graph)
            pres_graph.center = [3 * day, 650 - 2 * pressure]
            camera.draw(pres_graph)
            hum_graph.center = [3 * day, 500 - 0.1 * humidity]
            camera.draw(hum_graph)
            precip_graph.center = [3 * day, 650 - daily_precip]
            camera.draw(precip_graph)
            wind_graph.center = [3*day,400-wind_speed]
            wind_dir_grayscale = int(0.5*255*(math.cos(wind_direction)+1))
            wind_graph.color = (wind_dir_grayscale,wind_dir_grayscale,wind_dir_grayscale)
            # black means towards land, white means towards sea
            camera.draw(wind_graph)
            heat_graph.center = [3*day,375-0.5*heat_index]
            camera.draw(heat_graph)
            clouds_graph.center = [3*day,300-5*cloud_altitude]
            clouds_graph.color = (255*(1-cloud_thickness),255*(1-cloud_thickness),255*(1-cloud_thickness))
            # clouds_graph.color = "White"
            camera.draw(clouds_graph)

            weather_state.center = [3 * day, 600]
            weather_state.color = state_color
            camera.draw(weather_state)

            sun_graph.center = [450, 300 - num_clear]
            camera.draw(sun_graph)
            cloud_graph.center = [500, 300 - num_cloud]
            camera.draw(cloud_graph)
            rain_graph.center = [550, 300 - num_rain]
            camera.draw(rain_graph)
            snow_graph.center = [600, 300 - num_snow]
            camera.draw(snow_graph)


    camera.draw(rerun)
    if rerun.contains(camera.mouse) and camera.mouseclick:
        timer = 0
        day = 0
        num_clear = 0
        num_cloud = 0
        num_rain = 0
        num_snow = 0
        precip = 0
        num_precip = 0
    camera.display()

ticks_per_second = 30

gamebox.timer_loop(ticks_per_second, tick)
import agentpy as ap
import random

board = {
        'cars' : {},
        'roads': {},
        'traffic_lights': {},
}

class TrafficLight(ap.Agent):
  def setup(self, road):
    # 1 - Green, 2 - Yellow, 3 - Red
    self.currentColor = 3
    self.waitTime = 0
    self.road = road
    self.yellowTime = 0

  def changeColor(self):
    if self.currentColor == 1:
      for tl in board['traffic_lights']:
        if int(tl) != self.id:
          if board['traffic_lights'][str(tl)]['waitTime'] > 600:
            self.currentColor = 2
            board['traffic_lights'][str(self.id)]['color'] = 2
            # print('changed to yellow')

    elif self.currentColor == 2:
      if self.yellowTime >= 300:
        self.currentColor = 3
        board['traffic_lights'][str(self.id)]['color'] = 3
        self.yellowTime = 0
        self.waitTime = 0
        board['traffic_lights'][str(self.id)]['waitTime'] = self.waitTime
        # print('changed to red')
      else:
        self.yellowTime += 1

    waiting = False
    for car in board['cars']:
      if board['cars'][str(car)]['currentRoad'] == self.road:
        # If there's a car on the road
        if board['roads'][str(self.road + 1)]['direction'] == 'H':
          if abs(board['cars'][str(car)]['position'][0]) <= board['roads'][str(self.road + 1)]['endPosition'][0] + 5:
            waiting = True
        elif board['roads'][str(self.road + 1)]['direction'] == 'V':
          if abs(board['cars'][str(car)]['position'][1]) <= board['roads'][str(self.road + 1)]['endPosition'][1] + 5:
            waiting = True

    if waiting and self.currentColor != 1:
      self.waitTime += 1
      board['traffic_lights'][str(self.id)]['waitTime'] = self.waitTime

    found = False
    if self.waitTime > 600:
      for tl in board['traffic_lights']:
        if board['traffic_lights'][str(tl)]['color'] == 1 or board['traffic_lights'][str(tl)]['color'] == 2:
          found = True
      
      if not found:
        self.currentColor = 1
        board['traffic_lights'][str(self.id)]['color'] = 1
        self.waitTime = 0
        board['traffic_lights'][str(self.id)]['waitTime'] = self.waitTime

class Road(ap.Agent):
  # Road initializer
  def setup(self, max_velocity, direction, startPosition, endPosition, validChanges):
    self.max_velocity = max_velocity # Maximum velocity allowed
    self.direction = direction # Direction of the road (Horizontal or Vertical)
    self.cars = [] # List of cars that are currently on the road
    self.startPosition = startPosition # Position in which the road starts [x, y]
    self.endPosition = endPosition # Position in which the road ends [x, y]
    self.validChanges = validChanges # Matrix of valid road changes

  # Method to add a car to a road
  def addCar(self, car):
    self.cars.append(car)

class Intersection(ap.Agent):
  def setup(self, roads, traffic_lights):
    self.roads = roads
    self.traffic_lights = traffic_lights

class Car(ap.Agent):
  # Car initializer
  def setup(self, roads):
    validRoads = [0, 2] # Roads in which a car can start on
    self.startRoadIndex = random.randint(0, len(validRoads) - 1) # Random index of a valid road
    self.startRoad = roads[validRoads[self.startRoadIndex]] # Road object in which the car will start
    for i in self.startRoad.validChanges[self.startRoadIndex]: # Road object in which the car will end
      if i == 1:
        self.endRoad = roads[i]
    
    roads[validRoads[self.startRoadIndex]].addCar(self) # Add the car to the start road

    self.velocity = random.randint(round(self.startRoad.max_velocity / 10, 0), self.startRoad.max_velocity) # Start car with a random velocity
    self.acceleration = random.uniform(2, 5) # Random acceleration value
    self.deacceleration = random.uniform(4, 7) * -1 # Random deacceleration value
    self.length = 5 # Length of the car (m) (Longaniza de un carro)
    self.position = [self.startRoad.startPosition[0], self.startRoad.startPosition[1]] # Middle position of car (used for unity)
    if self.startRoad.direction == 'H': # If the car is on a horizontal road
      self.front_position = [self.position[0] + (self.length / 2), self.position[1]] # Calculate front position
      self.rear_position = [self.position[0] - (self.length / 2), self.position[1]] # Calculate rear position
    elif self.startRoad.direction == 'V': # If the car is on a vertical road
      self.front_position = [self.position[0], self.position[1] + (self.length / 2)] # Calculate front position
      self.rear_position = [self.position[0], self.position[1] - (self.length / 2)] # Calculate rear position

    self.currentRoad = validRoads[self.startRoadIndex]

  # Method to accelerate 
  def accelerate(self, mfR):
    if self.velocity < board['roads'][str(self.currentRoad)]['max_velocity']: # changed this to current road for when we change roads :) goldi ve esto
      self.velocity += (self.acceleration / mfR) 
    else:
      self.velocity = board['roads'][str(self.currentRoad)]['max_velocity'] # goldi ve aki gracias 

  # Method to brake
  def brake(self, mfR):
    if self.velocity == 0: # If the velocity is 0, pass
      pass
    if self.velocity > 0: # If the velocity is greater than 0, brake
      self.velocity += (self.deacceleration / mfR) 
    if self.velocity < 0: # If the velocity is less than 0, set it to 0
      self.velocity = 0

  # Calculate the necessary distance for the car to brake
  def distToBrake(self):
    return -(pow(self.velocity, 2)) / (self.deacceleration * 2) + 2

  # Update the position of the car (v * t)
  def updatePosition(self, mfR):
    if self.startRoad.direction == 'H':
      self.position[0] += self.velocity * (1/mfR)
      self.front_position[0] += self.velocity * (1/mfR)
      self.rear_position[0] += self.velocity * (1/mfR)
    elif self.startRoad.direction == 'V':
      self.position[1] -= self.velocity * (1/mfR)
      self.front_position[1] -= self.velocity * (1/mfR)
      self.rear_position[1] -= self.velocity * (1/mfR)

  # Calculate the distance between the car and the object in front
  def calculateDistance(self, road):
    index = road.cars.index(self)

    if road.direction == 'H':
      if index >= 1:
        return road.cars[index - 1].rear_position[0] - road.cars[index].front_position[0] 
      else:
        # El semáforo está en frente
        return road.endPosition[0] - road.cars[index].front_position[0] 
        
    elif road.direction == 'V':
      if index >= 1:
        return road.cars[index].front_position[1] - road.cars[index - 1].rear_position[1]
      else:
        # El semáforo está en frente
        return road.cars[index].front_position[1] - road.endPosition[1]

  # Calculate the distance between the car and the end of the road
  def calculateDistanceToTrafficLight(self, road):
    index = road.cars.index(self)

    if road.direction == 'H':
      return road.endPosition[0] - road.cars[index].front_position[0] 

    elif road.direction == 'V':
      return road.cars[index].front_position[1] - road.endPosition[1]

  def checkTrafficLight(self):
    for tl in board['traffic_lights']:
      if board['traffic_lights'][str(tl)]['road'] == self.currentRoad:
        return board['traffic_lights'][str(tl)]['color']
    else:
      return None

  # Main function that decides what the car should do
  def move(self, mfR):
    distance = self.calculateDistance(self.startRoad)
    distance_to_brake = self.distToBrake()

    if distance_to_brake < distance:
      # Look at traffic light 
      if 1 in board['roads'][str(self.currentRoad + 1)]['validChanges'][self.currentRoad]:
        if distance_to_brake < self.calculateDistanceToTrafficLight(self.startRoad):
          color = self.checkTrafficLight()

          if color == 2:
            self.brake(mfR)

          else:
            self.accelerate(mfR)

        else:
            self.brake(mfR)
      
      else:
        self.accelerate(mfR)

    else:
      if self.checkTrafficLight() == 1:
        self.accelerate(mfR)
      else:
        self.brake(mfR)

    self.updatePosition(mfR)

class Car(ap.Agent):
  # Car initializer
  def setup(self, roads):
    validRoads = [0, 2] # Roads in which a car can start on
    self.startRoadIndex = random.randint(0, len(validRoads) - 1) # Random index of a valid road
    self.startRoad = roads[validRoads[self.startRoadIndex]] # Road object in which the car will start
    for i in self.startRoad.validChanges[self.startRoadIndex]: # Road object in which the car will end
      if i == 1:
        self.endRoad = roads[i]
    
    roads[validRoads[self.startRoadIndex]].addCar(self) # Add the car to the start road

    self.velocity = random.randint(round(self.startRoad.max_velocity / 10, 0), self.startRoad.max_velocity) # Start car with a random velocity
    self.acceleration = random.uniform(2, 5) # Random acceleration value
    self.deacceleration = random.uniform(4, 7) * -1 # Random deacceleration value
    self.length = 5 # Length of the car (m) (Longaniza de un carro)
    self.position = [self.startRoad.startPosition[0], self.startRoad.startPosition[1]] # Middle position of car (used for unity)
    if self.startRoad.direction == 'H': # If the car is on a horizontal road
      self.front_position = [self.position[0] + (self.length / 2), self.position[1]] # Calculate front position
      self.rear_position = [self.position[0] - (self.length / 2), self.position[1]] # Calculate rear position
    elif self.startRoad.direction == 'V': # If the car is on a vertical road
      self.front_position = [self.position[0], self.position[1] + (self.length / 2)] # Calculate front position
      self.rear_position = [self.position[0], self.position[1] - (self.length / 2)] # Calculate rear position

    self.currentRoad = validRoads[self.startRoadIndex]

  # Method to accelerate 
  def accelerate(self, mfR):
    if self.velocity < board['roads'][str(self.currentRoad + 1)]['max_velocity']: # changed this to current road for when we change roads :) goldi ve esto
      self.velocity += (self.acceleration / mfR) 
    else:
      self.velocity = board['roads'][str(self.currentRoad + 1)]['max_velocity'] # goldi ve aki gracias 

  # Method to brake
  def brake(self, mfR):
    if self.velocity == 0: # If the velocity is 0, pass
      pass
    if self.velocity > 0: # If the velocity is greater than 0, brake
      self.velocity += (self.deacceleration / mfR) 
    if self.velocity < 0: # If the velocity is less than 0, set it to 0
      self.velocity = 0

  # Calculate the necessary distance for the car to brake
  def distToBrake(self):
    return -(pow(self.velocity, 2)) / (self.deacceleration * 2) + 2

  # Update the position of the car (v * t)
  def updatePosition(self, mfR):
    if self.startRoad.direction == 'H':
      self.position[0] += self.velocity * (1/mfR)
      self.front_position[0] += self.velocity * (1/mfR)
      self.rear_position[0] += self.velocity * (1/mfR)
    elif self.startRoad.direction == 'V':
      self.position[1] -= self.velocity * (1/mfR)
      self.front_position[1] -= self.velocity * (1/mfR)
      self.rear_position[1] -= self.velocity * (1/mfR)

  # Calculate the distance between the car and the object in front
  def calculateDistance(self, road):
    index = road.cars.index(self)

    if road.direction == 'H':
      if index >= 1:
        return road.cars[index - 1].rear_position[0] - road.cars[index].front_position[0] 
      else:
        # El semáforo está en frente
        return road.endPosition[0] - road.cars[index].front_position[0] 
        
    elif road.direction == 'V':
      if index >= 1:
        return road.cars[index].front_position[1] - road.cars[index - 1].rear_position[1]
      else:
        # El semáforo está en frente
        return road.cars[index].front_position[1] - road.endPosition[1]

  # Calculate the distance between the car and the end of the road
  def calculateDistanceToTrafficLight(self, road):
    index = road.cars.index(self)

    if road.direction == 'H':
      return road.endPosition[0] - road.cars[index].front_position[0] 

    elif road.direction == 'V':
      return road.cars[index].front_position[1] - road.endPosition[1]

  def checkTrafficLight(self):
    for tl in board['traffic_lights']:
      if board['traffic_lights'][str(tl)]['road'] == self.currentRoad:
        return board['traffic_lights'][str(tl)]['color']
    else:
      return None

  # Main function that decides what the car should do
  def move(self, mfR):
    distance = self.calculateDistance(self.startRoad)
    distance_to_brake = self.distToBrake()

    if distance_to_brake < distance:
      # Look at traffic light 
      if 1 in board['roads'][str(self.currentRoad + 1)]['validChanges'][self.currentRoad]:
        if distance_to_brake < self.calculateDistanceToTrafficLight(self.startRoad):
          color = self.checkTrafficLight()

          if color == 2:
            self.brake(mfR)

          else:
            self.accelerate(mfR)

        else:
            self.brake(mfR)
      
      else:
        self.accelerate(mfR)

    else:
      if self.checkTrafficLight() == 1:
        self.accelerate(mfR)
      else:
        self.brake(mfR)

    self.updatePosition(mfR)

class SimulationModel(ap.Model):
  def addCarToBoard(self, car):
    board['cars'][str(car.id)] = {      # estas cosas si se manejan con referencias
        'position': car.position,
        'currentRoad': car.currentRoad
    }

  def addTrafficLightToBoard(self, tl):
    board['traffic_lights'][str(tl.id)] = {
          'color': tl.currentColor,    # las cosas estas no se actualizan pq los ints strings y tuples no se manejan con referencias
          'waitTime': tl.waitTime,
          'road': tl.road,
      }

  def addRoadToBoard(self, road):
    board['roads'][str(road.id)] = {
          'endPosition': road.endPosition,
          'direction': road.direction,
          'validChanges': road.validChanges,
          'max_velocity': road.max_velocity
      }

  def setup(self):
    self.positions = []

    # Roads for the simulation
    newRoads = [
        Road(self, 20, 'H', [-300, 0], [0, 0], self.p.matrix),
        Road(self, 20, 'H', [50, 0], [350, 0], self.p.matrix),
        Road(self, 20, 'V', [0, 300], [0, 0], self.p.matrix),
        Road(self, 20, 'V', [0, -50], [0, -350], self.p.matrix)
    ]
    self.roads = ap.AgentList(self, newRoads)

    for road in self.roads:
      self.addRoadToBoard(road)

    # Traffic Lights for the simulation
    
    newTrafficLights = []
    for i in range(len(self.p.matrix)):
      if 1 in self.p.matrix[i]:
        newTrafficLights.append(TrafficLight(self, road=i))
    self.traffic_lights = ap.AgentList(self, newTrafficLights)

    for tl in self.traffic_lights:
      self.addTrafficLightToBoard(tl)

    # Intersection
    self.intersection = Intersection(self, roads=self.roads, traffic_lights=self.traffic_lights)

    # Cars
    self.cars = ap.AgentList(self, 1, Car, roads=self.roads)
    for car in self.cars:
      self.addCarToBoard(car)

    self.counter = 0
    self.carCounter = 1

  def step(self):
    if self.counter % 150 == 0 and self.carCounter < self.p.cars and self.counter != 0: # Goldi ve esto, aqui falta que el frame 0 creo no spawnee un carro pq sino puede haber 2 carros uno sobre otro si inician en la misma 
      tempCar = Car(self, self.roads)
      self.cars.append(tempCar)
      self.addCarToBoard(tempCar)
      self.carCounter += 1

    self.cars.move(60)
    self.traffic_lights.changeColor()
    self.counter += 1

    print(board)

  def update(self):
    # for car in self.cars:
      # self.record(str(car.id), car.position)
    self.cars.record("position")
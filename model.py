import agentpy as ap

from agents import Car, Road, Intersection, TrafficLight

from agents import board

class SimulationModel(ap.Model):
  def addCarToBoard(self, car):
    board['cars'][str(car.id)] = {      # estas cosas si se manejan con referencias
        'position': car.position,
        'currentRoad': car.currentRoad,
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
          'max_velocity': road.max_velocity
      }

  def addSteptoBoard(self,):
    tempStep = {}

    for car in self.cars:
      tempx = car.position[0]
      tempy = car.position[1]
      tempStep[str(car.id)] = {
          'position': [tempx, tempy],
          'velocity': car.velocity,
      }

    for tl in self.traffic_lights:
      tempStep[str(tl.id)] = {
          'color': tl.currentColor
      }

    self.results['results'].append(tempStep)

  def checkCars(self):
    carsToDelete = []

    for road in self.roads:
      for car in road.cars:
        if road.direction == 'H':
            if car.position[0] >= road.endPosition[0]:
                if road == car.endRoad:
                    road.deleteCar(car)
                    carsToDelete.append(car)
                else:
                    # Delete car from current road
                    road.deleteCar(car)
                    # Change road
                    newRoad = car.changeRoad()
                    # Add car to new road
                    newRoad.addCar(car)

        elif road.direction == 'V':
            if car.position[1] <= road.endPosition[1]:
                if road == car.endRoad:
                    road.deleteCar(car)
                    carsToDelete.append(car)
                else:
                    # Delete car from current road
                    road.deleteCar(car)
                    # Change road
                    newRoad = car.changeRoad()
                    # Add car to new road
                    newRoad.addCar(car)

    return carsToDelete
        
  def setup(self):
    board['validChanges'] = self.p.matrix

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

    self.results = {'results': []}

  def step(self):
    # Add a car evert 150 frames, until the max car limit has been reached
    if self.counter % 150 == 0 and self.carCounter < self.p.cars and self.counter != 0: 
      tempCar = Car(self, self.roads)
      self.cars.append(tempCar)
      self.addCarToBoard(tempCar)
      self.carCounter += 1

    # Check if any car has changed road
    carsToDelete = self.checkCars()
    if carsToDelete:
        for car in carsToDelete:
            print(car)
            self.cars.remove(car)
            del board['cars'][str(car.id)]
    # Move cars
    self.cars.move(60)
    # Change traffic light colors (if necessary)
    self.traffic_lights.changeColor()
    # Update counter
    self.counter += 1

    # print(board)

  def update(self):
    self.addSteptoBoard()

  def end(self):
    self.report('results')
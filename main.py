## HELPERS
def goto(x, y):
  while x < get_pos_x():
    move(East)
  while x > get_pos_x():
    move(West)
  while y < get_pos_y():
    move(South)
  while y > get_pos_y():
    move(North)

def adj():
  move(North)
  if get_pos_y() == 0:
    move(East)


def origin():
  return (get_pos_x() + get_pos_y()) == 0


def safe_till():
  if get_ground_type() == Grounds.Turf:
    till()


def safe_untill():
  if get_ground_type() == Grounds.Soil:
    till()


def bubbleSwap():
  sorted = True
  this = measure()
  that = measure(East)
  if this > that and get_pos_x() < farm_size - 1:
    swap(East)
    sorted = False

  that = measure(North)
  if this > that and get_pos_y() < farm_size - 1:
    swap(North)
    sorted = False

  return sorted


def sortField():
  goto(0, 0)
  passNum = 0
  sorted = False
  passSorted = True
  while not sorted and passNum < get_world_size()**2:
    if not bubbleSwap():
      passSorted = False
    adj()
    if origin():
      passNum = passNum + 1
      if passSorted:
        sorted = True
      else:
        passSorted = True


def purchase_tanks(num_tanks):
  total_tanks = num_items(Items.Empty_Tank) + num_items(Items.Water_Tank)
  num_wood = num_items(Items.Wood)
  if total_tanks != num_tanks:
    remaining = num_tanks - total_tanks
    if remaining < 0:
      return total_tanks
    if remaining * 5 > num_wood:
      remaining = num_wood // 5
    trade(Items.Empty_Tank, remaining)
    total_tanks += remaining
  return total_tanks


def water(baseline=0.75):
  if get_ground_type() == Grounds.Turf or num_items(Items.Water_Tank) == 0:
    return False
  if num_items(Items.Water_Tank) > 0 and get_water() < baseline:
    for _ in range(1 // (1 - get_water())):
      use_item(Items.Water_Tank)
  return True


def plantTilledEntity(entity):
  if num_items(plantSeedMap[entity]) == 0:
    trade(plantSeedMap[entity], trade_batch)
  safe_till()
  return plant(entity)


def harvestAll():
  goto(0, 0)
  harvest()
  adj()
  while not origin():
    harvest()
    adj()


## HAY
def hay():
  safe_untill()
  harvest()
  adj()
  while not origin():
    harvest()
    adj()


## WOOD
def wood():
  def plantWood():
    if get_ground_type() == Grounds.Turf:
      till()
      water()
    if (get_pos_y() + get_pos_x()) % 2 == 0:
      return plant(Entities.Tree)
    else:
      return plant(Entities.Bush)

  plantWood()
  adj()
  while not origin():
    harvest()  # hay
    water()
    plantWood()
    adj()
  harvestAll()


# pumpkin
def pumpkin():
  fullField = False
  fullPass = False
  while not fullField:
    if origin():
      if fullPass == True:
        fullField = True
      fullPass = True
    if plantTilledEntity(Entities.Pumpkin):
      fullPass = False
    adj()


def plantFullField(entity):
  if entity == Entities.Pumpkin:
    pumpkin()
    return
  water()
  plantTilledEntity(entity)
  adj()
  while not origin():
    if can_harvest():
      harvest()
    water()
    plantTilledEntity(entity)
    adj()


def harvestLargest():
  goto(0, 0)
  biggestValue = measure()
  smallestValue = measure()
  adj()

  while not origin():
    if measure() > biggestValue:
      biggestValue = measure()
    if measure() < smallestValue:
      smallestValue = measure()
    adj()

  for size in range(biggestValue, smallestValue - 1, -1):
    if measure() == size:
      harvest()
    adj()

    while not origin():
      if measure() == size:
        harvest()
      adj()

def harvestMode():
  if can_harvest():
    harvest()
  if num_items(Items.Hay) < min_hay:
      hay()
  elif num_items(Items.Wood) < min_wood:
    wood()
  elif num_items(Items.Carrot) < min_carrot:
    plantFullField(Entities.Carrots)
    harvestAll()
  elif num_items(Items.Pumpkin) < min_pumpkin:
    plantFullField(Entities.Pumpkin)
    harvest()
  elif num_items(Items.Power) < min_power:
    plantFullField(Entities.Sunflower)
    harvestLargest()
  else:
    plantFullField(Entities.Cactus)
    sortField()
    harvest()


# treasure
def treasureMode():
  if get_entity_type() == Entities.Hedge:
    solveMaze(North)

  if get_entity_type() == Entities.Grass:
    plant(Entities.Bush)
  elif get_entity_type() == Entities.Bush:
    if num_items(Items.Fertilizer) == 0:
      trade(Items.Fertilizer, trade_batch)
    use_item(Items.Fertilizer)
  else:
    clear()


def solveMaze(direction):
  if get_entity_type() == Entities.Treasure:
    harvest()
    return
  else:
    direction = rightHandRuleMove(direction)
  solveMaze(direction)


def rightHandRuleMove(direction):
  if move(right[direction]):
    return right[direction]
  elif move(direction):
    return direction
  else:
    return left[direction]


## main

# carrot seeds multiplier: 12

d = {"mode": 1}
base = 10000
min_hay = 6 * base
min_wood = 6 * base
min_carrot = 6 * base
min_pumpkin = 6 * base
min_gold = 4 * base
min_cactus = 3 * base
min_power = 3 * base

mode_change_threshold = 10000
max_wood = min_wood + mode_change_threshold
max_carrot = min_carrot + mode_change_threshold
max_pumpkin = min_pumpkin + mode_change_threshold
max_gold = min_gold + mode_change_threshold
max_cactus = min_cactus + mode_change_threshold

trade_batch = get_world_size() ** 2
farm_size = 1
dino_tuning = 8

plantSeedMap = {
  Entities.Carrots: Items.Carrot_Seed,
  Entities.Cactus: Items.Cactus_Seed,
  Entities.Pumpkin: Items.Pumpkin_Seed,
  Entities.Sunflower: Items.Sunflower_Seed,
}

right = {
  North: East,
  East: South,
  South: West,
  West: North,
}

left = {
  North: West,
  West: South,
  South: East,
  East: North,
}


def main_loop(run=True):
  while run:
    purchase_tanks(4000)
    if d['mode'] == 1:
      harvestMode()
    elif d['mode'] == 2:
      treasureMode()
    d['mode'] = switch(d['mode'])


def switch(automode):
  if origin() and automode == 1:
    if num_items(Items.Cactus) > max_cactus:
      return 3
    if num_items(Items.Gold) < min_gold and num_items(Items.Pumpkin) > min_pumpkin:
      return 2
  elif automode == 2:
    if num_items(Items.Cactus) > max_cactus:
      return 3
    if num_items(Items.Pumpkin) < min_pumpkin and num_items(Items.Gold) > max_gold:
      return 1
  elif automode == 3:
    if num_items(Items.Cactus) < min_cactus:
      return 1
  return automode

clear()
main_loop(True)

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


def sortField(passes=get_world_size() ** 2):
  goto(0, 0)
  passNum = 0
  sorted = False
  passSorted = True
  while not sorted and passNum < passes:
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


def water(baseline=0.5):
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
  while not can_harvest():
    do_a_flip()
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
      if fullPass:
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
    harvest()
    water()
    plantTilledEntity(entity)
    adj()


def harvestLargest():
  goto(0, 0)
  water()
  if measure() == None:
    plantTilledEntity(Entities.Sunflower)
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


# plant
def harvestMode(mode=1):
  if num_items(Items.Hay) < min_hay:
    hay()
  elif num_items(Items.Wood) < min_wood or mode == 2:
    wood()
  elif num_items(Items.Carrot) < min_carrot or mode == 3:
    plantFullField(Entities.Carrots)
    harvestAll()
  elif num_items(Items.Pumpkin) < min_pumpkin or mode == 4:
    plantFullField(Entities.Pumpkin)
    harvest()
  elif num_items(Items.Power) < min_power or mode == 5:
    plantFullField(Entities.Sunflower)
    harvestLargest()
  else:
    plantFullField(Entities.Cactus)
    sortField()
    harvest()


# dino
def dinoMode():
  clear()
  if num_items(Items.Egg) == 0:
    trade(Items.Egg, trade_batch)
  use_item(Items.Egg)
  adj()
  while not origin():
    if num_items(Items.Egg) == 0:
      trade(Items.Egg, trade_batch)
    use_item(Items.Egg)
    adj()
  sortField(dino_tuning)
  harvestAll()


# treasure
def treasureMode(mode='exhaustive'):
  if get_entity_type() == Entities.Hedge:
    if mode == 'exhaustive':
      solveExhaustive()
    elif mode == 'dfs':
      solveDFS()

  if get_entity_type() == Entities.Grass:
    plant(Entities.Bush)
  elif get_entity_type() == Entities.Bush:
    safe_fertilizer()
  else:
    clear()


def safe_fertilizer():
  if num_items(Items.Fertilizer) == 0:
    trade(Items.Fertilizer, trade_batch)
  return use_item(Items.Fertilizer)


def solveExhaustive(direction=North):
  def rightHandRuleMove(direction):
    if move(right[direction]):
      return right[direction]
    elif move(direction):
      return direction
    else:
      return left[direction]

  if get_entity_type() == Entities.Treasure:
    harvest()
    return
  else:
    direction = rightHandRuleMove(direction)
  solveExhaustive(direction)


def solveDFS(iterations=300):
  opp = {North: South, East: West, South: North, West: East}
  dx = {North: 0, East: 1, South: 0, West: -1}
  dy = {North: 1, East: 0, South: -1, West: 0}

  # Start the maze!
  harvest()
  plant(Entities.Bush)
  while get_entity_type() == Entities.Bush:
    safe_fertilizer()

  x, y = get_pos_x(), get_pos_y()
  goalx, goaly = None, None
  while iterations > 0:
    while get_entity_type() == Entities.Treasure:
      if measure() == None:
        iterations = 0
        break
      goalx, goaly = measure()
      iterations -= 1
      if iterations <= 0:
        break
      while not safe_fertilizer():
        pass

    stack = [([North, East, South, West], None)]
    visited = {(get_pos_x(), get_pos_y())}

    while get_entity_type() != Entities.Treasure:
      dirs, back = stack[-1]  # stack peek
      oldx = x
      oldy = y
      dir = None
      while len(dirs) > 0:
        dir = dirs.pop()
        x = oldx + dx[dir]
        y = oldy + dy[dir]
        if (x, y) in visited or not move(dir):
          dir = None
          continue
        else:
          break
      if dir == None:
        stack.pop()  # Get rid of the node we peeked
        if back == None:
          print('I give up!')
          while True:
            do_a_flip()
        move(back)
        x = oldx + dx[back]
        y = oldy + dy[back]
      else:
        visited.add((x, y))
        stack.append((get_ranked_dirs(x, y, goalx, goaly, opp[dir]), opp[dir]))
  harvest()


def get_ranked_dirs(pos_x, pos_y, goal_x, goal_y, exclude=None):
  if goal_x == None:
    all_dirs = [(1, North), (2, East), (3, South), (4, West)]
  else:
    all_dirs = [
      (goal_y - pos_y + 0.1, North),
      (goal_x - pos_x + 0.2, East),
      (pos_y - goal_y + 0.3, South),
      (pos_x - goal_x + 0.4, West),
    ]

  ranked_dirs = []
  for i in range(len(all_dirs)):
    worst_dir = min(all_dirs)
    all_dirs.remove(worst_dir)
    if worst_dir[1] != exclude:
      ranked_dirs.append(worst_dir[1])

  return ranked_dirs


## main

d = {'mode': 1}

base = 10000
min_hay = 12 * base
min_wood = 12 * base
min_carrot = 6 * base
min_pumpkin = 6 * base
min_gold = 6 * base / 5
min_cactus = 6 * base
min_power = base

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

right = {North: East, East: South, South: West, West: North}

left = {North: West, West: South, South: East, East: North}


def main_loop(run=True):
  while run:
    purchase_tanks(16000)
    if d['mode'] == 1:
      harvestMode()
    elif d['mode'] == 2:
      treasureMode('dfs')
    elif d['mode'] == 3:
      dinoMode()
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
    if num_items(Items.Cactus) == 0:
      return 1
  return automode


timed_reset()
clear()
main_loop(True)

# Imports
import numpy as np
import matplotlib.pyplot as plot
# Recursively calculates how many ways to roll a value from a list of dice
def ways(value : int, diceCount : int, dice : list) -> int:
	if value < 1 or diceCount < 1:
		return 0
	elif diceCount == 1:
		return int(value <= dice[0])
	else:
		return sum(
			ways(value - roll, diceCount - 1, dice[1:]) * ways(roll, 1, dice[0:1])
			for roll in range(1, dice[0] + 1)
		)
# Macro for getting list of ways to roll all possible values of a list of dice
allWays = lambda dice : [
	ways(v, len(dice), dice) for v in range(len(dice), sum(dice) + 1)
]
# Macro for turning the above list into a list of probabilites
diceDistribution = lambda dice : np.array(allWays(dice)) / np.prod(dice)
# Calculates P(X >= value) for a random variable X of a list of dice
def probDiceGEQ(value : int, dice : list, precision : int = 4) -> float:
	denom = np.prod(dice)
	c = len(dice)
	maxV = sum(dice)
	return round(
		sum([
			ways(v, c, dice) / denom for v in range(value, maxV + 1)
		]), precision
	)
# Calculates P(X <= value) for a random variable X of a list of dice
def probDiceLEQ(value : int, dice : list, precision : int = 4) -> float:
	denom = np.prod(dice)
	c = len(dice)
	return round(
		sum([
			ways(v, c, dice) / denom for v in range(value, c - 1, -1)
		]), precision
	)
# Calculates P(minVal <= X <= maxVal) for a random variable X of a list of dice
def probDiceInterval(
	minV : int, maxV : int, dice : list, precision : int = 4
) -> float:
	denom = np.prod(dice)
	c = len(dice)
	return round(
		sum([
			ways(v, c, dice) / denom for v in range(minV, maxV + 1)
		]), precision
	)
# Returns a formatted string describing a list of dice, largest dice first
def diceLabel(dice : list) -> str:
	s = ""
	S = set()
	for d in sorted(set(dice), reverse = True):
		s += str(dice.count(d)) + 'd' + str(d)
		S.add(d)
		if len(set(dice) - S) >= 1:
			s += " + "
	return s
# Produces a plot of a single dice list's ways to roll all values
def plotDiceWays(dice : list, color : str = "#4040B0"):
	possibilities = list(range(len(dice), sum(dice) + 1))
	f, a = plot.subplots()
	f.set_facecolor('w')
	f.set_figwidth(16)
	f.set_figheight(12)

	if len(possibilities) <= 32:
		a.set_xticks(possibilities)
	else:
		l = len(dice)
		s = sum(dice)
		a.set_xticks(list(range(l, s + 1, (s - l) // 32)))

	ways = allWays(dice)
	if max(ways) <= 16:
		a.set_yticks(list(range(1, max(ways) + 1)))
	else:
		a.set_yticks(list(range(1, max(ways) + 1, (max(ways) - min(ways)) // 16)))

	a.grid()
	a.set_title(
		"Ways To Roll all values of " + diceLabel(dice), fontsize = "xx-large"
	)
	a.set_xlabel("Dice Roll Value", fontsize = "x-large")
	a.set_ylabel("Ways To Roll", fontsize = "x-large")

	a.scatter(possibilities, ways, marker = '*', s = 128, c = color)
	a.plot(possibilities, ways, linestyle = "dotted", color = color)

	return f, a
# Produces a plot of a single dice list's probability distribution
def plotDiceDist(dice : list, color : str = "#4040B0"):
	possibilities = list(range(len(dice), sum(dice) + 1))
	f, a = plot.subplots()
	f.set_facecolor('w')
	f.set_figwidth(16)
	f.set_figheight(12)
	minV = len(dice)
	maxV = sum(dice)

	if len(possibilities) <= 32:
		a.set_xticks(possibilities)
	else:
		a.set_xticks(list(range(minV, maxV + 1, (maxV - minV) // 32)))

	possibilities.insert(0, minV)
	possibilities.append(maxV)
	distribution = diceDistribution(dice)
	distribution = np.insert(distribution, 0, 0)
	distribution = np.append(distribution, 0)

	a.grid()
	a.set_title(
		"Probability Distribution of " + diceLabel(dice), fontsize = "xx-large"
	)
	a.set_xlabel("Dice Roll Value", fontsize = "x-large")
	a.set_ylabel("Probability", fontsize = "x-large")

	a.fill(possibilities, distribution, color = color)

	return f, a
# Produces a plot of multiple probability distributions from multiple dice lists
def plotDiceDistMulti(
	diceSets : list, comments : list = None,
	color : str = '#4040B0A0'
):
	minX = min([len(d) for d in diceSets])
	maxX = max([sum(d) for d in diceSets])
	f, a = plot.subplots()
	f.set_facecolor('w')
	f.set_figwidth(16)
	f.set_figheight(12)
	
	if maxX - minX <= 32:
		a.set_xticks(list(range(minX, maxX + 1)))
	else:
		a.set_xticks(list(range(minX, maxX + 1, (maxX - minX) // 32)))
	
	a.grid()
	a.set_title(
		"Probability Distributions of multiple dice sets", fontsize = "xx-large"
	)
	a.set_xlabel("Dice Roll Value", fontsize = "x-large")
	a.set_ylabel("Probability", fontsize = "x-large")
	
	if comments is None:
		comments = ['' for x in range(len(diceSets))]
	c = 0
	
	for dice in diceSets:
		possibilities = list(range(len(dice), sum(dice) + 1))
		distribution = diceDistribution(dice)
		a.plot(
			possibilities, distribution,
			label = diceLabel(dice) + ' ' + comments[c]
		)
		
		possibilities.insert(0, len(dice))
		possibilities.append(sum(dice))
		distribution = np.insert(distribution, 0, 0)
		distribution = np.append(distribution, 0)
		
		a.fill(possibilities, distribution, color = color)
		c += 1
	a.legend()
	
	return f, a
# Calculates all ways to roll n of a die where the lowest k dice are discarded
def allWaysDropN(
	diceCount : int, dropCount : int,
	die : int, target : int = 0
) -> list:
	if diceCount - dropCount < 1:
		return []

	def increment(dice : list):
		i = 0
		while i < diceCount and (i == 0 or dice[i - 1] == 1):
			dice[i] = (dice[i] % die) + 1
			i += 1

	def evaluate(dice : list):
		diceSorted = sorted(dice)
		value = 0
		for v in range(diceCount - dropCount):
			value += diceSorted.pop()
		return value

	effectiveDice = diceCount - dropCount
	dice = [1 for d in range(diceCount)]
	values = [0 for v in range(effectiveDice, die * effectiveDice + 1)]

	for d in range(die ** diceCount):
		value = evaluate(dice)
		if value == target:
			print(dice, value)
		values[value - effectiveDice] += 1
		increment(dice)

	return values
# Macro for turning the above ways list into a probability distribution
diceDropDistribution = lambda count, drop, die : np.array(
	allWaysDropN(count, drop, die)
) / die ** count
# Produces a plot comparing rolling n dice with k dropped vs. rolling n-k dice
def plotDiceDropDist(
	diceCount : int, dropCount : int, die : int,
	color : str = "#4040B080"
):
	effectiveDice = diceCount - dropCount
	effectiveDiceList = [die for x in range(effectiveDice)]
	droppedLabel = str(diceCount) + 'd' + str(die) + "-drop-" + str(dropCount)
	f, a = plotDiceDist(effectiveDiceList, color)
	a.set_title(
		"Probability Distributions of " + droppedLabel
		+ " versus " + diceLabel(effectiveDiceList),
		fontsize = "xx-large"
	)

	possibilities = list(range(effectiveDice, die * effectiveDice + 1))
	distributionDropped = diceDropDistribution(diceCount, dropCount, die)
	distributionEffective = diceDistribution(effectiveDiceList)

	a.plot(possibilities, distributionDropped, label = droppedLabel)
	a.plot(
		possibilities, distributionEffective,
		label = diceLabel(effectiveDiceList)
	)
	a.legend()

	possibilities.insert(0, effectiveDice)
	possibilities.append(die * effectiveDice)
	distributionDropped = np.insert(distributionDropped, 0, 0)
	distributionDropped = np.append(distributionDropped, 0)
	distributionEffective = np.insert(distributionEffective, 0, 0)
	distributionEffective = np.append(distributionEffective, 0)

	a.fill(possibilities, distributionDropped, color = color)
	a.fill(possibilities, distributionEffective, color = color)

	return f, a

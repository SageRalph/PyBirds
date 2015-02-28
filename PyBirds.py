import math
from graphics import *
import random


def main(winLength,winheight):
    menuColumns = 4
    defaults = ["3","10","10","50","10","0.15","0.5","9.8","10","30","50","300"]
    win = GraphWin("PyBirds", winLength, winheight)
    menuInputs = intialiseMenuInputs(defaults,menuColumns)
    while True:
        menuInputs = menu(win, menuInputs, menuColumns, defaults)

def intialiseMenuInputs(defaults,columns):
    menuInputs = []
    for i in range(len(defaults)):
        menuInputs.append(Entry(Point(i%columns*200+100,i//columns*80+80),10))
        menuInputs[i].setText(defaults[i])
    return menuInputs

def menu(win, menuInputs, columns, defaults):
    drawBackdrop(win)
    playButton = drawButton(win,[0,20,0,80],"darkgreen","Play","gold")
    defaultsButton = drawButton(win,[0,20,80,160],"gold","Defaults","red")
    for item in menuInputs:
        item.draw(win)
    strings = [\
    "Number of targets",\
    "Number of obstacles",\
    "Number of trys",\
    "Game speed",\
    "Force multiplier",\
    "Surface friction",\
    "Projectile elasticity",\
    "Gravity",\
    "Min obstacle width",\
    "Max obstacle width",\
    "Min obstacle length",\
    "Max obstacle length"]
    drawMenuItemLabels(win,strings,columns)
    clickPos=win.getMouse()
    while not mouseOverrectangle(clickPos,playButton):
        if mouseOverrectangle(clickPos,defaultsButton):
            for item in menuInputs:
                item.undraw()
            menuInputs = intialiseMenuInputs(defaults,columns)
            for item in menuInputs:
                item.draw(win)
        clickPos=win.getMouse()
    menuOptions = []
    for item in menuInputs:
        try:
            float(item.getText())
        except ValueError:
            for menuItem in menuInputs:
                menuItem.undraw()
            return menuInputs
        menuOptions.append(eval(item.getText()))
        item.undraw()
    play(win,menuOptions[0],menuOptions[1], \
    menuOptions[2],menuOptions[3:8],menuOptions[8:12])
    return menuInputs

def drawMenuItemLabels(win,strings,columns):
    i=0
    while i < len(strings):
        Text(Point(i%columns*200+100,i//columns*80+50),strings[i]).draw(win)
        i += 1

def play(win, targetNumber,obstacleNumber,trysLeft,physicsConstants,obstacleDimensionRanges):
    bearingPoint = Point(win.getWidth()/10, win.getHeight() * 4/5)
    drawBackdrop(win)
    drawScenery(win, bearingPoint)
    menuButton = drawButton(win,[0,20,0,80],"red","Menu","gold")
    trysLeftDisplay = Text(Point(100,10),trysLeft)
    trysLeftDisplay.draw(win)
    #obstacles = setObstacles(win)
    #targets = setTargets(win)
    obstacles = genRandomObstacles(win,obstacleNumber,obstacleDimensionRanges)
    if obstacles == []:
        displayObjectPlacementError(win)
        return
    targets = genRandomTargets(win,targetNumber,obstacles)
    if targets == []:
        displayObjectPlacementError(win)
        return
    while trysLeft > 0 and len(targets) > 0:
        clickPos = Point(1000,0) #Invalid data for while
        while clickPos.getX() > win.getWidth()/10:
            clickPos = win.getMouse()
        if mouseOverrectangle(clickPos,menuButton):
            return
        trysLeft = trysLeft - 1
        trysLeftDisplay.setText(trysLeft)
        simulateProjectile(win,bearingPoint,clickPos,obstacles,targets, physicsConstants)
    displayEndGame(win, len(targets))
    win.getMouse()
    return

def displayObjectPlacementError(win):
    center = Point(win.getWidth() / 2, win.getHeight() / 2)
    errorBackdrop = Rectangle (Point(center.getX()-140, center.getY()-40), \
    Point(center.getX()+140,center.getY()+40))
    errorText = Text(center, "")
    errorText.setSize(15)
    errorBackdrop.setFill("orange")
    errorText.setText('''Timeout placing objects
    Reconfigure settings''')
    errorText.setFill("red")
    errorBackdrop.draw(win)
    errorText.draw(win)
    win.getMouse()

def drawButton(win,bounds,fillColour,text,textColour):
    top,bottom,left,right = bounds
    button = Rectangle(Point(left,top), Point(right,bottom))
    button.setFill(fillColour)
    button.draw(win)
    buttonText = Text(Point((left+right)/2,(top+bottom)/2),text)
    buttonText.setTextColor(textColour)
    buttonText.draw(win)
    return button

def displayEndGame(win, targetsleft):
    center = Point(win.getWidth() / 2, win.getHeight() / 2)
    endgameBackdrop = Rectangle (Point(center.getX()-130, center.getY()-40), \
    Point(center.getX()+130,center.getY()+40))
    endgameText = Text(center, "")
    endgameText.setSize(30)
    if targetsleft == 0:
        endgameBackdrop.setFill("yellow")
        endgameText.setText("You win")
        endgameText.setFill("darkgreen")
    else:
        endgameBackdrop.setFill("orange")
        endgameText.setText("Out of trys")
        endgameText.setFill("red")
    endgameBackdrop.draw(win)
    endgameText.draw(win)

def addTarget(win,targets,x,y,size):
    target = Circle(Point(x,y),size)
    target.setFill("green")
    target.draw(win)
    targets.append(target)
    return targets

def setTargets(win):
    targets = []
    #declare targets here
    targets = addTarget(win,targets,600,450,30)
    targets = addTarget(win,targets,800,200,30)
    return targets

def setObstacles(win):
    obstacles = []
    #declare obstacles here
    obstacles = addGradedWall(win,obstacles,[700,500,750,400],1)
    obstacles = addGradedWall(win,obstacles,[500,500,550,400],2)
    obstacles = addGradedWall(win,obstacles,[500,400,750,350],3)
    return obstacles

def genRandomTargets(win,targetNumber,obstacles):
    targets = []
    startTime = time.clock()
    for i in range(targetNumber):
        collided = True
        while collided == True:
            size = random.randint(20,40)
            x = random.randint(win.getWidth()//5 + size,win.getWidth() - size)
            y = random.randint(size, win.getHeight()-size)
            top = y - size
            bottom = y + size
            left = x - size
            right = x + size
            obstacleDimensions = top,bottom,left,right
            if circleOverlapsObstacle(Point(x,y),size,obstacles) \
            or circleOverlapsTarget(Point(x,y),size,targets) \
            or checkForObstacleOverlap(obstacleDimensions,obstacles):
                collided = True
                if time.clock() - startTime >= 30: #timeout
                    return []
            else:
                collided = False
        targets = addTarget(win,targets,x,y,size)
    return targets

def genRandomObstacles(win,obstacleNumber,obstacleDimensionRanges):
    obstacles = []
    startTime = time.clock()
    for i in range(obstacleNumber):
        collided = True
        while collided == True:
            longSide = random.randint(0,1)
            obstacleDimensions = \
            genTallOrWideRectangle(win,obstacleDimensionRanges,longSide)
            if rectanglePointsInsideObstacle(obstacleDimensions,obstacles) \
            or checkForObstacleOverlap(obstacleDimensions,obstacles):
                collided = True
                if time.clock() - startTime >= 30: #timeout
                    return []
            else:
                collided = False
        grade = random.randint(1,3)
        obstacles = addGradedWall(win,obstacles,obstacleDimensions,grade)
    return obstacles

def genTallOrWideRectangle(win,obstacleDimensionRanges,longSide):
    shortMin,shortMax,longMin,longMax = obstacleDimensionRanges
    long = random.randint(longMin,longMax)
    short = random.randint(shortMin,shortMax)
    if longSide == 0:
        left = random.randint(win.getWidth()//5,win.getWidth() - long)
        right = left + long
        top = random.randint(0, win.getHeight() - short)
        bottom = top + short
    else:
        left = random.randint(win.getWidth()//5,win.getWidth() - short)
        right = left + short
        top = random.randint(0, win.getHeight() - long)
        bottom = top + long
    #rectangle = Rectangle(Point(left,top),Point(right,bottom))
    return top,bottom,left,right

def rectanglePointsInsideObstacle(obstacleDimensions,obstacles):
    top,bottom,left,right = obstacleDimensions
    if checkForCollisions(left,top,obstacles,[]) != None \
    or checkForCollisions(left,bottom,obstacles,[]) != None \
    or checkForCollisions(right,top,obstacles,[]) != None \
    or checkForCollisions(right,bottom,obstacles,[]):
        return True
    return False

def circleOverlapsObstacle(center, radius, obstacles):
    for obstacle in obstacles:
        top,bottom,left,right = determineRectangleBounds(obstacle)
        if isBetween(center.getX(), left-radius,right+radius)\
        and isBetween(center.getY(), top-radius, bottom+radius):
            return True
    return False

def circleOverlapsTarget(center, radius, targets):
    for target in targets:
        if distance(center, target.getCenter()) <= radius + target.getRadius():
            return True
    return False

def addGradedWall(win, obstacles, obstacleDimensions, grade):
    y1, y2, x1, x2 = obstacleDimensions
    wallColours = ["brown", "grey", "gold"]
    for i in range (grade):
        wall = Rectangle(Point(x1,y1),Point(x2,y2))
        wall.setFill(wallColours[i])
        wall.draw(win)
        obstacles.append(wall)
    return obstacles

def drawBackdrop(win):
    backdrop = Rectangle(Point(0,0), \
    Point(win.getWidth(),win.getHeight()))
    backdrop.setFill("grey")
    backdrop.draw(win)

def drawScenery(win, bearingPoint):
    ringRadius = win.getWidth()/8
    redRing = Circle(bearingPoint,ringRadius)
    redRing.setFill("red")
    redRing.draw(win)
    yellowRing = Circle(bearingPoint,ringRadius * 2/3)
    yellowRing.setFill("yellow")
    yellowRing.draw(win)
    greenRing = Circle(bearingPoint,ringRadius/3)
    greenRing.setFill("green")
    greenRing.draw(win)
    catapult = Rectangle(bearingPoint, \
    Point(bearingPoint.getX() - 5, win.getHeight()))
    catapult.setFill("brown")
    catapult.draw(win)
    sky = Rectangle(Point(win.getWidth()/10,0), \
    Point(win.getWidth(),win.getHeight() + 10))
    sky.setFill("lightblue")
    sky.draw(win)

def simulateProjectile(win,start,arcStart,obstacles,targets, physicsConstants):
    timeMetric = 0.01
    gameSpeed,forceMetric,friction,elasticity,gravity = physicsConstants
    crosshair = Text(arcStart,"X")
    crosshair.setSize(10)
    crosshair.setTextColor("blue")
    crosshair.draw(win)
    x = start.getX()
    y = start.getY()
    Ux = (horizontalDistance(start, arcStart) * forceMetric * timeMetric)
    Uy = (verticalDistance(start, arcStart) * forceMetric * timeMetric)
    #If releaced above catapult, shoot downwards
    if arcStart.getY() < start.getY():
        Uy = Uy * -1
    t = 0
    canBreak = True
    stationary = False
    projectile = Circle(start, 5)
    projectile.setFill("blue")
    projectile.draw(win)
    while x < win.getWidth() and x > 0 and y < win.getHeight():
        newPoint = Point(x, y)
        Sx = Ux * t
        Sy = Uy * t + 0.5 * (-gravity * timeMetric) * t ** 2
        y = start.getY() - Sy
        x = start.getX() + Sx
        t = t + 1
        collided = checkForCollisions(x,y,obstacles,targets)
        if collided != None:
            impactCheck = checkCollision(newPoint.getX(),y,collided,obstacles,targets)
            if not impactCheck:
                Ux = Ux * elasticity * -1
            else:
                Ux = Ux * (1-friction)
            impactCheck = checkCollision(x,newPoint.getY(),collided,obstacles,targets)
            if not impactCheck:
                Uy =(Uy + (-gravity * timeMetric) * t) * elasticity * -1
            else:
                Uy =(Uy + (-gravity * timeMetric) * t) * (1-friction)
            if type(collided) == Circle:
                collided.undraw()
                targets.remove(collided)
            elif canBreak:
                collided.undraw()
                obstacles.remove(collided)
            if stationary:
                time.sleep(0.5)
                projectile.undraw()
                break
            if Ux**2 < 1 and Uy**2 < 1:
                stationary = True
            else:
                stationary = False
            t=1
            start = newPoint
            canBreak = False
        projectile.undraw()
        projectile = Circle(newPoint, 5)
        projectile.setFill("blue")
        projectile.draw(win)
        time.sleep(1/gameSpeed)
    projectile.undraw()

def checkForObstacleOverlap(obstacleDimensions,obstacles):
    newTop,newBottom,newLeft,newRight = obstacleDimensions
    for obstacle in obstacles:
        obTop,obBottom,obLeft,obRight = determineRectangleBounds(obstacle)
        if isBetween(newTop,obTop,obBottom) \
        or isBetween(newBottom,obTop,obBottom):
            if newLeft < obLeft and newRight > obRight:
                return True
        if isBetween(newLeft,obLeft,obRight) \
        or isBetween(newRight,obLeft,obRight):
            if newTop < obTop and newBottom > obBottom:
                return True
    return False

def isBetween(queryValue,bound1,bound2):
    if queryValue >= bound1 and queryValue <= bound2 \
    or queryValue >= bound2 and queryValue <= bound1:
        return True
    return False

def checkForCollisions(x,y,obstacles,targets):
    for i in range(len(targets)):
        if checkCollision(x,y,targets[i],obstacles,targets):
            return targets[i]
    for i in range(len(obstacles)-1,-1,-1):
        if checkCollision(x,y,obstacles[i],obstacles,targets):
            return obstacles[i]
    return None

def checkCollision(x,y,target,obstacles,targets):
    if type(target) == Circle:
            if distance(Point(x,y),target.getCenter()) <= target.getRadius():
                return True
    else:
            top,bottom,left,right = determineRectangleBounds(target)
            if x >= left and x <= right and y >= top and y <= bottom:
                return True
    return False

def determineRectangleBounds(rectangle):
    p1 = rectangle.getP1()
    p2 = rectangle.getP2()
    if p1.getX() < p2.getX():
        left = p1.getX()
        right = p2.getX()
    else:
        left = p2.getX()
        right = p1.getX()
    if p1.getY() < p2.getY():
        top = p1.getY()
        bottom = p2.getY()
    else:
        top = p2.getY()
        bottom = p1.getY()
    return top,bottom,left,right

def distance(p1, p2):
	return(math.sqrt(((p2.getX() - p1.getX()) ** 2) \
    + ((p2.getY() - p1.getY()) ** 2)))

def horizontalDistance(p1, p2):
	return abs(p2.getX() - p1.getX())

def verticalDistance(p1, p2):
	return abs((p2.getY() - p1.getY()))

def mouseOverrectangle(mousePosition,rectangle):
    top,bottom,left,right = determineRectangleBounds(rectangle)
    if mousePosition.getX() >= left \
    and mousePosition.getX() <= right \
    and mousePosition.getY() >= top \
    and mousePosition.getY() <= bottom:
        return True
    else:
        return False

main(1200,500)
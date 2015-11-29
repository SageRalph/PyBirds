import math
from graphics import *
import random

# Program entry point, opens window and displays options menu
def main(winLength,winheight):
    menuColumns = 4 # Max number of menu options listed on each row

    # Default value for each menu option
    defaults = ["3","10","10","50","10","0.15","0.5","9.8","10","30","50","300"]

    win = GraphWin("PyBirds", winLength, winheight)
    menuInputs = intialiseMenuInputs(defaults,menuColumns)
    while True:
        menuInputs = menu(win, menuInputs, menuColumns, defaults)


# Generates a list of interface components for modifying game settings using
# the default values provided
def intialiseMenuInputs(defaults,columns):
    menuInputs = []
    for i in range(len(defaults)):
        menuInputs.append(Entry(Point(i%columns*200+100,i//columns*80+80),10))
        menuInputs[i].setText(defaults[i])
    return menuInputs


# Draws the options menu
def menu(win, menuInputs, columns, defaults):
    drawBackdrop(win)
    playButton = drawButton(win,[0,20,0,80],"darkgreen","Play","gold")
    defaultsButton = drawButton(win,[0,20,80,160],"gold","Defaults","red")
    for item in menuInputs:
        item.draw(win)

    # List of the description text for each menu option
    strings = [\
    "Number of targets",\
    "Number of obstacles",\
    "Number of tries",\
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

    # Listen for click of play or defaults button
    clickPos=win.getMouse()
    while not mouseOverrectangle(clickPos,playButton):
        if mouseOverrectangle(clickPos,defaultsButton):
            # Redraw menu with default values
            for item in menuInputs:
                item.undraw()
            menuInputs = intialiseMenuInputs(defaults,columns)
            for item in menuInputs:
                item.draw(win)
        clickPos=win.getMouse()

    # => play button has been clicked

    # Validate menu option inputs, if any are invalid, returns defaults
    menuOptions = []
    for item in menuInputs:
        try:
            float(item.getText())   # Assumes all menu options are numeric
        except ValueError:
            for menuItem in menuInputs: # undraw menu
                menuItem.undraw()
            return menuInputs   # return default values

        # => value is valid
        menuOptions.append(eval(item.getText())) # Accept value
        item.undraw() # Remove option from menu

    play(win,menuOptions[0],menuOptions[1], \
    menuOptions[2],menuOptions[3:8],menuOptions[8:12])
    return menuInputs # Return new values


def drawMenuItemLabels(win,strings,columns):
    i=0
    while i < len(strings):
        Text(Point(i%columns*200+100,i//columns*80+50),strings[i]).draw(win)
        i += 1


# Run the game with the specified parameters
def play(win, targetNumber,obstacleNumber,triesLeft,physicsConstants,obstacleDimensionRanges):
    bearingPoint = Point(win.getWidth()/10, win.getHeight() * 4/5) # Top of catapult

    # Draw constants and UI
    drawBackdrop(win)
    drawScenery(win, bearingPoint)
    menuButton = drawButton(win,[0,20,0,80],"red","Menu","gold")
    triesLeftDisplay = Text(Point(100,10),triesLeft)
    triesLeftDisplay.draw(win)

    # Generate level
    obstacles = genRandomObstacles(win,obstacleNumber,obstacleDimensionRanges)
    if obstacles == []:
        displayObjectPlacementError(win)
        return
    targets = genRandomTargets(win,targetNumber,obstacles)
    if targets == []:
        displayObjectPlacementError(win)
        return

    # Testing - uncomment below for hard-coded level layout
    #obstacles = setObstacles(win)
    #targets = setTargets(win)

    # Listen for user interaction
    while triesLeft > 0 and len(targets) > 0:

        # Check for non game related clicking
        clickPos = Point(1000,0) #Invalid data for while
        while clickPos.getX() > win.getWidth()/10: # Out of bounds (right of catapult)
            clickPos = win.getMouse()
        if mouseOverrectangle(clickPos,menuButton):
            return # End game and return to menu

        # => valid position to fire from

        # Update tries left
        triesLeft = triesLeft - 1
        triesLeftDisplay.setText(triesLeft)

        # Run simulation
        simulateProjectile(win,bearingPoint,clickPos,obstacles,targets, physicsConstants)

    # => game finished (either no tries or targets remaining)
    displayEndGame(win, len(targets))
    win.getMouse()
    return


# Warns user of timeout when generating objects
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


# Draws a button with a solid fill colour
def drawButton(win,bounds,fillColour,text,textColour):
    top,bottom,left,right = bounds
    button = Rectangle(Point(left,top), Point(right,bottom))
    button.setFill(fillColour)
    button.draw(win)
    buttonText = Text(Point((left+right)/2,(top+bottom)/2),text)
    buttonText.setTextColor(textColour)
    buttonText.draw(win)
    return button


# Provides feedback to the user upon game completion
def displayEndGame(win, targetsleft):
    center = Point(win.getWidth() / 2, win.getHeight() / 2)
    endgameBackdrop = Rectangle (Point(center.getX()-130, center.getY()-40), \
    Point(center.getX()+130,center.getY()+40))
    endgameText = Text(center, "")
    endgameText.setSize(30)
    if targetsleft == 0:
        # If player wins
        endgameBackdrop.setFill("yellow")
        endgameText.setText("You win")
        endgameText.setFill("darkgreen")
    else:
        # If player looses
        endgameBackdrop.setFill("orange")
        endgameText.setText("Out of tries")
        endgameText.setFill("red")
    endgameBackdrop.draw(win)
    endgameText.draw(win)


def addTarget(win,targets,x,y,size):
    target = Circle(Point(x,y),size)
    target.setFill("green")
    target.draw(win)
    targets.append(target)
    return targets


# Testing - Returns a list of hard-coded targets
def setTargets(win):
    targets = []
    #declare targets here
    targets = addTarget(win,targets,600,450,30)
    targets = addTarget(win,targets,800,200,30)
    return targets


# Testing - Returns a list of hard-coded obstacles
def setObstacles(win):
    obstacles = []
    #declare obstacles here
    obstacles = addGradedWall(win,obstacles,[700,500,750,400],1)
    obstacles = addGradedWall(win,obstacles,[500,500,550,400],2)
    obstacles = addGradedWall(win,obstacles,[500,400,750,350],3)
    return obstacles


# Procedurally generates a list of non-overlapping targets
def genRandomTargets(win,targetNumber,obstacles):
    targets = []
    startTime = time.clock() # For timeout
    for i in range(targetNumber):
        # Prevent overlap
        collided = True # Ensure run once
        while collided == True:
            # Generate random size and position
            size = random.randint(20,40)
            x = random.randint(win.getWidth()//5 + size,win.getWidth() - size)
            y = random.randint(size, win.getHeight()-size)

            # Calculate bounding box
            top = y - size
            bottom = y + size
            left = x - size
            right = x + size
            obstacleDimensions = top,bottom,left,right

            #  Test for overlap
            if circleOverlapsObstacle(Point(x,y),size,obstacles) \
            or circleOverlapsTarget(Point(x,y),size,targets) \
            or checkForObstacleOverlap(obstacleDimensions,obstacles):
                collided = True
                if time.clock() - startTime >= 30: #timeout
                    return []
            else:
                collided = False

        # => Successfully generated valid target parameters
        targets = addTarget(win,targets,x,y,size)

    # => Generated desired number of targets successfully
    return targets


# Procedurally generates a list of non-overlapping obstacles
def genRandomObstacles(win,obstacleNumber,obstacleDimensionRanges):
    obstacles = []
    startTime = time.clock() # For timeout
    for i in range(obstacleNumber):
        collided = True # Ensure run once
        while collided == True:
            # Randomly pick rotation
            longSide = random.randint(0,1)

            # Generate random dimensions
            obstacleDimensions = \
            genTallOrWideRectangle(win,obstacleDimensionRanges,longSide)

            # Test for overlap
            if rectanglePointsInsideObstacle(obstacleDimensions,obstacles) \
            or checkForObstacleOverlap(obstacleDimensions,obstacles):
                collided = True
                if time.clock() - startTime >= 30: #timeout
                    return []
            else:
                collided = False

        # => Successfully generated valid obstacle position & dimensions
        grade = random.randint(1,3) # Randomly pick obstacle strength
        obstacles = addGradedWall(win,obstacles,obstacleDimensions,grade)

    # => Generated desired number of obstacles successfully
    return obstacles


# Generates a rectangle with random dimensions (within obstacleDimensionRanges)
def genTallOrWideRectangle(win,obstacleDimensionRanges,longSide):
    shortMin,shortMax,longMin,longMax = obstacleDimensionRanges

    # Generate random side lengths
    long = random.randint(longMin,longMax)
    short = random.randint(shortMin,shortMax)

    # Assign long-side & calculate rectangle edges
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


# Checks is the bounding points of a rectangle overlap any of a list
# of other rectangles
def rectanglePointsInsideObstacle(obstacleDimensions,obstacles):
    top,bottom,left,right = obstacleDimensions
    if checkForCollisions(left,top,obstacles,[]) != None \
    or checkForCollisions(left,bottom,obstacles,[]) != None \
    or checkForCollisions(right,top,obstacles,[]) != None \
    or checkForCollisions(right,bottom,obstacles,[]):
        return True
    return False


# Checks if a circle overlaps any of a list of rectangles
def circleOverlapsObstacle(center, radius, obstacles):
    for obstacle in obstacles:
        top,bottom,left,right = determineRectangleBounds(obstacle)
        if isBetween(center.getX(), left-radius,right+radius)\
        and isBetween(center.getY(), top-radius, bottom+radius):
            return True
    return False


# Checks if a circle overlaps any of a list of other circles
def circleOverlapsTarget(center, radius, targets):
    for target in targets:
        if distance(center, target.getCenter()) <= radius + target.getRadius():
            return True
    return False


# Draws an obstacle, colour coded based on strength
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
    # Draw power rings
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

    # Draw catapult
    catapult = Rectangle(bearingPoint, \
    Point(bearingPoint.getX() - 5, win.getHeight()))
    catapult.setFill("brown")
    catapult.draw(win)

    # Draw the sky
    sky = Rectangle(Point(win.getWidth()/10,0), \
    Point(win.getWidth(),win.getHeight() + 10))
    sky.setFill("lightblue")
    sky.draw(win)


# Simulates projectile motion based on the given parameters
def simulateProjectile(win,start,arcStart,obstacles,targets, physicsConstants):
    # Load constants
    timeMetric = 0.01 # Hidden constant for calibrating simulation speed
    gameSpeed,forceMetric,friction,elasticity,gravity = physicsConstants

    # Draw cross-hair
    crosshair = Text(arcStart,"X")
    crosshair.setSize(10)
    crosshair.setTextColor("blue")
    crosshair.draw(win)

    # Start position
    x = start.getX()
    y = start.getY()

    # Start velocity
    Ux = (horizontalDistance(start, arcStart) * forceMetric * timeMetric)
    Uy = (verticalDistance(start, arcStart) * forceMetric * timeMetric)
    #If released above catapult, shoot downwards
    if arcStart.getY() < start.getY():
        Uy = Uy * -1

    t = 0 # Start time
    canBreak = True # Determines projectiles ability to damage/destroy obstacles
    stationary = False # Ensure run once
    projectile = drawProjectile(win, start) # Draw projectile

    while x < win.getWidth() and x > 0 and y < win.getHeight(): # Test out of bounds
        newPoint = Point(x, y)

        # Run SUVAT
        Sx = Ux * t
        Sy = Uy * t + 0.5 * (-gravity * timeMetric) * t ** 2
        y = start.getY() - Sy
        x = start.getX() + Sx
        t = t + 1

        collided = checkForCollisions(x,y,obstacles,targets)
        if collided != None:
            # Determine nature of collision

            # Impacted from the side
            impactCheck = checkCollision(newPoint.getX(),y,collided)
            if not impactCheck:
                Ux = Ux * elasticity * -1   # Bounce
            else:
                Ux = Ux * (1-friction)      # Apply friction

            # Impacted from above/below
            impactCheck = checkCollision(x,newPoint.getY(),collided)
            if not impactCheck:
                Uy =(Uy + (-gravity * timeMetric) * t) * elasticity * -1 # Bounce
            else:
                Uy =(Uy + (-gravity * timeMetric) * t) * (1-friction)    # Apply friction

            # Interact with object hit
            if type(collided) == Circle: # If target then destroy
                collided.undraw()
                targets.remove(collided)
            elif canBreak:           # Otherwise try to damage obstacle
                collided.undraw()
                obstacles.remove(collided)

            # End simulation if no movement
            if stationary:
                time.sleep(0.5) # Prevent instant disappearance
                projectile.undraw()
                break
            if Ux**2 < 1 and Uy**2 < 1: # Ensures reasonable tolerance of minor movement
                stationary = True
            else:
                stationary = False

            # Prepare for new arc
            t=1
            start = newPoint
            canBreak = False # Can only break on first collision

        # => movement step complete
        projectile.undraw()
        projectile = drawProjectile(win, newPoint)

        time.sleep(1/gameSpeed) # Wait before next step

    # => Projectile out of bounds (off-screen)
    projectile.undraw()


# Draws a projectile at position or otherwise a position indicator if out of bounds
def drawProjectile(win, position):
    
    # If projectile is above top of window, display indicator instead
    if position.getY() < 0: 
        bottom = Point(position.getX(),10)
        top = Point(position.getX(),2)
        projectile = Line(bottom,top)
        projectile.setArrow('last')
    else:
        projectile = Circle(position, 5)
        
    projectile.setFill("blue")
    projectile.draw(win)
    return projectile
        

# Checks if one obstacle would overlap any other
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


# Determines if a value is within a range
def isBetween(queryValue,bound1,bound2):
    if queryValue >= bound1 and queryValue <= bound2 \
    or queryValue >= bound2 and queryValue <= bound1:
        return True
    return False


# Checks if a point collides with any obstacle or target
def checkForCollisions(x,y,obstacles,targets):
    for i in range(len(targets)):
        if checkCollision(x,y,targets[i]):
            return targets[i]
    for i in range(len(obstacles)-1,-1,-1):
        if checkCollision(x,y,obstacles[i]):
            return obstacles[i]
    return None


# Checks if a point collides with a shape (circle or rectangle)
def checkCollision(x,y,target):
    if type(target) == Circle:
        # Point in circle
        if distance(Point(x,y),target.getCenter()) <= target.getRadius():
            return True
    else:
        # Point in rectangle
        top,bottom,left,right = determineRectangleBounds(target)
        if x >= left and x <= right and y >= top and y <= bottom:
            return True
    return False


# Calculates the bounds of a rectangle
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


# Calculates the distance between two points
def distance(p1, p2):
    # Pythagoras theorem
	return(math.sqrt(((p2.getX() - p1.getX()) ** 2) \
    + ((p2.getY() - p1.getY()) ** 2)))


# Calculates the absolute horizontal distance between two points
def horizontalDistance(p1, p2):
	return abs(p2.getX() - p1.getX())


# Calculates the absolute vertical distance between two points
def verticalDistance(p1, p2):
	return abs((p2.getY() - p1.getY()))


# Determines whether a point is inside a rectangle
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
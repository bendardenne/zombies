var maxTilesPerLine = 22;

var tiles = new buckets.Dictionary();
var debugMode = false;

var EMPTY = 0,
	NECROMANCER = 1,
	HUGGER = 2,
	JUMPER = 3,
	SNEAKY = 4,
	SPRINTER = 5,
	PLAYER1 = 0,
	PLAYER2 = 1;

var initialPieceQuantities = [1, 2, 3, 2, 3];

var strokeColors = ['black', 'black'],
	fillColors = ['rgb(255,178,178)', 'rgb(178,178,255)'],
	sweetOrange = 'rgb(240,181,52)',
	tileImages = [['empty_tile', 'necromancer_tile_p1', 'hugger_tile_p1', 'jumper_tile_p1', 'creeper_tile_p1', 'sprinter_tile_p1'],
		['empty_tile', 'necromancer_tile_p1', 'hugger_tile_p1', 'jumper_tile_p1', 'creeper_tile_p1', 'sprinter_tile_p1']],
	pauseImage = 'pause',
	playImage = 'play',
	previousImage = 'previous',
	nextImage = 'next',
	okImage = 'ok',
	pauseDisabledImage = 'pause_disabled',
	playDisabledImage = 'play_disabled',
	previousDisabledImage = 'previous_disabled',
	helpOnImage = 'help_on',
	helpOffImage = 'help_off',
	nextDisabledImage = 'next_disabled',
	playPauseColor = 'rgb(229,28,35)',
	prevNextColor = 'rgb(139,195,74)',
	playPauseDisabledColor = 'rgb(114,14,17)',
	prevNextDisabledColor = 'rgb(69,97,37)',
	startImage = 'start',
	normalStrokeWidth = 2,
	stackStrokeWidth = 7,
	selectedStrokeWidth = 5,
	possibleStrokeWidth = 5,
	selectedStrokeColor = prevNextColor,
	possibleStrokeColor = sweetOrange;

var descriptionTitles = ['The Necromancer', 'The Hugger', 'The Jumper', 'The Creeper', 'The Sprinter'],
	descriptionTexts = ["The necromancer is the main piece of the game.\nThe necromancer has revived your zombies and command them.\nIf your necromancer is surrounded by zombies, you loose the game.",
		"The hugger is a very weak zombie.\nIt is rather stupid but immobilizes its enemies by hugging them.\nOnce a hugger is hugging you, you cannot move until he lets go.",
		"The jumper is a zombie which is always crouching except when he jumps.\nThe jumper surprises his enemies by jumping above them to attack them from behind.",
		"The creeper is a mysterious zombie rarely seen in plain light.\nThe creeper hides in shadows and waits the right time to attack his enemies.\nMany victims from the creeper didn't see their end coming.",
		"The sprinter is a very fast and athletic zombie.\nThe sprinter uses his over-developed legs to catch up his fleeing prey.\nThe only chance to survive when you see the sprinter is to stay hidden."],
	moveTexts = ["The necromancer can move to adjacent tiles if they are empty.\nThe Freedom to Move rule applies to necromancer moves.\nIf your necromancer is surrounded by six non-empty pieces, you loose the game.",
		"The hugger can move to adjacent tiles and can be placed on top of another piece.\nA piece with a hugger on top cannot move.\nThe Freedom to Move rule does not apply to the hugger.",
		"The jumper moves by only performing jumps over other tiles.\nThe jumper moves from its position to the next unoccupied tile\nalong a straight line of joined non-empty tiles.\nThe Freedom to Move rule does not apply to the jumper.",
		"The creeper moves exactly three tiles per turn.\nThe creeper must move in a direct path and cannot backtrack on itself.\nEvery step in his move must respect the Freedom to Move rule.",
		"The sprinter moves from its position to any other empty position.\nThe Freedom to Move rule applies to sprinter moves."];

var canvasWidth = view.viewSize._width,
	canvasHeight = view.viewSize._height,
	hudWidth = canvasWidth / 5,
	hudHeight = canvasHeight,
	boardWidth = canvasWidth - hudWidth,
	boardHeight = canvasHeight,
	boardCenterX = hudWidth + boardWidth / 2,
	boardCenterY = boardHeight / 2,
	xOffset = boardCenterX,
	yOffset = boardCenterY;

/* The configuration of the board */
var configuration = '',
	playModeOn = true,
	step = 0,
	playPauseActive = true,
	nextActive = true,
	previousActive = true; //boolean that is true if the button play is clicked, false otherwise. 

/*********************************************************
******************* Setting up the HUD *******************
*********************************************************/

var tileRadius = Math.floor(canvasHeight / maxTilesPerLine),
	tileWidth = tileRadius * Math.sqrt(3),
	tileHeight = tileRadius * 2;

var borderSize = 10;

var unplacedTiles = [[],[]];

var unplacedTileX = [hudWidth / 4, hudWidth / 2, 3 * hudWidth / 4, hudWidth / 3, 2 * hudWidth / 3],
	unplacedTileY = [hudHeight / 9, hudHeight / 9, hudHeight / 9, 17 * hudHeight / 72, 17 * hudHeight / 72],
	stackedTileX = [canvasWidth - borderSize - 32 * tileWidth / 6,
		canvasWidth - borderSize - 25 * tileWidth / 6,
		canvasWidth - borderSize - 18 * tileWidth / 6,
		canvasWidth - borderSize - 11 * tileWidth / 6,
		canvasWidth - borderSize - 4 * tileWidth / 6],
	stackedTileY = tileHeight + hudHeight / 42,
	cardYOffsets = [0, hudHeight / 3];

var buttonRadius = Math.min(hudWidth / 10, hudHeight / 24),
	buttonSpacing = buttonRadius * 7 / 4,
	arrowSize = buttonRadius / 2,
	buttonCenterX = hudWidth / 2,
	buttonCenterY = hudHeight - borderSize - 3 * buttonRadius / 2;

function UnplacedTile(pieceType, player, quantity) {
	this.pixCoords = [unplacedTileX[pieceType - 1], cardYOffsets[player] + unplacedTileY[pieceType - 1]];
	this.pieceType = pieceType;
	this.quantity = quantity;
	this.player = player;
	this.hexagon = new Path.RegularPolygon(
		new Point(this.pixCoords[0], this.pixCoords[1]),
		6, tileRadius - 2);
	this.hexagon.strokeWidth = normalStrokeWidth;
	this.hexagon.fillColor = fillColors[player];
  this.hexagon.strokeColor = strokeColors[player];
	this.text = new PointText({
		point: new Point(this.pixCoords[0], this.pixCoords[1] + tileRadius + hudHeight / 60),
		justification: 'center',
		fontFamily: 'Roboto, sans-serif',
		fontSize: hudHeight / 70,
		fillColor: 'black',
		content: this.quantity
	});
	this.raster = new Raster(tileImages[this.player][this.pieceType]);
	this.raster.scale(getScaleFactor(this.raster.width, this.raster.height,  tileWidth, tileWidth));
	this.raster.position = new Point(this.pixCoords[0], this.pixCoords[1]);
	this.tileGroup = new Group();
	this.tileGroup.addChild(this.hexagon);
	this.tileGroup.addChild(this.raster);
}

UnplacedTile.prototype.updateColor = function() {
  this.hexagon.strokeColor = strokeColors[this.player];
  this.hexagon.strokeWidth = normalStrokeWidth;
};

function StackedTile(pieceType, player, depth) {
	this.pixCoords = [stackedTileX[depth], stackedTileY];
	this.pieceType = pieceType;
	this.depth = depth;
	this.player = player;
	this.hexagon = new Path.RegularPolygon(
		new Point(this.pixCoords[0], this.pixCoords[1]),
		6, tileRadius - 2);
	this.hexagon.strokeWidth = normalStrokeWidth;
	this.hexagon.fillColor = fillColors[player];
  this.hexagon.strokeColor = strokeColors[player];
	this.text = new PointText({
		point: new Point(this.pixCoords[0], this.pixCoords[1] + tileRadius + hudHeight / 60),
		justification: 'center',
		fontSize: hudHeight / 70,
		fillColor: 'black',
		content: 'level ' + this.depth
	});
	this.raster = new Raster(tileImages[this.player][this.pieceType]);
	this.raster.scale(getScaleFactor(this.raster.width, this.raster.height,  tileWidth, tileWidth));
	this.raster.position = new Point(this.pixCoords[0], this.pixCoords[1]);
	this.tileGroup = new Group();
	this.tileGroup.addChild(this.hexagon);
	this.tileGroup.addChild(this.raster);
	this.tileGroup.addChild(this.text);
}

StackedTile.prototype.updateColor = function() {
	this.hexagon.fillColor = fillColors[this.player];
  this.hexagon.strokeColor = strokeColors[this.player];
  this.raster.source = tileImages[this.player][this.pieceType];
};

function Button(centerX, centerY, radius, bgColor, image) {
	this.bgbg = new Path.Circle(new Point(centerX, centerY), radius + 1);
	this.bgbg.fillColor = 'rgb(170,170,170)';
	this.bg = new Path.Circle(new Point(centerX, centerY), radius);
	this.bg.fillColor = bgColor;
	this.raster = new Raster(image);
	this.raster.scale(getScaleFactor(this.raster.width, this.raster.height,  5 * radius / 3, 5 * radius / 3));
	this.raster.position = new Point(centerX, centerY);
	this.buttonGroup = new Group();
	this.buttonGroup.addChild(this.bgbg);
	this.buttonGroup.addChild(this.bg);
	this.buttonGroup.addChild(this.raster);
	this.buttonGroup.visible = false;
}

function Card(x1, y1, x2, y2, shadowSizeX, shadowSizeY, title) {
	this.shadowSizeX = shadowSizeX;
	this.shadowSizeY = shadowSizeY;
	this.cornerSize = new Size(1, 1);
	this.bg = new Rectangle(new Point(x1 - shadowSizeX, y1), new Point(x2 + shadowSizeX, y2 + shadowSizeY));
	this.bgRounded = new Shape.Rectangle(this.bg, this.cornerSize);
	this.bgRounded.fillColor = 'rgb(170,170,170)';

	this.fg = new Rectangle(new Point(x1, y1), new Point(x2, y2));
	this.fgRounded = new Shape.Rectangle(this.fg, this.cornerSize);
	this.fgRounded.fillColor = 'white';

	this.banner = new Rectangle(new Point(x1, y1), new Point(x2, y1 + hudHeight / 30));
	this.bannerRounded = new Shape.Rectangle(this.banner, this.cornerSize);
	this.bannerRounded.fillColor = sweetOrange;

	this.text = new PointText({
		point: new Point(x1 + (x2 - x1) / 2, y1 + hudHeight / 42),
		justification: 'center',
		fontSize: hudHeight / 60,
		fillColor: 'black',
		content: title,
		fontFamily: 'Roboto, sans-serif',
		fontWeight: 200,
		lineHeight:1.2
	});

	this.cardGroup = new Group();
	this.cardGroup.addChild(this.bgRounded);
	this.cardGroup.addChild(this.fgRounded);
	this.cardGroup.addChild(this.bannerRounded);
	this.cardGroup.addChild(this.text);
	this.cardGroup.visible = false;
}

function Tile(q, r) {
	this.q = q;
	this.r = r;
	this.pixCoords = hexToPixCoord(this.q, this.r);
	this.pieceType = [[PLAYER1, EMPTY]];
	this.hexagon = new Path.RegularPolygon(
		new Point(this.pixCoords[0], this.pixCoords[1]),
		6, tileRadius - 2);
	this.hexagon.strokeWidth = normalStrokeWidth;
	if (debugMode) {
		this.text = new PointText({
			point: new Point(this.pixCoords[0], this.pixCoords[1]),
			justification: 'center',
			fontSize: 14,
			fontFamily: 'Roboto, sans-serif',
			fillColor: 'black',
			content: this.q + ", " + this.r
		});
	}
	this.raster = new Raster(tileImages[this.pieceType[this.pieceType.length - 1][0]][this.pieceType[this.pieceType.length - 1][1]]);
	this.raster.scale(getScaleFactor(this.raster.width, this.raster.height,  (2 * tileRadius) - 10, (2 * tileRadius) - 10));
	this.raster.position = new Point(this.pixCoords[0], this.pixCoords[1]);
	this.tileGroup = new Group();
	this.tileGroup.addChild(this.hexagon);
	if (debugMode) {
		this.tileGroup.addChild(this.text);
	}
	this.tileGroup.addChild(this.raster);
}

Tile.prototype.updateColor = function() {
	if (this.pieceType[this.pieceType.length - 1][1] == EMPTY){
		this.hexagon.fillColor = 'white';
	  this.hexagon.strokeColor = [PLAYER1][EMPTY];
	  this.raster.source = tileImages[PLAYER1][EMPTY];
	  this.hexagon.strokeWidth = normalStrokeWidth;
	}
	else {
		this.hexagon.fillColor = fillColors[this.pieceType[this.pieceType.length - 1][0]];
	  this.hexagon.strokeColor = strokeColors[this.pieceType[this.pieceType.length - 1][0]];
	  this.raster.source = tileImages[this.pieceType[this.pieceType.length - 1][0]][this.pieceType[this.pieceType.length - 1][1]];
	  if (this.pieceType.length > 1) {
	  	this.hexagon.strokeWidth = stackStrokeWidth;
	  }
	  else {
	  	this.hexagon.strokeWidth = normalStrokeWidth;
	  }
	}
};

Tile.prototype.updatePosition = function() {
	this.pixCoords = hexToPixCoord(this.q, this.r);
	var newPosition = new Point(this.pixCoords[0], this.pixCoords[1]);
	this.tileGroup.position = newPosition;
};

function getScaleFactor(imgWidth, imgHeight, desiredWidth, desiredHeight) {
	var imgWidthScale = desiredWidth / imgWidth,
		imgHeightScale = desiredHeight / imgHeight;
	return Math.min(imgWidthScale, imgHeightScale);
}

function getHexScaleFactor(imgWidth, imgHeight) {
	return getScaleFactor(imgWidth, imgHeight, Math.sqrt(3) * (tileRadius - 3), 2 * (tileRadius - 3));
}

function coordToKey(q, r) {
	return q + " " + r;
}

function addTile(q, r, pieceType) {
	var newTile = new Tile(q, r);
	tiles.set(coordToKey(q, r), newTile);
	newTile.pieceType = [pieceType];
	newTile.updateColor();
	newTile.tileGroup.onClick = function(event) {
		tileClicked(q, r);
	};
	newTile.tileGroup.onMouseEnter = function(event) {
		tileMouseEnter(q, r);
	};
	newTile.tileGroup.onMouseLeave = function(event) {
		tileMouseLeave(q, r);
	};
}

function centerBoard() {
	var minX = 4200,
		minY = 4200,
		maxX = -4200,
		maxY = -4200;
	var keys = tiles.keys();
  for(var i = 0; i < keys.length; i++) {
  	minX = Math.min(minX, tiles.get(keys[i]).pixCoords[0]);
  	minY = Math.min(minY, tiles.get(keys[i]).pixCoords[1]);
  	maxX = Math.max(maxX, tiles.get(keys[i]).pixCoords[0]);
  	maxY = Math.max(maxY, tiles.get(keys[i]).pixCoords[1]);
  }
  xOffset += boardCenterX - ((maxX + minX) / 2);
  yOffset += boardCenterY - ((maxY + minY) / 2);

  for(var i = 0; i < keys.length; i++) {
  	tiles.get(keys[i]).updatePosition()
  }
}

// Converts hex axial coordinates with pointy top into pixel coordinates
function hexToPixCoord(q, r) {
	var x = xOffset + (tileRadius * Math.sqrt(3) * (q + (r / 2))),
		y = yOffset + (tileRadius * (3 / 2) * r);
	return [x, y];
}

// Converts pixel coordinates into hex axial coordinates with pointy top
function pixToHexCoord(x, y) {
	var truncatedQ = ((1 / 3) * Math.sqrt(3) * (x - xOffset) - (1 / 3) * (y - yOffset)) / tileRadius,
		truncatedR = (2 / 3) * (y - yOffset) / tileRadius;

	var truncatedCubeCoord = axialToCube(truncatedQ, truncatedR);

	var correctCubeCoord = hexRound(truncatedCubeCoord[0], truncatedCubeCoord[1], truncatedCubeCoord[2]);

	var correctCoord = cubeToAxial(correctCubeCoord[0], correctCubeCoord[1], correctCubeCoord[2]);

	return [correctCoord[0], correctCoord[1]];
}

// Converts hex axial coordinates with pointy top to hex cube coordinates with pointy top
function axialToCube(q, r) {
	var x = q,
		z = r,
		y = -x - z;
	return [x, y, z];
}

// Converts hex cube coordinates with pointy top to hex axial coordinates with pointy top
function cubeToAxial(x, y, z) {
	var q = x,
		r = z;
	return [q, r];
}

// Rounding x, y, z (double) to the nearest x, y, z integer cube coordinate
function hexRound(x, y, z) {
  var rx = Math.round(x),
  	ry = Math.round(y),
  	rz = Math.round(z);

  if (rx + ry + rz != 0) {
  	var x_diff = Math.abs(rx - x),
  	y_diff = Math.abs(ry - y),
  	z_diff = Math.abs(rz - z);

	  if (x_diff > y_diff && x_diff > z_diff)
	  {
	    rx = -ry - rz;
	  }
	  else if (y_diff > z_diff) {
	    ry = -rx - rz;
	  }
	  else {
	    rz = -rx - ry;
    }
  }
  return [rx, ry, rz];  
}

function getTileNeighbourCoordinates(q, r) {
	var tileNeighbours = [[1,  0], [1, -1], [ 0, -1], [-1,  0], [-1, 1], [ 0, 1]];
	return tileNeighbours.map(function(pair) { return [q + pair[0], r + pair[1]]; });
}

// Returns true if the piece in (q, r) has no non-empty neighbour
function isIsolated(q, r) {
	var tileNeighbours = getTileNeighbourCoordinates(q, r);
	return tileNeighbours.every(function(item){
		return !tiles.containsKey(coordToKey(item[0], item[1])) || tiles.get(coordToKey(item[0], item[1])).pieceType[0][1] == EMPTY;
	});
}

/******************************************************************************
************************* Creating Graphical Elements *************************
******************************************************************************/
var possiblePlacements = new buckets.Dictionary(),
	possibleMoves = new buckets.Dictionary(),
	currentPlayer = PLAYER1,
	selectedTile = '',
	unplacedTileIds = new buckets.Dictionary(),
	tileStack = [];

var startButtonRadius = Math.min(canvasWidth / 10, canvasHeight / 10),
	startButtonX = view.center.x,
	startButtonY = view.center.y,
	startButtonColor = sweetOrange;

var startButton = new Button(startButtonX, startButtonY, startButtonRadius, sweetOrange, startImage);
startButton.buttonGroup.visible = true;
startButton.buttonGroup.on('click', initializeBoard);

var helpOn = true;

var player1PiecesCard = new Card(borderSize, borderSize, hudWidth - borderSize, hudHeight / 3 - borderSize, 1, 2, "Player 1 Pieces"),
	player2PiecesCard = new Card(borderSize, borderSize + hudHeight / 3, hudWidth - borderSize, 2 * hudHeight / 3 - borderSize, 1, 2, "Player 2 Pieces"),
	hudCard = new Card(borderSize, borderSize + 2 * hudHeight / 3, hudWidth - borderSize, hudHeight - borderSize, 1, 2, "HUD"),
	stackCard = new Card(canvasWidth - borderSize - 6 * tileWidth, borderSize, canvasWidth - borderSize, borderSize + 2 * tileHeight, 1, 2, "Tile Stack"),
	skipCard = new Card(hudWidth + borderSize, borderSize, hudWidth + borderSize + 6 * tileWidth, borderSize + 2 * tileHeight, 1, 2, "No Action Possible"),
	descriptionCard = new Card(hudWidth + borderSize, borderSize, hudWidth + borderSize + 8 * tileWidth, borderSize + (5 / 2) * tileHeight, 1, 2, "Description"),
	playPauseButton = new Button(buttonCenterX, buttonCenterY, buttonRadius, playPauseColor, pauseImage),
	previousButton = new Button(buttonCenterX - (buttonRadius + buttonSpacing), buttonCenterY, buttonRadius, prevNextColor, previousImage),
	nextButton = new Button(buttonCenterX + (buttonRadius + buttonSpacing), buttonCenterY, buttonRadius, prevNextColor, nextImage);
	okButton = new Button(hudWidth + borderSize + 3 * tileWidth, borderSize + (7 / 5) * tileHeight, buttonRadius, sweetOrange, okImage);

	playPauseButton.buttonGroup.on('click', playPauseClicked);
	nextButton.buttonGroup.on('click', nextClicked);
	previousButton.buttonGroup.on('click', previousClicked);
	okButton.buttonGroup.on('click', skipPerformed);

var helpLine = new PointText({
	point: new Point(hudWidth / 8, 2 * hudHeight / 3 + 5 * hudHeight / 60),
	justification: 'left',
	fontSize: hudHeight / 70,
	fillColor: 'black',
	content: 'Help',
	fontFamily: 'Roboto, sans-serif',
	fontWeight: 200,
	lineHeight: 1.2,
	visible: false
});

var helpRaster = new Raster(helpOnImage);
	helpRaster.scale(getScaleFactor(helpRaster.width, helpRaster.height, hudHeight / 32, hudHeight / 32));
	helpRaster.position = new Point(2 * hudWidth / 8 + hudHeight / 120, (2 * hudHeight / 3) + (5  * hudHeight / 60) - (hudHeight / 160));
	helpRaster.on('click', helpSwitchClicked);
	helpRaster.visible = false;

var statusLine1 = new PointText({
	point: new Point(hudWidth / 8, 2 * hudHeight / 3 + 4 * hudHeight / 30),
	justification: 'left',
	fontSize: hudHeight / 70,
	fillColor: 'black',
	content: '',
	fontFamily: 'Roboto, sans-serif',
	fontWeight: 200,
	lineHeight: 1.2,
	visible: false
});

var statusLine2 = new PointText({
	point: new Point(hudWidth / 8, 2 * hudHeight / 3 + 5 * hudHeight / 30),
	justification: 'left',
	fontSize: hudHeight / 70,
	fillColor: 'black',
	content: '',
	fontFamily: 'Roboto, sans-serif',
	fontWeight: 200,
	lineHeight:1.2,
	visible: false
});

var skipLine = new PointText({
	point: new Point(hudWidth + borderSize + 3 * tileWidth, borderSize + (2 / 3) * tileHeight),
	justification: 'center',
	fontSize: hudHeight / 70,
	fillColor: 'black',
	content: 'You have to skip your turn.',
	fontFamily: 'Roboto, sans-serif',
	fontWeight: 200,
	lineHeight: 1.2,
	visible: false
});

var descriptionLine = new PointText({
	point: new Point(hudWidth + borderSize + (1 / 4) * tileWidth, borderSize + (2 / 3) * tileHeight),
	justification: 'left',
	fontSize: hudHeight / 70,
	fillColor: 'black',
	content: '',
	fontFamily: 'Roboto, sans-serif',
	fontWeight: 200,
	lineHeight: 1.2,
	visible: false
});

function initializeBoard() {
	startButton.buttonGroup.remove();

	player1PiecesCard.cardGroup.visible = true;
	player2PiecesCard.cardGroup.visible = true;
	hudCard.cardGroup.visible = true;
	stackCard.cardGroup.visible = false;
	statusLine1.visible = true;
	statusLine2.visible = true;
	statusLine1.content = 'Step 1: ' + "Player 1's turn";
	statusLine2.content = '';
	helpLine.visible = true;
	helpRaster.visible = true;

	for(var piece = NECROMANCER; piece <= SPRINTER; piece++) {
		var tile0 = new UnplacedTile(piece, PLAYER1, initialPieceQuantities[piece - 1]),
			tile1 = new UnplacedTile(piece, PLAYER2, initialPieceQuantities[piece - 1]);
		unplacedTileIds.set(tile0.id)
		unplacedTiles[0][piece - 1] = tile0;
		unplacedTiles[1][piece - 1] = tile1;
		unplacedTiles[0][piece - 1].tileGroup.onClick = function(event) {
			for (var j = 0; j < unplacedTiles[0].length; j++) {
				if (this == unplacedTiles[0][j].tileGroup) {
					unplacedTileClicked(0, j + 1)
				}
			} 
		}
		unplacedTiles[0][piece - 1].tileGroup.onMouseEnter = function(event) {
			for (var j = 0; j < unplacedTiles[0].length; j++) {
				if (this == unplacedTiles[0][j].tileGroup) {
					unplacedtileMouseEnter(0, j + 1)
				}
			} 
		}
		unplacedTiles[0][piece - 1].tileGroup.onMouseLeave = function(event) {
			for (var j = 0; j < unplacedTiles[0].length; j++) {
				if (this == unplacedTiles[0][j].tileGroup) {
					unplacedtileMouseLeave(0, j + 1)
				}
			} 
		}
		unplacedTiles[1][piece - 1].tileGroup.onClick = function(event) {
			for (var j = 0; j < unplacedTiles[1].length; j++) {
				if (this == unplacedTiles[1][j].tileGroup) {
					unplacedTileClicked(1, j + 1)
				}
			} 
		}
		unplacedTiles[1][piece - 1].tileGroup.onMouseEnter = function(event) {
			for (var j = 0; j < unplacedTiles[0].length; j++) {
				if (this == unplacedTiles[1][j].tileGroup) {
					unplacedtileMouseEnter(1, j + 1)
				}
			} 
		}
		unplacedTiles[1][piece - 1].tileGroup.onMouseLeave = function(event) {
			for (var j = 0; j < unplacedTiles[0].length; j++) {
				if (this == unplacedTiles[1][j].tileGroup) {
					unplacedtileMouseLeave(1, j + 1)
				}
			} 
		}
	}

	for (var i = 0; i < 5; i++) {
		var tileStacked = new StackedTile(NECROMANCER, PLAYER1, i);
		tileStacked.tileGroup.visible = false;
		tileStack.push(tileStacked);
	}

	addTile(0, 0, [PLAYER1, EMPTY]);

	doConnect();
}

/******************************************************************************
*************************** Websockect Communication **************************
******************************************************************************/

var CONFIG_MSG = 'CONFIG',
	READY_MSG = 'READY',
	PLAYMOVE_MSG = 'PLAY',
	PAUSE_MSG = 'PAUSE',
	NEXT_MSG = 'NEXT',
	PREVIOUS_MSG = 'PREVIOUS',
	FINISHED_MSG = 'FINISHED',
	ACKNOWLEDGEMENT_MSG = 'ACKNOWLEDGEMENT',
	ACTIONS_MSG = 'ACTIONS',
	HASMOVED_MSG = 'MOVE';

var CONFIG_HvH = 'human vs human',
	CONFIG_HvA = 'human vs ai',
	CONFIG_AvH = 'ai vs human',
	CONFIG_AvA = 'ai vs ai',
	CONFIG_R = 'replay';

function doConnect() {
	console.log("Connected at ws://localhost:8500/");
  websocket = new WebSocket("ws://localhost:8500/");
  websocket.onopen = function(evt) { onOpen(evt) };
  websocket.onclose = function(evt) { onClose(evt) };
  websocket.onmessage = function(evt) { onMessage(evt) };
  websocket.onerror = function(evt) { onError(evt) };
}

function onOpen(evt) {
	console.log("onOpen");
}

function onClose(evt) {
	console.log("onClose");
}

function onMessage(evt) {
	var msg = evt.data.trim().split("\n");
	if (msg[0] == CONFIG_MSG) {
		if (msg[1] == CONFIG_R) {
			setReplayConfig();
		}
		else {
			setPlayConfig(msg[1]);
		}
	}
	else if (msg[0] == PLAYMOVE_MSG) {
		playAction(msg.slice(1));
		doSend(ACKNOWLEDGEMENT_MSG + "\n");
	}
	else if (msg[0] == PREVIOUS_MSG) {
		undoAction(msg.slice(1));
	}
	else if (msg[0] == FINISHED_MSG) {
		finished(msg.slice(1));
	}
	else if (msg[0] == ACTIONS_MSG) {
		possibleActions(msg.slice(1));
	}
}

function onError(evt) {
	console.log("onError: " + evt);
	websocket.close();
}

function doSend(message) {
	websocket.send(message);
}

function doDisconnect() {
	console.log("doDisconnect");
	websocket.close();
}

function setReplayConfig() {
	playPauseButton.buttonGroup.visible = true;
	previousButton.buttonGroup.visible = true;
	nextButton.buttonGroup.visible = true;
	activatePlayPause();
	desactivateNext();
	desactivatePrevious();

	doSend(READY_MSG + "\n" + CONFIG_R);
}

function setPlayConfig(configType) {
	nextActive = false;
	previousActive = false;
	playPauseActive = false;
	playPauseButton.buttonGroup.visible = false;
	previousButton.buttonGroup.visible = false;
	nextButton.buttonGroup.visible = false;
	doSend(READY_MSG + "\n" + configType);
}

function activateNext() {
	nextActive = true;
	nextButton.bg.fillColor = prevNextColor;
	nextButton.raster.source = nextImage;
}

function desactivateNext() {
	nextActive = false;
	nextButton.bg.fillColor = prevNextDisabledColor;
	nextButton.raster.source = nextDisabledImage;
}

function activatePrevious() {
	previousActive = true;
	previousButton.bg.fillColor = prevNextColor;
	previousButton.raster.source = previousImage;
}

function desactivatePrevious() {
	previousActive = false;
	previousButton.bg.fillColor = prevNextDisabledColor;
	previousButton.raster.source = previousDisabledImage;
}

function activatePlayPause() {
	playPauseActive = true;
	playPauseButton.bg.fillColor = playPauseColor;
	if (playModeOn) {
		playPauseButton.raster.source = pauseImage;
	}
	else {
		playPauseButton.raster.source = playImage;
	}
}

function desactivatePlayPause() {
	playPauseActive = false;
	playPauseButton.bg.fillColor = playPauseDisabledColor;
	playPauseButton.raster.source = playDisabledImage;
	playModeOn = false;
}

function playPauseClicked() {
	if (playPauseActive) {
		if (playModeOn) {
			playPauseButton.raster.source = playImage;
			doSend(PAUSE_MSG + "\n");
			if (step > 1) {
				activatePrevious();
			}
			activateNext();
		}
		else {
			playPauseButton.raster.source = pauseImage;
			doSend(PLAYMOVE_MSG + "\n");
			desactivatePrevious();
			desactivateNext();
		}
		playModeOn = !playModeOn;
	}
}

function nextClicked() {
	if (nextActive){
		doSend(NEXT_MSG + "\n");
	}
}

function previousClicked() {
	if (previousActive) {
		doSend(PREVIOUS_MSG + "\n");
	}
}

function unplacedTileClicked(player, pieceType) {
	if (selectedTile == '' && player == currentPlayer) {
		if (possiblePlacements.containsKey(pieceType)) {
			selectedTile = pieceType;
			unplacedTiles[currentPlayer][pieceType - 1].hexagon.strokeWidth = selectedStrokeWidth;
			unplacedTiles[currentPlayer][pieceType - 1].hexagon.strokeColor = selectedStrokeColor;
			var placements = possiblePlacements.get(selectedTile);
			for (var i = 0; i < placements.length; i++) {
				tiles.get(coordToKey(placements[i][0], placements[i][1])).hexagon.strokeWidth = possibleStrokeWidth;
				tiles.get(coordToKey(placements[i][0], placements[i][1])).hexagon.strokeColor = possibleStrokeColor;
			}
			statusLine2.content = 'Click on a highlighted tile\nto perform your move.';
		}
	}
	else if (selectedTile == pieceType && player == currentPlayer){
		selectedTile = '';
		unplacedTiles[currentPlayer][pieceType - 1].hexagon.strokeWidth = normalStrokeWidth;
		unplacedTiles[currentPlayer][pieceType - 1].hexagon.strokeColor = strokeColors[player];
		var placements = possiblePlacements.get(pieceType);
		for (var i = 0; i < placements.length; i++) {
			tiles.get(coordToKey(placements[i][0], placements[i][1])).updateColor();
		}
		statusLine2.content = 'Click on a tile to select it.';
	}
}

function tileClicked(q, r) {
	if (selectedTile == '' && possibleMoves.containsKey(coordToKey(q, r))) {
		selectedTile = coordToKey(q, r);
		tiles.get(selectedTile).hexagon.strokeWidth = selectedStrokeWidth;
		tiles.get(selectedTile).hexagon.strokeColor = selectedStrokeColor;
		var moves = possibleMoves.get(selectedTile)
		for (var i = 0; i < moves.length; i++) {
			tiles.get(coordToKey(moves[i][0], moves[i][1])).hexagon.strokeWidth = possibleStrokeWidth;
			tiles.get(coordToKey(moves[i][0], moves[i][1])).hexagon.strokeColor = possibleStrokeColor;
		}
	}
	else if (selectedTile == coordToKey(q, r)) {
		selectedTile = '';
		var tile = tiles.get(coordToKey(q, r));
		tile.updateColor();
		var moves = possibleMoves.get(coordToKey(q, r))
		for (var i = 0; i < moves.length; i++) {
			tiles.get(coordToKey(moves[i][0], moves[i][1])).updateColor();
		}
	}
	else if (typeof selectedTile == "number") {
		var placements = possiblePlacements.get(selectedTile)
		for (var i = 0; i < placements.length; i ++) {
			if (placements[i][0] == q && placements[i][1] == r) {
				placementPerformed(selectedTile, q, r)
				i = placements.length
			}
		}
	}
	else if (selectedTile != '' && typeof selectedTile == "string") {
		var moves = possibleMoves.get(selectedTile)
		for (var i = 0; i < moves.length; i ++) {
			if (moves[i][0] == q && moves[i][1] == r) {
				movePerformed(selectedTile, q, r)
				i = moves.length
			}
		}
	}
}

function unplacedtileMouseEnter(player, pieceType) {
	if (helpOn) {
		descriptionCard.text.content = descriptionTitles[pieceType - 1];
		descriptionLine.content = descriptionTexts[pieceType - 1] + "\n\nMoves:\n" + moveTexts[pieceType - 1];
		descriptionCard.cardGroup.visible = true
		descriptionLine.visible = true
	}
	if (selectedTile == '' && player == currentPlayer) {
		if (possiblePlacements.containsKey(pieceType)) {
			unplacedTiles[currentPlayer][pieceType - 1].hexagon.strokeWidth = possibleStrokeWidth;
			unplacedTiles[currentPlayer][pieceType - 1].hexagon.strokeColor = possibleStrokeColor;
		}
	}
}

function unplacedtileMouseLeave(player, pieceType) {
	if (helpOn) {
		descriptionCard.cardGroup.visible = false
		descriptionLine.visible = false
	}
	if (selectedTile == '' && player == currentPlayer) {
		if (possiblePlacements.containsKey(pieceType)) {
			unplacedTiles[currentPlayer][pieceType - 1].updateColor();
		}
	}
}

function tileMouseEnter(q, r) {
	var tile = tiles.get(coordToKey(q, r));
	if (tile.pieceType.length > 1) {
		stackCard.cardGroup.visible = true;
		for (var i = 0; i < tile.pieceType.length; i++) {
			tileStack[i].tileGroup.visible = true;
			tileStack[i].player = tile.pieceType[i][0];
			tileStack[i].pieceType = tile.pieceType[i][1];
			tileStack[i].updateColor();
		}
	}
	if (selectedTile == '' && possibleMoves.containsKey(coordToKey(q, r))) {
		tile.hexagon.strokeWidth = possibleStrokeWidth;
		tile.hexagon.strokeColor = possibleStrokeColor;
	}
}

function tileMouseLeave(q, r) {
	var tile = tiles.get(coordToKey(q, r));
	if (tile.pieceType.length > 1) {
		stackCard.cardGroup.visible = false;
		for (var i = 0; i < tile.pieceType.length; i++) {
			tileStack[i].tileGroup.visible = false;
		}
	}
	if (selectedTile == '' && possibleMoves.containsKey(coordToKey(q, r))) {
		tile.updateColor();
	}
}

function helpSwitchClicked() {
	if (helpOn) {
		helpRaster.source = helpOffImage;
	}
	else {
		helpRaster.source = helpOnImage;
	}
	helpOn = !helpOn
}

function playAction(action) {
	currentPlayer = PLAYER1;
	if (parseInt(action[0]) == -1) {
		currentPlayer = PLAYER2;
	}
	step = parseInt(action[1]) + 1;
	if (!playModeOn) {
		activatePrevious();
	}
	var moveType = action[2];
	var fromPos = action[3].split(" ").map(function(key, val, array) {
    return parseInt(key);
  });
	var toPos = action[4].split(" ").map(function(key, val, array) {
		return parseInt(key);
  });
	statusLine1.content = 'Step ' + (step) + ": " + 'Player ' + (2 - currentPlayer) + "'s turn";
	statusLine2.content = ''
	if (moveType == 'P') {
		unplacedTiles[currentPlayer][Math.abs(fromPos[0]) - 1].quantity -= 1;
		unplacedTiles[currentPlayer][Math.abs(fromPos[0]) - 1].text.content = unplacedTiles[currentPlayer][Math.abs(fromPos[0]) - 1].quantity;
		placeTile(toPos[0], toPos[1], [currentPlayer, Math.abs(fromPos[0])]);
	}
	else if (moveType == 'M') {
		moveTile(fromPos[0], fromPos[1], toPos[0], toPos[1]);
	}
	else if (moveType == 'S') {
		statusLine2.content = 'Player ' + (2 - currentPlayer) + ' skips his turn.'
	}
	if (action.length > 5) {
		finished(action.slice(5))
	}
}

function undoAction(action) {
	currentPlayer = PLAYER1;
	if (parseInt(action[0]) == 1) {
		currentPlayer = PLAYER2;
	}
	step = parseInt(action[1]) + 1;
	if (step == 1) {
		desactivatePrevious();
	}
	activatePlayPause();
	activateNext();
	var moveType = action[2];
	var toPos = action[3].split(" ").map(function(key, val, array) {
    return parseInt(key);
  });
	var fromPos = action[4].split(" ").map(function(key, val, array) {
		return parseInt(key);
  });
	statusLine1.content = 'Step ' + (step) + ": " + 'Player ' + (2 - currentPlayer) + "'s turn";
	statusLine2.content = ''
	if (moveType == 'P') {
		unplacedTiles[1 - currentPlayer][Math.abs(toPos[0]) - 1].quantity += 1;
		unplacedTiles[1 - currentPlayer][Math.abs(toPos[0]) - 1].text.content = unplacedTiles[1 - currentPlayer][Math.abs(toPos[0]) - 1].quantity;
		unplaceTile(fromPos[0], fromPos[1]);
	}
	else if (moveType == 'M') {
		moveTile(fromPos[0], fromPos[1], toPos[0], toPos[1]);
	}
}

function finished(message) {
	statusLine1.content = message[0];
	if (message.length > 1) {
		statusLine2.content = message[1];
	}
	playPauseButton.buttonGroup.visible = true
	nextButton.buttonGroup.visible = true
	previousButton.buttonGroup.visible = true
	desactivateNext();
	desactivatePlayPause();
	activatePrevious();
}

function placeTile(q, r, pieceType) {
	var coordKey = coordToKey(q, r);
	if (tiles.containsKey(coordKey)) {
		tiles.get(coordKey).pieceType = [pieceType];
		tiles.get(coordKey).updateColor();
		var neighbourCoords = getTileNeighbourCoordinates(q, r);
		for(var i = 0; i < neighbourCoords.length; i++) {
	  	if(!tiles.containsKey(coordToKey(neighbourCoords[i][0], neighbourCoords[i][1]))) {
	  		addTile(neighbourCoords[i][0], neighbourCoords[i][1], [PLAYER1, EMPTY]);
			}
	  }
	  centerBoard();
	}
	else {
		addTile(q, r, pieceType);
	}
}

function unplaceTile(q, r) {
	var coordKey = coordToKey(q, r);
	if (tiles.containsKey(coordKey)) {
		tiles.get(coordKey).pieceType = [[PLAYER1, EMPTY]];
		tiles.get(coordKey).updateColor();
		var neighbourCoords = getTileNeighbourCoordinates(q, r);
		for(var i = 0; i < neighbourCoords.length; i++) {
			var coordKey = coordToKey(neighbourCoords[i][0], neighbourCoords[i][1])
  		if(tiles.containsKey(coordKey)) {
  			if (tiles.get(coordKey).pieceType[0][1] == EMPTY && isIsolated(neighbourCoords[i][0], neighbourCoords[i][1])) {
  				var tileToRemove = tiles.remove(coordToKey(neighbourCoords[i][0], neighbourCoords[i][1]));
  				tileToRemove.tileGroup.remove();
  			}
			}
  	}
	  centerBoard();
	}
	else {
		console.log("There is an error somewhere: You cannot unplace a tile that doesn't exist")
	}
}

function moveTile(q1, r1, q2, r2) {
	var coordKey1 = coordToKey(q1, r1);
	var coordKey2 = coordToKey(q2, r2);
	var pieceType1 = tiles.get(coordKey1).pieceType[tiles.get(coordKey1).pieceType.length - 1];
	if (tiles.get(coordKey1).pieceType.length == 1) {
		tiles.get(coordKey1).pieceType = [[PLAYER1, EMPTY]];
	}
	else {
		tiles.get(coordKey1).pieceType.pop();
	}
	if (tiles.get(coordKey2).pieceType.length == 1 && tiles.get(coordKey2).pieceType[0][1] == EMPTY) {
		tiles.get(coordKey2).pieceType = [pieceType1];
	}
	else {
		tiles.get(coordKey2).pieceType.push(pieceType1);
	}
	tiles.get(coordKey1).updateColor();
	tiles.get(coordKey2).updateColor();
	var neighbourCoords1 = getTileNeighbourCoordinates(q1, r1);
	for(var i = 0; i < neighbourCoords1.length; i++) {
  	if(tiles.containsKey(coordToKey(neighbourCoords1[i][0], neighbourCoords1[i][1]))) {
  		if (isIsolated(neighbourCoords1[i][0], neighbourCoords1[i][1])) {
  			var tileToRemove = tiles.remove(coordToKey(neighbourCoords1[i][0], neighbourCoords1[i][1]));
  			tileToRemove.tileGroup.remove();
  		}
		}
  }
  var neighbourCoords2 = getTileNeighbourCoordinates(q2, r2);
	for(var i = 0; i < neighbourCoords2.length; i++) {
  	if(!tiles.containsKey(coordToKey(neighbourCoords2[i][0], neighbourCoords2[i][1]))) {
	  	addTile(neighbourCoords2[i][0], neighbourCoords2[i][1], [PLAYER1, EMPTY]);
		}
  }
  centerBoard();
}

function possibleActions(msg) {
	currentPlayer = PLAYER1;
	if (parseInt(msg[0]) == -1) {
		currentPlayer = PLAYER2;
	}
	step = parseInt(msg[1]);
	statusLine1.content = 'Step ' + step + ": " + 'Player ' + (currentPlayer + 1) + "'s turn";
	statusLine2.content = 'Click on a tile to select it.';
	for(var i = 2; i < msg.length; i++) {
  	var action = msg[i].split(" ");
  	if (action[0] == 'P') {
  		if (possiblePlacements.containsKey(Math.abs(parseInt(action[1])))) {
  			possiblePlacements.get(Math.abs(parseInt(action[1]))).push([parseInt(action[3]), parseInt(action[4])]);
  		}
  		else {
	  		possiblePlacements.set(Math.abs(parseInt(action[1])), [[parseInt(action[3]), parseInt(action[4])]]);
	  	}
  	}
  	else if (action[0] == 'M') {
  		var fromPos = coordToKey(parseInt(action[1]), parseInt(action[2]));
  		var toPos = [parseInt(action[3]), parseInt(action[4])];
  		if (possibleMoves.containsKey(fromPos)) {
  			possibleMoves.get(fromPos).push(toPos);
  		}
  		else {
  			possibleMoves.set(fromPos, [toPos]);
  		}
  	}
  	else if (action[0] == 'S') {
  		skipCard.cardGroup.visible = true;
  		okButton.buttonGroup.visible = true;
  		skipLine.visible = true;
  	}
  	else {
  		console.log("I have received an invalid action.");
  	}
  }
}

function placementPerformed(pieceType, q, r) {
	var actionStr = "P\n";
	if (currentPlayer == PLAYER1) {
		actionStr += pieceType + "\n";
	}
	else {
		actionStr += -pieceType + "\n";
	}
	actionStr += unplacedTiles[currentPlayer][pieceType - 1].quantity + "\n";
	actionStr += q + "\n";
	actionStr += r;
	unplacedTiles[currentPlayer][pieceType - 1].updateColor();
	var posPlacements = possiblePlacements.get(pieceType);
	for (var i = 0; i < posPlacements.length; i++) {
		tiles.get(coordToKey(posPlacements[i][0], posPlacements[i][1])).updateColor();
	}
	possibleMoves.clear();
	possiblePlacements.clear();
	selectedTile = '';
	doSend(HASMOVED_MSG + "\n" + actionStr);
}

function movePerformed(pieceType, q, r) {
	var actionStr = "M\n";
	actionStr += pieceType.split(" ")[0] + "\n";
	actionStr += pieceType.split(" ")[1] + "\n";
	actionStr += q + "\n"
	actionStr += r
	var posMoves = possibleMoves.get(pieceType)
	for (var i = 0; i < posMoves.length; i++) {
		tiles.get(coordToKey(posMoves[i][0], posMoves[i][1])).updateColor();
	}
	possibleMoves.clear();
	possiblePlacements.clear();
	selectedTile = '';
	doSend(HASMOVED_MSG + "\n" + actionStr);
}

function skipPerformed(pieceType, q, r) {
	if (okButton.buttonGroup.visible) {
		var actionStr = "S\n";
		actionStr += 0 + "\n";
		actionStr += 0 + "\n";
		actionStr += 0 + "\n"
		actionStr += 0
		possibleMoves.clear();
		possiblePlacements.clear();
		selectedTile = '';
		skipCard.cardGroup.visible = false;
		okButton.buttonGroup.visible = false;
		skipLine.visible = false;
		doSend(HASMOVED_MSG + "\n" + actionStr);
	}
}

function clearBoard() {
	var keys = tiles.keys();
  for(var i = 0; i < keys.length; i++) {
  	var tileToRemove = tiles.remove(keys[i]);
  	tileToRemove.tileGroup.remove();
  }
}

function onKeyDown(event) {
	if(event.key == 'space') {
		playPauseClicked();
	}

	if(event.key == 'left') {
		previousClicked();
	}

	if(event.key == 'right') {
		nextClicked();
	}
}

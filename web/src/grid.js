import { SPACE, GRID_SQUARE } from './constants.js'
import { WALL_STROKE_WIDTH as strokeWidth } from './constants.js'
import { equal, coordinateFromEdge } from './util.js'
const { Path, Size, Point, Color, Group } = paper

export function drawGrid() {
  var gridSquare = new Path.Rectangle({
    size: [GRID_SQUARE, GRID_SQUARE],
    strokeColor: '#ddd',
    fillColor: 'white',
    locked: true,
  })

  var definition = new SymbolDefinition(gridSquare)
  const rows = 45
  const columns = 80
  const width = columns * GRID_SQUARE
  const height = rows * GRID_SQUARE
  var column = 0

  const group = new Group(new Path.Rectangle({
    center: [width * 0.5, height * 0.5],
    size: [width, height],
    fillColor: 'white',
  }))

  for (var row = 0; row < rows; row++) {
    var line = new Path.Line(new Point(0, row * GRID_SQUARE), new Point(width, row * GRID_SQUARE))
    line.strokeColor = '#ddd'
    group.addChild(line)
    for (column = 0; column < columns; column++) {
      var line = new Path.Line(new Point(column * GRID_SQUARE, 0), new Point(column * GRID_SQUARE, height))
      line.strokeColor = '#ddd'
      group.addChild(line)
    }
  }

  group.replaceWith(group.rasterize())
}

const ONE_COLOR = true
var cyclingColor = new Color(1, 0, 0)
const nextColor = () => {
  if (ONE_COLOR)
    return new Color(0.2, 0.2, 0.2)
  const oldColor = cyclingColor
  cyclingColor = cyclingColor.clone()
  cyclingColor.hue += 65
  return oldColor
}

const pathSpacesFromCurve = curve => {
  var curve = curve.clone()
  var count = curve.isStraight() ? Math.max(Math.round(curve.length / SPACE), 1) : 1
  var paths = []

  for (var i = 0; i < count; i++) {
    var newCurve
    if (i != count - 1)
      newCurve = curve.divideAt(curve.length / (count-i))


    var path = new Path({
      segments: [curve.segment1, curve.segment2],
      strokeWidth,
      strokeCap: 'round',
      strokeColor: nextColor(),
    })
    paths.push(path)

    curve = newCurve
  }

  return paths
}

export function rectangleChamber(opts) {
  var fillColor = new Color(0.7, 0.6, 0.7)
  var path = new Path.Rectangle({
    point: opts.point.multiply(SPACE),
    size: opts.size.multiply(SPACE),
    // strokeColor: '#333',
    fillColor: fillColor,
  })

  // add walls
  var color = new Color(1, 0, 0)
  var wallPaths = []

  for (var i = 0; i < path.curves.length; i++) {
    wallPaths = wallPaths + pathSpacesFromCurve(path.curves[i])
  }

  path.onMouseEnter = event => {
    var newColor = fillColor.clone()
    newColor.brightness *= 1.2
    path.fillColor = newColor
  }
  path.onMouseLeave = event => path.fillColor = fillColor
}

export function circleChamber(opts) {
  var center = opts.center.multiply(SPACE)
  var fillColor = new Color(0.6, 0.7, 0.7)
  var group = new Group()
  var path = new Path.Circle({
    center: center,
    radius: opts.radius * SPACE,
    // strokeColor: '#333',
    strokeWidth,
    fillColor,
  })

  var exitWidth = ((opts.radius * 2 % 2 == 0) ? 2 : 1) * SPACE
  var exitCorner = new Point(
    center.x - exitWidth / 2.0,
    path.bounds.top
  )

  // add well
  if (opts.well) {
    var oldPath = path
    path = oldPath.subtract(new Path.Circle({
      center: center,
      radius: exitWidth / 2.0
    }))
    oldPath.remove()
  }

  // add square exits
  for (var i = 0; i < 4; i++) {
    var exitPath = new Path.Rectangle({
      point: exitCorner,
      size: new Size(exitWidth, SPACE),
      fillColor: 'black'
    })

    exitPath.rotate(90 * i, center)

    exitPath.remove()
    oldPath = path
    path = oldPath.unite(exitPath)
    oldPath.remove()
  }

  var selected = null
  // add walls
  path.data.cardinals = {}
  for (var j = 0; j < path.curves.length; j++) {
    var curve = path.curves[j].clone()
    var bounds = curve.bounds

    var cardinal = curve.isStraight() &&
                   (equal(bounds.height, exitWidth) || equal(bounds.width, exitWidth))
    var pathlings = pathSpacesFromCurve(curve)

    if (cardinal) {
      var middle = curve.bounds.center
      var direction = null
      if (equal(middle.x, center.x)) {
        if (middle.y > center.y) {
          direction = 's'
        } else {
          direction = 'n'
        }
      } else if (equal(middle.y, center.y)) {
        if (middle.x > center.x) {
          direction = 'e'
        } else {
          direction = 'w'
        }
      }

      path.data.cardinals[direction] = pathlings

      pathlings.forEach(p => {
        (coordinateFromEdge(p.curves[0]))
      })
    }

    // if (!cardinal && pathlings[0].curves[0].isStraight()) {
    //   if (selected)
    //     selected.fullySelected = false
    //   selected = pathlings[0]
    //   selected.fullySelected = true
    // }

    group.addChildren(pathlings)
  }

  path.onMouseEnter = event => {
    var newColor = fillColor.clone()
    newColor.brightness *= 1.2
    path.fillColor = newColor
  }
  path.onMouseLeave = event => path.fillColor = fillColor

  path.onMouseDown = event => {
    const directions = ['n', 'e', 's', 'w']
    directions.forEach(direction => {
      var open = Math.random() < 0.5
      path.data.cardinals[direction].forEach(d => d.strokeWidth = open ? 0 : strokeWidth)
    })
  }

  group.addChild(path)
  // group.strokeWidth = strokeWidth
  return group
}

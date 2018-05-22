import { SPACE, GRID_SQUARE } from './constants.js'
import { WALL_STROKE_WIDTH as strokeWidth } from './constants.js'
import { equal, coordinateFromEdge } from './util.js'

const { Path, Size, Point, Color, Group } = paper

const doors = {}

export function door(opts) {
  var origin = opts.origin.multiply(SPACE)
  var size = (opts.size || 1) * SPACE
  var vertical = !!opts.vertical
  var doorWidth = SPACE * 0.5
  var key = `${opts.origin.x}_${opts.origin.y}_${vertical ? 'v' : 'h'}`

  if (doors[key]) {
    if (opts.toggle) {
      doors[key].remove()
      delete doors[key]
    }
    return
  }

  const calculatePoint = vertical => origin.subtract([
    vertical ? doorWidth * 0.5 : 0,
    vertical ? 0 : doorWidth * 0.5,
  ])

  const calculateSize = vertical => new Size(
    vertical ? doorWidth : size,
    vertical ? size : doorWidth,
  )

  var door = Path.Rectangle({
    point: calculatePoint(vertical),
    size: calculateSize(vertical),
    strokeWidth,
    strokeColor: '#222',
    fillColor: 'white',
  })

  doors[key] = door

  return door
}

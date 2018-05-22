import { drawGrid, rectangleChamber, circleChamber } from './grid.js'
import { door } from './door.js'
import { spaceFromPoint, coordinateFromPoint } from './util.js'
import { SPACE } from './constants.js'
const { Point, Size, Path } = paper

paper.install(window)
window.onload = () => {
  paper.setup('grid')
  drawGrid()

  rectangleChamber({
    point: new Point(1, 1),
    size: new Size(4, 8)
  })

  circleChamber({
    center: new Point(12, 5),
    radius: 4,
    well: true,
  })

  rectangleChamber({
    point: new Point(18, 3),
    size: new Size(5, 4)
  })

  circleChamber({
    center: new Point(27.5, 5.5),
    radius: 2.5,
      // well: true,
    })

  door({
    origin: new Point(1, 2),
    vertical: true
  })

  door({
    origin: new Point(2, 1),
    vertical: false
  })

  // paper.project.activeLayer.onClick = event => {
  //   mode = (mode + 1) % Object.keys(pointers).length
  //   updatePointerMode()
  // }

  const cellCenterForPoint = point => spaceFromPoint(point).center
  const setupPointers = () => {
    var cellPointer = Path.Rectangle({
      point: new Point(0, 0),
      size: new Size(SPACE, SPACE),
      strokeWidth: 2,
      strokeColor: 'white',
      blendMode: 'negation',
      locked: true,
    })
    pointers['cell'] = cellPointer
    cellPointer.data.moveHandler = event => {
      var center = cellCenterForPoint(event.point)
      cellPointer.position = center
      var coordinate = center.subtract(SPACE * 0.5).divide(SPACE)
      $('#debug').text(coordinate.toString())
    }

    var sidePointer = Path.Line({
      from: [0, 0],
      to: [SPACE, 0],
      strokeWidth: 2,
      strokeColor: 'white',
      blendMode: 'negation',
      locked: true,
    })
    pointers['side'] = sidePointer
    sidePointer.data.moveHandler = event => {
      var center = cellCenterForPoint(event.point)
      // get nearest side
      var degreesFromCenter = Math.atan2(event.point.y - center.y, event.point.x - center.x) * 180 / Math.PI
      var degreesFromTopLeft = (degreesFromCenter + 360 + 90 + 45) % 360
      var sideDist = SPACE * 0.5
      if (degreesFromTopLeft <= 90) {
        sidePointer.firstSegment.point = center.add([-sideDist, -sideDist])
        sidePointer.lastSegment.point = center.add([sideDist, -sideDist])
      } else if (degreesFromTopLeft <= 180) {
        sidePointer.firstSegment.point = center.add([sideDist, -sideDist])
        sidePointer.lastSegment.point = center.add([sideDist, sideDist])
      } else if (degreesFromTopLeft <= 270) {
        sidePointer.firstSegment.point = center.add([sideDist, sideDist])
        sidePointer.lastSegment.point = center.add([-sideDist, sideDist])
      } else if (degreesFromTopLeft <= 360) {
        sidePointer.firstSegment.point = center.add([-sideDist, sideDist])
        sidePointer.lastSegment.point = center.add([-sideDist, -sideDist])
      }
      // $('#debug').text(degreesFromTopLeft)
    }

    var doorPointer = door({ origin: new Point(0, 0) })
    doorPointer.applyMatrix = false
    doorPointer.locked = true
    pointers['door'] = doorPointer
    doorPointer.data.moveHandler = event => {
      var space = spaceFromPoint(event.point)
      var relativePoint = event.point.subtract(space.topLeft)
      var vertical = relativePoint.x < relativePoint.y
      doorPointer.rotation = vertical ? 90 : 0
      doorPointer.position = space.topLeft.add(
        vertical ? 0 : SPACE * 0.5,
        vertical ? SPACE * 0.5 : 0,
      )
    }

    const pointerLayer = new paper.Layer()
    for (var name in pointers) {
      var pointer = pointers[name]
      paper.project.layers[0].on('mousemove', pointer.data.moveHandler)
      pointerLayer.addChild(pointer)
    }
    paper.project.layers[0].activate()

    paper.project.activeLayer.on('click', event => {
      if (pointers['door'].visible) {
        var space = spaceFromPoint(event.point)
        var relativePoint = event.point.subtract(space.topLeft)
        var vertical = relativePoint.x < relativePoint.y
        door({
          origin: coordinateFromPoint(event.point),
          vertical,
          toggle: true,
        })
      }
    })
  }
  setupPointers()
  updatePointerMode()
}

var mode = 0
const pointers = {}
const updatePointerMode = () => {
  pointers['cell'].visible = (mode === 0)
  pointers['side'].visible = (mode === 1)
  pointers['door'].visible = (mode === 2)
}

window.addEventListener('keypress', event => {
  if (event.key == 'w')
    mode = 1
  else if (event.key == 'd')
    mode = 2
  else if (event.key == 's')
    mode = 0

  updatePointerMode()
})

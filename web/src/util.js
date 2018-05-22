import { SPACE } from './constants.js'
const { Point, Rectangle } = paper

export const equal = (a, b, threshold=0.0001) => Math.abs(a - b) < Math.abs(threshold)

export const coordinateFromPoint = point => new Point(
    Math.floor(point.x / SPACE),
    Math.floor(point.y / SPACE),
)

export const spaceFromPoint = point => new Rectangle({
    point: coordinateFromPoint(point).multiply(SPACE),
    size: [SPACE, SPACE]
})

export const coordinateFromEdge = curve => {
    const edgeBounds = curve.bounds
    const midpoint = edgeBounds.center
    const vertical = edgeBounds.height > edgeBounds.width
    const coordinate = coordinateFromPoint(midpoint.add([
        vertical ? SPACE * 0.5 : 0,
        vertical ? 0 : SPACE * 0.5,
    ]))
    console.log(vertical ? 'v' : 'h', coordinate.toString())
    return coordinate
}
